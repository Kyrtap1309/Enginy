# README: Enginy - Jet Engine Component Analysis Application

## Overview

**Enginy** is a **Flask-based web application** designed for **analyzing components of jet engines**. The application provides users with insights into the performance, condition, and efficiency of different jet engine parts through data analysis, visualization, and reporting. It is built using Python and Flask and can be extended with additional features for more in-depth engineering analysis.

The application can serve as a helpful tool for engineers, researchers, and students working on **aeronautical engineering** projects related to jet propulsion systems.

## Features

- **Component Analysis**: Perform detailed analysis of key components of a jet engine, such as the turbine, compressor, combustion chamber, and inlet.
- **Data Visualization**: Graphical representation of performance metrics and parameters using **Plotly**.
- **Simulation Inputs**: Accepts user inputs for various operational conditions  to simulate engine performance.
- **Modular Design**: Easy to extend for additional functionalities such as real-time data monitoring or advanced thermodynamic simulations.

## Technologies Used

- **Backend**: Python, Flask
- **Thermodynamic calculations**: Numpy, Cantera
- **Frontend**: HTML, CSS (Bootstrap), JavaScript
- **Data Visualization**: Plotly
- **Database** (In development): SQLite for storing engine data and analysis results
- **Containerization**: Docker for easy deployment and testing
- **Version Control**: Git, GitHub

## Installation

### Prerequisites

Before you begin, ensure you have the following installed on your machine:

- Python 3.9 or later
- Pip (Python package installer)
- Docker (optional, for containerized deployment)
- Poetry

### Steps to Set Up

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Kyrtap1309/Enginy.git
   cd Enginy
    ```
2. **Install poetry**:
    ```bash
    pip install poetry
    ```

3. **Install the required dependencies and activate virtual environment**:
    ```bash
    poetry install
    ```
    ```bash
    poetry shell
    ```

4. **Setting Flask Secret Key**
    For security reasons, the `SECRET_KEY` is not hard-coded and must be provided via the `FLASK_SECRET_KEY` environment variable.
    ```bash
    export FLASK_SECRET_KEY="your-secret-key"
    #On Windows CMD use: setx FLASK_SECRET_KEY "your-secret-key"
    ```

5. **Run the flask application**:
    ```bash
    cd Enginy #You must be in folder with app.py
    flask run --host=0.0.0.0
    ```

6. **(Optional) Running with Docker**:

    - Set the `FLASK_SECRET_KEY` environment variable via `Dockerfile`
    
    
    - Build the Docker image (Be sure that working directory points at the folder with Dockerfile):
    ```bash
    docker build --tag enginy-app .
    ```
    - Run the Docker container:
    ```bash
    docker run -d -p 5000:5000 enginy-app
    ```

    - You can override `FLASK_SECRET_KEY` env with:
    ```bash
    docker run -d -p 5000:5000 -e FLASK_SECRET_KEY="your-secret-key" enginy-app
    ```

## Usage
1. After running the Flask app, open your browser and navigate to http://localhost:5000.
2. On the main page, you can create engine's part with your own parameters.
3. View detailed performance metrics and analysis of each engine component by clicking **view plot** button


