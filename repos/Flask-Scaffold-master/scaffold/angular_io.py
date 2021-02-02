#Function to generate the front end angular templates
import os
import shutil
import sys
import subprocess
import json
import yaml
import inflect
from scaffold.angular_custom_fields import *
from typing import Dict, List


#Get a list of files from the module directory that we need to recreate
object_scaffold_folder = "scaffold/app/templates/module"
object_add_scaffold_folder =os.path.join(object_scaffold_folder, "add")
object_edit_scaffold_folder =os.path.join(object_scaffold_folder, "edit")
object_scaffold_files = os.listdir(path="scaffold/app/templates/module")
object_scaffold_add_files = os.listdir(path="scaffold/app/templates/module/add")
object_scaffold_edit_files = os.listdir(path="scaffold/app/templates/module/edit")


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

# Function to create Angular files
def create_angular_files(object_name:str , attributes:Dict[str,str]):
    
    resource,resources = make_plural(object_name)
    Resource = resource.title()
    #Create Angular folders and files
    object_dir = os.path.join('app/templates/static/src/app/', resources)
    object_add_dir = os.path.join(object_dir, "add")
    object_edit_dir = os.path.join(object_dir, "edit")





    try: 
        os.mkdir(object_dir)
        os.mkdir(object_add_dir)
        os.mkdir(object_edit_dir)


        #First generate the fields
        
        #Fields to add to module.component.html
        table_headers = ""
        table_rows = ""

        #Fields to add to add/edit-component.html
        angular_form_fields = ""

        #Fields to add to edit.component.ts
        edit_FormControl_value_strings = ""
        edit_attribute_strings = ""
        edit_getter_strings = ""

        #Fields to add to add.component.ts
        add_FormControl_init_strings = ""
        add_getter_strings = ""
        add_attribute_strings = " "



        for attribute in attributes:
                field, field_type = attribute.split(':')
                Field=field.title()
                if field_type == "integer":
                    angular_form_fields += user_add_edit_string.format(field=field,type="number")
                elif field_type == "email":
                    angular_form_fields += user_add_edit_string.format(field=field,type="email")
                elif field_type == "boolean":
                    angular_form_fields += boolean_form_string.format(field=field,Field=Field)
                elif field_type == "url":
                    angular_form_fields += user_add_edit_string.format(field=field,type="radio")
                elif field_type == "decimal":
                    angular_form_fields += user_add_edit_string.format(field=field,type="decimal")
                #Need to add backend code    
                elif field_type == "password":
                    angular_form_fields += user_add_edit_string.format(field=field,type="password")
                elif field_type == "datetime":
                    table_headers += table_header_field.format(Field=Field)
                    table_rows += table_date_row_field.format(field=field, resource=resource)
                
                    continue   
                else:
                    angular_form_fields += user_add_edit_string.format(field=field,type="text")


                table_headers += table_header_field.format(Field=Field)
                table_rows += table_row_field.format(field=field, resource=resource)
                edit_FormControl_value_strings += edit_FormControl_value_string.format(field=field)
                edit_attribute_strings += edit_attribute_string.format(field=field, Resource=Resource)
                edit_getter_strings += edit_getter_string.format(field=field, Resource=Resource)
                add_FormControl_init_strings += FormControl_string.format(field=field)
                add_getter_strings += getter_string.format(field=field, Resource=Resource)
                add_attribute_strings += attribute_string.format(field=field, Resource=Resource)

        
         


                
                    
        #Main object files            
        for file in object_scaffold_files:
            
            if file == "module.component.html":
                with open(os.path.join(object_dir, '{resources}.component.html'.format(resources=resources)), "w") as new_file:
                    with open(os.path.join(object_scaffold_folder, "module.component.html"), "r") as old_file:
                        for line in old_file:
                            new_file.write(line.format(resource=resource, resources=resources,
                                                    Resource=resource.title(),
                                                    Resources=resources.title(),
                                                    table_headers=table_headers,
                                                    table_rows=table_rows))
            elif file == "module-routing.module.ts":
                with open(os.path.join(object_dir, '{resources}-routing.module.ts'.format(resources=resources)), "w") as new_file:
                    with open(os.path.join(object_scaffold_folder, "module-routing.module.ts"), "r") as old_file:
                        for line in old_file:
                            new_file.write(line.format(resource=resource,
                                                    resources=resources,
                                                    Resources=resources.title(),
                                                    Resource=resource.title()
                                                    ))

            elif file == "module.component.ts":
                with open(os.path.join(object_dir, '{resources}.component.ts'.format(resources=resources)), "w") as new_file:
                    with open(os.path.join(object_scaffold_folder,"module.component.ts"), "r") as old_file:
                        for line in old_file:
                            new_file.write(line.format(resource=resource, resources=resources,
                                                    Resource=resource.title(),
                                                    Resources=resources.title()))
            
            elif file == "module.component.scss":
                with open(os.path.join(object_dir, '{resources}.component.scss'.format(resources=resources)), "w") as new_file:
                    with open(os.path.join(object_scaffold_folder, "module.component.scss"), "r") as old_file:
                        for line in old_file:
                            new_file.write(line.format(resource=resource, resources=resources,
                                                    Resource=resource.title()))
            elif file == "module.module.ts":
                with open(os.path.join(object_dir, '{resources}.module.ts'.format(resources=resources)), "w") as new_file:
                    with open(os.path.join(object_scaffold_folder,"module.module.ts"), "r") as old_file:
                        for line in old_file:
                            new_file.write(line.format(resource=resource, resources=resources,
                                                    Resource=resource.title(),
                                                    Resources=resources.title()
                                                    ) )
            elif file == "module.service.ts":
                with open(os.path.join(object_dir, '{resources}.service.ts'.format(resources=resources)), "w") as new_file:
                    with open(os.path.join(object_scaffold_folder,"module.service.ts"), "r") as old_file:
                        for line in old_file:
                            new_file.write(line.format(resource=resource, 
                                                    resources=resources,
                                                    Resource=resource.title(),
                                                    Resources=resources.title()
                                                    ))

        #Add object files            
        for file in object_scaffold_add_files:
            
            if file == "module-add.component.html":
                with open(os.path.join(object_add_dir, '{resources}-add.component.html'.format(resources=resources)), "w") as new_file:
                    with open(os.path.join(object_add_scaffold_folder, "module-add.component.html"), "r") as old_file:
                        for line in old_file:
                            new_file.write(line.format(resource=resource, resources=resources,
                                                    Resource=resource.title(),
                                                    Resources=resources.title(),
                                                    angular_form_fields=angular_form_fields,
                                                    ))
            elif file == "module-routing.module.ts":
                with open(os.path.join(object_add_dir, '{resources}-routing.module.ts'.format(resources=resources)), "w") as new_file:
                    with open(os.path.join(object_add_scaffold_folder, "module-routing.module.ts"), "r") as old_file:
                        for line in old_file:
                            new_file.write(line.format(resource=resource,
                                                    resources=resources,
                                                    Resources=resources.title(),
                                                    Resource=resource.title()
                                                    ))

            elif file == "module-add.component.ts":
                with open(os.path.join(object_add_dir, '{resources}-add.component.ts'.format(resources=resources)), "w") as new_file:
                    with open(os.path.join(object_add_scaffold_folder,"module-add.component.ts"), "r") as old_file:
                        for line in old_file:
                            new_file.write(line.format(resource=resource, resources=resources,
                                                    Resource=resource.title(),
                                                    Resources=resources.title(),
                                                    FormControl_fields=add_FormControl_init_strings,
                                                    attribute_fields=add_attribute_strings,
                                                    getter_fields=add_getter_strings))

         
            
            elif file == "module-add.component.scss":
                with open(os.path.join(object_add_dir, '{resources}-add.component.scss'.format(resources=resources)), "w") as new_file:
                    with open(os.path.join(object_add_scaffold_folder, "module-add.component.scss"), "r") as old_file:
                        for line in old_file:
                            new_file.write(line.format(resource=resource, resources=resources,
                                                    Resource=resource.title()))
            elif file == "module-add.module.ts":
                with open(os.path.join(object_add_dir, '{resources}-add.module.ts'.format(resources=resources)), "w") as new_file:
                    with open(os.path.join(object_add_scaffold_folder,"module-add.module.ts"), "r") as old_file:
                        for line in old_file:
                            new_file.write(line.format(resource=resource, resources=resources,
                                                    Resource=resource.title(),
                                                    Resources=resources.title()
                                                    ) )
                                                     


        #Edit Object files            
        for file in object_scaffold_edit_files:
            
            if file == "module-edit.component.html":
                with open(os.path.join(object_edit_dir, '{resources}-edit.component.html'.format(resources=resources)), "w") as new_file:
                    with open(os.path.join(object_edit_scaffold_folder, "module-edit.component.html"), "r") as old_file:
                        for line in old_file:
                            new_file.write(line.format(resource=resource, resources=resources,
                                                    Resource=resource.title(),
                                                    Resources=resources.title(),
                                                    angular_form_fields=angular_form_fields
                                                    ))
            elif file == "module-routing.module.ts":
                with open(os.path.join(object_edit_dir, '{resources}-routing.module.ts'.format(resources=resources)), "w") as new_file:
                    with open(os.path.join(object_edit_scaffold_folder, "module-routing.module.ts"), "r") as old_file:
                        for line in old_file:
                            new_file.write(line.format(resource=resource,
                                                    resources=resources,
                                                    Resources=resources.title(),
                                                    Resource=resource.title()
                                                    ))

            elif file == "module-edit.component.ts":
                with open(os.path.join(object_edit_dir, '{resources}-edit.component.ts'.format(resources=resources)), "w") as new_file:
                    with open(os.path.join(object_edit_scaffold_folder,"module-edit.component.ts"), "r") as old_file:
                        for line in old_file:
                            new_file.write(line.format(resource=resource, resources=resources,
                                                    Resource=resource.title(),
                                                    Resources=resources.title(),
                                                    edit_FormControl_strings= add_FormControl_init_strings,
                                                    edit_FormControl_value_strings = edit_FormControl_value_strings,
                                                    edit_attributes = edit_attribute_strings,
                                                    edit_getter_fields=edit_getter_strings))
           
            elif file == "module-edit.component.scss":
                with open(os.path.join(object_edit_dir, '{resources}-edit.component.scss'.format(resources=resources)), "w") as new_file:
                    with open(os.path.join(object_edit_scaffold_folder, "module-edit.component.scss"), "r") as old_file:
                        for line in old_file:
                            new_file.write(line.format(resource=resource, resources=resources,
                                                    Resource=resource.title()))
            elif file == "module-edit.module.ts":
                with open(os.path.join(object_edit_dir, '{resources}-edit.module.ts'.format(resources=resources)), "w") as new_file:
                    with open(os.path.join(object_edit_scaffold_folder,"module-edit.module.ts"), "r") as old_file:
                        for line in old_file:
                            new_file.write(line.format(resource=resource, resources=resources,
                                                    Resource=resource.title(),
                                                    Resources=resources.title()
                                                    ) )
            

    except:
        if os.path.isdir(object_dir):
            shutil.rmtree(object_dir)
        raise 

        
     
     

     
        
    
