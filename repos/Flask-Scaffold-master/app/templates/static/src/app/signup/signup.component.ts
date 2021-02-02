import { Component, OnInit } from '@angular/core';
import { routerTransition } from '../router.animations';
import { Subscription } from 'rxjs';
import { UsersService } from '../users/users.service';
import {Router} from "@angular/router";
import { FormGroup, FormControl, Validators } from '@angular/forms';

@Component({
    selector: 'app-signup',
    templateUrl: './signup.component.html',
    styleUrls: ['./signup.component.scss'],
    animations: [routerTransition()]
})
export class SignupComponent implements OnInit {
   
   
    userAddSubs: Subscription;
    obj :any;

    SignUpForm:FormGroup;
    http_errors :boolean = false;
    error_message:any;

    ngOnInit ()   {
      
      this.SignUpForm = new FormGroup(
    
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

  get name() { return this.SignUpForm.get('name'); }
  get email() { return this.SignUpForm.get('email'); }

  get password() { return this.SignUpForm.get('password'); }


    constructor(private usersApi: UsersService, private router: Router) { 
             }
 
 
  
 
  onSubmit() { 
     
 
    this.obj = {
        "data": {
          "type": "users",
          "attributes": {
            "email" : this.SignUpForm.value.email,
            "password" : this.SignUpForm.value.password,
            "name" : this.SignUpForm.value.name,
        }
            
          }
        }


    this.userAddSubs = this.usersApi
      .signUp(this.obj)
      .subscribe(res => {
         // console.log( res.data);

         

        

         this.router.navigate(['/login']);


        
        },
      
        error => {
          this.http_errors = true;

            this.error_message = error // error path


        }
        
        
      );

     
}
 
 

}

    








