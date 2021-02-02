import {{ NgModule }} from '@angular/core';
import {{ Routes, RouterModule }} from '@angular/router';
import {{ {Resource}AddComponent }} from './{resources}-add.component';

const routes: Routes = [
    {{
        path: '', component: {Resource}AddComponent
    }}
];

@NgModule({{
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule]
}})
export class {Resource}AddRoutingModule {{
}}
