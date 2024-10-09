import numpy as np
import matplotlib.pyplot as plt

# Constants

##Convertion of length units to meters
CONVERT_TO_M = {
    "meter": 1,
    "feet": 0.3048,
    "kilometer": 1000,
}

## Physic Constants
### Troposphere
R = 287.053  # Gas Constant [m2/s2/K]
g_st = 9.8067  # Standard Acceleration of Gravity [m/s2]
L = -6.5 / 1000  # Temperature ISA gradient [K/m]
H_top_troposphere = 11_000  # ISA Top of Troposphere [m]
T_st = 288.15  # ISA Temperature on the 0 level [K]
p_st = 101325  # ISA Pressure on the 0 level [Pa]

### Stratosphere
H_bottom_stratosphere = H_top_troposphere + 0.01  # ISA Bottom of Stratosphere
H_top_stratosphere = 47_000  # ISA Top of Stratosphere [m]
T_bottom_stratosphere = 216.65  # Temperature at the bottom of Stratosphere [K]
p_bottom_stratosphere = 22632.06  # Pressure at the bottom of Stratosphere [Pa]
delta_bottom_strato = p_bottom_stratosphere / p_st


def ISA_delta(H: float, unit="meter") -> float:
    """
    Calucate ISA delta, the ISA pressure ratio, for a given pressure altitude
    limited to top of stratosphere
    args:
        H: Absolute height with unit declared in unit variable
    return:
        delta: Ratio of Air pressure at input height to ground pressure according to ISA [Pa]
    """

    if unit not in CONVERT_TO_M:
        raise ValueError("Invalid input unit")

    H *= CONVERT_TO_M[unit]

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
    
ISA_delta_vectorize = np.vectorize(ISA_delta)

def ISA_p(H: float, unit="meter") -> float:
    """
    Calculate the ISA pressure, for a input pressure altitude
    limited to top of stratosphere
    args:
        H: Absolute height with unit declared in unit variable
    return:
        pressure: Air pressure at input height according to ISA [Pa]
    """
    if unit not in CONVERT_TO_M:
        raise ValueError("Invalid input unit")

    H *= CONVERT_TO_M[unit]
    
    pressure = p_st * ISA_delta_vectorize(H)
    return pressure
