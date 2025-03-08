import os
import subprocess
import sys
import time

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
    
    subprocess.run(["flask", "run", "--host=0.0.0.0"], env=env)

if __name__ == "__main__":
    if not check_mongodb():
        print("MongoDB not running locally. Attempting to start with Docker...")
        if not start_mongodb_container():
            print("Failed to start MongoDB. Please start MongoDB manually. ")
            sys.exit(1)
    
    start_flask_app()