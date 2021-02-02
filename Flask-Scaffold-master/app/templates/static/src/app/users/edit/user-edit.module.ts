import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UserEditRoutingModule } from './user-edit-routing.module';
import { UserEditComponent } from './user-edit.component';
import { PageHeaderModule } from '../../shared';
import { ReactiveFormsModule } from '@angular/forms';


@NgModule({
  imports: [CommonModule, UserEditRoutingModule,  PageHeaderModule,  ReactiveFormsModule],
  declarations: [UserEditComponent]
})

export class UserEditModule { }






