import cantera as ct

gas = {}

st = ["a", 1, 2, 3, 4, 5, 6]
station_names = {st[0]:'ambient',
                 st[1]:'inlet',
                 st[2]:'inlet end (comp. face)',
                 st[3]:'after compressor',
                 st[4]:'after combustor',
                 st[5]:'after turbine',
                 st[6]:'nozzle exit'}

reaction_mechanism = "nDodecane_Reitz.yaml"
phase_name = "nDodecane_IG"

comp_air = "02:0.209, N2:0.787, CO2:004"
comp_fuel = "c12h26:1"

def initialize_gas(T_amp, p_amb):
    for station in st:
        gas[station] = (ct.Solution(reaction_mechanism, phase_name))
        gas[station].X = comp_air
        gas[station].TP = T_amp, p_amb
