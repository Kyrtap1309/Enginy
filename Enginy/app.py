import importlib
import os
import json
from datetime import datetime
from enum import Enum
from typing import Dict, List, Union, Optional
from flask import Flask, render_template, request, redirect, url_for, jsonify, Response, flash, session
from bson import json_util

from .engine_parts.engine_part import EnginePart
from .forms import BasePartForm
from .database import init_app, get_db
from .repositories import EnginePartRepository
from .models import EnginePart as EnginePartModel

class EnginePartType(Enum):
    INLET = "Inlet"
    COMPRESSOR = "Compressor"
    COMBUSTOR = "Combustor"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "default-secret-key")

init_app(app)

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

def get_current_user_id() -> Optional[str]:
    """Get the current user ID from session"""
    # Placeholder: In the future, this will be from authentification.
    # For now, we'll use a session-based pseudo user ID
    if 'user_id' not in session:
        session['user_id'] =  f"session_{datetime.now().timestamp()}"
    return session['user_id']

@app.route('/')
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
    
    return render_template('index.html', engine_parts=engine_parts, show_welcome=show_welcome)


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
    user_id = get_current_user_id()

    try:
        part_type = EnginePartType(part_type_str)
    except ValueError:
        part_type = EnginePartType.INLET
    
    # Get the corresponding form class (defaulting to InletForm) and create an instance.
    form_class = AVAILABLE_FORMS.get(part_type.value, AVAILABLE_FORMS[EnginePartType.INLET.value])
    form = form_class()

    # Dynamically set choice lists for dependency fields, e.g., inlet choice for Compressor.
    for field_name, dependency_name in form.get_dependency_fields().items():

        parts = EnginePartRepository.get_parts_by_type(dependency_name, user_id)
        choices = [(part['id'], part['user_part_name']) for part in parts]
        getattr(form, field_name).choices = choices

    if form.validate_on_submit():
        data = form.data
        user_part_name = data.pop("user_part_name")
        data.pop("csrf_token", None)
        data.pop("submit", None)

        dependencies = {}
        dependency_ids ={}

        for field_name, dependency_name in form.get_dependency_fields().items():
            dependency_id = data.pop(field_name)
            dependency_ids[dependency_name.lower()] = dependency_id

            # Here we would retrieve the actual part from the database
            # and reconstruct the part object
            # This is a complex part that requires serialization/deserialization strategies
            # For now, this is a placeholder
            
            # dependencies[dependency_name.lower()] = get_dependency_object(dependency_id)
        
        #create the part instance
        part_class = ENGINE_PARTS_CLASSES[part_type.value]
        
        #part_instance = part_class(data, **dependencies)


        # For now, store just the data without reconstructing objects
        part_dict = {
            'part_data': data,
            'name': part_type.value,
            'user_part_name': user_part_name,
            'part_type': part_type.value,
        }

        part_id = EnginePartRepository.save_part(part_dict, user_id)

        for dep_name, dep_id in dependency_ids.items():
            EnginePartModel.add_dependency(part_id, dep_id)

        flash(f'{part_type.value} created successfully!', 'success')
        return redirect(url_for('index'))

    return render_template(
        'create_part.html', 
        form=form, 
        available_parts=AVAILABLE_PARTS, 
        current_type=part_type.value, 
    )


@app.route('/delete_part/<string:part_id>', methods=['POST'])
def delete_part(part_id: str) -> Response:
    """
    Delete an existing engine part by its ID.
    
    Args:
        part_index (str): The ID of the engine part to be deleted.
    
    Returns:
        A redirect response to the index page.
    """
    part = EnginePartRepository.get_part(part_id)
    if part:
        success = EnginePartRepository.delete_part(part_id)
        if success:
            flash(f'{part["name"]} deleted successfully!', 'success')
        else:
            flash(f'Failed to delete {part["name"]}', 'danger')
    else:
        flash("Invalid part ID for deletion.", "danger")

    return redirect(url_for('index'))


@app.route('/analyze_part/<string:part_id>', methods=['GET'])
def analyze_part(part_id: str) -> Union[str, Response]:
    """
    Analyze a single engine part and render an analysis page.
    
    Args:
        part_id (str): The ID of the engine part to analyze.
    
    Returns:
        Rendered HTML analysis page if valid,
        Otherwise, a JSON error response.
    """
    part = EnginePartRepository.get_part(part_id)
    if part:
        # For analysis, we need to reconstruct the original part object
        # This would require serialization/deserialization logic
        
        # Placeholder for demonstration
        analysis = {"data": [{"x": [1, 2, 3], "y": [4, 5, 6], "type": "scatter"}]}
        analysis_json = json.dumps(analysis)
        
        flash("Analysis completed successfully!", 'success')
        return render_template("analyze.html", analysis=analysis_json)
    
    flash("Invalid part ID.", "danger")
    return jsonify({'error': 'Invalid part ID'}), 400


@app.route('/analyze_engine', methods=['POST'])
def analyze_engine() -> Response:
    """
    PLACEHOLDER

    Perform analysis on the complete engine assembly.
    
    Returns:
        JSON response containing the engine analysis result.
    """
    user_id = get_current_user_id()
    parts = EnginePartRepository.get_all_parts(user_id)

    if len(parts) < 5:
        flash("Not enough parts to analyze the engine.", "danger")
        return jsonify({'error': 'Not enough parts to analyze the engine.'}), 400
    
    engine_analysis_result = "Complete Engine Analysis"
    flash("Complete engine analysis completed successfully!", 'success')
    return jsonify({'result': engine_analysis_result})

if __name__ == '__main__':
    app.run(debug=True)