import {{ Component, OnInit }} from '@angular/core';
import {{ routerTransition }} from '../../router.animations';
import {{ Subscription }} from 'rxjs';
import {{ {Resources}Service }} from '../{resources}.service';
import {{Router}} from "@angular/router";
import {{ FormGroup, FormControl, Validators }} from '@angular/forms';




@Component({{
    selector: '{resource}-add',
    templateUrl: './{resources}-add.component.html',
    styleUrls: ['./{resources}-add.component.scss'],
    animations: [routerTransition()]
}})



export class {Resource}AddComponent implements OnInit {{
   
    {resource}AddSubs: Subscription;
    obj :any;

    {Resource}AddForm:FormGroup;
    http_errors :boolean = false;
    error_message:any;

    ngOnInit ()   {{
      
      this.{Resource}AddForm = new FormGroup(
    
      {{
      
        {FormControl_fields}

      
    

     
    }},{{updateOn: 'blur'}} );

  }}

 {getter_fields}


    constructor(private {resources}Api: {Resources}Service, private router: Router) {{ 
             }}
 
 
  
 
  onSubmit() {{ 
     
 
    this.obj = {{
        "data": {{
          "type": "{resources}",
          "attributes": {{
           
            {attribute_fields}
        }}
            
          }}
        }}


    this.{resource}AddSubs = this.{resources}Api
      .add(this.obj)
      .subscribe(res => {{    
        
         this.router.navigate(['/{resources}']);

        }},
      
        error => {{
          this.http_errors = true;

            this.error_message = error // error path


        }}
        
        
      );

     
}}
 
 

}}

    








