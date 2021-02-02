import { Component, Input } from '@angular/core';
import { Router } from '@angular/router';
import { routerTransition } from '../router.animations';
import { Subscription } from 'rxjs';
import { UsersService } from '../users/users.service';
import { FormGroup, FormControl } from '@angular/forms';
import { analyzeAndValidateNgModules } from '@angular/compiler';



@Component({
    selector: 'app-login',
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.scss'],
    animations: [routerTransition()]
})
export class LoginComponent  {

    LoginSubs: Subscription;
    obj :any;
    LoginForm = new FormGroup({
        email: new FormControl(''),
        password: new FormControl(''),
      });
    token : any;
     http_errors :boolean = false;
     error_message:any;



    constructor(private usersApi: UsersService, private router: Router, 
         ) { 
             }
    
    
    onLoggedin() {

        

        this.obj = {
            "data": {
              "type": "users",
              "attributes": {
                  "email" : this.LoginForm.value.email,
                  "password" : this.LoginForm.value.password
              }
                
              }
            }

           

        this.LoginSubs = this.usersApi
            
            .login(this.obj)
            .subscribe(res => {
               //console.log( res.token);
               localStorage.setItem('id_token', res.token);

      
               this.router.navigate(['/dashboard']);
      
      
              
              },

              error => {
                this.http_errors = true;

                  this.error_message = error // error path


              }
              
              
            );
        

        
        //this.LoginSubs.unsubscribe();

        //localStorage.setItem('isLoggedin', 'true');
    }
}
