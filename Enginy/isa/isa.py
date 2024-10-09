import numpy as np
#TODO after finishing testing remove matplot
import matplotlib.pyplot as plt

# Constants

##Convertion of length units to meters
CONVERT_TO_M = {
    "meter": 1,
    "feet": 0.3048,
    "kilometer": 1000,
}
##Convertion of length units in meters
CONVERT_FROM_M = {key: 1/value for key, value in CONVERT_TO_M.items()}

## Physic Constants
### Troposphere
R = 287.053  # Gas Constant [m2/s2/K]
g_st = 9.8067  # Standard Acceleration of Gravity [m/s2]
L = -6.5 / 1000  # Temperature ISA gradient [K/m]
H_top_troposphere = 11_000  # ISA Top of Troposphere [m]
T_st = 288.15  # ISA Temperature on the 0 level [K]
p_st = 101_325  # ISA Pressure on the 0 level [Pa]
Rho_st = 1.225 # ISA Density on the 0 level [kg/m3]

### Stratosphere
H_bottom_stratosphere = H_top_troposphere + 0.01  # ISA Bottom of Stratosphere
H_top_stratosphere = 47_000  # ISA Top of Stratosphere [m]
T_bottom_stratosphere = 216.65  # Temperature at the bottom of Stratosphere [K]
p_bottom_stratosphere = 22_632.06  # Pressure at the bottom of Stratosphere [Pa]
p_top_stratosphere = 5474.88 #Pressure at the top of Stratosphere [Pa]
Rho_bottom_stratosphere = 0.36392 # Density at the bottom of Stratosphere [kg/m3]
delta_bottom_strato = (
    p_bottom_stratosphere / p_st
)  # ISA Delta value at the bottom of Stratosphere
delta_top_strato = (
    p_top_stratosphere / p_st
)  # ISA Delta value at the top of Stratosphere
theta_bottom_strato = (
    T_bottom_stratosphere / T_st
)  # ISA Theta value at the bottom of Stratosphere
sigma_bottom_strato = (
    Rho_bottom_stratosphere / Rho_st
)  # ISA Sigma value at the bottom of Stratosphere


def _handle_units(H: float, unit, converter:dict = CONVERT_TO_M) -> float:
    if unit not in CONVERT_TO_M:
        raise ValueError("Invalid input unit")
    else:
        return H * converter[unit]


def ISA_delta(H: float, unit="meter") -> float:
    """
    Calucate ISA delta: the ISA pressure ratio, for a given pressure altitude
    limited to top of stratosphere
    args:
        H: Absolute height with unit declared in unit variable
    return:
        delta: Ratio of Air pressure at input height to ground pressure according to ISA [Pa]
    """

    H = _handle_units(H, unit)

    if H <= H_top_troposphere:
        delta = (1 + (L / T_st) * H) ** (-g_st / (L * R))
        return delta
    elif H <= H_top_stratosphere:
        delta = delta_bottom_strato * np.exp(
            -(g_st / (R * T_bottom_stratosphere)) * (H - H_bottom_stratosphere)
        )
        return delta
    else:
        raise ValueError("Altitude above stratospheric limit")


def ISA_p(H: float, unit="meter") -> float:
    """
    Calculate the ISA pressure, for a input pressure altitude
    limited to top of stratosphere
    args:
        H: Absolute height with unit declared in unit variable
    return:
        pressure: Air pressure at input height according to ISA [Pa]
    """
    H = _handle_units(H, unit)

    pressure = p_st * ISA_delta(H, unit="meter")
    return pressure


def ISA_theta(H: float, unit="meter") -> float:
    """
    Calucate ISA theta: the ISA temperature ratio, for a given temperature altitude
    limited to top of stratosphere
    args:
        H: Absolute height with unit declared in unit variable
    return:
        temperature: Air temperature at input height according to ISA [K]
    """
    H = _handle_units(H, unit)

    if H <= H_top_troposphere:
        temperature = 1 + (L / T_st) * H
        return temperature
    elif H <= H_top_stratosphere:
        temperature = theta_bottom_strato
        return temperature
    else:
        raise ValueError("Altitude above stratospheric limit")


def ISA_T(H: float, unit="meter") -> float:
    """
    Calculate the ISA temperature, for a input temperature altitude
    limited to top of stratosphere
    args:
        H: Absolute height with unit declared in unit variable
    return:
        temperature: Air pressure at input height according to ISA [Pa]
    """
    H = _handle_units(H, unit)

    temperature = T_st * ISA_theta(H, unit="meter")
    return temperature

def ISA_sigma(H: float, unit="meter") -> float:
    """
    Calucate ISA sigma: the ISA density ratio, for a given pressure altitude
    limited to top of stratosphere
    args:
        H: Absolute height with unit declared in unit variable
    return:
        delta: Ratio of density pressure at input height to ground density according to ISA [Pa]
    """

    H = _handle_units(H, unit)

    if H <= H_top_troposphere:
        sigma = (1 + (L / T_st) * H) ** (-g_st / (L * R) - 1)
        return sigma
    elif H <= H_top_stratosphere:
        sigma = sigma_bottom_strato * np.exp(
            -(g_st / (R * T_bottom_stratosphere)) * (H - H_bottom_stratosphere)
        )
        return sigma
    else:
        raise ValueError("Altitude above stratospheric limit")


def ISA_rho(H: float, unit="meter") -> float:
    """
    Calculate the ISA density, for a input density altitude
    limited to top of stratosphere
    args:
        H: Absolute height with unit declared in unit variable
    return:
        rho: Air density at input height according to ISA [Pa]
    """
    H = _handle_units(H, unit)

    rho = Rho_st * ISA_sigma(H, unit="meter")
    return rho

def inv_ISA_delta(delta: float, unit = "meter") -> float:
    """
    Calucate ISA pressure alitute based on input ISA delta limited to top of stratosphere
    args:
        delta: ISA delta 
        unit: Unit of returned altitude
    return:
        H: Altitude with input unit
    """
    if delta > delta_bottom_strato:
        altitude = (T_st / L) * ((delta) **(-(L * R) / g_st) - 1)
        altitude = _handle_units(altitude, unit, CONVERT_FROM_M)
        return altitude
    elif delta >= delta_top_strato:
        altitude = H_bottom_stratosphere + (R * T_bottom_stratosphere / g_st) * np.log(delta_bottom_strato/delta)
        altitude = _handle_units(altitude, unit, CONVERT_FROM_M)
        return altitude
    else:
        raise ValueError("Pressure/Altitude lower than top stratosphere level")

