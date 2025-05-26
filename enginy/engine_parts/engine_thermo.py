import cantera as ct
import numpy as np

from enginy.engine_parts import gas_management

MIN_COMPRESSOR_NUM_OF_STAGES = 2


def get_p_total(p_static: float, gamma: float, mach: float) -> float:
    """
    Calculate the stagnation pressure for isentropic process
    args:
        p_static: static pressure
        gamma: heat capacity ratio
        mach: Mach number of a gas
    return:
        p_total: Stagnation pressure of a gas
    """
    p_total: float = p_static * (
        (1 + ((gamma - 1) / 2) * mach**2) ** (gamma / (gamma - 1))
    )
    return p_total


def get_temperature_total(
    temperature_static: float, gamma: float, mach: float
) -> float:
    """
    Calculate the stagnation temperature for isentropic process
    args:
        temperature_static: static temperature of a gas [K]
        gamma: heat capacity ratio
        mach: Mach number of a gas
    return:
        temperature_total: Stagnation temperature of a gas
    """
    temperature_total: float = temperature_static * (1 + ((gamma - 1) / 2) * mach**2)
    return temperature_total


def get_temperature_static(
    temperature_total: float, gamma: float, mach: float
) -> float:
    """
    Calculate the static temperature for isentropic process
    args:
        temperature_total: stagnatic temperature of a gas [K]
        gamma: heat capacity ratio
        mach: Mach number of a gas
    return:
        temperature_static: Static temperature of a gas
    """
    temperature_static: float = temperature_total / (1 + ((gamma - 1) / 2) * mach**2)
    return temperature_static


def get_p_static(
    p_total: float,
    temperature_static: float,
    temperature_total: float,
    gamma: float,
) -> float:
    """
    Calculate the static pressure for isentropic process
    args:
        p_total: stagnatic pressure of a gas
        temperature_static: Static temperature of a gas [K]
        temperature_total: Stagnation temperature of a gas [K]
        gamma: heat capacity ratio
        M: Mach number of a gas
    return:
        p_static: Static pressure of a gas
    """
    p_static: float = p_total * (temperature_static / temperature_total) ** (
        gamma / (gamma - 1)
    )
    return p_static


def get_gamma(gas: ct.Solution) -> float:
    """
    Calculate a heat capacity ratio
    args:
        gas: cantera.Solution object which represents gas or mixture of gases
    return:
        gamma: het capacity ratio of a gas
    """
    gamma: float = float(gas.cp / gas.cv)  # Fix: Explicitly cast to float
    return gamma


def get_gas_constant(gas: ct.Solution) -> float:
    """
    Calculate a gas constant:
    args:
        gas: cantera.Solution object which represents gas or mixture of gases
    return:
        R: gas constant (J/(kg * K))
    """
    gas_constant: float = float(gas.cp - gas.cv)  # Fix: Explicitly cast to float
    return gas_constant


def get_a(gas: ct.Solution) -> float:
    """
    Calculate a local speed of sound for a input gas:
    args:
        gas: cantera.Solution object which represents gas or mixture of gases
    return:
        a: local speed of sound [m/s]
    """
    a = np.sqrt(get_gas_constant(gas) * get_gamma(gas) * gas.T)
    return float(a)


def mach_solver(
    mass_flow: float,
    area: float,
    gas_in: ct.Solution,
    eta: float,
    mach_in: float,
    gas_out: ct.Solution,
    max_iterations: int = 100,
    tol: float = 0.01,
) -> tuple[float, bool]:
    """
    Calculate gas velocity at the end of engine part

    args:
        mass_flow: mass flow of gas in engine part [kg/s]
        area: Cross-sectional area [m^2]
        gas_in: Gas at entrance of engine part
        eta: engine part thermodynamic efficiency
        mach_in: Mach number at the entrance of engine part
        gas_out: Gas at exit of engine part
        max_iterations: maximum iterations of algorithm
        tol: tolerance of calculation of gas velocity at the end
    Return:
        mach_out: Mach number for gas at the end of inlet
        convergence: True if calculations are converged
    """
    n_iter = 0
    converged = False
    mach_out = 0.0

    # calculated input gas properties
    velocity_in = mach_in * get_a(gas_in)
    gamma_in = get_gamma(gas_in)
    temperature_total_in = get_temperature_total(gas_in.T, gamma_in, mach_in)

    # initial assumptions
    temperature_total_out = temperature_total_in
    velocity_out_guess = mass_flow / (gas_in.density * area)
    gamma_out = gamma_in

    while not converged and n_iter <= max_iterations:
        # calc properties using current guess

        temperature_static_out = gas_in.T + (
            velocity_in**2 / (2 * gas_in.cp) - velocity_out_guess**2 / (2 * gas_out.cp)
        )
        p_total_out = gas_in.P * (
            1 + eta * velocity_in**2 / (2 * gas_in.cp * gas_in.T)
        ) ** (gamma_in / (gamma_in - 1))
        p_static_out = p_total_out * (
            temperature_total_out / temperature_static_out
        ) ** (gamma_out / (gamma_out - 1))

        # update gas to get new properties (especially density)
        gas_out.TP = temperature_static_out, p_static_out
        gamma_out = get_gamma(gas_out)

        # update velocity calculation with new gas properties
        velocity_out = velocity_out_guess
        velocity_out_guess = mass_flow / (gas_out.density * area)

        # Check convergence
        if abs(velocity_out - velocity_out_guess) < tol:
            print(f"Mach calculations finished in {n_iter} iterations")
            converged = True
            mach_out = velocity_out / get_a(gas_out)
        elif n_iter < max_iterations:
            n_iter += 1
        else:
            mach_out = 0
            print("Inlet calculations failed")

    return mach_out, converged


def _process_compressor_stages(
    gas_in: ct.Solution,
    n_stages: int,
    compress_stage: float,
    comp_eta: float,
    mach_in: float,
    stage_multiplier: np.ndarray,
    temperature_total_in: float,
    p_total_in: float,
) -> tuple[float, float, float, np.ndarray, np.ndarray, float]:
    """
    Process all compressor stages and return the results.

    Args:
        gas_in: Gas at entrance of compressor
        n_stages: Number of stages
        compress_stage: Compression ratio per stage
        comp_eta: Compressor efficiency
        mach_in: Mach number at inlet
        stage_multiplier: Multipliers for each stage
        temperature_total_in: Total temperature at inlet
        p_total_in: Total pressure at inlet

    Returns:
        temperature_static: Final static temperature
        p_static: Final static pressure
        compressor_work: Work consumed by compressor
        stages_temperature_out: Temperatures at each stage
        stages_p_out: Pressures at each stage
        max_delta_t: Maximum temperature delta between stages
    """
    # stage properties
    stages_p_out = np.zeros(n_stages)
    stages_temperature_out = np.zeros(n_stages)
    stage_gas = ct.Solution(
        gas_management.reaction_mechanism, gas_management.phase_name
    )
    stage_gas.X = gas_management.comp_air
    stage_gas.TP = gas_in.T, gas_in.P

    # compressor output data
    compressor_work = 0.0

    # Stage calculation
    p_total_stage = p_total_in
    temperature_total_stage = temperature_total_in

    for st_counter in range(n_stages):
        temperature_i = stage_gas.T
        gamma = get_gamma(stage_gas)
        p_total = (
            get_p_total(stage_gas.P, gamma, mach_in)
            * compress_stage
            * stage_multiplier[st_counter]
        )  # pressure rise per stage
        temperature_total = (
            temperature_total_stage
            / comp_eta
            * ((p_total / p_total_stage) ** ((gamma - 1) / gamma) - 1)
            + temperature_total_stage
        )

        temperature_static = get_temperature_static(temperature_total, gamma, mach_in)
        p_static = get_p_static(p_total, temperature_static, temperature_total, gamma)
        stage_gas.TP = temperature_static, p_static

        # store conditions for plotting later
        stages_p_out[st_counter] = p_static
        stages_temperature_out[st_counter] = temperature_static

        # store stage work
        compressor_work += stage_gas.cp * (
            temperature_static - temperature_i
        )  # in kJ/kg

        # update for next stage
        p_total_stage = p_total
        temperature_total_stage = temperature_total

    # Calculate temperature differences between stages
    if n_stages > MIN_COMPRESSOR_NUM_OF_STAGES:  # typical multi-stage case
        max_delta_t = float(np.diff(stages_temperature_out).max())
    elif n_stages > 1:  # special case : np.diff will drop one in vector length
        max_delta_t = max(
            stages_temperature_out[1] - stages_temperature_out[0],
            stages_temperature_out[0] - gas_in.T,
        )
    else:  # case for 1 stage
        max_delta_t = temperature_static - gas_in.T

    return (
        temperature_static,
        p_static,
        compressor_work,
        stages_temperature_out,
        stages_p_out,
        max_delta_t,
    )


def compressor_solver(
    gas_in: ct.Solution,
    n_stages: int,
    compress: float,
    comp_eta: float,
    mach_in: float,
    gas_out: ct.Solution,
    max_iterations: int = 5000,
) -> tuple[list[tuple[float, float]], bool, float]:
    """
    Calculate output parameters of compressor

    args:
        gas_in: Gas at entrance of compressor
        n_stages: Number of stages of compressor
        compress: Overall compression ratio
        comp_eta: Compressor's thermodynamic efficiency
        mach_in: Mach number at the entrance of compressor
        gas_out: Gas at exit of engine part
        max_iterations: maximum iterations of algorithm

    Return:
        temperature_out, p_out : list with static temperatures, static pressures of each stage
        convergence  : True if converged, False if not
        compressor_work : specific work used to compress gas [in kJ/kg]
    """
    # Input gas properties
    gamma_in = get_gamma(gas_in)
    temperature_total_in = get_temperature_total(gas_in.T, gamma_in, mach_in)
    p_total_in = get_p_total(gas_in.P, gamma_in, mach_in)

    # Pressure ratio per stage
    compress_stage = compress ** (1 / n_stages)
    n_stages_int = int(n_stages)

    # gradually shift pressure towards the initial stages
    stage_multiplier = np.ones(n_stages_int)
    shift = 0.001  # overall shift amount, per iteration
    shifter = np.ones(n_stages_int)
    step_shift = shift / n_stages_int  # shift step per stage

    center = int(n_stages_int / 2)
    for i in range(center):
        shifter[i] = 1 + (center - i) * step_shift  # shift initial stages UP
        shifter[n_stages_int - i - 1] = 1 - (
            (center - i) * step_shift
        )  # shift later stages DOWN

    # pressure rise shift loop control
    converged = False
    n_iter = 0
    prev_delta_t = 1000.0  # start with high value to trigger condition
    temperature_static = 0.0
    p_static = 0.0
    compressor_work = 0.0
    stages_temperature_out = np.zeros(n_stages_int)
    stages_p_out = np.zeros(n_stages_int)

    while not converged and n_iter <= max_iterations:
        # Process all stages in the helper function
        (
            temperature_static,
            p_static,
            compressor_work,
            stages_temperature_out,
            stages_p_out,
            max_delta_t,
        ) = _process_compressor_stages(
            gas_in,
            n_stages_int,
            compress_stage,
            comp_eta,
            mach_in,
            stage_multiplier,
            temperature_total_in,
            p_total_in,
        )

        # loop objective is to get minimum temperature difference between all stages
        # by shifting pressure rise towards initial stages
        if max_delta_t < prev_delta_t and n_iter < max_iterations:
            n_iter += 1
            # increase pressure shift towards initial stages
            # Fix: Use explicit array assignment to maintain proper typing
            multiplied_result = np.multiply(stage_multiplier, shifter)
            stage_multiplier[:] = multiplied_result
            prev_delta_t = max_delta_t

        elif n_iter >= max_iterations:
            print(
                f"compressor finished, NOT converged, niter={n_iter}, max delta T={max_delta_t:0.1f}"
            )
            n_iter += 1
        else:
            converged = True
            print(
                f"compressor finished, converged, niter={n_iter}, max delta T={max_delta_t:0.1f}, pressure p = {p_static}"
            )

    # update gas_out to pass properties back
    gas_out.TP = temperature_static, p_static

    return (
        list(zip(stages_temperature_out, stages_p_out, strict=False)),
        converged,
        compressor_work,
    )


def combustor_solver(
    gas_in: ct.Solution,
    velocity_nominal: float,
    mach_in: float,
    pressure_lost: float,
    gas_out: ct.Solution,
) -> tuple[float, bool]:
    """
    Calculate output parameters of combustor

    args:
        gas_in: Gas at entrance of combustor
        velocity_nominal: Nominal velocity of gas at combustor
        mach_in: Mach number at the entrance of compressor
        pressure_lost: Relative total pressure loss,
        gas_out: Gas at exit of engine part

    Return:
        mach_out: Mach number for gas at exit of combustor
        convergence: Convergence bool
        gas_out: Cantera solution with updated gas parameters

    """

    tol = 0.01
    max_iter = 100
    converged = False
    n_iter = 0

    gamma_in = get_gamma(gas_in)
    temperature_total_in = get_temperature_total(gas_in.T, gamma_in, mach_in)
    p_total_in = get_p_total(gas_in.P, gamma_in, mach_in)

    temperature_total_out = temperature_total_in
    p_total_out = p_total_in * (1 - pressure_lost)
    temperature_out = gas_in.T
    p_out = gas_in.P

    while not converged and n_iter <= max_iter:
        gas_out.TP = temperature_out, p_out
        a_out = get_a(gas_out)
        mach_out = velocity_nominal / a_out
        gamma_out = get_gamma(gas_out)
        temperature_out = get_temperature_static(
            temperature_total_out, gamma_out, mach_out
        )
        p_out = get_p_static(
            p_total_out, temperature_out, temperature_total_out, gamma_out
        )

        if abs(gas_out.P - p_out) < tol:
            print(f"Combustor finished, converged, niter = {n_iter}")
            converged = True
        elif n_iter < max_iter:
            n_iter += 1
        else:
            mach_out = 0
            print(f"Combustor finished, NOT converged, niter = {n_iter}")

    return mach_out, converged


def turbine_solver(
    gas_in: ct.Solution,
    compressor_work: float,
    turbine_n_stages: int,
    turbine_eta: float,
    turbine_loss: float,
    mach_in: float,
    mach_out: float,
    gas_out: ct.Solution,
) -> None:
    """Calculate output parameters of turbine

    args:
        gas_in: Gas at entrance of turbine
        compressor_work: Work from compressor that turbine needs to provide
        turbine_n_stages: Number of turbine stages
        turbine_eta: Turbine efficiency
        turbine_loss: Turbine loss factor
        mach_in: Mach number at turbine entrance
        mach_out: Mach number at turbine exit
        gas_out: Gas at exit of turbine
    """
    gamma_in = get_gamma(gas_in)
    temperature_total_in = get_temperature_total(gas_in.T, gamma_in, mach_in)
    p_total_in = get_p_total(gas_in.P, gamma_in, mach_in)

    temperature_static_in = get_temperature_static(
        temperature_total_in, gamma_in, mach_out
    )
    p_static_in = get_p_static(
        p_total_in, temperature_static_in, temperature_total_in, gamma_in
    )

    work_per_stage = (compressor_work / turbine_loss) / turbine_n_stages

    stages_p_out = np.zeros(turbine_n_stages)
    stages_temperature_out = np.zeros(turbine_n_stages)
    stage_gas = ct.Solution(
        gas_management.reaction_mechanism, gas_management.phase_name
    )
    stage_gas.TPX = temperature_static_in, p_static_in, gas_in.X

    turbine_work = 0.0

    for st_counter in range(turbine_n_stages):
        gamma = get_gamma(stage_gas)
        temperature_static_in = stage_gas.T
        temperature_total_prime = temperature_total_in - work_per_stage / (
            stage_gas.cp * turbine_eta
        )
        p_total_out = p_total_in * (temperature_total_prime / temperature_total_in) ** (
            gamma / (gamma - 1)
        )
        temperature_total_out = temperature_total_in - turbine_eta * (
            temperature_total_in - temperature_total_prime
        )

        temperature_out = get_temperature_static(temperature_total_out, gamma, mach_out)
        p_out = get_p_static(p_total_out, temperature_out, temperature_total_out, gamma)
        stage_gas.TP = temperature_out, p_out

        gamma = get_gamma(stage_gas)
        temperature_out = get_temperature_static(temperature_total_out, gamma, mach_out)
        p_out = get_p_static(p_total_out, temperature_out, temperature_total_out, gamma)
        stage_gas.TP = temperature_out, p_out

        stages_p_out[st_counter] = p_out
        stages_temperature_out[st_counter] = temperature_out

        turbine_work += stage_gas.cp * (
            temperature_out - temperature_static_in
        )  # in kJ/kg

        p_total_in = p_total_out
        temperature_total_in = temperature_total_out

    gas_out.TP = temperature_out, p_out
