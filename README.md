# README: Enginy - Jet Engine Component Analysis Application

## Overview

**Enginy** is a **Flask-based web application** designed for **analyzing components of jet engines**. The application provides users with insights into the performance, condition, and efficiency of different jet engine parts through data analysis, visualization, and reporting. It is built using Python and Flask and can be extended with additional features for more in-depth engineering analysis.

This tool can be a valuable resource for engineers, researchers, and students working on **aeronautical engineering** projects related to jet propulsion systems.

## Features

- **Component Analysis**: Perform detailed analysis of key components of a jet engine, such as the turbine, compressor, combustion chamber, and inlet.
- **Data Visualization**: Graphical representation of performance metrics and parameters using **Plotly**.
- **Simulation Inputs**: Accepts user inputs for various operational conditions to simulate engine performance.
- **Modular Design**: Easily extendable for additional functionalities such as real-time data monitoring or advanced thermodynamic simulations.
- **Persistent Storage**: MongoDB database for storing engine parts data and analysis results.

## Technologies Used

- **Backend**: Python, Flask
- **Thermodynamic Calculations**: NumPy, Cantera
- **Frontend**: HTML, CSS (Bootstrap), JavaScript
- **Data Visualization**: Plotly
- **Database**: MongoDB for storing engine parts and analysis results
- **Containerization**: Docker for easy deployment and testing
- **Dependency Management**: Poetry
- **Version Control**: Git, GitHub

## Installation & Setup

### Prerequisites

Before you begin, ensure you have the following installed on your machine:

- Python 3.11 or later (required for built-in tomllib)
- Poetry (for dependency management)
- Docker (optional, for containerized deployment)
- MongoDB (optional, automated setup available)

### Clone the repository

Before you go further, you must clone the repository:
```bash
git clone https://github.com/Kyrtap1309/Enginy.git
cd Enginy
```

Now you can continue with running the **Enginy** app:

### Option 1: Quick Start with Automated Setup Script

The quickest way to set up and run Enginy is using the provided startup script:

```bash
python start_dev.py
```

### Option 2: Docker Compose (Recommended for Prodcution-like Environment)

To run both the application and MongoDB in containers:

1. **Start the environment**:
    ```bash
    docker-compose up
    ```
    This will build and start both the MongoDB contaner and the Enginy application container.

2. **Access the application** in your browser at http://localhost:5000
3. **Stop the environment** when done
    ```bash
    docker-compose down
    ```

### Option 3: Manual Setup (Not recommended)

1. **Install poetry**:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```
   On Windows, use this:
   ```bash
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
   ```

2. **Install the required dependencies and activate virtual environment**:
   ```bash
   poetry install
   ```
   ```bash
   poetry shell
   ```

3. **Start MongoDB**
   ```bash
   docker run -d -p 27017:27017 --name enginy-mongodb mongo:latest
   ```

4. **Set environment variables**:
   ```bash
   export FLASK_APP=Enginy/app.py
   export FLASK_SECRET_KEY="your-secret-key"
   export MONGO_URI="mongodb://localhost:27017/enginy"
   ```
   On Windows Command Prompt:
   ```bash
   set FLASK_APP=Enginy/app.py
   set FLASK_SECRET_KEY=your-secret-key
   set MONGO_URI=mongodb://localhost:27017/enginy
   ```

5. **Run the Flask application**:
    ```bash
    flask run --host=0.0.0.0
    ```

## Contributing
Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.


