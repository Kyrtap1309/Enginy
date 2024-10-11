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
