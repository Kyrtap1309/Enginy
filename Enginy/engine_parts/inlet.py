import json
from plotly import utils

from ..isa import isa
from . import engine_thermo
from . import gas_management


class Inlet:
    def __init__(self, inlet_data):
        """
        Constructor of inlet of aircraft jet engine
    
        """
        self.inlet_data = inlet_data

        self.T_ambient = isa.ISA_T(self.inlet_data["altitude"])
        self.p_ambient = isa.ISA_p(self.inlet_data["altitude"])
        self.M_ambient = self.inlet_data["M_ambient_input"]
        self.mass_flow = self.inlet_data["mass_flow"]
        self.A_1 = self.inlet_data["A1"]
        self.A_2 = self.inlet_data["A2"]
        self.inlet_eta = self.inlet_data["eta"]
        self.gas = gas_management.initialize_gas(self.T_ambient, self.p_ambient)

        _ambient_stage_index = gas_management.st[0]
        self.ambient_stage_gas = self.gas[_ambient_stage_index]

        self.v_input = self.M_ambient * engine_thermo.get_a(self.ambient_stage_gas)
        self.gamma = engine_thermo.get_gamma(self.ambient_stage_gas)
        self.T_total_inlet_in = engine_thermo.get_T_total(
            self.ambient_stage_gas.T, self.gamma, self.M_ambient
        )
        self.p_total_inlet_in = engine_thermo.get_p_total(
            self.ambient_stage_gas.P, self.gamma, self.M_ambient
        )

        _inlet_in_stage_index = gas_management.st[1]
        self.inlet_in_stage_gas = self.gas[_inlet_in_stage_index]

        _inlet_out_stage_index = gas_management.st[2]
        self.inlet_out_stage_gas = self.gas[_inlet_out_stage_index]

        self.mach_inlet_from_ambient_to_entrance()
        self.mach_inlet_from_entrance_to_output()

    def mach_inlet_from_ambient_to_entrance(self):
        M_calc, convergence = engine_thermo.mach_solver(
            self.mass_flow,
            self.A_1,
            self.ambient_stage_gas,
            self.inlet_eta,
            self.M_ambient,
            self.inlet_in_stage_gas,
        )

        if convergence:
            self.M_inlet_in = M_calc

    def mach_inlet_from_entrance_to_output(self):
        M_calc, convergence = engine_thermo.mach_solver(
            self.mass_flow,
            self.A_2,
            self.inlet_in_stage_gas,
            self.inlet_eta,
            self.M_inlet_in,
            self.inlet_out_stage_gas,
        )

        if convergence:
            self.M_inlet_out = M_calc

    def analyze(self):
        inlet_T = []
        inlet_p = []
        inlet_X = []

        for x in range(0, 3):
            inlet_T.append(self.gas[gas_management.st[x]].T)
            inlet_p.append(self.gas[gas_management.st[x]].P)
            inlet_X.append(self.gas[gas_management.st[x]].X)

        plot = gas_management.plot_T_s(
            inlet_T,
            inlet_p,
            inlet_X,
            gas_management.reaction_mechanism,
            gas_management.phase_name,
        )

        graphJSON = json.dumps(plot, cls = utils.PlotlyJSONEncoder)
        return graphJSON
