webpackJsonp([47],{"/M7r":function(t,e,a){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var i={render:function(){var t=this.$createElement,e=this._self._c||t;return e("div",{staticStyle:{padding:"20px",overflow:"auto"},attrs:{div:""}},[e("div",{staticStyle:{"min-width":"900px"}},[e("Tabs",{attrs:{size:"small",type:"card",value:this.page.state},on:{"on-click":this.handleTabChange}},this._l(this.stateList,function(t){return e("TabPane",{key:t.value,attrs:{label:t.label,name:t.value}})})),this._v(" "),e("Table",{attrs:{loading:this.tableLoading,border:"",columns:this.tablecolumns,data:this.tableData,"no-data-text":"未找到相关订单"}})],1),this._v(" "),e("div",{staticStyle:{"margin-top":"15px",overflow:"hidden"}},[e("div",{staticStyle:{float:"right"}},[e("Page",{attrs:{total:this.totalcount,"page-size":this.page.pagesize,"page-size-opts":[10,20,30,40],"show-elevator":"","show-sizer":"",placement:"top","show-total":""},on:{"on-change":this.indexChange,"on-page-size-change":this.sizeChange}})],1)])])},staticRenderFns:[]},n=a("VU/8")({name:"repair-list",data:function(){var t=this;return{tableLoading:!1,page:{pagesize:10,pageindex:0,state:"-1",type:-1},repairTypeObj:{1:"手机",2:"电脑",3:"宽带"},stateList:[{value:"-1",label:"全部"},{value:"0",label:"未处理"},{value:"1",label:"已同意"},{value:"2",label:"已拒绝"}],stateObj:{"-1":"全部",0:"未处理",1:"已同意",2:"已拒绝"},totalcount:0,tablecolumns:[{title:"#",width:60,align:"center",render:function(e,a){return a.index+t.page.pageindex*t.page.pagesize+1}},{title:"申请人",width:120,key:"realname",align:"center"},{title:"联系方式",width:140,key:"telphone",align:"center"},{title:"故障类型",width:200,key:"repairtype",align:"center",render:function(e,a){return t.repairTypeObj[a.row.repairtype]||""}},{title:"申请时间",minwidth:200,key:"createtime",align:"center"},{title:"申请状态",key:"state",width:130,align:"center",render:function(e,a){return t.stateObj[a.row.state]||""}},{title:"操作",key:"action",width:200,align:"center",render:function(e,a){var i=e("Button",{props:{type:"primary",size:"small"},style:{marginRight:"5px"},on:{click:function(){t.$Confirm("处理用户的维修申请，请确认","提示").then(function(e){t.dealApply(a.row.id,1)},function(t){})}}},"同意"),n=e("Button",{props:{type:"warning",size:"small"},style:{marginRight:"5px"},on:{click:function(){t.$Confirm("拒绝用户的维修申请，请确认","提示").then(function(e){t.dealApply(a.row.id,2)},function(t){})}}},"拒绝"),s=e("Button",{props:{type:"primary",size:"small"},style:{marginRight:"5px"},on:{click:function(){t.$router.push({name:"RepairDetail",query:{repairid:a.row.id}})}}},"详情");return e("div",0==a.row.state?[i,n,s]:[s])}}],tableData:[{id:1,realname:"大陈",telphone:"18879701111",repairtype:2,createtime:"2018-12-21",state:0}]}},mounted:function(){this.$sitemap.prvname="订单管理",this.$sitemap.currname="维修申请",this.$menuactive.open=["OrderBlock"],this.$menuactive.active="RepairList",this.getRepairList()},watch:{page:{handler:function(t,e){this.getRepairList()},deep:!0}},methods:{getRepairList:function(){var t=this,e={};e.pageindex=this.page.pageindex,e.pagesize=this.page.pagesize,e.type=this.page.type,e.state=this.page.state,this.tableLoading=!0,this.$http.post(this.$api.repair_list,e).then(function(e){t.tableLoading=!1,1==e.data.result&&e.data.data?(t.tableData=e.data.data,t.totalcount=+e.data.totalcount):t.$Message.error(e.data.msg)})},indexChange:function(t){this.page.pageindex=t-1},sizeChange:function(t){this.page.pagesize=t},handleTabChange:function(t){this.page.state=t,this.page.pageindex=0},dealApply:function(t,e){var a=this;this.$http.post(this.$api.repair_editstate,{repairid:t,state:e}).then(function(t){1==t.data.result&&a.getRepairList()})}}},i,!1,null,null,null);e.default=n.exports}});
//# sourceMappingURL=47.bdcc52285e706ef6367a.js.map