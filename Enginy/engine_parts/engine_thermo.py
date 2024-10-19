import cantera as ct
import numpy as np


def get_p_total(p_static: float, gamma: float, M: float) -> float:
    """
    Calculate the stagnation pressure for isentropic process
    args:
        p_static: static pressure
        gamma: heat capacity ratio
        M: Mach number of a gas
    return:
        p_total: Stagnation pressure of a gas
    """
    p_total = p_static * ((1 + ((gamma - 1) / 2) * M**2) ** (gamma / (gamma - 1)))
    return p_total


def get_T_total(T_static: float, gamma: float, M: float) -> float:
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


def get_T_static(T_total: float, gamma: float, M: float) -> float:
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


def get_p_static(
    p_total: float,
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
    p_static = p_total * (T_static / T_total) ** (gamma / (gamma - 1))
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


def mach_solver(
    mass_flow: float,
    A: float,
    gas_in: ct.Solution,
    eta: float,
    Ma_in: float,
    gas_out: ct.Solution,
    max_iterations: int = 100,
    tol: float = 0.01,
) -> tuple[float, bool]:
    """
        Calculate gas velocity at the end of engine part

        args:
            mass_flow: mass flow of gas in engine part [kg/s]
            A: Cross-sectional area [m^2]
            gas_in: Gas at entrance of engine part
            eta: engine part thermodynamic efficiency
            Ma_in: Mach number at the entrance of engine part
            gas_out: Gas at exit of engine part
            max_iterations: maximum iterations of algorithm
            tol: tolerance of calculation of gas velocity at the end
        Return:
            M_out: Mach number for gas at the end of inlet
            convergence: True if calculations are converged
    """
    n_iter = 0 #iteration counter
    converged = False #Tracking of convergence
    
    # calculated input gas properties
    V_in = Ma_in * get_a(gas_in)
    gamma_in = get_gamma(gas_in)
    T_total_in = get_T_total(gas_in.T, gamma_in, Ma_in)
    p_total_in = get_p_total(gas_in.P, gamma_in, Ma_in)

    # initial assumptions
    T_total_out = T_total_in
    V_out_guess = mass_flow / (gas_in.density * A)
    gamma_out = gamma_in
    
    while not converged and n_iter <= max_iterations:
        
        # calc properties using current guess
        
        T_static_out = gas_in.T + (V_in**2 / (2 * gas_in.cp) - V_out_guess**2 / (2 * gas_out.cp))
        p_total_out = gas_in.P * (1 + eta * V_in**2 / (2 * gas_in.cp * gas_in.T))**(gamma_in / (gamma_in - 1))
        p_static_out = p_total_out * (T_total_out / T_static_out)**(gamma_out / (gamma_out - 1))
              
        # update gas to get new properties (especially density)
        gas_out.TP = T_static_out, p_static_out
        gamma_out = get_gamma(gas_out)
        
        # update velocity calculation with new gas properties
        V_out = V_out_guess
        V_out_guess = mass_flow / (gas_out.density * A)
