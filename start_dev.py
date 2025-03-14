import os
import subprocess
import sys
import time
import tomllib
import signal
import atexit

# Global variables to track the processes
flask_process = None
mongodb_container_name = "engine-mongodb"

def signal_handler(sig, frame):
    """Handle SIGINT (Ctrl+C) and other termination signals"""
    print("\nShutting down gracefully. Please wait...")
    cleanup_resources()
    sys.exit(0)

def cleanup_resources():
    """Clean up resources before exiting"""
    # Stop Flask process if running
    if flask_process and flask_process.poll() is None:
        print("Stopping Flask application...")
        flask_process.terminate()
        try:
            flask_process.wait(timeout=5)  # Wait up to 5 seconds for process to terminate
        except subprocess.TimeoutExpired:
            flask_process.kill()  # Force kill if it doesn't terminate

    # Stop MongoDB container if it was started by us
    if os.environ.get("MONGODB_STARTED_BY_SCRIPT") == "true":
        print("Stopping MongoDB container...")
        try:
            subprocess.run(["docker", "stop", mongodb_container_name], 
                          stdout=subprocess.DEVNULL, 
                          stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"Error stopping MongoDB container: {e}")

def check_python_version():
    if sys.version_info < (3, 11):
        print("Error: This project requires Python 3.11 or newer.")
        print(f"Current Python version: {sys.version}")
        sys.exit(1)
    print(f"Using Python {sys.version}")

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
        ["docker", "run", "-d", "--name", mongodb_container_name, "-p", "27017:27017", "mongo:latest"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if result.returncode != 0:
        if b"already in use" in result.stderr:
            print("MongoDB container already exists, starting it...")
            subprocess.run(["docker", "start", mongodb_container_name])
        else:
            print(f"Error starting MongoDB container: {result.stderr.decode()}")
            return False
    
    # Mark that we started MongoDB
    os.environ["MONGODB_STARTED_BY_SCRIPT"] = "true"
    
    # Give MongoDB time to start
    time.sleep(3)
    return True

def get_dependencies_from_pyproject():
    """Extract dependencies from pyproject.toml file"""
    if not os.path.exists("pyproject.toml"):
        print("pyproject.toml not found, using default dependencies")
        return ["flask", "pymongo", "flask-pymongo"]
    
    try:
        with open("pyproject.toml", "rb") as f:
            pyproject_data = tomllib.load(f)
        
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
    
    # Install dependencies directly - no need for tomli installation
    pip_path = os.path.join(".venv", "Scripts", "pip.exe") if os.name == "nt" else os.path.join(".venv", "bin", "pip")
    if os.path.exists(pip_path):        
        # Get and install the dependencies
        dependencies = get_dependencies_from_pyproject()
        print(f"Installing dependencies: {', '.join(dependencies)}")
        subprocess.run([pip_path, "install"] + dependencies, check=False)
    
    return True

def start_flask_app():
    """Start the Flask application"""
    global flask_process
    print("Starting Flask application...")
    env = os.environ.copy()
    env["FLASK_APP"] = "Enginy/app.py"
    env["FLASK_ENV"] = "development"
    env["FLASK_DEBUG"] = "1"
    env["MONGO_URI"] = f"mongodb://localhost:27017/enginy"

    if "FLASK_SECRET_KEY" not in env:
        env["FLASK_SECRET_KEY"] = "dev-secret-key"
    
    # Check if we're using Poetry
    if os.path.exists("poetry.lock"):
        try:
            # Use Poetry to run the Flask app
            print("Using Poetry to run Flask...")
            print("\nFlask server is running. Press Ctrl+C to stop.")
            flask_process = subprocess.Popen(
                ["poetry", "run", "flask", "run", "--host=127.0.0.1"], 
                env=env
            )
            # Keep the script running until the Flask process exits or is killed
            flask_process.wait()
            return
        except FileNotFoundError:
            print("Poetry command not found, trying alternative methods...")
    
    # Try to find Python in the virtual environment
    python_path = os.path.join(".venv", "Scripts", "python.exe") if os.name == "nt" else os.path.join(".venv", "bin", "python")
    
    if os.path.exists(python_path):
        print("\nFlask server is running. Press Ctrl+C to stop.")
        flask_process = subprocess.Popen(
            [python_path, "-m", "flask", "run", "--host=127.0.0.1"], 
            env=env
        )
        flask_process.wait()
    else:
        # If venv python not found, try the system Python
        try:
            print("Virtual environment Python not found, using system Python...")
            print("\nFlask server is running. Press Ctrl+C to stop.")
            flask_process = subprocess.Popen(
                [sys.executable, "-m", "flask", "run", "--host=127.0.0.1"], 
                env=env
            )
            flask_process.wait()
        except Exception as e:
            print(f"Failed to start Flask: {str(e)}")
            # Last resort - try the flask command directly
            try:
                print("\nFlask server is running. Press Ctrl+C to stop.")
                flask_process = subprocess.Popen(
                    ["flask", "run", "--host=127.0.0.1"], 
                    env=env
                )
                flask_process.wait()
            except FileNotFoundError:
                print("Error: Could not find a way to run Flask. Please make sure Flask is installed.")

if __name__ == "__main__":
    # Register the signal handler for graceful termination
    signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Handle termination signal
    
    # Register cleanup function to run at exit
    atexit.register(cleanup_resources)
    
    check_python_version() 
    
    if not check_mongodb():
        print("MongoDB not running locally. Attempting to start with Docker...")
        if not start_mongodb_container():
            print("Failed to start MongoDB. Please start MongoDB manually.")
            sys.exit(1)
    
    setup_environment()
    start_flask_app()