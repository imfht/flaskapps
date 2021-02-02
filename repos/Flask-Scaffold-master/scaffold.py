#!/usr/bin/env python
import os
import shutil
import sys
import subprocess
import json
import yaml
import inflect
from scaffold.custom_fields import *
from scaffold.replace_string import *
from scaffold.modules.errors import BlueprintError
from scaffold.angular_io import create_angular_files

blueprint_file = 'app/__init__.py'
test_script = 'tests.bash'
yaml_file = sys.argv[1]
# Angular 6 files
app_js_file = "app/templates/static/src/app/app.module.ts"

#change var name to layout file
sidebar_file = "app/templates/static/src/app/layout/components/sidebar/sidebar.component.html"
layout_route_file = "app/templates/static/src/app/layout/layout-routing.module.ts"
#end js layout

#Path to files for scaffolding js files
path_scaffold_template = "scaffold/app/templates/"
conf_js_file = "conf.js"

# Error classes
def make_plural(resource):
    # https://pypi.python.org/pypi/inflect
    p = inflect.engine()
    if p.singular_noun(resource):
        resources = resource
        resource = p.singular_noun(resource)
        return resource, resources
    else:
        resources = p.plural(resource)
        return resource, resources

#Generate Flask API files
def generate_files(module_path):

    app_files = ['views.py', 'models.py', '__init__.py',  'tests.py']

    for file in app_files:

        # Generate App files
        if file == "views.py":
            with open(os.path.join(module_path, 'views.py'), "w") as new_file:
                with open("scaffold/app/views.py", "r") as old_file:
                    for line in old_file:
                        new_file.write(line.format(resource=resource,
                                                   resources=resources,
                                                   Resources=resources.title(),
                                                   Resource=resource.title(),
                                                   add_fields=add_fields))

        elif file == "models.py":
            with open(os.path.join(module_path, 'models.py'), "w") as new_file:
                with open("scaffold/app/models.py", "r") as old_file:
                    for line in old_file:
                        new_file.write(line.format(resource=resource, resources=resources,
                                                   Resources=resources.title(),
                                                   db_rows=db_rows,
                                                   schema=schema, meta=meta,
                                                   init_self_vars=init_self_vars,
                                                   init_args=init_args))

        elif file == "__init__.py":
            with open(os.path.join(module_path, '__init__.py'), "w") as new_file:
                with open("scaffold/app/__init__.py", "r") as old_file:
                    for line in old_file:
                        new_file.write(line)

      
        

def register_blueprints():
    string_to_insert_after = '# Blueprints'
    new_blueprint = """
    # Blueprints
    from app.{resources}.views import {resources}
    app.register_blueprint({resources}, url_prefix='/api/v1/{resources}')""".format(resources=resources)

    with open(blueprint_file, 'r+') as old_file:
        filedata = old_file.read()
    if string_to_insert_after in filedata:
        # replace the first occurrence
        new_filedata = filedata.replace(
            string_to_insert_after, new_blueprint, 1)
        with open(blueprint_file, 'w') as new_file:
            new_file.write(new_filedata)
            print("Registered Blueprints for ", resources)
    else:
        raise BlueprintError()

        


def clean_up(module_path):
    if os.path.isdir(module_path):
        shutil.rmtree(module_path)
 

#change to exclude template folder
def run_autopep8():
    try:
        cmd_output = subprocess.check_output(
            ['autopep8', '--in-place', '--recursive', 'app'])
        print("Ran autopep8")
    except subprocess.CalledProcessError:
        print("autopep8 failed")
        raise

def run_ngbuild():
    try:
        os.chdir("app/templates/static/")
        cmd_output = subprocess.check_output(
            ['ng', 'build', '--prod'])    
        print("Ran Ng Build --prod")
    except subprocess.CalledProcessError:
        print("Ng build --prod failed")
        raise

# Main Code Start
#
# Parse YAML file
with open(yaml_file, "r") as file:

    yaml_data = yaml.load(file)

    for module, fields in yaml_data.items():
            # make module name plural
        resource, resources = make_plural(module)

        # Start strings to insert into models
        db_rows = ""
        schema = ""
        meta = ""
        init_self_vars = ""
        init_args = ""
        # End strings to insert into models

        # Start strings to insert into views
        add_fields = ""

        for f in fields:
            field, field_type = f.split(':')
            if field_type == "string":
                db_rows += """
    {} = db.Column(db.String(250), nullable=False)""".format(field)
                schema += """
    {} = fields.String(validate=not_blank)""".format(field)
                

            elif field_type == "boolean":
                db_rows += """
    {} = db.Column(db.Integer, nullable=False)""".format(field)
                schema += """
    {} = fields.Integer(required=True)""".format(field)
               

            elif field_type == "integer":
                db_rows += """
    {} = db.Column(db.Integer, nullable=False)""".format(field)
                schema += """
    {} = fields.Integer(required=True)""".format(field)
             

            elif field_type == "email":
                db_rows += """
    {} = db.Column(db.String(250), nullable=False)""".format(field)
                schema += """
    {} = fields.Email(validate=not_blank)""".format(field)
               


            elif field_type == "url":
                db_rows += """
    {} = db.Column(db.String(250), nullable=False)""".format(field)
                schema += """
    {} = fields.URL(validate=not_blank)""".format(field)
                

            #Will be auto populated at the db level
            elif field_type == "datetime":
                db_rows += """
    {} = db.Column(db.TIMESTAMP,nullable=False, default=datetime.utcnow)""".format(field)
                schema += """
    {} = fields.DateTime()""".format(field)
                continue


            elif field_type == "date":
                db_rows += """
    {} = db.Column(db.Date, nullable=False)""".format(field)
                schema += """
    {} = fields.Date(required=True)""".format(field)
               

            elif field_type == "decimal":
                db_rows += """
    {} = db.Column(db.Numeric, nullable=False)""".format(field)
                schema += """
    {} = fields.Decimal(as_string=True)""".format(field)
                

            elif field_type == "text":
                db_rows += """
    {} = db.Column(db.Text, nullable=False)""".format(field)
                schema += """
    {} = fields.String(validate=not_blank)""".format(field)
               

            # models
            meta += """ '{}', """.format(field)
            init_args += """ {}, """.format(field)
            init_self_vars += """
        self.{field} = {field}""".format(field=field)
            # Views
            add_fields += add_string.format(field)

        module_dir = os.path.join('app', resources)
        try:
            os.mkdir(module_dir)
            try:
                
                generate_files(module_dir)
                create_angular_files(module, fields)
                print("files created successfully")
                register_blueprints()
                # Update service in app.module.ts
                replace_string(resource, resources , app_js_file, "// service", app_module_string)
                replace_string(resource, resources , app_js_file, "// import", app_import_string)


                # Add js files to index.html
                replace_string(
                    resource, resources, layout_route_file, "// route", layout_route_string)

                # Add menus to the sidebar.html
                replace_string(
                    resource, resources, sidebar_file, "<!-- menu -->", menu_string)
                # Add routes __init__.py
                replace_string(resource,resources,blueprint_file, "#app-route", app_route)    
              
                
                #run_autopep8()
            except:
                clean_up(module_dir)
                raise

        except:
            raise
run_ngbuild()