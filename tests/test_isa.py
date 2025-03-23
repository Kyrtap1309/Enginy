import pytest
from math import isclose

from Enginy.isa.isa import (
    ISA_delta,
    ISA_p,
    ISA_theta,
    ISA_T,
    ISA_sigma,
    ISA_rho,
    inv_ISA_delta,
    inv_ISA_p,
    inv_ISA_sigma,
    inv_ISA_rho,
    _handle_units,
    CONVERT_TO_M,
    CONVERT_FROM_M,
    H_top_troposphere,
    p_st,
    Rho_st,
    T_st,
)

# Tolerance for floating-point comparisons
tol = 10e-6


# Test for the function that handles unit conversion
def test_handle_units_valid():
    assert isclose(_handle_units(1, "meter"), 1.0, abs_tol=tol)
    assert isclose(_handle_units(1, "feet"), 0.3048, abs_tol=tol)
    assert isclose(_handle_units(1, "kilometer"), 1000.0, abs_tol=tol)


# Test for invalid input units, expecting a ValueError
def test_handle_units_invalid():
    with pytest.raises(ValueError, match="Invalid input unit"):
        _handle_units(1, "yard")


# Test ISA_delta function for tropospheric values (pressure ratio in the troposphere)
def test_ISA_delta_troposphere():
    assert isclose(ISA_delta(0), 1.0, abs_tol=tol)  # At sea level
    assert isclose(
        ISA_delta(H_top_troposphere), 0.2233609, abs_tol=tol
    )  # At the top of the troposphere (~11,000 m)


# Test ISA_delta function for stratospheric values (pressure ratio in the stratosphere)
def test_ISA_delta_stratosphere():
    assert isclose(
        ISA_delta(20_000), 0.0540321, abs_tol=tol
    )  # At an altitude of 20,000 m


# Test ISA_p function for pressure in the troposphere
def test_ISA_p_troposphere():
    tol = 1
    assert isclose(ISA_p(0), p_st, abs_tol=tol)  # Sea-level pressure
    assert isclose(
        ISA_p(H_top_troposphere), 22632.06, abs_tol=tol
    )  # Pressure at the top of the troposphere


# Test ISA_p function for pressure in the stratosphere
def test_ISA_p_stratosphere():
    tol = 0.1
    assert isclose(
        ISA_p(20_000), 5474.88, abs_tol=tol
    )  # Pressure at an altitude of 20,000 m


# Test ISA_T function for temperature in the troposphere
def test_ISA_T_troposphere():
    assert isclose(ISA_T(0), T_st, abs_tol=tol)  # Sea-level temperature
    assert isclose(
        ISA_T(H_top_troposphere), 216.65, abs_tol=tol
    )  # Temperature at the top of the troposphere


# Test ISA_T function for temperature in the stratosphere
def test_ISA_T_stratosphere():
    assert isclose(
        ISA_T(20_000), 216.65, abs_tol=tol
    )  # Temperature at 20,000 m (constant in the lower stratosphere)


# Test ISA_rho function for density in the troposphere
def test_ISA_rho_troposphere():
    assert isclose(ISA_rho(0), Rho_st, abs_tol=tol)  # Sea-level air density
    assert isclose(
        ISA_rho(H_top_troposphere), 0.36392, abs_tol=tol
    )  # Air density at the top of the troposphere


# Test ISA_rho function for density in the stratosphere
def test_ISA_rho_stratosphere():
    assert isclose(ISA_rho(20_000), 0.08803, abs_tol=tol)  # Air density at 20,000 m


# Test inv_ISA_delta function (inverting pressure ratio to altitude) for troposphere and lower stratosphere
def test_inv_ISA_delta():
    tol = 0.1
    assert isclose(
        inv_ISA_delta(1.0), 0, abs_tol=tol
    )  # Delta of 1.0 should correspond to sea level
    assert isclose(
        inv_ISA_delta(0.2233609), H_top_troposphere, abs_tol=tol
    )  # Delta at the top of the troposphere


# Test inv_ISA_p function (inverting pressure to altitude)
def test_inv_ISA_p():
    tol = 0.1
    assert isclose(
        inv_ISA_p(p_st), 0, abs_tol=tol
    )  # Sea-level pressure should return altitude of 0 m
    assert isclose(
        inv_ISA_p(22632.06), H_top_troposphere, abs_tol=tol
    )  # Pressure at the top of the troposphere


# Test inv_ISA_sigma function (inverting density ratio to altitude)
def test_inv_ISA_sigma():
    tol = 2
    assert isclose(
        inv_ISA_sigma(1.0), 0, abs_tol=tol
    )  # Sigma of 1.0 corresponds to sea level
    assert isclose(
        inv_ISA_sigma(0.297), H_top_troposphere, abs_tol=tol
    )  # Sigma at the top of the troposphere


# Test inv_ISA_rho function (inverting air density to altitude)
def test_inv_ISA_rho():
    tol = 0.1
    assert isclose(
        inv_ISA_rho(Rho_st), 0, abs_tol=tol
    )  # Sea-level density should return altitude of 0 m
    assert isclose(
        inv_ISA_rho(0.36392), H_top_troposphere, abs_tol=tol
    )  # Density at the top of the troposphere
