import json
from dataclasses import dataclass
from typing import Union, List, Any
from plotly import utils

from . import engine_thermo
from . import gas_management
from .engine_part import EnginePart
from .compressor import Compressor

@dataclass
class CombustorData:
    """
    Data class for storing combustor parameters.

    Attributes:
        throttle_position (float): Throttle position.
        V_nominal (float): Nominal velocity in the combustor.
        Pressure_lost (float): Relative pressure loss.
        max_f (float): Maximum fuel percentage.
        min_f (float): Minimum fuel percentage.
    """
    throttle_position: float
    V_nominal: float
    Pressure_lost: float
    max_f: float
    min_f: float

class Combustor(EnginePart):
    """
    Represents a combustor component of an aircraft jet engine.
    """
    def __init__(self, combustor_data: Union[dict, CombustorData], compressor: Compressor, **kwargs):
        """
        Initialize the Combustor object with provided combustor data and compressor dependency.

        Args:
            combustor_data (Union[dict, CombustorData]): Dictionary or CombustorData instance containing:
                - throttle_position: Throttle position.
                - V_nominal: Nominal velocity in the combustor.
                - Pressure_lost: Relative pressure loss.
                - max_f: Maximum fuel percentage.
                - min_f: Minimum fuel percentage.
            compressor (Compressor): An instance of Compressor providing necessary inlet conditions.
            kwargs: Additional keyword arguments.
        """
        self.compressor: Compressor = compressor 

        if isinstance(combustor_data, dict):
            self.combustor_data = CombustorData(**combustor_data)
        else:
            self.combustor_data = combustor_data

        self.throttle_position: float = self.combustor_data.throttle_position
        self.M_comb_in: float = self.compressor.M_comp_in
        self.V_nominal: float = self.combustor_data.V_nominal
        self.pressure_lost: float = self.combustor_data.Pressure_lost

        self.gas: List[Any] = compressor.gas

        self.max_fuel: float = self.combustor_data.max_f
        self.min_fuel: float = self.combustor_data.min_f

        self._gas_update()

        
    def _gas_update(self):
        """
        Update the gas properties based on the combustor parameters.

        Computes the equivalence ratio, updates the gas composition, and performs combustor calculations
        using the combustor solver. Equilibrates the output gas station after computation.
        """

        phi: float = (self.max_fuel - self.min_fuel) * self.throttle_position + self.min_fuel # 
        
        self.gas[4].set_equivalence_ratio(phi=phi, fuel=gas_management.comp_fuel, oxidizer=gas_management.comp_air, basis='mole')
        
        mixt_frac: float = self.gas[4].mixture_fraction(fuel=gas_management.comp_fuel, oxidizer=gas_management.comp_air, basis='mass')


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

    def analyze(self) -> str:
        """
        Analyze the combustor parameters and produce a JSON-encoded plot.

        Iterates over selected gas stages to collect temperature, pressure, and composition data.
        Generates a plot using the gas management module.

        Returns:
            str: JSON-encoded plot of the combustor analysis.
        """
        compressor_T: List[float] = []
        compressor_p: List[float] = []
        compressor_X: List[Any] = []

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

        graphJSON: str = json.dumps(plot, cls = utils.PlotlyJSONEncoder)
        return graphJSON
        
    
    