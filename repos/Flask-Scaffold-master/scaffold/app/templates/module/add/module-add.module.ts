import {{ NgModule }} from '@angular/core';
import {{ CommonModule }} from '@angular/common';

import {{ {Resource}AddRoutingModule }} from './{resources}-routing.module';
import {{ {Resource}AddComponent }} from './{resources}-add.component';
import {{ PageHeaderModule }} from '../../shared';
import {{ ReactiveFormsModule }} from '@angular/forms';


@NgModule({{
    imports: [CommonModule, {Resource}AddRoutingModule, PageHeaderModule,  ReactiveFormsModule],
    declarations: [{Resource}AddComponent]
}})
export class {Resource}AddModule {{}}