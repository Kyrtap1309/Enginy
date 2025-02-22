import json
from dataclasses import dataclass
from typing import Union
from plotly import utils

from . import engine_thermo
from . import gas_management
from .engine_part import EnginePart
from .compressor import Compressor

@dataclass
class CombustorData:
    throttle_position: float
    V_nominal: float
    Pressure_lost: float
    max_f: float
    min_f: float

class Combustor(EnginePart):
    """
    Combustor of Jet Engine
    """
    def __init__(self, combustor_data: Union[dict, CombustorData], compressor: Compressor, **kwargs):
        
        self.compressor = compressor 

        if isinstance(combustor_data, dict):
            self.combustor_data = CombustorData(**combustor_data)
        else:
            self.combustor_data = combustor_data

        self.throttle_position = self.combustor_data.throttle_position
        self.M_comb_in = self.compressor.M_comp_in
        self.V_nominal = self.combustor_data.V_nominal
        self.pressure_lost = self.combustor_data.Pressure_lost

        self.gas = compressor.gas

        self.max_fuel = self.combustor_data.max_f
        self.min_fuel = self.combustor_data.min_f

        self._gas_update()

        
    def _gas_update(self):
        phi = (self.max_fuel - self.min_fuel) * self.throttle_position + self.min_fuel # 
        self.gas[4].set_equivalence_ratio(phi=phi, fuel=gas_management.comp_fuel, oxidizer=gas_management.comp_air, basis='mole')
        mixt_frac = self.gas[4].mixture_fraction(fuel=gas_management.comp_fuel, oxidizer=gas_management.comp_air, basis='mass')


        M_calc, conv = engine_thermo.combustor_solver(gas_in=self.gas[3],
                                       V_nominal=self.V_nominal,
                                       M_in=self.M_comb_in,
                                       pressure_lost=self.pressure_lost,
                                       gas_out=self.gas[4]
                                       )
        if conv:
            self.M_comb_out = M_calc
        else:
            print("Combustor calculation did not converge")
        
        self.gas[4].equilibrate('HP')

    def analyze(self):
        compressor_T = []
        compressor_p = []
        compressor_X = []

        for x in range(0, 5):
            compressor_T.append(self.gas[gas_management.st[x]].T)
            compressor_p.append(self.gas[gas_management.st[x]].P)
            compressor_X.append(self.gas[gas_management.st[x]].X)

        plot = gas_management.plot_T_s(
            compressor_T,
            compressor_p,
            compressor_X,
            gas_management.reaction_mechanism,
            gas_management.phase_name,
        )

        graphJSON = json.dumps(plot, cls = utils.PlotlyJSONEncoder)
        return graphJSON
        
    
    