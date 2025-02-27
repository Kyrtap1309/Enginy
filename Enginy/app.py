import importlib
import os
from enum import Enum
from typing import Dict, List, Union
from flask import Flask, render_template, request, redirect, url_for, jsonify, Response, flash
from .engine_parts.engine_part import EnginePart
from .forms import BasePartForm

class EnginePartType(Enum):
    INLET = "Inlet"
    COMPRESSOR = "Compressor"
    COMBUSTOR = "Combustor"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "default-secret-key")

# List of available engine parts.
AVAILABLE_PARTS: List[str] = [e.value for e in EnginePartType]

# Dynamically import and map engine part classes.
ENGINE_PARTS_CLASSES: Dict[str, EnginePart] = {
    part: getattr(importlib.import_module(f"Enginy.engine_parts.{part.lower()}"), part)
    for part in AVAILABLE_PARTS
}

# Dynamically import and map form classes.
AVAILABLE_FORMS: Dict[str, BasePartForm] = {
    part: getattr(importlib.import_module("Enginy.forms"), f"{part}Form")
    for part in AVAILABLE_PARTS
}


# Global list storing created engine parts.
engine_parts = []

@app.route('/')
def index() -> str:
    """
    Render the main page with a list of created engine parts.
    
    Returns:
        Rendered HTML page showing the engine parts.
    """
    return render_template('index.html', engine_parts=engine_parts)


@app.route('/create_part', methods=['GET', 'POST'])
def create_part() -> Union[str, Response]:
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
    part_type_str = request.args.get('type', EnginePartType.INLET.value)

    try:
        part_type = EnginePartType(part_type_str)
    except ValueError:
        part_type = EnginePartType.INLET
    
    # Get the corresponding form class (defaulting to InletForm) and create an instance.
    form_class = AVAILABLE_FORMS.get(part_type.value, AVAILABLE_FORMS[EnginePartType.INLET.value])
    form = form_class()

    # Dynamically set choice lists for dependency fields, e.g., inlet choice for Compressor.
    for field_name, dependency_name in form.get_dependency_fields().items():
        choices = [
            (i, ep["user_part_name"]) 
            for i, ep in enumerate(engine_parts) 
            if ep["name"] == dependency_name
        ]
        getattr(form, field_name).choices = choices

    if form.validate_on_submit():
        data = form.data
        user_part_name = data.pop("user_part_name")
        data.pop("csrf_token", None)
        data.pop("submit", None)

        dependencies = {}
        for field_name, dependency_name in form.get_dependency_fields().items():
            part_index = data.pop(field_name)
            dependencies[dependency_name.lower()] = engine_parts[part_index]["part"]

        part_class = ENGINE_PARTS_CLASSES[part_type.value]
        part_instance = part_class(data, **dependencies)

        engine_parts.append({
            'part': part_instance,
            'name': part_type.value,
            'user_part_name': user_part_name,
            'analysis': f"Analysis for {part_type.value}"
        })

        flash(f'{part_type.value} created successfully!', 'success')
        return redirect(url_for('index'))

    return render_template(
        'create_part.html', 
        form=form, 
        available_parts=AVAILABLE_PARTS, 
        current_type=part_type.value, 
        engine_parts=engine_parts
    )


@app.route('/delete_part/<int:part_index>', methods=['POST'])
def delete_part(part_index: int) -> Response:
    """
    Delete an existing engine part by its index.
    
    Args:
        part_index (int): The index of the engine part to be deleted.
    
    Returns:
        A redirect response to the index page.
    """
    if 0 <= part_index < len(engine_parts):
        removed_part = engine_parts.pop(part_index)
        flash(f'{removed_part["name"]} "{removed_part["user_part_name"]}" deleted successfully!', 'success')
    else:
        flash("Invalid part index for deletion.", 'danger')
    return redirect(url_for('index'))


@app.route('/analyze_part/<int:part_index>', methods=['GET'])
def analyze_part(part_index) -> Union[str, Response]:
    """
    Analyze a single engine part and render an analysis page.
    
    Args:
        part_index (int): The index of the engine part to analyze.
    
    Returns:
        Rendered HTML analysis page if valid,
        Otherwise, a JSON error response.
    """
    if 0 <= part_index < len(engine_parts):
        analysis = engine_parts[part_index]["part"].analyze()
        flash("Analysis completed successfully!", 'success')
        return render_template("analyze.html", analysis=analysis)
    flash("Invalid part index.", "danger")
    return jsonify({'error': 'Invalid part index'}), 400


@app.route('/analyze_engine', methods=['POST'])
def analyze_engine() -> Response:
    """
    PLACEHOLDER

    Perform analysis on the complete engine assembly.
    
    Note:
        At least 5 parts are required to perform a full analysis.
    
    Returns:
        JSON response containing the engine analysis result.
    """
    if len(engine_parts) < 5:
        flash("Not enough parts to build the engine!", "danger")
        return jsonify({'error': 'Not enough parts to build the engine!'}), 400

    # Placeholder for complete engine analysis logic.
    engine_analysis_result = "Complete Engine Analysis"
    flash("Complete engine analysis completed successfully!", 'success')
    return jsonify({'result': engine_analysis_result})


if __name__ == '__main__':
    app.run(debug=True)