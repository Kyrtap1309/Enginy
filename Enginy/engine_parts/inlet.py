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
        
        self.T_ambient = isa.ISA_T(self.inlet_data["altitude"])
        self.p_ambient = isa.ISA_p(self.inlet_data["altitude"])
        self.M_input = self.inlet_data["M_inlet_input"]
        self.mass_flow = self.inlet_data["mass_flow"]
        self.A_1 = self.inlet_data["A1"]
        self.A_2 = self.inlet_data["A2"]
        self.inlet_eta = self.inlet_data["eta"]
        self.gas = gas_management.initialize_gas(self.T_ambient, self.p_ambient)
        
        _inlet_stage_index = gas_management.st[0]
        self.inlet_stage_gas = self.gas[_inlet_stage_index]
        
        self.v_input = self.M_input * engine_thermo.get_a(self.inlet_stage_gas)
        self.gamma = engine_thermo.get_gamma(self.inlet_stage_gas)
        self.T_total_inlet_in = engine_thermo.get_T_total(self.inlet_stage_gas.T, self.gamma, self.M_input)
        self.p_total_inlet_in = engine_thermo.get_p_total(self.inlet_stage_gas.P, self.gamma, self.M_input)
    
    def mach_inlet(self, max_iterations = 100, tol = 0.01) -> tuple[float, bool]:
        """
        Calculate gas velocity at the end of inlet

        args:
            max_iterations: maximum iterations of algorithm
            tol: tolerance of calculation of gas velocity at the end
        Return:
            M_out: Mach number for gas at the end of inlet
            convergence: True if calculations are converged
        """
        n_iter = 0 #iteration counter
        converged = False #Tracking of convergence

        #Initial assumptions of result
        T_total_inlet_out = self.T_total_inlet_in
        p_total_inlet_out = self.p_total_inlet_in
        v_out_assumed = self.mass_flow / (self.inlet_stage_gas.density * self.A_1)
        gamma_out = self.gamma
        inlet_stage_gas_out = self.gas[gas_management.st[1]]

        while not converged and n_iter <= max_iterations:
            
            T_static_inlet_out = self.inlet_stage_gas.T + ((self.v_input)**2 / (2 * self.inlet_stage_gas.cp) - v_out_assumed**2 / (2 * inlet_stage_gas_out.cp))
            p_total_inlet_out = self.inlet_stage_gas.P * (1 + self.inlet_eta * self.v_input**2 / (2 * self.inlet_stage_gas.cp * self.inlet_stage_gas.T))**(self.gamma / (self.gamma - 1))
            p_static_inlet_out = p_total_inlet_out * (T_static_inlet_out / T_total_inlet_out)**(gamma_out / (gamma_out - 1))

            inlet_stage_gas_out.TP = T_static_inlet_out, p_static_inlet_out
            gamma_out = engine_thermo.get_gamma(inlet_stage_gas_out)

            v_out = v_out_assumed
            v_out_assumed = self.mass_flow / (inlet_stage_gas_out.density * self.A_1)

            if abs(v_out - v_out_assumed) < tol:
                print(f"Calculation for output gas velocity in inlet finished correctly with {n_iter} iterations")
                converged = True
                mach_inlet_output = v_out / engine_thermo.get_a(inlet_stage_gas_out)
                self.mach_inlet_output = mach_inlet_output
            elif n_iter < max_iterations:
                n_iter += 1
            else:
                mach_inlet_output = None
                self.mach_inlet_output = mach_inlet_output
                print(f"Calculations for output gas velocity in inlet failed")
        
        return mach_inlet_output, converged
    
        