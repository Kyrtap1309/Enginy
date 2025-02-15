import cantera as ct
import numpy as np
from . import gas_management

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

        #Check convergence
        if abs(V_out - V_out_guess) < tol:
            print(f"Mach calculations finished in {n_iter} iterations")
            converged = True
            M_out = V_out / get_a(gas_out)
        elif n_iter < max_iterations:
            n_iter += 1
        else:
            M_out = 0
            print(f"Inlet calculations failed")
    
    return M_out, converged


def compressor_solver(gas_in: ct.Solution,
                      n_stages: int,
                      compress: float, 
                      comp_eta: float,
                      M_in: float,
                      gas_out: ct.Solution,
                      max_iterations: int = 5000):
    
    """
        Calculate output parameters of compressor

        args:
            gas_in: Gas at entrance of compressor
            n_stages: Number of stages of compressor
            compress: Overall compression ratio
            comp_eta: Compressor's thermodynamic efficiency
            M_in: Mach number at the entrance of compressor
            gas_out: Gas at exit of engine part
            max_iterations: maximum iterations of algorithm
            
        Return:
            T_out, p_out : list with static temperatures, static pressures of each stage
            convergence  : True if converged, False if not
            compressor_work : specific work used to compress gas [in kJ/kg]
    """

    #Input gas properties
    gamma_in = get_gamma(gas_in)
    T_total_in = get_T_total(gas_in.T, gamma_in, M_in)
    p_total_in = get_p_total(gas_in.P, gamma_in, M_in)

    #Pressure ratio per stage
    compress_stage = compress ** (1 / n_stages)

    n_stages = int(n_stages)

    # gradually shift pressure towards the initial stages
    stage_multiplier = np.ones(n_stages)
    shift = 0.001 # overall shift amount, per iteration
    shifter = np.ones(n_stages)
    step_shift = shift / n_stages # shift step per stage

    center = int(n_stages/2)
    for i in range(center):
        shifter[i] = 1 + (center - i) * step_shift # shift initial stages UP
        shifter[n_stages - i - 1] = 1 - ((center - i) * step_shift) # shift later stages DOWN

    # pressure rise shift loop control
    converged = False
    n_iter = 0
    prev_delta_t = 1000 # start with high value to trigger condition

    # stage properties
    stages_p_out = np.zeros(n_stages) # holds the press data for each stage
    stages_T_out = np.zeros(n_stages) # holds the temp data for each stage
    stage_gas = (ct.Solution(gas_management.reaction_mechanism, gas_management.phase_name)) # internal object to keep track of gas properties
    stage_gas.X = gas_management.comp_air

    # compressor output data
    compressor_work = 0 # collector for specific work used to compress gas, for all stages, in kJ/kg


    while not converged and n_iter <= max_iterations:

        stage_gas.TP = gas_in.T, gas_in.P
        
        for st_counter in range(n_stages):
            T_i = stage_gas.T

            gamma = get_gamma(stage_gas)
            p_total = get_p_total(stage_gas.P, gamma, M_in) * compress_stage * stage_multiplier[st_counter] # pressure rise per stage
            T_total = T_total_in / comp_eta * ((p_total / p_total_in) ** ((gamma - 1) / gamma) - 1) + T_total_in

            T_static = get_T_static(T_total, gamma, M_in)
            p_static = get_p_static(p_total, T_static, T_total, gamma)
            stage_gas.TP = T_static, p_static

            gamma = get_gamma(stage_gas)
            T_static = get_T_static(T_total, gamma, M_in)
            p_static = get_p_static(p_total, T_static, T_total, gamma)
            stage_gas.TP = T_static, p_static

            # store conditions for plotting later
            stages_p_out[st_counter] = p_static
            stages_T_out[st_counter] = T_static

            # store stage work
            compressor_work += stage_gas.cp * (T_static - T_i) # in kJ/kg

            # update for next stage
            p_total_in = p_total
            T_total_in = T_total

            # logic to account for different number of stages
        if n_stages > 2: # typical multi-stage case
            max_delta_t = np.diff(stages_T_out).max()
        elif n_stages > 1: # special case : np.diff will drop one in vector length
            max_delta_t = max(stages_T_out[1] - stages_T_out[0], stages_T_out[0] - gas_in.T)
        else: # case for 1 stage
            max_delta_t = T_static - gas_in.T

        
        # loop objective is to get minimum temperature difference between all stages
        # by shifting pressure rise towards initial stages
        if max_delta_t < prev_delta_t and n_iter < max_iterations:

            n_iter += 1
            # clear previous data and reset inputs
            T_total_in = get_T_total(gas_in.T, gamma_in, M_in)
            p_total_in = get_p_total(gas_in.P, gamma_in, M_in)
            compressor_work = 0 #zero out work absorbed by compressor
            
            # increase pressure shift towards initial stages
            stage_multiplier = np.multiply(stage_multiplier, shifter)
            prev_delta_t = max_delta_t
        
        elif n_iter >= max_iterations:
            print(f'compressor finished, NOT converged, niter={n_iter}, max delta T={max_delta_t:0.1f}')
            n_iter += 1
        else:
            converged = True
            print(f'compressor finished, converged, niter={n_iter}, max delta T={max_delta_t:0.1f}, pressure p = {p_static}')
        
        
    # update gas_out to pass properties back
    gas_out.TP = T_static, p_static


    return list(zip(stages_T_out, stages_p_out)), converged, compressor_work

def combustor_solver(gas_in: ct.Solution,
                     V_nominal: float,
                     M_in: float,
                     pressure_lost: float,
                     gas_out: ct.Solution):
    
    """
        Calculate output parameters of combustor

        args:
            gas_in: Gas at entrance of combustor
            v_nominal: Nominal velocity of gas at combustor
            M_in: Mach number at the entrance of compressor
            pressure_lost: Relative total pressure loss,
            gas_out: Gas at exit of engine part
            
        Return:
            M_out: Mach number for gas at exit of combustor
            convergence: Convergence bool
            gas_out: Cantera solution with updated gas parameters

    """

    tol = 0.01
    max_iter = 100
    converged = False
    n_iter = 0

    gamma_in = get_gamma(gas_in)
    T_total_in = get_T_total(gas_in.T, gamma_in, M_in)
    p_total_in = get_p_total(gas_in.P, gamma_in, M_in)


    T_total_out = T_total_in
    p_total_out = p_total_in * (1 - pressure_lost)
    T_out = gas_in.T
    p_out = gas_in.P

    while not converged and n_iter <= max_iter:

        gas_out.TP = T_out, p_out
        a_out = get_a(gas_out)
        M_out = V_nominal / a_out
        gamma_out = get_gamma(gas_out)
        T_out = get_T_static(T_total_out, gamma_out, M_out)
        p_out = get_p_static(p_total_out, T_out, T_total_out, gamma_out)

        if abs(gas_out.P - p_out) < tol:
            print(f"Combustor finished, converged, niter = {n_iter}")
            converged = True
        elif n_iter < max_iter:
            n_iter += 1
        else:
            M_out = 0
            print(f"Combustor finished, NOT converged, niter = {n_iter}")
    
    return M_out, converged