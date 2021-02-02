import { Component, OnDestroy, OnInit,ChangeDetectorRef } from '@angular/core';
import { routerTransition } from '../router.animations';

import { Subscription } from 'rxjs';
import { UsersService } from './users.service';
import * as $ from 'jquery';
import 'datatables.net';
import 'datatables.net-bs4';
import {Router} from "@angular/router";



@Component({
    selector: 'app-tables',
    templateUrl: './users.component.html',
    styleUrls: ['./users.component.scss'],
    animations: [routerTransition()]
})
export class UsersComponent implements OnInit {
   
 usersListSubs: Subscription;
 
  authenticated = false;
 
  users: any[];
  dataTable: any;
  http_errors :boolean = false;
  error_message:any;

  constructor(private usersApi: UsersService, private chRef: ChangeDetectorRef,  private router: Router) {  }

 

  ngOnInit() {
    this.usersListSubs = this.usersApi
      .getLists()
      .subscribe(res => {
          this.users = res.data;

          // Datatables startYou'll have to wait that changeDetection occurs and projects data into 
        // the HTML template, you can ask Angular to that for you ;-)
        this.chRef.detectChanges();

        // Now you can use jQuery DataTables :
        const table: any = $('table');
        this.dataTable = table.DataTable();
        // data tables end
        },
        console.error
      );
    
  }



  deleteUser(id : number )  {

    this.usersApi

         .delete(id)
         .subscribe(res => {
            
          location.reload();

              },
              error => {
                this.http_errors = true;
      
                  this.error_message = error 
      
      
              }  
                    );
            
            }

  ngOnDestroy() {
    this.usersListSubs.unsubscribe();
  }
    
}







