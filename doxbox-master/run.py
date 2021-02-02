#!/usr/bin/python
"""
main.py

    Flask routers and handlers for doxbox instance

"""
import os
import sys
import time
import socket
import signal
import getpass
import csv
import yaml
import ast
import json

import whois
import pygeoip
import crtsh

import flask
import flask_bootstrap
import flask_googlemaps
import flask_nav
import flask_sqlalchemy

from flask_nav.elements import Navbar, View
from sqlalchemy import Column, Integer, String, Text

from doxbox import config, forms

# initialize flask and config manager
app = flask.Flask(__name__, template_folder="doxbox/templates")
app.secret_key = config.SECRET_KEY

app.config.from_object('doxbox.config')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['GOOGLEMAPS_KEY'] = config.GOOGLEMAPS_API_KEY
app.config['ONLINE_LAST_MINUTES'] = config.ONLINE_LAST_MINUTES
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///doxkit.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# initialize other flask libs
flask_bootstrap.Bootstrap(app)
flask_googlemaps.GoogleMaps(app)
nav = flask_nav.Nav()
db = flask_sqlalchemy.SQLAlchemy(app)

# other global variables
user  = socket.gethostname()
localhost = socket.gethostbyname(user)
lan_ip = os.popen("ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'").read()


class DoxDB(db.Model):
    """
    SQLAlchemy model for Dox function
    """
    __tablename__ = "dox"
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    textarea = Column(Text)

    def __init__(self, name, textarea):
        self.name = name
        self.textarea = textarea

    def __repr__(self):
        return '<Name {0}>'.format(self.name)

# initialize database
db.create_all()


def signal_handler(signal, frame):
    """
    helper function for sighandler to kill safely
    as well as actual app
    """
    print("\033[1;32m\nKilling doxbox.\033[0m")
    sys.exit(0)

# initialize signal handler
signal.signal(signal.SIGINT, signal_handler)


def yaml_from_model(model):
    """
    helper function to deserialize model to yaml
    """
    columns = { c.name: c.type.python_type.__name__
                for c in model.__table__.columns }

    return yaml.dump({model.__name__.lower(): columns},
                     default_flow_style=False)


def to_dict_from_json(value):
    """
    helper function that converts json to dict
    """
    return ast.literal_eval(value)

def subdomain_search(value):
    """
    helper function for interacting with crt.sh
    """
    return json.dumps(crtsh.crtshAPI().search(str(value)))


@app.template_filter('to_dict')
def to_dict(value):
    """
    helper for converting str to dict, registered
    as filter for jinja templates
    """
    return ast.literal_eval(value).items()


@app.route('/')
def hello():
    return flask.redirect(flask.url_for('index'))


@app.route('/index')
def index():
    return flask.render_template('index.html',
                user=user,
                title="Admin Dashboard",
                small="Welcome to doxbox!",
                localhost=localhost,
                lan_ip=lan_ip)


@app.route('/dox', methods=['GET', 'POST'])
def dox():
    description = """  The Dox module is a comprehensive info-gathering database that enables the pentester
    to write "Dox", or a file that holds a collection of data of a certain target, or targets.
    Using this data, the tester will be able to effectively understand their target, which is a
    critical point in the attacker's kill chain. Usually deemed malicious and black-hat in nature,
    the D0x module, however, aims to help security researchers gain momentum when conducting in-the-field
    pentesting. The Dox module does come with several features, improved upon based off of the prior
    revision. Not only does it provide an user interface for at-ease use, but also capabilities to store
    already-collected information, as well as import non-doxbox written Dox reports."""

    form = forms.DoxForm()

    # query DB entries
    rows = DoxDB.query.all()

    # if POST, parse yaml and add to DB
    if flask.request.method == "POST":
        # Create empty dict to store parsed yaml
        parsed_yaml = {}

        # Load raw text as yaml data into dict
        # ... will now have a key-value structure for template
        parsed_yaml = yaml.load(flask.request.form["textarea"])

        # Add 'n commit 'n flask.flash success!
        d = DoxDB(flask.request.form['name'], str(parsed_yaml))
        db.flask.session.add(d)
        db.flask.session.commit()
        flask.flash("Dox created successfully!", "success")

    # Render normally, assumption with GET flask.request
    return flask.render_template('dox.html',
                            title="Dox Module",
                            small="Writing comprehensive reports for the purpose of information gathering",
                            user=user,
                            description=description,
                            form=form, rows=rows)


@app.route('/delete-dox/<delete_id>', methods=['GET'])
def deletedox(delete_id):
    DoxDB.query.filter_by(id=delete_id).delete()
    db.flask.session.commit()
    flask.flash("Deleted query!", "success")
    return flask.redirect(flask.url_for('dox'))


@app.route('/export-dox-csv/<export_id>', methods=['GET'])
def exportdox_csv(export_id):
    time = time.strftime("%Y-%m-%d-%H:%M:%S", time.gmtime())

    # open csv for writing
    with open('{}.csv'.format(time), 'wb') as csv:
        outcsv = csv.writer(csv)
        records = db.flask.session.query(DoxDB).all()
        [ outcsv.writerow([getattr(curr, column.name)
          for column in DoxDB.__mapper__.columns])
          for curr in records ]

    flask.flash("Exported Dox! Stored in your doxbox path.", "success")
    return flask.redirect(flask.url_for('dox'))


@app.route('/geoip', methods=['GET', 'POST'])
def geoip():
    description = """
    When working with metadata, IP addresses often pop up as a point-of-interest.
    Using Maxmind and Google Map's APIs, the GeoIP module aims to collect geolocation
    information on public IP addresses, in order to gather data on physical location during
    the reconaissance stage of the killchain. In order to make this module work, please provide a
    Google Maps API key."""

    form = forms.GeoIPForm()

    if flask.request.method == "POST":

        geoip = pygeoip.GeoIP("extras/GeoLiteCity.dat")
        try:
            ip_data = geoip.record_by_addr(flask.request.form['ip'])
            return flask.render_template('geoip.html',
                    title="GeoIP Module", user=user, description=description, form=form,
                    latitude=ip_data["latitude"], longitude=ip_data["longitude"], ip_data=ip_data)

        except (TypeError, ValueError, socket.error):
            flask.flash("Invalid IP Address provided!", "danger")
            return flask.redirect(flask.url_for('geoip'))
    else:
        return flask.render_template('geoip.html',
                title="GeoIP Module", small="Using locational data to conduct info-gathering",
                user=user, description=description, form=form,
                latitude="0", longitude="0")


@app.route('/api/geoip/<ip_address>')
def ipinfo(ip_address):
    geoip = pygeoip.GeoIP("extras/GeoLiteCity.dat")
    ip_data = geoip.record_by_addr(ip_address)
    return flask.jsonify(ip_data)


@app.route('/dns', methods=['GET', 'POST'])
def dns():
    description = """
    Targets, whether it be a company or a person, may utilize domains in order to
    display web content. Domains, especially those that are not properly configured,
    give penetration testers great opportunity to gather sensitive information in the
    form of metadata, whether it be an address from a WHOIS lookup, or nameservers."""

    form = forms.DNSForm()

    if flask.request.method == "POST":
        whois_data = whois.whois(flask.request.form["url"])

        # Subdomain enumeration using crt.sh
        _subdomain = subdomain_search(flask.request.form["url"])
        subdomain = [y['domain'] for y in to_dict_from_json(_subdomain)]
        # Re-render with appopriate parameters
        return flask.render_template('dns.html', title="DNS Enumeration Module",
                            user=user, description=description,
                            form=form, whois=whois_data, subdomain=subdomain)
    else:
        return flask.render_template('dns.html', title="DNS Enumeration Module",
                            user=user,description=description,
                            form=form, whois=None, subdomain=None)

# register filters
app.jinja_env.filters['to_dict'] = to_dict

if __name__ == '__main__':
    app.run()
