from flask import Flask, render_template, request, redirect, url_for, jsonify
from .engine_parts.inlet import Inlet
from .engine_parts.compressor import Compressor
from .engine_parts.combustor import Combustor

app = Flask(__name__)

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
    """
    Create a new engine part based on POSTed form data.
    For 'Compressor' and 'Combustor', an existing part is required.
    """
    if request.method == 'POST':
        data = request.form.to_dict()
        part_type = data.pop("part_name")
        user_part_name = data.pop("user_part_name")

        # Convert numeric values to float.
        for key, value in data.items():
            if key not in ["part_name"]:
                try:
                    data[key] = float(value)
                except ValueError:
                    return jsonify({'error': f'Invalid value for {key}'}), 400

        # Create part based on type, handling dependencies if any.
        if part_type == "Compressor":
            try:
                inlet_index = int(data.pop("inlet_part"))
                inlet_part = engine_parts[inlet_index]["part"]
                data["inlet"] = inlet_part
            except (ValueError, IndexError) as e:
                return jsonify({'error': 'Invalid inlet part selection'}), 400
            part_instance = ENGINE_PARTS_CLASSES[part_type](data, inlet_part)

        elif part_type == "Combustor":
            try:
                compressor_index = int(data.pop("compressor_part"))
                compressor_part = engine_parts[compressor_index]["part"]
                data["compressor"] = compressor_part
            except (ValueError, IndexError) as e:
                return jsonify({'error': 'Invalid compressor part selection'}), 400
            part_instance = ENGINE_PARTS_CLASSES[part_type](data, compressor_part)

        else:
            part_instance = ENGINE_PARTS_CLASSES[part_type](data)

        # Analysis logic (replace with actual calculation when ready).
        analysis_result = f"Analysis for {part_type}"

        # Save the new engine part.
        engine_parts.append({
            'part': part_instance,
            'name': part_type,
            'user_part_name': user_part_name,
            'analysis': analysis_result
        })
        return redirect(url_for('index'))

    # GET method: render form with available parts.
    return render_template('create_part.html', available_parts=AVAILABLE_PARTS, engine_parts=engine_parts)


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