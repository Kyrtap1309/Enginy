import json


from ..isa import isa 
from ..engine_parts import engine_thermo
from ..engine_parts import gas_management

class Inlet:
    def __init__(self, inlet_json):
        """
        Constructor of inlet of aircraft jet engine
        Args:
            inlet_json (json): Json file with all engine params
        """
        with open(inlet_json, 'r') as file:
            self.inlet_data = json.load(file)
    
    def mach_inlet(self) -> tuple[float, bool]:
        """
        Calculate gas velocity at the end of inlet

        Return:
            M_out: Mach number for gas at the end of inlet
            convergence: True if calculations are converged
        """
        #Calculations params
        max_iterations = 100 #Maximum number of iterations
        tol = 0.01 #Toleration for convergence
        n_iter = 0 #iteration counter

        T_input = isa.ISA_T(self.inlet_data["altitude"])
        p_input = isa.ISA_p(self.inlet_data["altitude"])
        M_input = self.inlet_data["M_inlet_input"]
        gas = gas_management.initialize_gas(T_input, p_input)
        