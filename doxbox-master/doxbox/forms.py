"""
forms.py

    Flask form models to be rendered

"""
import flask_wtf
from wtforms import StringField, DateField, IntegerField, TextAreaField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, IPAddress, InputRequired


class DoxForm(flask_wtf.FlaskForm):
    """
    flask form for Dox module
    """
    name = StringField('Full Name', validators=[DataRequired()])
    textarea = TextAreaField('Other Information (will be parsed as YAML)',
    render_kw = {"placeholder": """e.g\n Website: https://google.com"""})


class GeoIPForm(flask_wtf.FlaskForm):
    """
    flask form for GeoIP module
    """
    ip = StringField('IP Address', validators=[IPAddress()])


class DNSForm(flask_wtf.FlaskForm):
    """
    flask form for DNS module
    """
    url = StringField('Domain Name', [InputRequired()], render_kw={"placeholder": "example.com"})
