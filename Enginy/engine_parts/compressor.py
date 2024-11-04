from .engine_part import EnginePart

class Compressor(EnginePart):
    def __init__(self, inlet_data) -> None:
        self.inlet_data = inlet_data

        self.stage_number = self.inlet_data["comp_n_stages"]
        self.compress = self.inlet_data["compress"]
        self.comp_eta = self.inlet_data["comp_eta"]
         