import importlib
import os
import json
from datetime import datetime
from enum import Enum
from typing import Dict, List, Union, Optional
from flask import Flask, render_template, request, redirect, url_for, jsonify, Response, flash, session
from bson import json_util

from Enginy.engine_parts.engine_part import EnginePart
from Enginy.forms import BasePartForm
from Enginy.database import init_app, get_db
from Enginy.repositories import EnginePartRepository
from Enginy.models import EnginePart as EnginePartModel
from Enginy.engine_config import AVAILABLE_PARTS, CLASS_MAP, DATA_CLASS_MAP, EnginePartType

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "default-secret-key")

init_app(app)

#Check MongoDB status
mongodb_available = app.config.get("MONGO_AVAILABLE", False)
if not mongodb_available:
    app.logger.warning("MongoDB is not available. Application running in limited mode.")

ENGINE_PARTS_CLASSES = CLASS_MAP

# Dynamically import and map form classes.
AVAILABLE_FORMS: Dict[str, BasePartForm] = {}
for part in AVAILABLE_PARTS:
    try:
        form_class = getattr(importlib.import_module("Enginy.forms"), f"{part}Form")
        AVAILABLE_FORMS[part] = form_class
    except (ImportError, AttributeError) as e:
        app.logger.error(f"Could not import form for {part}: {e}")

def get_current_user_id() -> Optional[str]:
    """Get the current user ID from session"""
    # Placeholder: In the future, this will be from authentication.
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
                'part': part_instance,
                'name': part_type.value,
                'user_part_name': user_part_name,
                'part_type': part_type.value
            }
            
            part_id = EnginePartRepository.save_part(part_dict, user_id)
            
            # Save dependency relationships
            for _, dep_id in dependency_ids.items():
                EnginePartModel.add_dependency(part_id, dep_id)

            flash(f'{part_type.value} created successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash(f'Error creating {part_type.value}. Data class not found.', 'danger')

    return render_template(
        'create_part.html', 
        form=form, 
        available_parts=AVAILABLE_PARTS, 
        current_type=part_type.value
    )

@app.route('/delete_part/<string:part_id>', methods=['POST'])
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
            flash(f'{part["name"]} "{part["user_part_name"]}" deleted successfully!', 'success')
        else:
            flash(f'Failed to delete {part["name"]}', 'danger')
    else:
        flash("Invalid part ID for deletion.", 'danger')
    
    return redirect(url_for('index'))

@app.route('/analyze_part/<string:part_id>', methods=['GET'])
def analyze_part(part_id: str) -> Union[str, Response]:
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
        flash("Showing saved analysis result.", 'info')
        return render_template("analyze.html", analysis=cached_analysis)
    
    # No cached result, retrieve and reconstruct the part object
    part_obj = EnginePartRepository.get_part_object(part_id)
    
    if part_obj:
        try:
            # Call the analyze method on the reconstructed part object
            analysis_json = part_obj.analyze()
            
            # Cache the analysis result
            EnginePartRepository.save_analysis_result(part_id, analysis_json)
            
            flash("Analysis completed successfully!", 'success')
            return render_template("analyze.html", analysis=analysis_json)
        except Exception as e:
            flash(f"Error during analysis: {str(e)}", 'danger')
            return jsonify({'error': f'Analysis error: {str(e)}'}), 500
    else:
        flash("Invalid part ID.", "danger")
        return jsonify({'error': 'Invalid part ID'}), 400

@app.route('/analyze_engine', methods=['POST'])
def analyze_engine() -> Response:
    """
    Perform analysis on the complete engine assembly.

    IT'S STILL PLACEHOLDER
    
    This requires having all necessary engine parts available.
    
    Returns:
        JSON response containing the engine analysis result.
    """
    user_id = get_current_user_id()
    parts = EnginePartRepository.get_all_parts(user_id)
    
    if len(parts) < 3:  # Need at least an inlet, compressor, and combustor
        flash("Not enough parts to build the engine!", "danger")
        return jsonify({'error': 'Not enough parts to build the engine!'}), 400
    
    # Get one of each required part type
    inlet = next((EnginePartRepository.get_part_object(p['id']) 
                 for p in parts if p['name'] == 'Inlet'), None)
    compressor = next((EnginePartRepository.get_part_object(p['id']) 
                      for p in parts if p['name'] == 'Compressor'), None)
    combustor = next((EnginePartRepository.get_part_object(p['id']) 
                    for p in parts if p['name'] == 'Combustor'), None)
    
    if not all([inlet, compressor, combustor]):
        missing = []
        if not inlet: missing.append("Inlet")
        if not compressor: missing.append("Compressor")
        if not combustor: missing.append("Combustor")
        flash(f"Missing required engine parts: {', '.join(missing)}", "danger")
        return jsonify({'error': f'Missing required engine parts: {", ".join(missing)}'}), 400
    
    try:
        # Combine analyses from all parts
        inlet_analysis = json.loads(inlet.analyze())
        compressor_analysis = json.loads(compressor.analyze())
        combustor_analysis = json.loads(combustor.analyze())
        
        # Combine all data traces from the analyses
        combined_traces = []
        combined_traces.extend(inlet_analysis.get('data', []))
        combined_traces.extend(compressor_analysis.get('data', []))
        combined_traces.extend(combustor_analysis.get('data', []))
        
        engine_analysis = {
            'data': combined_traces,
            'layout': {
                'title': 'Complete Engine Analysis',
                'xaxis': {'title': 'Entropy (kJ/kg)'},
                'yaxis': {'title': 'Temperature (K)'}
            }
        }
        
        flash("Complete engine analysis performed successfully.", 'success')
        return jsonify(engine_analysis)
        
    except Exception as e:
        flash(f"Error during engine analysis: {str(e)}", 'danger')
        return jsonify({'error': f'Engine analysis error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)