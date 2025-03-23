import importlib
import os
from datetime import datetime

from flask import (
    Flask,
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from enginy.database import init_app
from enginy.engine_config import (
    AVAILABLE_PARTS,
    CLASS_MAP,
    DATA_CLASS_MAP,
    EnginePartType,
)
from enginy.forms import BasePartForm
from enginy.models import EnginePart as EnginePartModel
from enginy.repositories import EnginePartRepository

MIN_REQUIRED_ENGINE_PARTS = 3

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "default-secret-key")

init_app(app)

# Check MongoDB status
mongodb_available = app.config.get("MONGO_AVAILABLE", False)
if not mongodb_available:
    app.logger.warning("MongoDB is not available. Application running in limited mode.")

ENGINE_PARTS_CLASSES = CLASS_MAP

# Dynamically import and map form classes.
AVAILABLE_FORMS: dict[str, BasePartForm] = {}
for part in AVAILABLE_PARTS:
    try:
        form_class = getattr(importlib.import_module("enginy.forms"), f"{part}Form")
        AVAILABLE_FORMS[part] = form_class
    except (ImportError, AttributeError) as e:
        app.logger.error(f"Could not import form for {part}: {e}")


def get_current_user_id() -> str | None:
    """Get the current user ID from session"""
    # Placeholder: In the future, this will be from authentication.
    # For now, we'll use a session-based pseudo user ID
    if "user_id" not in session:
        session["user_id"] = f"session_{datetime.now().timestamp()}"
    return session["user_id"]


@app.route("/")
def index() -> str:
    """
    Render the main page with a list of created engine parts.

    Returns:
        Rendered HTML page showing the engine parts.
    """
    user_id = get_current_user_id()
    engine_parts = EnginePartRepository.get_all_parts(user_id)

    show_welcome = False
    if not session.get("welcome_shown"):
        show_welcome = True
        session["welcome_shown"] = True

    return render_template(
        "index.html", engine_parts=engine_parts, show_welcome=show_welcome
    )


@app.route("/create_part", methods=["GET", "POST"])
def create_part() -> str | Response:
    """
    Create a new engine part by handling GET and POST requests.

    GET:
        Render the form page to create a new engine part.

    POST:
        Validate and process the submitted form data to create the engine part.

    Returns:
        - Redirect to the index page after successful creation.
        - Rendered form page with errors if validation fails.
    """
    # Get the type of part from query parameter (default is "Inlet")
    part_type_str = request.args.get("type", EnginePartType.INLET.value)
    user_id = get_current_user_id()

    try:
        part_type = EnginePartType(part_type_str)
    except ValueError:
        part_type = EnginePartType.INLET

    # Get the corresponding form class (defaulting to InletForm) and create an instance.
    form_class = AVAILABLE_FORMS.get(
        part_type.value, AVAILABLE_FORMS[EnginePartType.INLET.value]
    )
    form = form_class()

    # Dynamically set choice lists for dependency fields, e.g., inlet choice for Compressor.
    for field_name, dependency_name in form.get_dependency_fields().items():
        parts = EnginePartRepository.get_parts_by_type(dependency_name, user_id)
        choices = [(part["id"], part["user_part_name"]) for part in parts]
        getattr(form, field_name).choices = choices

    if form.validate_on_submit():
        data = form.data
        user_part_name = data.pop("user_part_name")
        data.pop("csrf_token", None)
        data.pop("submit", None)

        dependency_ids = {}
        part_dependencies = {}

        # Collect dependencies and reconstruct dependency objects
        for field_name, dependency_name in form.get_dependency_fields().items():
            dependency_id = data.pop(field_name)
            dependency_ids[dependency_name.lower()] = dependency_id

            # Reconstruct the dependency object
            dependency_obj = EnginePartRepository.get_part_object(dependency_id)
            if dependency_obj:
                part_dependencies[dependency_name.lower()] = dependency_obj

        # Create the data object for the part
        data_class = DATA_CLASS_MAP.get(part_type.value)
        if data_class:
            data_obj = data_class(**data)

            # Create the part instance
            part_class = ENGINE_PARTS_CLASSES[part_type.value]

            if part_dependencies:
                part_instance = part_class(data_obj, **part_dependencies)
            else:
                part_instance = part_class(data_obj)

            # Save to database
            part_dict = {
                "part": part_instance,
                "name": part_type.value,
                "user_part_name": user_part_name,
                "part_type": part_type.value,
            }

            part_id = EnginePartRepository.save_part(part_dict, user_id)

            for dep_id in dependency_ids.values():
                EnginePartModel.add_dependency(part_id, dep_id)

            flash(f"{part_type.value} created successfully!", "success")
            return redirect(url_for("index"))
        else:
            flash(f"Error creating {part_type.value}. Data class not found.", "danger")

    return render_template(
        "create_part.html",
        form=form,
        available_parts=AVAILABLE_PARTS,
        current_type=part_type.value,
    )


@app.route("/delete_part/<string:part_id>", methods=["POST"])
def delete_part(part_id: str) -> Response:
    """
    Delete an existing engine part by its ID.

    Args:
        part_id (str): The ID of the engine part to be deleted.

    Returns:
        A redirect response to the index page.
    """
    part = EnginePartRepository.get_part(part_id)
    if part:
        success = EnginePartRepository.delete_part(part_id)
        if success:
            flash(
                f'{part["name"]} "{part["user_part_name"]}" deleted successfully!',
                "success",
            )
        else:
            flash(f"Failed to delete {part['name']}", "danger")
    else:
        flash("Invalid part ID for deletion.", "danger")

    return redirect(url_for("index"))


@app.route("/analyze_part/<string:part_id>", methods=["GET"])
def analyze_part(part_id: str) -> str | Response:
    """
    Analyze a single engine part and render an analysis page.

    First checks for a cached analysis result. If not found, reconstructs
    the part object and runs the analysis.

    Args:
        part_id (str): The ID of the engine part to analyze.

    Returns:
        Rendered HTML analysis page if valid,
        Otherwise, a JSON error response.
    """
    # First check for cached analysis
    cached_analysis = EnginePartRepository.get_analysis_result(part_id)
    if cached_analysis:
        flash("Showing saved analysis result.", "info")
        return render_template("analyze.html", analysis=cached_analysis)

    # No cached result, retrieve and reconstruct the part object
    part_obj = EnginePartRepository.get_part_object(part_id)

    if part_obj:
        try:
            # Call the analyze method on the reconstructed part object
            analysis_json = part_obj.analyze()

            # Cache the analysis result
            EnginePartRepository.save_analysis_result(part_id, analysis_json)

            flash("Analysis completed successfully!", "success")
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            return render_template("analyze.html", analysis=analysis_json, now=now)
        except Exception as e:
            flash(f"Error during analysis: {str(e)}", "danger")
            return jsonify({"error": f"Analysis error: {str(e)}"}), 500
    else:
        flash("Invalid part ID.", "danger")
        return jsonify({"error": "Invalid part ID"}), 400


@app.route("/analyze_engine", methods=["POST"])
def analyze_engine() -> Response:
    """
    Perform analysis on the entire engine with all parts.

    Returns:
        JSON response with analysis results or error message.
    """
    user_id = get_current_user_id()
    parts = EnginePartRepository.get_all_parts(user_id)

    if len(parts) < MIN_REQUIRED_ENGINE_PARTS:
        flash("Not enough parts to build the engine!", "danger")
        return jsonify({"error": "Not enough parts to build the engine!"}), 400

    # Simple placeholder response
    engine_analysis = {
        "status": "success",
        "message": "Engine analysis placeholder. Real implementation coming soon.",
        "timestamp": datetime.now().isoformat(),
        "parts_count": len(parts),
        "performance": {
            "thrust": "10,000 N",
            "specific_fuel_consumption": "0.5 kg/N/hr",
            "efficiency": "35%",
            "temperature_ratio": "4.2",
        },
    }

    flash("Engine analysis completed!", "success")
    return jsonify(engine_analysis)


if __name__ == "__main__":
    app.run(debug=True)
