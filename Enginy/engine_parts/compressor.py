import json
from typing import Union, Any, List
from plotly import utils
from dataclasses import dataclass

from Enginy.engine_parts.engine_part import EnginePart
from Enginy.engine_parts import gas_management, engine_thermo
from Enginy.engine_parts.inlet import Inlet

from Enginy.isa import isa

@dataclass
class CompressorData:
    """
    Data class for storing compressor parameters.

    Attributes:
        comp_n_stages (int): Number of compressor stages.
        compress (float): Compression ratio.
        comp_eta (float): Compressor efficiency.
    """

    comp_n_stages: int
    compress: float
    comp_eta: float

class Compressor(EnginePart):
    """
    Represents a compressor component of an aircraft jet engine.
    """
    def __init__(self, compressor_data: Union[dict, CompressorData], inlet: Inlet, **kwargs) -> None:
        """
        Initialize the Compressor object with provided compressor data and inlet dependency.

        Args:
            compressor_data (Union[dict, CompressorData]): Dictionary or CompressorData instance containing:
                - comp_n_stages: Number of compressor stages.
                - compress: Compression ratio.
                - comp_eta: Compressor efficiency.
            inlet (Inlet): An instance of Inlet from which compressor takes gas properties and Mach number.
            kwargs: Additional keyword arguments.
        """
        self.inlet: Inlet = inlet
        
        if isinstance(compressor_data, dict):
            self.compressor_data = CompressorData(**compressor_data)
        else:
            self.compressor_data = compressor_data

        self.stage_number: int = self.compressor_data.comp_n_stages
        self.compress: float = self.compressor_data.compress
        self.comp_eta: float = self.compressor_data.comp_eta
        
        self.gas: List[Any] = inlet.gas
        self.M_comp_in: float = inlet.M_inlet_out

        self.st_out, convergence, self.compressor_work = engine_thermo.compressor_solver(
            gas_in=self.gas[2],
            n_stages=self.stage_number,
            compress=self.compress,
            comp_eta=self.comp_eta,
            M_in=self.M_comp_in,
            gas_out=self.gas[3])
        
    def analyze(self) -> str:
        """
        Analyze the compressor parameters and produce a JSON encoded plot.

        Iterates over selected gas stages to collect temperature, pressure, and composition data.
        Generates a plot using the gas management module.

        Returns:
            str: JSON-encoded plot of the compressor analysis.
        """
        compressor_T: List[float] = []
        compressor_p: List[float] = []
        compressor_X: List[Any] = []

        for x in range(0, 4):
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

                                                                                         

        