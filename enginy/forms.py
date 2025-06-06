from abc import ABCMeta, abstractmethod

from flask_wtf import FlaskForm
from wtforms import FloatField, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange


# Combine the ABCMeta with the FlaskForm metaclass to support abstract methods.
class FormMeta(ABCMeta, type(FlaskForm)):  # type: ignore
    pass


class BasePartForm(FlaskForm, metaclass=FormMeta):
    """
    Base form for creating engine parts.

    This abstract class requires a definition of get_dependency_fields method,
    which should return a mapping of dependency field names to the engine part types.
    """

    @classmethod
    @abstractmethod
    def get_dependency_fields(cls) -> dict[str, str]:
        """
        Return a dictionary mapping dependent field names to required part types.

        Example:
            {"inlet_part": "Inlet"}
        """
        pass


class InletForm(BasePartForm):
    """
    Form for creating an Inlet engine part.

    Fields:
        user_part_name: Name of the part.
        altitude: Altitude (meters).
        M_ambient_input: Aircraft's ambient Mach speed.
        mass_flow: Mass flow rate through the inlet.
        A1: Inlet area.
        A2: Outlet area.
        eta: Efficiency of the inlet.
    """

    user_part_name = StringField("Part Name", validators=[DataRequired()])
    altitude = FloatField(
        "Altitude (m)", validators=[DataRequired(), NumberRange(0, 15_000)]
    )
    M_ambient_input = FloatField(
        "Aircraft Mach Speed (Ma)", validators=[DataRequired(), NumberRange(0, 5)]
    )
    mass_flow = FloatField(
        "Inlet mass flow (kg/s)", validators=[DataRequired(), NumberRange(0, 250)]
    )
    A1 = FloatField(
        "Inlet air cross-sectional area (m²)",
        validators=[DataRequired(), NumberRange(0.05, 20)],
    )
    A2 = FloatField(
        "Outlet air cross-sectional area (m²)",
        validators=[DataRequired(), NumberRange(0.05, 20)],
    )
    eta = FloatField(
        "Efficiency of air inlet", validators=[DataRequired(), NumberRange(0, 1)]
    )
    submit = SubmitField("Create Inlet Part")

    @classmethod
    def get_dependency_fields(cls) -> dict[str, str]:
        """
        Inlet form does not have dependency fields.

        Returns:
            An empty dictionary.
        """
        return {}


class CompressorForm(BasePartForm):
    """
    Form for creating a Compressor engine part.

    Fields:
        user_part_name: Name of the part.
        inlet_part: Select field to choose an existing Inlet part.
        comp_n_stages: Number of compressor stages.
        compress: Compression ratio.
        comp_eta: Compressor efficiency.
    """

    user_part_name = StringField("Part Name", validators=[DataRequired()])
    # Change coerce to str since MongoDB uses string IDs
    inlet_part = SelectField(
        "Select Inlet Part", coerce=str, choices=[], validate_choice=False
    )
    comp_n_stages = IntegerField(
        "Number of Stages", validators=[DataRequired(), NumberRange(1, 20)]
    )
    compress = FloatField(
        "Compression Ratio", validators=[DataRequired(), NumberRange(0.5, 40)]
    )
    comp_eta = FloatField(
        "Compressor Efficiency", validators=[DataRequired(), NumberRange(0, 1)]
    )
    submit = SubmitField("Create Compressor Part")

    @classmethod
    def get_dependency_fields(cls) -> dict[str, str]:
        """
        Returns:
            A dictionary indicating that the field 'inlet_part' depends on an 'Inlet' part.
        """
        return {"inlet_part": "Inlet"}


class CombustorForm(BasePartForm):
    """
    Form for creating a Combustor engine part.

    Fields:
        user_part_name: Name of the part.
        compressor_part: Select field to choose an existing Compressor part.
        throttle_position: Throttle position.
        V_nominal: Nominal velocity in the combustor.
        Pressure_lost: Relative pressure loss.
        max_f: Maximum fuel percentage.
        min_f: Minimum fuel percentage.
    """

    user_part_name = StringField("Part Name", validators=[DataRequired()])
    # Change coerce to str since MongoDB uses string IDs
    compressor_part = SelectField(
        "Select Compressor Part", coerce=str, validate_choice=False
    )
    throttle_position = FloatField(
        "Throttle Position", validators=[DataRequired(), NumberRange(0, 1)]
    )
    V_nominal = FloatField(
        "Nominal velocity in combustor(m/s)",
        validators=[DataRequired(), NumberRange(0, 1000)],
    )
    Pressure_lost = FloatField(
        "Relative pressure lost", validators=[DataRequired(), NumberRange(0, 1)]
    )
    max_f = FloatField(
        "Relative maximum fuel", validators=[DataRequired(), NumberRange(0, 1)]
    )
    min_f = FloatField(
        "Relative minimum fuel", validators=[DataRequired(), NumberRange(0, 1)]
    )
    submit = SubmitField("Create Combustor Part")

    @classmethod
    def get_dependency_fields(cls) -> dict[str, str]:
        """
        Returns:
            A dictionary indicating that the field 'compressor_part' depends on a 'Compressor' part.
        """
        return {"compressor_part": "Compressor"}


class TurbineForm(BasePartForm):
    user_part_name = StringField("Part Name", validators=[DataRequired()])

    compressor_part = SelectField(
        "Select Compressor Part", coerce=str, validate_choice=False
    )
    combustor_part = SelectField(
        "Select Combustor Part", coerce=str, validate_choice=False
    )

    turbine_n_stages = IntegerField(
        "Number of Stages", validators=[DataRequired(), NumberRange(1, 10)]
    )
    turbine_eta = FloatField(
        "Turbine Efficiency", validators=[DataRequired(), NumberRange(0, 1)]
    )
    turbine_loss = FloatField(
        "Relative Pressure Loss", validators=[DataRequired(), NumberRange(0.6, 1)]
    )
    submit = SubmitField("Create Turbine Part")

    @classmethod
    def get_dependency_fields(cls) -> dict[str, str]:
        """
        Returns:
            A dictionary indicating that the field 'compressor_part' depends on a 'Compressor' part.
        """
        return {"compressor_part": "Compressor", "combustor_part": "Combustor"}
