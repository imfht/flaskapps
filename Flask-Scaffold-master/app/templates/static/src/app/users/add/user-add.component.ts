import { Component, OnInit } from '@angular/core';
import { routerTransition } from '../../router.animations';
import { Subscription } from 'rxjs';
import { UsersService } from '../users.service';
import {Router} from "@angular/router";
import { FormGroup, FormControl, Validators } from '@angular/forms';




@Component({
    selector: 'user-add',
    templateUrl: './user-add.component.html',
    styleUrls: ['./user-add.component.scss'],
    animations: [routerTransition()]
})



export class UserAddComponent implements OnInit {
   
    userAddSubs: Subscription;
    obj :any;

    UserAddForm:FormGroup;
    http_errors :boolean = false;
    error_message:any;

    ngOnInit ()   {
      
      this.UserAddForm = new FormGroup(
    
      {
      email: new FormControl('', [
      Validators.required,
      
      
          ]),
      
      name: new FormControl('',[
        Validators.required,
        
        
      ]),

      password: new FormControl('', [
        Validators.required,
        Validators.minLength(8),
        
        
      ]),
    },{updateOn: 'blur'} );

  }

  get name() { return this.UserAddForm.get('name'); }
  get email() { return this.UserAddForm.get('email'); }

  get password() { return this.UserAddForm.get('password'); }


    constructor(private usersApi: UsersService, private router: Router) { 
             }
 
 
  
 
  onSubmit() { 
     
 
    this.obj = {
        "data": {
          "type": "users",
          "attributes": {
            "email" : this.UserAddForm.value.email,
            "password" : this.UserAddForm.value.password,
            "name" : this.UserAddForm.value.name,
        }
            
          }
        }


    this.userAddSubs = this.usersApi
      .add(this.obj)
      .subscribe(res => {
         // console.log( res.data);

         

        

         this.router.navigate(['/users']);


        
        },
      
        error => {
          this.http_errors = true;

            this.error_message = error // error path


        }
        
        
      );

     
}
 
 

}

    








