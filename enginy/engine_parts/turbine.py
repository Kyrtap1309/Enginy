import json
from dataclasses import dataclass
from typing import Any

from plotly import utils

from enginy.engine_parts import engine_thermo, gas_management
from enginy.engine_parts.combustor import Combustor
from enginy.engine_parts.compressor import Compressor
from enginy.engine_parts.engine_part import EnginePart


@dataclass
class TurbineData:
    """
    Data class for storing turbine parameters.

    Attributes:
        turbine_n_stages (int): Number of turbine stages.
        turbine_eta (float): Turbine efficiency.
        turbine_loss (float): Relative pressure loss across the turbine.
    """

    turbine_n_stages: int
    turbine_eta: float
    turbine_loss: float


class Turbine(EnginePart):
    """Represents a turbine component of an aircraft jet engine."""

    def __init__(
        self,
        turbine_data: dict | TurbineData,
        compressor: Compressor,
        combustor: Combustor,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the Turbine object with provided turbine data and compressor dependency.

        Args:
            turbine_data (Union[dict, TurbineData]): Dictionary or TurbineData instance containing:
                - turbine_n_stages: Number of turbine stages.
                - turbine_eta: Turbine efficiency.
                - turbine_loss: Relative pressure loss across the turbine.
            compressor (Compressor): An instance of Compressor providing necessary inlet conditions.
            combustor (Combustor): An instance of Combustor providing necessary inlet conditions.
            kwargs: Additional keyword arguments.
        """
        self.compressor: Compressor = compressor
        self.combustor: Combustor = combustor

        if isinstance(turbine_data, dict):
            self.turbine_data = TurbineData(**turbine_data)
        else:
            self.turbine_data = turbine_data

        self.stage_number: int = self.turbine_data.turbine_n_stages
        self.turbine_eta: float = self.turbine_data.turbine_eta
        self.turbine_loss: float = self.turbine_data.turbine_loss

        self.gas: dict[str | int, Any] = combustor.gas

        engine_thermo.turbine_solver(
            gas_in=self.gas[4],
            compressor_work=self.compressor.compressor_work,
            turbine_n_stages=self.stage_number,
            turbine_eta=self.turbine_eta,
            turbine_loss=self.turbine_loss,
            mach_in=self.combustor.M_comb_out,
            mach_out=self.combustor.M_comb_out,
            gas_out=self.gas[5],
        )

    def analyze(self) -> str:
        """
        Analyze the turbine parameters and produce a JSON-encoded plot.

        Iterates over selected gas stages to collect temperature, pressure, and composition data.
        Generates a plot using the gas management module.

        Returns:
            str: JSON-encoded plot of the turbine analysis.
        """
        compressor_t: list[float] = []
        compressor_p: list[float] = []
        compressor_x: list[Any] = []

        for x in range(0, 6):
            compressor_t.append(self.gas[gas_management.st[x]].T)
            compressor_p.append(self.gas[gas_management.st[x]].P)
            compressor_x.append(self.gas[gas_management.st[x]].X)

        plot = gas_management.plot_temperature_enthropy(
            compressor_t,
            compressor_p,
            compressor_x,
            gas_management.reaction_mechanism,
            gas_management.phase_name,
        )

        graphjson: str = json.dumps(plot, cls=utils.PlotlyJSONEncoder)
        return graphjson
