import importlib

from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)
app.config["SECRET_KEY"] = "..."


AVAILABLE_PARTS = ["Inlet", "Compressor", "Combustor"]

ENGINE_PARTS_CLASSES = {
    part: getattr(importlib.import_module(f"Enginy.engine_parts.{part.lower()}"), part)
    for part in AVAILABLE_PARTS
}

AVAILABLE_FORMS = {
    part: getattr(importlib.import_module("Enginy.forms"), f"{part}Form")
    for part in AVAILABLE_PARTS
}

print(ENGINE_PARTS_CLASSES)
print(AVAILABLE_FORMS)


engine_parts = []


@app.route('/')
def index():
    """
    Render the main page with the list of engine parts.
    """
    return render_template('index.html', engine_parts=engine_parts)


@app.route('/create_part', methods=['GET', 'POST'])
def create_part():
    # Pobranie typu części z parametru (domyślnie "Inlet")
    part_type = request.args.get('type', 'Inlet')
    
    # Pobranie odpowiedniego formularza, jeśli nie istnieje - domyślnie InletForm
    form_class = AVAILABLE_FORMS.get(part_type, AVAILABLE_FORMS["Inlet"])
    form = form_class()

    # Dynamiczne ustawianie opcji dla pól zależności (np. wybór Inlet dla Compressor)
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

        part_class = ENGINE_PARTS_CLASSES[part_type]
        part_instance = part_class(data, **dependencies)

        engine_parts.append({
            'part': part_instance,
            'name': part_type,
            'user_part_name': user_part_name,
            'analysis': f"Analysis for {part_type}"
        })

        return redirect(url_for('index'))

    return render_template(
        'create_part.html', 
        form=form, 
        available_parts=AVAILABLE_PARTS, 
        current_type=part_type, 
        engine_parts=engine_parts
    )

@app.route('/delete_part/<int:part_index>', methods=['POST'])
def delete_part(part_index):
    """
    Delete an engine part given its index.
    """
    if 0 <= part_index < len(engine_parts):
        engine_parts.pop(part_index)
    return redirect(url_for('index'))


@app.route('/analyze_part/<int:part_index>', methods=['GET'])
def analyze_part(part_index):
    """
    Analyze a single engine part and render the analyze template.
    """
    if 0 <= part_index < len(engine_parts):
        analysis = engine_parts[part_index]["part"].analyze()
        return render_template("analyze.html", analysis=analysis)
    return jsonify({'error': 'Invalid part index'}), 400


@app.route('/analyze_engine', methods=['POST'])
def analyze_engine():
    """
    Perform analysis on the entire engine. At least 5 parts are required.
    """
    if len(engine_parts) < 5:
        return jsonify({'error': 'Not enough parts to build the engine!'}), 400

    # Replace with comprehensive engine analysis logic as needed.
    engine_analysis_result = "Complete Engine Analysis"
    return jsonify({'result': engine_analysis_result})


if __name__ == '__main__':
    app.run(debug=True)