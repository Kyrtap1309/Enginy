import json
from dataclasses import dataclass
from typing import Any

from plotly import utils

from enginy.engine_parts import engine_thermo, gas_management
from enginy.engine_parts.engine_part import EnginePart
from enginy.isa import isa


@dataclass
class InletData:
    altitude: float
    M_ambient_input: float
    mass_flow: float
    A1: float
    A2: float
    eta: float


class Inlet(EnginePart):
    """
    Represents an inlet component of an aircraft jet engine.
    """

    def __init__(
        self, inlet_data: dict | InletData, **kwargs: dict[str, float]
    ) -> None:
        """
        Initialize the Inlet object with provided inlet data.

        Args:
            inlet_data (Union[dict, InletData]): Dictionary or InletData instance containing:
                - altitude: Altitude in meters.
                - M_ambient_input: Ambient Mach number.
                - mass_flow: Mass flow rate.
                - A1: Inlet cross-sectional area.
                - A2: Outlet cross-sectional area.
                - eta: Inlet efficiency.
            kwargs: Additional keyword arguments.
        """

        if isinstance(inlet_data, dict):
            self.inlet_data = InletData(**inlet_data)
        else:
            self.inlet_data = inlet_data

        self.temperature_ambient: float = isa.isa_temperature(self.inlet_data.altitude)
        self.p_ambient: float = isa.isa_p(self.inlet_data.altitude)
        self.M_ambient: float = self.inlet_data.M_ambient_input
        self.mass_flow: float = self.inlet_data.mass_flow
        self.A_1: float = self.inlet_data.A1
        self.A_2: float = self.inlet_data.A2
        self.inlet_eta: float = self.inlet_data.eta
        self.gas: dict[str | int, Any] = gas_management.initialize_gas(
            self.temperature_ambient, self.p_ambient
        )

        _ambient_stage_index: str | int = gas_management.st[0]
        self.ambient_stage_gas = self.gas[_ambient_stage_index]

        self.v_input: float = self.M_ambient * engine_thermo.get_a(
            self.ambient_stage_gas
        )
        self.gamma: float = engine_thermo.get_gamma(self.ambient_stage_gas)
        self.T_total_inlet_in: float = engine_thermo.get_temperature_total(
            self.ambient_stage_gas.T, self.gamma, self.M_ambient
        )
        self.p_total_inlet_in = engine_thermo.get_p_total(
            self.ambient_stage_gas.P, self.gamma, self.M_ambient
        )

        _inlet_in_stage_index: str | int = gas_management.st[1]
        self.inlet_in_stage_gas = self.gas[_inlet_in_stage_index]

        _inlet_out_stage_index: str | int = gas_management.st[2]
        self.inlet_out_stage_gas = self.gas[_inlet_out_stage_index]

        self.mach_inlet_from_ambient_to_entrance()
        self.mach_inlet_from_entrance_to_output()

    def mach_inlet_from_ambient_to_entrance(self) -> None:
        """
        Compute the Mach number from ambient conditions to inlet entrance.

        Uses the mach solver to compute the Mach number and assigns it to M_inlet_in if convergence is achieved.
        """
        mach_calc, convergence = engine_thermo.mach_solver(
            self.mass_flow,
            self.A_1,
            self.ambient_stage_gas,
            self.inlet_eta,
            self.M_ambient,
            self.inlet_in_stage_gas,
        )

        if convergence:
            self.M_inlet_in = mach_calc

    def mach_inlet_from_entrance_to_output(self) -> None:
        """
        Compute the Mach number from inlet entrance to outlet.

        Uses the mach solver to compute the Mach number and assigns it to M_inlet_out if convergence is achieved.
        """
        mach_calc, convergence = engine_thermo.mach_solver(
            self.mass_flow,
            self.A_2,
            self.inlet_in_stage_gas,
            self.inlet_eta,
            self.M_inlet_in,
            self.inlet_out_stage_gas,
        )

        if convergence:
            self.M_inlet_out = mach_calc

    def analyze(self) -> str:
        """
        Analyze the inlet parameters and produce a JSON encoded plot.

        Iterates over selected gas stages to collect temperature, pressure, and composition data.
        Generates a plot using the gas management module.

        Returns:
            str: JSON-encoded plot of the inlet analysis.
        """
        inlet_t = []
        inlet_p = []
        inlet_x = []

        for x in range(0, 3):
            inlet_t.append(self.gas[gas_management.st[x]].T)
            inlet_p.append(self.gas[gas_management.st[x]].P)
            inlet_x.append(self.gas[gas_management.st[x]].X)

        plot = gas_management.plot_temperature_enthropy(
            inlet_t,
            inlet_p,
            inlet_x,
            gas_management.reaction_mechanism,
            gas_management.phase_name,
        )

        graphjson = json.dumps(plot, cls=utils.PlotlyJSONEncoder)
        return graphjson
