webpackJsonp([48],{"O+gj":function(e,t,a){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var i={render:function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("div",{staticStyle:{padding:"20px",overflow:"auto"},attrs:{div:""}},[a("div",{staticStyle:{"min-width":"900px"}},[a("Tabs",{attrs:{size:"small",type:"card",value:e.page.state},on:{"on-click":e.handleTabChange}},e._l(e.stateList,function(e){return a("TabPane",{key:e.value,attrs:{label:e.label,name:e.value}})})),e._v(" "),a("Table",{attrs:{loading:e.tableLoading,border:"",columns:e.tablecolumns,data:e.tableData,"no-data-text":"未找到相关订单"}})],1),e._v(" "),a("div",{staticStyle:{"margin-top":"15px",overflow:"hidden"}},[a("div",{staticStyle:{float:"right"}},[a("Page",{attrs:{total:e.totalcount,"page-size":e.page.pagesize,"page-size-opts":[10,20,30,40],"show-elevator":"","show-sizer":"",placement:"top","show-total":""},on:{"on-change":e.indexChange,"on-page-size-change":e.sizeChange}})],1)]),e._v(" "),a("Modal",{attrs:{title:"拒绝理由",width:"300"},model:{value:e.showConfirm,callback:function(t){e.showConfirm=t},expression:"showConfirm"}},[a("Input",{attrs:{placeholder:"请输入拒绝理由！",maxlength:11},model:{value:e.addMobile,callback:function(t){e.addMobile="string"==typeof t?t.trim():t},expression:"addMobile"}}),e._v(" "),a("div",{directives:[{name:"show",rawName:"v-show",value:e.mobileRuleBol,expression:"mobileRuleBol"}],staticStyle:{color:"#ed3f14","font-size":"12px",padding:"4px 0 0 4px"}},[e._v(e._s(e.mobileRuleText))]),e._v(" "),a("div",{attrs:{slot:"footer"},slot:"footer"},[a("Button",{attrs:{size:"large"},on:{click:function(t){e.showConfirm=!1}}},[e._v("取消")]),e._v(" "),a("Button",{attrs:{type:"primary",size:"large"},on:{click:e.addRow}},[e._v("提交")])],1)],1)],1)},staticRenderFns:[]},n=a("VU/8")({name:"repair-list",data:function(){var e=this;return{tableLoading:!1,showConfirm:!1,mobileRuleText:"",addMobile:"",mobileRuleBol:!1,confirmId:"",page:{pagesize:10,pageindex:0,state:"-1"},repairTypeObj:{1:"手机",2:"电脑",3:"宽带"},stateList:[{value:"-1",label:"全部"},{value:"0",label:"未处理"},{value:"1",label:"已同意"},{value:"2",label:"已拒绝"}],stateObj:{"-1":"全部",0:"未处理",1:"已同意",2:"已拒绝"},totalcount:0,tablecolumns:[{title:"#",width:60,align:"center",render:function(t,a){return a.index+e.page.pageindex*e.page.pagesize+1}},{title:"申请人",width:200,key:"realname",align:"center"},{title:"联系方式",width:200,key:"telphone",align:"center"},{title:"申请地区",key:"province",align:"center",render:function(e,t){return e("span",t.row.province+t.row.city+t.row.county)}},{title:"申请学校",key:"school",align:"center"},{title:"申请状态",key:"state",width:130,align:"center",render:function(t,a){return e.stateObj[a.row.state]||""}},{title:"操作",key:"action",width:200,align:"center",render:function(t,a){var i=t("Button",{props:{type:"primary",size:"small"},style:{marginRight:"5px"},on:{click:function(){e.$Confirm("处理用户的申请代理人，请确认","提示").then(function(t){e.dealApply(a.row.id,1)},function(e){})}}},"同意"),n=t("Button",{props:{type:"warning",size:"small"},style:{marginRight:"5px"},on:{click:function(){e.showConfirm=!0,e.mobileRuleText="",e.confirmId=a.row.id}}},"拒绝");return t("div",0==a.row.state?[i,n]:"已完成")}}],tableData:[{id:1,realname:"大陈",telphone:"18879701111",repairtype:2,createtime:"2018-12-21",state:0}]}},mounted:function(){this.$sitemap.prvname="用户管理",this.$sitemap.currname="代理人列表",this.$menuactive.open=["MemberBlock"],this.$menuactive.active="ProxyList",this.getRepairList()},watch:{page:{handler:function(e,t){this.getRepairList()},deep:!0}},methods:{addAdmin:function(){this.showConfirm=!0,this.mobileRuleBol=!1,this.mobileRuleText="",this.addMobile=""},addRow:function(){var e=this;e.showConfirm=!1;var t=e.confirmId,a={refusereason:e.addMobile,applyid:t,state:2};e.$http.post(e.$api.applyshop_updatestate,a).then(function(t){1==t.data.result?(e.$Message.success("操作成功!"),e.getRepairList()):e.$Message.error(t.data.msg)})},getRepairList:function(){var e=this,t={};t.pageindex=this.page.pageindex,t.pagesize=this.page.pagesize,t.state=this.page.state,this.tableLoading=!0,this.$http.post(this.$api.applyshop_list,t).then(function(t){e.tableLoading=!1,1==t.data.result&&t.data.data?(e.tableData=t.data.data,e.totalcount=+t.data.totalcount):e.$Message.error(t.data.msg)})},indexChange:function(e){this.page.pageindex=e-1},sizeChange:function(e){this.page.pagesize=e},handleTabChange:function(e){this.page.state=e,this.page.pageindex=0},dealApply:function(e,t){var a=this;this.$http.post(this.$api.applyshop_updatestate,{applyid:e,state:t}).then(function(e){1==e.data.result&&a.getRepairList()})}}},i,!1,null,null,null);t.default=n.exports}});
//# sourceMappingURL=48.c8735ebf7e70b7585068.js.map