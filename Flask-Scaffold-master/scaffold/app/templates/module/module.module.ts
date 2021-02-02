import {{ NgModule }} from '@angular/core';
import {{ CommonModule }} from '@angular/common';

import {{ {Resources}RoutingModule }} from './{resources}-routing.module';
import {{ {Resources}Component }} from './{resources}.component';
import {{ PageHeaderModule }} from '../shared';

@NgModule({{
    imports: [CommonModule, {Resources}RoutingModule, PageHeaderModule],
    declarations: [{Resources}Component]
}})
export class {Resources}Module {{}}
