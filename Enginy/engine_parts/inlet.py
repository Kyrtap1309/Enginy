import json


from ..isa import isa 
from . import engine_thermo
from . import gas_management

class Inlet:
    def __init__(self, inlet_json):
        """
        Constructor of inlet of aircraft jet engine
        Args:
            inlet_json (json): Json file with all engine params
        """
        with open(inlet_json, 'r') as file:
            self.inlet_data = json.load(file)
        
        self.T_ambient = isa.ISA_T(self.inlet_data["altitude"])
        self.p_ambient = isa.ISA_p(self.inlet_data["altitude"])
        self.M_ambient = self.inlet_data["M_inlet_input"]
        self.mass_flow = self.inlet_data["mass_flow"]
        self.A_1 = self.inlet_data["A1"]
        self.A_2 = self.inlet_data["A2"]
        self.inlet_eta = self.inlet_data["eta"]
        self.gas = gas_management.initialize_gas(self.T_ambient, self.p_ambient)
        
        _ambient_stage_index = gas_management.st[0]
        self.ambient_stage_gas = self.gas[_ambient_stage_index]
        
        self.v_input = self.M_input * engine_thermo.get_a(self.ambient_stage_gas)
        self.gamma = engine_thermo.get_gamma(self.ambient_stage_gas)
        self.T_total_inlet_in = engine_thermo.get_T_total(self.ambient_stage_gas.T, self.gamma, self.M_ambient)
        self.p_total_inlet_in = engine_thermo.get_p_total(self.ambient_stage_gas.P, self.gamma, self.M_ambient)

        _inlet_in_stage_index = gas_management.st[1]
        self.inlet_in_stage_gas = self.gas[_inlet_in_stage_index]

        _inlet_out_stage_index = gas_management.st[2]
        self.inlet_out_stage_gas = self.gas[_inlet_out_stage_index]
    
    def mach_inlet_from_ambient_to_entrance(self):
        M_calc, convergence = engine_thermo.mach_solver(self.mass_flow, self.A_1, self.ambient_stage_gas, self.inlet_eta, self.M_ambient, self.inlet_in_stage_gas)

        if convergence:
            self.M_inlet_in = M_calc
    
    def mach_inlet_from_entrance_to_output(self):
        M_calc, convergence = engine_thermo.mach_solver(self.mass_flow, self.A_2, self.inlet_in_stage_gas, self.inlet_eta, self.M_inlet_in, self.inlet_out_stage_gas)

        if convergence:
            self.M_inlet_out = M_calc
            
    def plot_T_s(self):
        pass