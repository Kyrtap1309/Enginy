from flask import Flask, render_template, request, redirect, url_for, jsonify
from .engine_parts.inlet import Inlet
from .engine_parts.compressor import Compressor
from .engine_parts.combustor import Combustor
from .forms import InletForm, CompressorForm, CombustorForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "..."

# Available engine part types and their corresponding classes.
AVAILABLE_PARTS = ["Inlet", "Compressor", "Combustor"]
ENGINE_PARTS_CLASSES = {
    "Inlet": Inlet,
    "Compressor": Compressor,
    "Combustor": Combustor
}

# List to store created engine parts.
engine_parts = []


@app.route('/')
def index():
    """
    Render the main page with the list of engine parts.
    """
    return render_template('index.html', engine_parts=engine_parts)


@app.route('/create_part', methods=['GET', 'POST'])
def create_part():
    # Get desired part type from query parameter (default to Inlet)
    part_type = request.args.get('type', 'Inlet')
    if part_type == "Inlet":
        form = InletForm()
    elif part_type == "Compressor":
        form = CompressorForm()
        # Populate inlet selections from created parts
        inlet_choices = [(i, ep["user_part_name"]) for i, ep in enumerate(engine_parts) if ep["name"] == "Inlet"]
        form.inlet_part.choices = inlet_choices
    elif part_type == "Combustor":
        form = CombustorForm()
        # Populate compressor selections from created parts
        compressor_choices = [(i, ep["user_part_name"]) for i, ep in enumerate(engine_parts) if ep["name"] == "Compressor"]
        form.compressor_part.choices = compressor_choices
    else:
        form = InletForm()

    if form.validate_on_submit():
        data = form.data
        user_part_name = data.pop("user_part_name")
        # Remove unneeded keys (csrf_token, submit)
        data.pop("csrf_token", None)
        data.pop("submit", None)
        if part_type == "Compressor":
            inlet_index = data.pop("inlet_part")
            inlet_part = engine_parts[inlet_index]["part"]
            data["inlet"] = inlet_part
            part_instance = Compressor(data, inlet_part)
        elif part_type == "Combustor":
            compressor_index = data.pop("compressor_part")
            compressor_part = engine_parts[compressor_index]["part"]
            data["compressor"] = compressor_part
            part_instance = Combustor(data, compressor_part)
        else:
            part_instance = Inlet(data)
        analysis_result = f"Analysis for {part_type}"
        engine_parts.append({
            'part': part_instance,
            'name': part_type,
            'user_part_name': user_part_name,
            'analysis': analysis_result
        })
        return redirect(url_for('index'))

    return render_template('create_part.html', form=form, available_parts=AVAILABLE_PARTS, current_type=part_type, engine_parts=engine_parts)

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