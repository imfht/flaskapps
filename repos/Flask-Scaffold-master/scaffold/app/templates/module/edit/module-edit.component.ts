import {{ Component, OnInit }} from '@angular/core';
import {{ {Resources}Service }} from '../{resources}.service';
import {{Router, ActivatedRoute}} from "@angular/router";
import {{ FormGroup, FormControl, Validators }} from '@angular/forms';


@Component({{
  selector: '{resource}-edit',
  templateUrl: './{resources}-edit.component.html',
  styleUrls: ['./{resources}-edit.component.scss']
}})
export class {Resource}EditComponent implements OnInit  {{

   {Resource}EditForm = new FormGroup({{
    
      {edit_FormControl_strings}
     
  }});


  

   id:number  =  parseInt(this.route.snapshot.paramMap.get('id'));
   http_errors :boolean = false;
   error_message:any;
  
    {edit_getter_fields}

  constructor(private {resources}Api: {Resources}Service, private router: Router, private route: ActivatedRoute,) {{ 
   
  }}

  ngOnInit() {{

  

    this.{resources}Api
    .get{Resource}(this.id)
    .subscribe(res => {{
       this.{Resource}EditForm.setValue({{
        

        {edit_FormControl_value_strings}
        

       }}
       
          )
       
       
      }});
          
      



        }}

       

        onSubmit() {{

          let {resource} = {{

        

              "data": {{
                "type": "{resources}",
                "attributes": {{
                  {edit_attributes}
              }}
                  
                }}
              
          }}

       


          this.{resources}Api
   
               .edit({resource}, this.id)
               .subscribe(res => {{
                  
                this.router.navigate(['/{resources}']);

                    }},
                    error => {{
                      this.http_errors = true;
            
                        this.error_message = error // error path
            
            
                    }}                 );
        
        }}


       



        }}





  
  

  




