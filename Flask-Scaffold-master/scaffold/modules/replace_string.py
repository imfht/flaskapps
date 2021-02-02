from scaffold.modules.errors import ReplaceError


#String to add Routes to app.js
new_route_string = """
   // States
  // Routes for {resources}
   .state('{resources}', {{
        abstract: true, //An abstract state cannot be loaded, but it still needs a ui-view for its children to populate.
                         // https://github.com/angular-ui/ui-router/wiki/Nested-States-and-Nested-Views
        url: '/{resources}',
        title: '{Resources}',
        template: '<ui-view/>'
   }})
  .state('{resources}.list', {{
    url: '/list',
    templateUrl: '{resources}/index.html',
    controller: '{Resource}ListController',


  }}).state('{resources}.new', {{
    url: '/new',
    templateUrl: '/{resources}/add.html',
    controller: '{Resource}CreateController',

    }}).state('{resources}.edit', {{
    url: '/:id/edit',
    templateUrl: '{resources}/update.html',
    controller: '{Resource}EditController',

        }})

        // End Routes for {resources}"""

# Strings to add to to main index.html
js_src_string =""" <!-- Controllers -->
    <script type="text/javascript" src="{resources}/controllers.js"></script>"""

menu_string ="""  <!-- menu -->
             <li><a ui-sref="{resources}.list" id="{resources}_menu" >{Resources}</a></li>"""

#Strings to test.bash
test_script_string = """
#TESTS
#Tests for {resources}
protractor  app/templates/{resources}/conf.js  &&
python app/{resources}/test_{resources}.py
#End Tests for {resources}"""


conf_js_string="""
   //Specs
   , 'app/templates/{resources}/spec.js' """

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
