import os
import subprocess
import sys
import time
import tomli 

def check_mongodb():
    """Check if MongoDB is running using mongosh"""
    try:
        result = subprocess.run(
            ["mongosh", "--eval", "db.stats()"], 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def start_mongodb_container():
    """Start a MongoDB container using Docker"""
    print("Starting MongoDB container...")
    result = subprocess.run(
        ["docker", "run", "-d", "--name", "engine-mongodb", "-p", "27017:27017", "mongo:latest"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if result.returncode != 0:
        if b"already in use" in result.stderr:
            print("MongoDB container already exists, starting it...")
            subprocess.run(["docker", "start", "engine-mongodb"])
        else:
            print(f"Error starting MongoDB container: {result.stderr.decode()}")
            return False
    
    #Give MongoDB time to start
    time.sleep(3)
    return True

def get_dependencies_from_pyproject():
    """Extract dependencies from pyproject.toml file"""
    if not os.path.exists("pyproject.toml"):
        print("pyproject.toml not found, using default dependencies")
        return ["flask", "pymongo", "flask-pymongo"]
    
    try:
        with open("pyproject.toml", "rb") as f:
            pyproject_data = tomli.load(f)
        
        # Extract dependencies from pyproject.toml
        dependencies = []
        
        # Handle poetry dependencies
        poetry_deps = pyproject_data.get("tool", {}).get("poetry", {}).get("dependencies", {})
        if poetry_deps:
            # Filter out python dependency
            dependencies.extend([dep for dep in poetry_deps.keys() if dep.lower() != "python"])
        
        # Handle project dependencies (PEP 621)
        project_deps = pyproject_data.get("project", {}).get("dependencies", [])
        if project_deps:
            dependencies.extend(project_deps)
        
        # If no dependencies found, use defaults
        if not dependencies:
            print("No dependencies found in pyproject.toml, using defaults")
            return ["flask", "pymongo", "flask-pymongo"]
            
        return dependencies
    except Exception as e:
        print(f"Error parsing pyproject.toml: {e}")
        return ["flask", "pymongo", "flask-pymongo"]

def setup_environment():
    """Setup virtual environment if needed"""
    if os.path.exists("poetry.lock"):
        print("Poetry lock file found, using Poetry...")
        try:
            # Install dependencies if not already installed
            subprocess.run(["poetry", "install"], check=False)
            return True
        except FileNotFoundError:
            print("Poetry not found. Falling back to direct pip installation.")
    
    # Create venv if it doesn't exist
    if not os.path.exists(".venv"):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=False)
    
    # Install tomli first (we need it to parse pyproject.toml)
    pip_path = os.path.join(".venv", "Scripts", "pip.exe") if os.name == "nt" else os.path.join(".venv", "bin", "pip")
    if os.path.exists(pip_path):
        print("Installing tomli for pyproject.toml parsing...")
        subprocess.run([pip_path, "install", "tomli"], check=False)
        
        # Now get and install the actual dependencies
        dependencies = get_dependencies_from_pyproject()
        print(f"Installing dependencies: {', '.join(dependencies)}")
        subprocess.run([pip_path, "install"] + dependencies, check=False)
    
    return True

def start_flask_app():
    """Start the Flask application"""
    print("Starting Flask application...")
    env = os.environ.copy()
    env["FLASK_APP"] = "Enginy/app.py"
    env["FLASK_ENV"] = "development"
    env["FLASK_DEBUG"] = "1"
    env["MONGO_URI"] = "mongodb://localhost:27017/enginy"

    if "FLASK_SECRET_KEY" not in env:
        env["FLASK_SECRET_KEY"] = "dev-secret-key"
    
    # Use the venv Python or try fallback approaches
    python_path = os.path.join(".venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(".venv", "bin", "python")
    
    if os.path.exists(python_path):
        subprocess.run([python_path, "-m", "flask", "run", "--host=0.0.0.0"], env=env)
    else:
        try:
            subprocess.run(["flask", "run", "--host=0.0.0.0"], env=env)
        except FileNotFoundError:
            try:
                subprocess.run([python_path, "-m", "flask", "run", "--host=0.0.0.0"], env=env)
            except Exception as e:
                print(f"Failed to start Flask: {e}")
                sys.exit(1)

if __name__ == "__main__":
    if not check_mongodb():
        print("MongoDB not running locally. Attempting to start with Docker...")
        if not start_mongodb_container():
            print("Failed to start MongoDB. Please start MongoDB manually.")
            sys.exit(1)
    
    setup_environment()
    start_flask_app()