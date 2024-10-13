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


def _handle_units(H: float, unit, converter: dict = CONVERT_TO_M) -> float:
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


def inv_ISA_delta(delta: float, unit="meter") -> float:
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


def inv_ISA_p(p: float, unit="meter") -> float:
    """
    Calucate ISA pressure alitute based on input ISA pressure limited to top of stratosphere
    args:
        pressure: Air pressure [Pa]
        unit: Unit of returned altitude
    return:
        H: Altitude with input unit
    """
    altitude = inv_ISA_delta(p / p_st, unit)
    return altitude


def inv_ISA_sigma(sigma: float, unit="meter") -> float:
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


def inv_ISA_rho(rho: float, unit="meter") -> float:
    """
    Calucate ISA density alitute based on input ISA density limited to top of stratosphere
    args:
        pressure: Air density [kg/m3]
        unit: Unit of returned altitude
    return:
        H: Altitude with input unit
    """
    altitude = inv_ISA_sigma(rho / Rho_st, unit)
    return altitude


def calibrated_v_to_mach(Vc, H, speed_unit="mps", altitude_unit="meter") -> float:
    """
    Calculate Mach number for a given calibrated airspeed and altitude
    args:
        Vc: calibrated airspeed
        Hc: Altitude
        speed_unit: unit of input calibrated airspeed
        altitude_unit: unit of input alititude
    return:
        Ma: Mach number
    """
    d = ISA_delta(H, altitude_unit)
    Vc = _handle_units(Vc, speed_unit, CONVERT_TO_M_S)
    ma = np.sqrt(
        5
        * (
            ((1 / d) * ((1 + 0.2 * ((Vc) / a_st) ** 2) ** (7 / 2) - 1) + 1) ** (2 / 7)
            - 1
        )
    )
    return ma


def mach_to_calibrated_v(Ma, H, speed_unit="mps", altitude_unit="meter") -> float:
    """
    Calculate calibrate airspeed for a given mach number and altitude
    args:
        Ma: Mach number
        Hc: Altitude
        speed_unit: unit of return calibrated airspeed
        altitude_unit: unit of input alititude
    return:
        Vc: Calibrated airspeed
    """
    d = ISA_delta(H, altitude_unit)
    Vc = a_st * np.sqrt(
        5 * (((d * ((1 + 0.2 * Ma**2) ** (7 / 2) - 1)) + 1) ** (2 / 7) - 1)
    )
    Vc = _handle_units(Vc, speed_unit, converter=CONVERT_FROM_M_S)
    return Vc


def true_v_to_eq_v(
    Vt, H, input_speed_unit="mps", altitude_unit="meter", return_speed_unit="mps"
) -> float:
    """
    Calculate equivalent airspeed for a given true airspeed and altitude
    args:
        Vt: True airspeed
        H: Altitude
        input_speed_unit: unit of input true airspeed
        return_speed_unit: unit of return equivalent airspeed
        altitude_unit: unit of input alititude
    return:
        Ve: Equivalent airspeed
    """
    Vt = _handle_units(Vt, unit=input_speed_unit, converter=CONVERT_TO_M_S)
    H = _handle_units(H, unit=altitude_unit, converter=CONVERT_TO_M)
    Ve = Vt * np.sqrt(ISA_sigma(H, unit="meter"))
    Ve = _handle_units(Ve, unit=return_speed_unit, converter=CONVERT_FROM_M_S)
    return Ve


def eq_v_to_true_v(
    Ve, H, input_speed_unit="mps", altitude_unit="meter", return_speed_unit="mps"
) -> float:
    """
    Calculate true airspeed for a given equivalent airspeed and altitude
    args:
        Ve: equivalent airspeed
        H: Altitude
        input_speed_unit: unit of input equivalent airspeed
        return_speed_unit: unit of return true airspeed
        altitude_unit: unit of input alititude
    return:
        Vt: True airspeed
    """
    Ve = _handle_units(Ve, unit=input_speed_unit, converter=CONVERT_TO_M_S)
    H = _handle_units(H, unit=altitude_unit, converter=CONVERT_TO_M)
    Vt = Ve / np.sqrt(ISA_sigma(H, unit="meter"))
    Vt = _handle_units(Vt, unit=return_speed_unit, converter=CONVERT_FROM_M_S)
    return Vt


def mach_to_eq_v(Ma, H, alitude_unit="meter", speed_unit="mps") -> float:
    """
    Calculate equivalent airspeed for a given mach number and altitude
    args:
        Ma: Mach number
        Hc: Altitude
        altitude_unit: unit of input alititude
        speed_unit: unit of return equivalent airspeed
    return:
        Ve: Equivalent airspeed
    """
    temp = (1 + 0.2 * Ma**2) ** (7 / 2) - 1
    pa = ISA_p(H, alitude_unit)
    Ve = np.sqrt((1 / Rho_st) * (7 * pa * ((temp + 1) ** (2 / 7) - 1)))
    Ve = _handle_units(Ve, speed_unit, converter=CONVERT_FROM_M_S)
    return Ve


def mach_to_true_v(Ma, H, alitude_unit="meter", speed_unit="mps") -> float:
    """
    Calculate true airspeed for a given mach number and altitude
    args:
        Ma: Mach number
        Hc: Altitude
        altitude_unit: unit of input alititude
        speed_unit: unit of return true airspeed
    return:
        Vt: True airspeed
    """
    H = _handle_units(H, unit=alitude_unit, converter=CONVERT_TO_M)
    temp = (1 + 0.2 * Ma**2) ** (7 / 2) - 1
    pa = ISA_p(H, unit="meter")
    Ve = np.sqrt((1 / Rho_st) * (7 * pa * ((temp + 1) ** (2 / 7) - 1)))
    Vt = eq_v_to_true_v(
        Ve=Ve,
        H=H,
        input_speed_unit="meter",
        altitude_unit="meter",
        return_speed_unit=speed_unit,
    )
    return Vt


def true_v_to_mach(Vt, H, altitude_unit="meter", speed_unit="mps") -> float:
    """
    Calculate Mach number for a given true airspeed and altitude
    args:
        Vt: True Airspeed
        Hc: Altitude
        altitude_unit: unit of input alititude
        speed_unit: unit of input true airspeed
    return:
        Ma: Mach number
    """
    Vt = _handle_units(Vt, unit=speed_unit, converter=CONVERT_TO_M_S)
    H = _handle_units(H, unit=altitude_unit, converter=CONVERT_TO_M)
    Ma = Vt / (np.sqrt(gamma * R * ISA_T(H, unit="meter")))
    return Ma


def true_v_to_calibrated_v(
    Vt, H, input_speed_unit="mps", altitude_unit="meter", return_speed_unit="mps"
) -> float:
    """
    Calculate calibrated airspeed for a given true airspeed and altitude
    args:
        Vt: True airspeed
        H: Altitude
        input_speed_unit: unit of input true airspeed
        return_speed_unit: unit of return calibrated airspeed
        altitude_unit: unit of input alititude
    return:
        Vc: Calibrated airspeed
    """
    Ma = true_v_to_mach(Vt, H, altitude_unit, input_speed_unit)
    Vc = mach_to_calibrated_v(Ma, H, return_speed_unit, altitude_unit)
    return Vc


def calibrated_v_to_true_v(
    Vc, H, input_speed_unit="mps", altitude_unit="meter", return_speed_unit="mps"
) -> float:
    """
    Calculate true airspeed for a given calibrated airspeed and altitude
    args:
        Vt: Calibrated airspeed
        H: Altitude
        input_speed_unit: unit of input calibrated airspeed
        return_speed_unit: unit of return true airspeed
        altitude_unit: unit of input alititude
    return:
        Vc: True airspeed
    """
    Ma = calibrated_v_to_mach(Vc, H, input_speed_unit, altitude_unit)
    Vt = mach_to_true_v(Ma, altitude_unit, altitude_unit, return_speed_unit)
    return Vt


def calibrated_v_to_eq_v(
    Vc, H, input_speed_unit="mps", altitude_unit="meter", return_speed_unit="mps"
) -> float:
    """
    Calculate equivalent airspeed for a given calibrated airspeed and altitude
    args:
        Vc: Calibrated airspeed
        H: Altitude
        input_speed_unit: unit of input calibrated airspeed
        return_speed_unit: unit of return equivalent airspeed
        altitude_unit: unit of input alititude
    return:
        Ve: Equivalent airspeed
    """
    Ma = calibrated_v_to_mach(Vc, H, input_speed_unit, altitude_unit)
    Ve = mach_to_eq_v(Ma, H, altitude_unit, return_speed_unit)
    return Ve


def eq_v_to_calibrated_v(
    Ve, H, input_speed_unit="mps", altitude_unit="meter", return_speed_unit="mps"
) -> float:
    """
    Calculate calibrated airspeed for a given equivalent airspeed and altitude
    args:
        Ve: Equivalent airspeed
        H: Altitude
        input_speed_unit: unit of input equivalent airspeed
        return_speed_unit: unit of return calibrated airspeed
        altitude_unit: unit of input alititude
    return:
        Vc: Calibrated airspeed
    """
    Vt = eq_v_to_true_v(Ve, H, input_speed_unit, altitude_unit, return_speed_unit="mps")
    Ma = true_v_to_mach(Vt, H, altitude_unit, speed_unit="mps")
    Vc = mach_to_calibrated_v(Ma, H, return_speed_unit, altitude_unit)
    return Vc


def eq_v_to_mach(Ve, H, speed_unit="mps", altitude_unit="meter") -> float:
    """
    Calculate Mach number for a given equivalent airspeed and altitude
    args:
        Ve: Equivalent Airspeed
        Hc: Altitude
        altitude_unit: unit of input alititude
        speed_unit: unit of input equivalent airspeed
    return:
        Ma: Mach number
    """
    Vt = eq_v_to_true_v(Ve, H, speed_unit, altitude_unit, return_speed_unit="mps")
    Ma = true_v_to_mach(Vt, H, altitude_unit, speed_unit="mps")
    return Ma
