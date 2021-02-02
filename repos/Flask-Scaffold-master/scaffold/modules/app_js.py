from scaffold.modules.errors import AppjsError


#Module to add states and routes to the app.js
new_state_string = """
   // States
  // Routes for {resources}
  .state('{resources}', {{
    url: '/{resources}',
    templateUrl: '{resources}/index.html',
    controller: '{Resource}ListController',
    
  
  }}).state('new{Resource}', {{
    url: '/{resources}/new',
    templateUrl: '/{resources}/add.html',
    controller: '{Resource}CreateController',
    
    }}).state('edit{Resource}', {{ 
    url: '/{resources}/:id/edit',
    templateUrl: '{resources}/update.html',
    controller: '{Resource}EditController',
    
        }})"""
        
        
        

def create_appjs(resource, resources, app_js_file):
    string_to_insert_after = '// States'
    new_states = new_state_string.format(resources=resources, resource=resource, Resource=resource.title())

    with open(app_js_file, 'r+') as old_file:
        filedata = old_file.read()
    if string_to_insert_after in filedata:
        # replace the first occurrence
        new_filedata = filedata.replace(
            string_to_insert_after, new_states, 1)
        with open(app_js_file, 'w') as new_file:
            new_file.write(new_filedata)
            print("Routes added to app.js for ", resources)
    else:
        raise AppjsError()