import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { UserAddRoutingModule } from './user-add-routing.module';
import { UserAddComponent } from './user-add.component';
import { PageHeaderModule } from '../../shared';
import { ReactiveFormsModule } from '@angular/forms';


@NgModule({
    imports: [CommonModule, UserAddRoutingModule, PageHeaderModule,  ReactiveFormsModule],
    declarations: [UserAddComponent]
})
export class UserAddModule {}