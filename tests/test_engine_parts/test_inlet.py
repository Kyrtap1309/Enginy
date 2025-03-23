import pytest
import cantera as ct
from Enginy.engine_parts.inlet import Inlet
import json
import math


@pytest.fixture
def inlet_json_file(tmp_path):
    """Fixture that creates a temporary JSON file with inlet data."""
    sample_inlet_json = {
        "altitude": 10000,  # Altitude in meters
        "M_inlet_input": 0.8,  # Mach number at the inlet
        "mass_flow": 100,  # Mass flow in kg/s
        "A1": 1.0,  # Inlet area in m^2
        "A2": 0.8,  # Outlet area in m^2
        "eta": 0.95,  # Efficiency of the inlet
    }
    inlet_json_path = tmp_path / "test_inlet_data.json"
    with open(inlet_json_path, "w") as json_file:
        json.dump(sample_inlet_json, json_file)

    return str(inlet_json_path)


def test_inlet_initialization(inlet_json_file):
    """Test if the Inlet class initializes correctly and reads data from the JSON file."""
    inlet = Inlet(inlet_json_file)

    # Verify if the class correctly loads and initializes data
    assert inlet.M_input == 0.8
    assert inlet.mass_flow == 100
    assert inlet.A_1 == 1.0
    assert inlet.A_2 == 0.8
    assert inlet.inlet_eta == 0.95


def test_mach_inlet_converges(inlet_json_file):
    """Test if the mach_inlet method converges and returns a valid Mach number."""
    inlet = Inlet(inlet_json_file)

    # Call the mach_inlet method to calculate the Mach number at the end of the inlet
    mach, converged = inlet.mach_inlet()

    # Check if the Mach number is calculated correctly and the process converged
    assert mach is not None
    assert converged is True
    assert mach > 0  # The Mach number must be positive


def test_mach_inlet_non_convergence(inlet_json_file):
    """Test the mach_inlet method when convergence is not achieved."""
    inlet = Inlet(inlet_json_file)

    # Manually set incorrect parameters to induce non-convergence
    inlet.gas[1].TP = 230, 100  # Set unphysical values for temperature and pressure

    # Call the mach_inlet method with a small number of iterations to force non-convergence
    mach, converged = inlet.mach_inlet(max_iterations=5)

    # Check that the method does not converge and returns None for the Mach number
    assert mach is None
    assert converged is False
