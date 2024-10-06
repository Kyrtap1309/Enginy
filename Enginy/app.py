from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

# Example engine parts
engine_parts = []

# Main Page
@app.route('/')
def index():
    return render_template('index.html', engine_parts=engine_parts)

# Create Engine Parts
@app.route('/create_part', methods=['GET', 'POST'])
def create_part():
    if request.method == 'POST':
        part_name = request.form['part_name']
        analysis_result = f"Analysis for {part_name}"  # Tu idzie logika analizy
        engine_parts.append({'name': part_name, 'analysis': analysis_result})
        return redirect(url_for('index'))
    return render_template('create_part.html')

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
