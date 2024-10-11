import cantera as ct
import numpy as np

def get_p_total(p_static: float,
                gamma: float,
                M:float) -> float:
    """
    Calculate the stagnation pressure for isentropic process
    args:
        p_static: static pressure 
        gamma: heat capacity ratio
        M: Mach number of a gas
    return:
        p_total: Stagnation pressure of a gas
    """
    p_total = p_static * ((1 + ((gamma - 1) / 2) * M ** 2) ** (gamma / (gamma - 1)))
    return p_total

def get_T_total(T_static: float,
                gamma: float,
                M:float) -> float:
    """
    Calculate the stagnation temperature for isentropic process
    args:
        T_static: static temperature of a gas [K]
        gamma: heat capacity ratio
        M: Mach number of a gas
    return:
        T_total: Stagnation temperature of a gas
    """
    T_total = T_static * (1 + ((gamma - 1) / 2) * M**2)
    return T_total

def get_T_static(T_total: float,
                gamma: float,
                M:float) -> float:
    """
    Calculate the static temperature for isentropic process
    args:
        T_total: stagnatic temperature of a gas [K]
        gamma: heat capacity ratio
        M: Mach number of a gas
    return:
        T_static: Static temperature of a gas
    """
    T_static = T_total / (1 + ((gamma - 1) / 2) * M**2)
    return T_static

def get_p_static(p_total: float,
                 T_static: float,
                 T_total: float,
                 gamma: float,
                 ) -> float:
    """
    Calculate the static pressure for isentropic process
    args:
        p_total: stagnatic pressure of a gas 
        T_static: Static temperature of a gas [K] 
        T_total: Stagnation temperature of a gas [K]
        gamma: heat capacity ratio
        M: Mach number of a gas
    return:
        p_static: Static pressure of a gas
    """
    p_static = p_total * (T_static/T_total) ** (gamma/(gamma - 1))
    return p_static

def get_gamma(gas: ct.Solution) -> float:
    """
    Calculate a heat capacity ratio
    args:
        gas: cantera.Solution object which represents gas or mixture of gases
    return:
        gamma: het capacity ratio of a gas
    """
    gamma = gas.cp / gas.cv
    return gamma

def get_R(gas: ct.Solution) -> float:
    """
    Calculate a gas constant:
    args:
        gas: cantera.Solution object which represents gas or mixture of gases
    return:
        R: gas constant (J/(kg * K))
    """
    r_constant = gas.cp - gas.cv
    return r_constant

def get_a(gas: ct.Solution) -> float:
    """
    Calculate a local speed of sound for a input gas:
    args:
        gas: cantera.Solution object which represents gas or mixture of gases
    return:
        a: local speed of sound [m/s]
    """
    a = np.sqrt(get_R(gas) * get_gamma(gas) * gas.T)
    return a