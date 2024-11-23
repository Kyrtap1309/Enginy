import json
from plotly import utils

from .engine_part import EnginePart
from . import gas_management, engine_thermo
from .inlet import Inlet

from ..isa import isa

class Compressor(EnginePart):
    def __init__(self, compressor_data, inlet: Inlet) -> None:
        
        self.inlet = inlet
        
        self.compressor_data = compressor_data

        self.stage_number = self.compressor_data["comp_n_stages"]
        self.compress = self.compressor_data["compress"]
        self.comp_eta = self.compressor_data["comp_eta"]
        
        self.gas = inlet.gas
        self.M_comp_in = inlet.M_inlet_out

        self.st_out, convergence, self.compressor_work = engine_thermo.compressor_solver(
            gas_in=self.gas["2"],
            n_stages=self.stage_number,
            compress=self.compress,
            comp_eta=self.comp_eta,
            M_in=self.M_comp_in,
            gas_out=self.gas["3"])
        
    def analyze(self):
        compressor_T = []
        compressor_p = []
        compressor_X = []

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

        graphJSON = json.dumps(plot, cls = utils.PlotlyJSONEncoder)
        return graphJSON

                                                                                         

        