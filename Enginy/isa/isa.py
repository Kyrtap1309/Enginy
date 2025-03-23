import numpy as np

# Constants

##Convertion of length units to meters
CONVERT_TO_M = {
    "meter": 1,
    "feet": 0.3048,
    "kilometer": 1000,
}

##Convertion of speed units to meters per second
CONVERT_TO_M_S = {"mps": 1, "knots": 0.5144, "kph": 0.27777}

##Convertion of length units in meters
CONVERT_FROM_M = {key: 1 / value for key, value in CONVERT_TO_M.items()}
##Convertion of speed units in meters per second
CONVERT_FROM_M_S = {key: 1 / value for key, value in CONVERT_TO_M_S.items()}

## Physic Constants
### Troposphere
R = 287.053  # Gas Constant [m2/s2/K]
g_st = 9.8067  # Standard Acceleration of Gravity [m/s2]
L = -6.5 / 1000  # Temperature ISA gradient [K/m]
H_top_troposphere = 11_000  # ISA Top of Troposphere [m]
T_st = 288.15  # ISA Temperature on the 0 level [K]
p_st = 101_325  # ISA Pressure on the 0 level [Pa]
Rho_st = 1.225  # ISA Density on the 0 level [kg/m3]
a_st = np.sqrt(1.4 * R * T_st)  # ISA speed of sound on the 0 level [m/s]
gamma = 1.4  # ISA heat capacity ratio for air

### Stratosphere
H_bottom_stratosphere = H_top_troposphere + 0.01  # ISA Bottom of Stratosphere
H_top_stratosphere = 47_000  # ISA Top of Stratosphere [m]
T_bottom_stratosphere = 216.65  # Temperature at the bottom of Stratosphere [K]
p_bottom_stratosphere = 22_632.06  # Pressure at the bottom of Stratosphere [Pa]
p_top_stratosphere = 5474.88  # Pressure at the top of Stratosphere [Pa]
Rho_bottom_stratosphere = 0.36392  # Density at the bottom of Stratosphere [kg/m3]
Rho_top_stratosphere = 0.08803  # Density at the top of Stratosphere [kg/m3]
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
sigma_top_strato = (
    Rho_top_stratosphere / Rho_st
)  # ISA Sigma value at the top of Stratosphere


def _handle_units(height: float, unit, converter: dict = CONVERT_TO_M) -> float:
    if unit not in CONVERT_TO_M:
        raise ValueError("Invalid input unit")
    else:
        return height * converter[unit]


def isa_delta(height: float, unit="meter") -> float:
    """
    Calucate ISA delta: the ISA pressure ratio, for a given pressure altitude
    limited to top of stratosphere
    args:
        height: Absolute height with unit declared in unit variable
    return:
        delta: Ratio of Air pressure at input height to ground pressure according to ISA [Pa]
    """

    height = _handle_units(height, unit)

    if H_top_troposphere >= height:
        delta = (1 + (L / T_st) * height) ** (-g_st / (L * R))
        return delta
    elif H_top_stratosphere >= height:
        delta = delta_bottom_strato * np.exp(
            -(g_st / (R * T_bottom_stratosphere)) * (height - H_bottom_stratosphere)
        )
        return delta
    else:
        raise ValueError("Altitude above stratospheric limit")


def isa_p(height: float, unit="meter") -> float:
    """
    Calculate the ISA pressure, for a input pressure altitude
    limited to top of stratosphere
    args:
        H: Absolute height with unit declared in unit variable
    return:
        pressure: Air pressure at input height according to ISA [Pa]
    """
    height = _handle_units(height, unit)

    pressure = p_st * isa_delta(height, unit="meter")
    return pressure


def isa_theta(height: float, unit="meter") -> float:
    """
    Calucate ISA theta: the ISA temperature ratio, for a given temperature altitude
    limited to top of stratosphere
    args:
        height: Absolute height with unit declared in unit variable
    return:
        temperature: Air temperature at input height according to ISA [K]
    """
    height = _handle_units(height, unit)

    if H_top_troposphere >= height:
        temperature = 1 + (L / T_st) * height
        return temperature
    elif H_top_stratosphere >= height:
        temperature = theta_bottom_strato
        return temperature
    else:
        raise ValueError("Altitude above stratospheric limit")


def isa_temperature(height: float, unit="meter") -> float:
    """
    Calculate the ISA temperature, for a input temperature altitude
    limited to top of stratosphere
    args:
        height: Absolute height with unit declared in unit variable
    return:
        temperature: Air pressure at input height according to ISA [Pa]
    """
    height = _handle_units(height, unit)

    temperature = T_st * isa_theta(height, unit="meter")
    return temperature


def isa_sigma(height: float, unit="meter") -> float:
    """
    Calucate ISA sigma: the ISA density ratio, for a given pressure altitude
    limited to top of stratosphere
    args:
        height: Absolute height with unit declared in unit variable
    return:
        delta: Ratio of density pressure at input height to ground density according to ISA [Pa]
    """

    height = _handle_units(height, unit)

    if H_top_troposphere >= height:
        sigma = (1 + (L / T_st) * height) ** (-g_st / (L * R) - 1)
        return sigma
    elif H_top_stratosphere >= height:
        sigma = sigma_bottom_strato * np.exp(
            -(g_st / (R * T_bottom_stratosphere)) * (height - H_bottom_stratosphere)
        )
        return sigma
    else:
        raise ValueError("Altitude above stratospheric limit")


def isa_rho(height: float, unit="meter") -> float:
    """
    Calculate the ISA density, for a input density altitude
    limited to top of stratosphere
    args:
        height: Absolute height with unit declared in unit variable
    return:
        rho: Air density at input height according to ISA [Pa]
    """
    height = _handle_units(height, unit)

    rho = Rho_st * isa_sigma(height, unit="meter")
    return rho


def inv_isa_delta(delta: float, unit="meter") -> float:
    """
    Calucate ISA pressure alitute based on input ISA delta limited to top of stratosphere
    args:
        delta: ISA delta
        unit: Unit of returned altitude
    return:
        H: Altitude with input unit
    """
    if delta > delta_bottom_strato:
        altitude = (T_st / L) * ((delta) ** (-(L * R) / g_st) - 1)
        altitude = _handle_units(altitude, unit, CONVERT_FROM_M)
        return altitude
    elif delta >= delta_top_strato:
        altitude = H_bottom_stratosphere + (R * T_bottom_stratosphere / g_st) * np.log(
            delta_bottom_strato / delta
        )
        altitude = _handle_units(altitude, unit, CONVERT_FROM_M)
        return altitude
    else:
        raise ValueError("Pressure/Altitude lower than top stratosphere level")


def inv_isa_p(p: float, unit="meter") -> float:
    """
    Calucate ISA pressure alitute based on input ISA pressure limited to top of stratosphere
    args:
        pressure: Air pressure [Pa]
        unit: Unit of returned altitude
    return:
        H: Altitude with input unit
    """
    altitude = inv_isa_delta(p / p_st, unit)
    return altitude


def inv_isa_sigma(sigma: float, unit="meter") -> float:
    """
    Calucate  alitute based on input ISA sigma limited to top of stratosphere
    args:
        sigma: ISA sigma
        unit: Unit of returned altitude
    return:
        H: Altitude with input unit
    """
    if sigma > sigma_bottom_strato:
        altitude = (T_st / L) * ((sigma) ** (1 / (-g_st / (L * R) - 1)) - 1)
        altitude = _handle_units(altitude, unit, CONVERT_FROM_M)
        return altitude
    elif sigma >= sigma_top_strato:
        altitude = H_bottom_stratosphere + (R * T_bottom_stratosphere / g_st) * np.log(
            sigma_bottom_strato / sigma
        )
        altitude = _handle_units(altitude, unit, CONVERT_FROM_M)
        return altitude
    else:
        raise ValueError("Pressure/Altitude lower than top stratosphere level")


def inv_isa_rho(rho: float, unit="meter") -> float:
    """
    Calucate ISA density alitute based on input ISA density limited to top of stratosphere
    args:
        pressure: Air density [kg/m3]
        unit: Unit of returned altitude
    return:
        H: Altitude with input unit
    """
    altitude = inv_isa_sigma(rho / Rho_st, unit)
    return altitude


def calibrated_v_to_mach(
    v_calibrated, height, speed_unit="mps", altitude_unit="meter"
) -> float:
    """
    Calculate Mach number for a given calibrated airspeed and altitude
    args:
        V_calibrated: calibrated airspeed
        Hc: Altitude
        speed_unit: unit of input calibrated airspeed
        altitude_unit: unit of input alititude
    return:
        Ma: Mach number
    """
    d = isa_delta(height, altitude_unit)
    v_calibrated = _handle_units(v_calibrated, speed_unit, CONVERT_TO_M_S)
    ma = np.sqrt(
        5
        * (
            ((1 / d) * ((1 + 0.2 * ((v_calibrated) / a_st) ** 2) ** (7 / 2) - 1) + 1)
            ** (2 / 7)
            - 1
        )
    )
    return ma


def mach_to_calibrated_v(ma, height, speed_unit="mps", altitude_unit="meter") -> float:
    """
    Calculate calibrate airspeed for a given mach number and altitude
    args:
        ma: Mach number
        height: Altitude
        speed_unit: unit of return calibrated airspeed
        altitude_unit: unit of input alititude
    return:
        v_calibrated: Calibrated airspeed
    """
    d = isa_delta(height, altitude_unit)
    v_calibrated = a_st * np.sqrt(
        5 * (((d * ((1 + 0.2 * ma**2) ** (7 / 2) - 1)) + 1) ** (2 / 7) - 1)
    )
    v_calibrated = _handle_units(v_calibrated, speed_unit, converter=CONVERT_FROM_M_S)
    return v_calibrated


def true_v_to_eq_v(
    v_true,
    height,
    input_speed_unit="mps",
    altitude_unit="meter",
    return_speed_unit="mps",
) -> float:
    """
    Calculate equivalent airspeed for a given true airspeed and altitude
    args:
        v_true: True airspeed
        height: Altitude
        input_speed_unit: unit of input true airspeed
        return_speed_unit: unit of return equivalent airspeed
        altitude_unit: unit of input alititude
    return:
        v_equivalent: Equivalent airspeed
    """
    v_true = _handle_units(v_true, unit=input_speed_unit, converter=CONVERT_TO_M_S)
    height = _handle_units(height, unit=altitude_unit, converter=CONVERT_TO_M)
    v_equivalent = v_true * np.sqrt(isa_sigma(height, unit="meter"))
    v_equivalent = _handle_units(
        v_equivalent, unit=return_speed_unit, converter=CONVERT_FROM_M_S
    )
    return v_equivalent


def eq_v_to_true_v(
    v_equivalent,
    height,
    input_speed_unit="mps",
    altitude_unit="meter",
    return_speed_unit="mps",
) -> float:
    """
    Calculate true airspeed for a given equivalent airspeed and altitude
    args:
        v_equivalent: equivalent airspeed
        height: Altitude
        input_speed_unit: unit of input equivalent airspeed
        return_speed_unit: unit of return true airspeed
        altitude_unit: unit of input alititude
    return:
        v_true: True airspeed
    """
    v_equivalent = _handle_units(
        v_equivalent, unit=input_speed_unit, converter=CONVERT_TO_M_S
    )
    height = _handle_units(height, unit=altitude_unit, converter=CONVERT_TO_M)
    v_true = v_equivalent / np.sqrt(isa_sigma(height, unit="meter"))
    v_true = _handle_units(v_true, unit=return_speed_unit, converter=CONVERT_FROM_M_S)
    return v_true


def mach_to_eq_v(ma, height, alitude_unit="meter", speed_unit="mps") -> float:
    """
    Calculate equivalent airspeed for a given mach number and altitude
    args:
        ma: Mach number
        height: Altitude
        altitude_unit: unit of input alititude
        speed_unit: unit of return equivalent airspeed
    return:
        v_equivalent: Equivalent airspeed
    """
    temp = (1 + 0.2 * ma**2) ** (7 / 2) - 1
    pa = isa_p(height, alitude_unit)
    v_equivalent = np.sqrt((1 / Rho_st) * (7 * pa * ((temp + 1) ** (2 / 7) - 1)))
    v_equivalent = _handle_units(v_equivalent, speed_unit, converter=CONVERT_FROM_M_S)
    return v_equivalent


def mach_to_true_v(ma, height, alitude_unit="meter", speed_unit="mps") -> float:
    """
    Calculate true airspeed for a given mach number and altitude
    args:
        ma: Mach number
        height: Altitude
        altitude_unit: unit of input alititude
        speed_unit: unit of return true airspeed
    return:
        v_true: True airspeed
    """
    height = _handle_units(height, unit=alitude_unit, converter=CONVERT_TO_M)
    temperature = (1 + 0.2 * ma**2) ** (7 / 2) - 1
    pressure = isa_p(height, unit="meter")
    v_equivalent = np.sqrt(
        (1 / Rho_st) * (7 * pressure * ((temperature + 1) ** (2 / 7) - 1))
    )
    v_true = eq_v_to_true_v(
        v_equivalent=v_equivalent,
        height=height,
        input_speed_unit="meter",
        altitude_unit="meter",
        return_speed_unit=speed_unit,
    )
    return v_true


def true_v_to_mach(v_true, height, altitude_unit="meter", speed_unit="mps") -> float:
    """
    Calculate Mach number or a given true airspeed and altitude
    args:
        v_true: True Airspeed
        height: Altitude
        altitude_unit: unit of input alititude
        speed_unit: unit of input true airspeed
    return:
        ma: Mach number
    """
    v_true = _handle_units(v_true, unit=speed_unit, converter=CONVERT_TO_M_S)
    height = _handle_units(height, unit=altitude_unit, converter=CONVERT_TO_M)
    ma = v_true / (np.sqrt(gamma * R * isa_temperature(height, unit="meter")))
    return ma


def true_v_to_calibrated_v(
    v_true,
    height,
    input_speed_unit="mps",
    altitude_unit="meter",
    return_speed_unit="mps",
) -> float:
    """
    Calculate calibrated airspeed for a given true airspeed and altitude
    args:
        v_true: True airspeed
        height: Altitude
        input_speed_unit: unit of input true airspeed
        return_speed_unit: unit of return calibrated airspeed
        altitude_unit: unit of input alititude
    return:
        Vc: Calibrated airspeed
    """
    ma = true_v_to_mach(v_true, height, altitude_unit, input_speed_unit)
    v_calibrated = mach_to_calibrated_v(ma, height, return_speed_unit, altitude_unit)
    return v_calibrated


def calibrated_v_to_true_v(
    v_calibrated,
    height,
    input_speed_unit="mps",
    altitude_unit="meter",
    return_speed_unit="mps",
) -> float:
    """
    Calculate true airspeed for a given calibrated airspeed and altitude
    args:
        V_calibrated: Calibrated airspeed
        height: Altitude
        input_speed_unit: unit of input calibrated airspeed
        return_speed_unit: unit of return true airspeed
        altitude_unit: unit of input alititude
    return:
        v_true: True airspeed
    """
    ma = calibrated_v_to_mach(v_calibrated, height, input_speed_unit, altitude_unit)
    v_true = mach_to_true_v(ma, altitude_unit, altitude_unit, return_speed_unit)
    return v_true


def calibrated_v_to_eq_v(
    v_calibrated,
    height,
    input_speed_unit="mps",
    altitude_unit="meter",
    return_speed_unit="mps",
) -> float:
    """
    Calculate equivalent airspeed for a given calibrated airspeed and altitude
    args:
        v_calibrated: Calibrated airspeed
        height: Altitude
        input_speed_unit: unit of input calibrated airspeed
        return_speed_unit: unit of return equivalent airspeed
        altitude_unit: unit of input alititude
    return:
        v_equivalent: Equivalent airspeed
    """
    ma = calibrated_v_to_mach(v_calibrated, height, input_speed_unit, altitude_unit)
    v_equivalent = mach_to_eq_v(ma, height, altitude_unit, return_speed_unit)
    return v_equivalent


def eq_v_to_calibrated_v(
    v_equivalent,
    height,
    input_speed_unit="mps",
    altitude_unit="meter",
    return_speed_unit="mps",
) -> float:
    """
    Calculate calibrated airspeed for a given equivalent airspeed and altitude
    args:
        V_equivalent: Equivalent airspeed
        height: Altitude
        input_speed_unit: unit of input equivalent airspeed
        return_speed_unit: unit of return calibrated airspeed
        altitude_unit: unit of input alititude
    return:
        v_calibrated: Calibrated airspeed
    """
    v_true = eq_v_to_true_v(
        v_equivalent, height, input_speed_unit, altitude_unit, return_speed_unit="mps"
    )
    ma = true_v_to_mach(v_true, height, altitude_unit, speed_unit="mps")
    v_calibrated = mach_to_calibrated_v(ma, height, return_speed_unit, altitude_unit)
    return v_calibrated


def eq_v_to_mach(
    v_equivalent, height, speed_unit="mps", altitude_unit="meter"
) -> float:
    """
    Calculate Mach number for a given equivalent airspeed and altitude
    args:
        v_equivalent: Equivalent Airspeed
        Hc: Altitude
        altitude_unit: unit of input alititude
        speed_unit: unit of input equivalent airspeed
    return:
        ma: Mach number
    """
    v_true = eq_v_to_true_v(
        v_equivalent, height, speed_unit, altitude_unit, return_speed_unit="mps"
    )
    ma = true_v_to_mach(v_true, height, altitude_unit, speed_unit="mps")
    return ma
