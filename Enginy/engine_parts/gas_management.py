import cantera as ct
import plotly.graph_objs as go


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

comp_air = "O2:0.209, N2:0.787, CO2:004"
comp_fuel = "c12h26:1"

def initialize_gas(T_amp, p_amb):
    gas = {}
    for station in st:
        gas[station] = (ct.Solution(reaction_mechanism, phase_name))
        gas[station].X = comp_air
        gas[station].TP = T_amp, p_amb
    return gas

def plot_T_s(T: list, p: list, X: list, reaction_mechanism, phase_name):
    '''
    This function plots T-s states with isobars using Plotly
    
    inputs:
    T    : list with temperatures
    p    : list with pressures
    X    : list with gas composition
    
    returns:
    fig : plotly figure
    '''
    to_st = len(T)
    dummy_gas = ct.Solution(reaction_mechanism, phase_name)

    cycle_T = [0, 0]
    cycle_s = [0, 0]
    
    fig = go.Figure()

    for i in range(to_st):
        dummy_gas.TPX = T[i], p[i], X[i]
        
        # ISOBARS
        curve_P = p[i]
        T_min = int(T[i]) - 100
        T_max = int(T[i]) + 100
    
        s_isobar_data = []
        T_isobar_data = []

        for curve_T in range(T_min, T_max, 1):
            dummy_gas.TP = curve_T, curve_P
            s_isobar_data.append(dummy_gas.s)
            T_isobar_data.append(dummy_gas.T)
        
        # Plotting isobar curves
        fig.add_trace(go.Scatter(x=s_isobar_data, y=T_isobar_data, 
                                 mode='lines', 
                                 line=dict(color='#31edd8', width=1), 
                                 opacity=0.35, name=f'Isobar at {p[i]/1000:.3f} kPa'))
        
        # State points (cycle line)
        dummy_gas.TPX = T[i], p[i], X[i]
        cycle_T[0] = cycle_T[1]
        cycle_s[0] = cycle_s[1]
        cycle_T[1] = dummy_gas.T
        cycle_s[1] = dummy_gas.entropy_mass

        if i != 0:
            fig.add_trace(go.Scatter(x=cycle_s, y=cycle_T, mode='lines+markers', 
                                     line=dict(dash='dash', color='green', width=1),
                                     marker=dict(size=6),
                                     name=f'Station name {station_names[st[i]]}'))

    # Customize the layout of the plot
    fig.update_layout(
        title='T-s Diagram',
        xaxis_title='Entropy (kJ/kg)',
        yaxis_title='Temperature (K)',
        xaxis=dict(autorange=True),
        yaxis=dict(autorange=True),
        template='plotly_dark'
    )
    
    return fig
