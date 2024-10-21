from flask import Flask, render_template, request, redirect, url_for, jsonify

from .engine_parts.inlet import Inlet
from .utils.constants import available_parts


app = Flask(__name__)

#Engine parts
engine_parts = []

#Engine parts mapping
engine_parts_classes = {
    "Inlet": Inlet,
}

# Main Page
@app.route('/')
def index():
    return render_template('index.html', engine_parts=engine_parts)

# Create Engine Parts
@app.route('/create_part', methods=['GET', 'POST'])
def create_part():
    if request.method == 'POST':
        data = request.form.to_dict()
        # Float convertion
        for key in data:
            if key != "part_name":
                data[key] = float(data[key])
        part_name = request.form["part_name"]
        part = engine_parts_classes[part_name](data)
        analysis_result = f"Analysis for {part_name}"  # Analysis' Logic
        engine_parts.append({'part': part, 'name': part_name, 'analysis': analysis_result})
        return redirect(url_for('index'))
    
    return render_template('create_part.html', available_parts=available_parts)

@app.route('/delete_part/<int:part_index>', methods=['POST'])
def delete_part(part_index):
    # Delete parts
    if 0 <= part_index < len(engine_parts):
        engine_parts.pop(part_index)  # Delete from the engine part list
    
    return redirect(url_for('index'))

@app.route('/analyze_part/<int:part_index>', methods=['GET'])
def analyze_part(part_index):
    if 0 <= part_index < len(engine_parts):
        analysis = engine_parts[part_index]["part"].analyze()
        return render_template("analyze.html", analysis=analysis)
    

# Analysis of whole engine
@app.route('/analyze_engine', methods=['POST'])
def analyze_engine():
    if len(engine_parts) < 5:  
        return jsonify({'error': 'Not enough parts to build the engine!'}), 400
    # Logic of engine analysis
    engine_analysis_result = "Complete Engine Analysis"
    return jsonify({'result': engine_analysis_result})


if __name__ == '__main__':
    app.run(debug=True)
