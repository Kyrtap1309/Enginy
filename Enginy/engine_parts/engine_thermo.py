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
