import {{ NgModule }} from '@angular/core';
import {{ Routes, RouterModule }} from '@angular/router';
import {{ {Resource}EditComponent }} from './{resources}-edit.component';

const routes: Routes = [
    {{
        path: '', component: {Resource}EditComponent
    }}
];

@NgModule({{
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule]
}})
export class {Resource}EditRoutingModule {{
}}
