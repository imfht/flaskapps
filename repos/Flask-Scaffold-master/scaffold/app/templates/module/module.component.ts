import {{ Component, OnDestroy, OnInit,ChangeDetectorRef }} from '@angular/core';
import {{ routerTransition }} from '../router.animations';

import {{ Subscription }} from 'rxjs';
import {{ {Resources}Service }} from './{resources}.service';
import * as $ from 'jquery';
import 'datatables.net';
import 'datatables.net-bs4';


@Component({{
    selector: 'app-tables',
    templateUrl: './{resources}.component.html',
    styleUrls: ['./{resources}.component.scss'],
    animations: [routerTransition()]
}})
export class {Resources}Component implements OnInit {{
   
 {resources}ListSubs: Subscription;
 
  authenticated = false;
 
  {resources}: any[];
  // Our future instance of DataTable
  dataTable: any;

  http_errors :boolean = false;
  error_message:any;

  constructor(private {resources}Api: {Resources}Service, private chRef: ChangeDetectorRef) {{  }}

 

  ngOnInit() {{
    this.{resources}ListSubs = this.{resources}Api
      .getLists()
      .subscribe(res => {{
          this.{resources} = res.data;

          // Datatables startYou'll have to wait that changeDetection occurs and projects data into 
        // the HTML template, you can ask Angular to that for you ;-)
        this.chRef.detectChanges();

        // Now you can use jQuery DataTables :
        const table: any = $('table');
        this.dataTable = table.DataTable();
        // data tables end
        }},
        error => {{
          this.http_errors = true;

            this.error_message = error 


        }}  
      );
    
  }}

  delete{Resource}(id : number )  {{

    this.{resources}Api

         .delete(id)
         .subscribe(res => {{
            
          location.reload();

              }},
              error => {{
                this.http_errors = true;
      
                  this.error_message = error 
      
      
              }} 
                    );
            
            }}

  ngOnDestroy() {{
    this.{resources}ListSubs.unsubscribe();
  }}
    
}}







