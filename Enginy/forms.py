from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, FloatField, IntegerField, SubmitField
from wtforms.validators import DataRequired
from abc import ABCMeta, abstractmethod

# Łączymy metaklasę ABCMeta z metaklasą FlaskForm
class FormMeta(ABCMeta, type(FlaskForm)):
    pass

class BasePartForm(FlaskForm, metaclass=FormMeta):
    @classmethod
    @abstractmethod
    def get_dependency_fields(cls):
        pass

class InletForm(BasePartForm):
    user_part_name = StringField('Part Name', validators=[DataRequired()])
    altitude = FloatField('Altitude (m)', validators=[DataRequired()])
    M_ambient_input = FloatField('Aircraft Mach Speed (Ma)', validators=[DataRequired()])
    mass_flow = FloatField('Inlet mass flow (kg/s)', validators=[DataRequired()])
    A1 = FloatField('Inlet air cross-sectional area (m²)', validators=[DataRequired()])
    A2 = FloatField('Outlet air cross-sectional area (m²)', validators=[DataRequired()])
    eta = FloatField('Efficiency of air inlet', validators=[DataRequired()])
    submit = SubmitField('Create Inlet Part')

    @classmethod
    def get_dependency_fields(cls):
        return {}

class CompressorForm(BasePartForm):
    user_part_name = StringField('Part Name', validators=[DataRequired()])
    inlet_part = SelectField('Select Inlet Part', coerce=int, choices=[], validate_choice=None)
    comp_n_stages = IntegerField('Number of Stages', validators=[DataRequired()])
    compress = FloatField('Compression Ratio', validators=[DataRequired()])
    comp_eta = FloatField('Compressor Efficiency', validators=[DataRequired()])
    submit = SubmitField('Create Compressor Part')

    @classmethod
    def get_dependency_fields(cls):
        return {"inlet_part": "Inlet"}

class CombustorForm(BasePartForm):
    user_part_name = StringField('Part Name', validators=[DataRequired()])
    compressor_part = SelectField('Select Compressor Part', coerce=int, validate_choice=None)
    throttle_position = FloatField('Throttle Position', validators=[DataRequired()])
    V_nominal = FloatField('Nominal velocity in combustor', validators=[DataRequired()])
    Pressure_lost = FloatField('Relative pressure lost', validators=[DataRequired()])
    max_f = FloatField('Maximum fuel (%)', validators=[DataRequired()])
    min_f = FloatField('Minimum fuel (%)', validators=[DataRequired()])
    submit = SubmitField('Create Combustor Part')

    @classmethod
    def get_dependency_fields(cls):
        return {"compressor_part": "Compressor"}