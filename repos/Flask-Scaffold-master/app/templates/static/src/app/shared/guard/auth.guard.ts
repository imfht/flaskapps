// not used check authguard/auth-guard.service.ts

import { Injectable } from '@angular/core';
import { CanActivate } from '@angular/router';
import { Router } from '@angular/router';
//import { JwtHelperService } from '@auth0/angular-jwt';


@Injectable()
export class AuthGuard implements CanActivate {
    constructor(private router: Router) {}

    canActivate():  boolean{
        if (localStorage.getItem('id_token')) {
            return true;
        }

        this.router.navigate(['/login']);
        return false;
    }
    

} 
//https://medium.com/@ryanchenkie_40935/angular-authentication-using-route-guards-bf7a4ca13ae3

