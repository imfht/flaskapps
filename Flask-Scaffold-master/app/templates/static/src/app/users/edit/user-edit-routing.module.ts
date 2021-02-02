import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { UserEditComponent } from './user-edit.component';



const routes: Routes = [
    {
        path: '', component: UserEditComponent,
        
       
        
    }
];




       

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule]
})
export class UserEditRoutingModule {
}
