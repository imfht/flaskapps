from scaffold.modules.errors import ReplaceError


#String to add to app.module.ts

app_import_string = """
        import {{ {Resources}Service }} from './{resources}/{resources}.service'
        // import

        """

app_module_string = """
                // service
                {Resources}Service,
                """

# String to Add to layout-routing.module.ts
layout_route_string = """
                // route
                {{ path: '{resources}', loadChildren: '../{resources}/{resources}.module#{Resources}Module' }},
                {{ path: '{resource}-add', loadChildren: '../{resources}/add/{resources}-add.module#{Resource}AddModule' }},
                 {{ path: '{resources}/:id', loadChildren: '../{resources}/edit/{resources}-edit.module#{Resource}EditModule' }},
                """

#   String to add to sidebar.component.html

menu_string ="""
  <a [routerLink]="['/{resources}']" [routerLinkActive]="['router-link-active']" class="list-group-item">
            <i class="fa fa-fw fa-table"></i>&nbsp;
            <span>{{{{ '{Resources}' | translate }}}}</span>
        </a>
        
            <!-- menu -->

                                    """

#String to add to __init__.py for routes
app_route = """
    #app-route  
    @app.route('/{resources}')
           """



def replace_string(resource, resources, file, string_to_insert_after, new_string):

    new_string = new_string.format(resources=resources, resource=resource, Resource=resource.title(), Resources=resources.title())

    with open(file, 'r+', encoding = "utf-8") as old_file:
        filedata = old_file.read()
    if string_to_insert_after in filedata:
        # replace the first occurrence
        new_filedata = filedata.replace(
            string_to_insert_after, new_string, 1)
        with open(file, 'w', encoding = "utf-8") as new_file:
            new_file.write(new_filedata)
            print("Updated", file)
    else:
        error_msg = """Unable to replace {string_to_insert_after}, with {new_string}
                      in file {file} """.format(string_to_insert_after=string_to_insert_after, new_string=new_string,
                                                 file=file)
        raise ReplaceError(error_msg)
