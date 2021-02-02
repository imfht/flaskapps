# String for add/edit.component.html

user_add_edit_string = """ <div class="form-group">
                                <input type="{type}" class="form-control input-underline input-lg" id="{field}" 
                                         required    formControlName = "{field}" placeholder=" {field}">

                                         <div *ngIf="{field}.invalid && ({field}.dirty || {field}.touched)"
                                                class="alert alert-danger">

                                            <div *ngIf="{field}.errors.required">
                                                {field} is required.
                                            </div>
                                            
                                            
                                            </div>
                            </div> """
boolean_form_string = """
        <fieldset class="form-group">
               <label>{Field}</label>
              
          <label class="radio-inline"> 
                <input type="radio"  id="{field}" value="true" formControlName = "{field}" checked> yes</label>
                <label class="radio-inline">
               <input type="radio"  id="{field}" value="true" formControlName = "{field}" checked> no</label>               
           </fieldset>
"""
#Add to module-add.component.ts

#Common for edit and add
FormControl_string = """
       {field}: new FormControl('', [  Validators.required,]),
       """

getter_string = """

            get {field}() {{ return this.{Resource}AddForm.get('{field}'); }}

            """

attribute_string = """

             "{field}" : this.{Resource}AddForm.value.{field},
                      """

#Add to module-edit.component.ts
edit_FormControl_value_string = """
    
              "{field}" : res.data.attributes.{field},

              """
edit_attribute_string = """

                  "{field}" : this.{Resource}EditForm.value.{field},
                """  

edit_getter_string =  """
        get {field}() {{ return this.{Resource}EditForm.get('{field}'); }}

        """

              
########### module.component.html Fields ##########
table_header_field = """
                         <th>{Field}</th>"""
table_row_field = """
                         <td>{{{{ {resource}.attributes.{field} }}}}</td>"""

                                                  
table_date_row_field = """
                         <td>{{{{ {resource}.attributes.{field} | date:'long' }}}}</td>"""
