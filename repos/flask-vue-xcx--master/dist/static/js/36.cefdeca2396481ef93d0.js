webpackJsonp([36],{DdJ0:function(e,t,a){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var r=a("Dd8w"),n=a.n(r),i=a("fZjL"),o=a.n(i),l={data:function(){var e=this;return{dateOption:{shortcuts:[{text:"一周",value:function(){var e=new Date,t=new Date;return t.setTime(t.getTime()-6048e5),[t,e]}},{text:"1个月",value:function(){var e=new Date,t=new Date;return t.setTime(t.getTime()-2592e6),[t,e]}},{text:"3个月",value:function(){var e=new Date,t=new Date;return t.setTime(t.getTime()-7776e6),[t,e]}}],disabledDate:function(e){return e&&e.valueOf()>Date.now()}},orderstatus:[{value:"-1",label:"全部"},{value:"0",label:"未支付"},{value:"1",label:"待发货"},{value:"2",label:"已发货"},{value:"3",label:"待评价"},{value:"5",label:"已取消"},{value:"4",label:"已完成"}],orderForm:{ordermodel:-1,date:[],realname:"",orderid:"",telephone:""},page:{pageindex:0,pagesize:10,status:"-1"},payTypeObj:{1:"微信",2:"积分",3:"钱包"},totalcount:0,tableLoading:!1,itemcolumns:[{title:"#",width:60,align:"center",render:function(t,a){return a.index+e.page.pageindex*e.page.pagesize+1}},{title:"订单编号",key:"orderid",minWidth:200,align:"center"},{title:"收货人姓名",width:120,key:"realname",align:"center"},{title:"收货人手机号",key:"telephone",width:130,align:"center"},{title:"金额",key:"amount",width:100,align:"center"},{title:"订单状态",key:"paystatus",width:100,align:"center",render:function(t,a){var r=e.orderstatus.find(function(e){return e.value==""+a.row.paystatus});return t("span",r?r.label:"")}},{title:"创建日期",key:"createtime",width:200,align:"center"},{title:"操作",key:"action",width:120,align:"center",render:function(t,a){return t("div",[t("Button",{props:{type:"primary",size:"small"},style:{marginRight:"5px"},on:{click:function(){e.$router.push({path:"/order/detail",query:{orderid:a.row.orderid}})}}},"查看详情")])}}],itemdata:[]}},mounted:function(){var e=this;this.$sitemap.prvname="订单管理",this.$sitemap.currname="订单列表",this.$menuactive.open=["OrderBlock"],this.$menuactive.active="OrderList",this.$Loading.start(),this.getOrderList().then(function(){e.$Loading.finish()})},methods:{handlerTabChange:function(e){this.page.status=e,this.page.pageindex=0},handleReset:function(e){this.$refs[e].resetFields()},formatDate:function(){var e=this,t={};return o()(e.orderForm).forEach(function(a){switch(a){case"date":""!==e.orderForm[a][0]&&""!==e.orderForm[a][1]&&(t.starttime=Date.parse(e.orderForm[a][0])/1e3,t.endtime=Date.parse(e.orderForm[a][1])/1e3);break;default:t[a]=e.orderForm[a]}}),n()({},e.page,t)},getOrderList:function(){var e=this;return this.tableLoading=!0,this.$http.post(this.$api.order_list,e.formatDate()).then(function(t){1==t.data.result&&t.data.data?(e.itemdata=t.data.data?t.data.data:[],e.totalcount=+t.data.totalcount):e.$Message.error(t.data.msg)}).catch(function(t){e.$Message.error("服务器异常")}).then(function(){e.tableLoading=!1})},indexChange:function(e){this.page.pageindex=e-1},sizeChange:function(e){this.page.pagesize=e}},watch:{page:{handler:function(e,t){this.getOrderList()},deep:!0}}},s={render:function(){var e=this,t=e.$createElement,a=e._self._c||t;return a("div",{staticStyle:{padding:"20px",overflow:"auto"}},[a("div",{staticStyle:{width:"900px"}},[a("Form",{ref:"orderForm",attrs:{"label-width":80,"label-position":"left",model:e.orderForm}},[a("Row",{attrs:{gutter:20}},[a("Col",{attrs:{span:"16"}},[a("FormItem",{attrs:{label:"创建时间",prop:"date"}},[a("DatePicker",{staticStyle:{width:"100%"},attrs:{type:"datetimerange",options:e.dateOption,"split-panels":"",placeholder:"选择时间"},model:{value:e.orderForm.date,callback:function(t){e.$set(e.orderForm,"date",t)},expression:"orderForm.date"}})],1)],1),e._v(" "),a("Col",{attrs:{span:"8"}},[a("FormItem",{attrs:{label:"收货姓名",prop:"realname"}},[a("Input",{attrs:{placeholder:"请输入收货人姓名"},model:{value:e.orderForm.realname,callback:function(t){e.$set(e.orderForm,"realname",t)},expression:"orderForm.realname"}})],1)],1)],1),e._v(" "),a("Row",{attrs:{gutter:20}},[a("Col",{attrs:{span:"16"}},[a("FormItem",{attrs:{label:"订单编号",prop:"orderid"}},[a("Input",{attrs:{placeholder:"请输入订单编号"},model:{value:e.orderForm.orderid,callback:function(t){e.$set(e.orderForm,"orderid",t)},expression:"orderForm.orderid"}})],1)],1)],1),e._v(" "),a("FormItem",[a("Button",{staticStyle:{width:"100px","margin-right":"20px"},attrs:{type:"primary"},on:{click:e.getOrderList}},[e._v("查询")]),e._v(" "),a("Button",{staticStyle:{width:"100px"},attrs:{type:"ghost"},on:{click:function(t){e.handleReset("orderForm")}}},[e._v("重置")])],1)],1)],1),e._v(" "),a("Tabs",{attrs:{size:"small",type:"card",value:e.page.status},on:{"on-click":e.handlerTabChange}},e._l(e.orderstatus,function(e){return a("TabPane",{key:e.value,attrs:{label:e.label,name:e.value}})})),e._v(" "),a("div",{staticStyle:{"min-width":"900px"}},[a("Table",{attrs:{loading:e.tableLoading,border:"",columns:e.itemcolumns,data:e.itemdata,"no-data-text":"未找到相关订单"}})],1),e._v(" "),a("div",{staticStyle:{"margin-top":"15px",overflow:"hidden"}},[a("div",{staticStyle:{float:"right"}},[a("Page",{attrs:{total:e.totalcount,"page-size":e.page.pagesize,"page-size-opts":[10,20,30,40],"show-elevator":"","show-sizer":"",placement:"top","show-total":""},on:{"on-change":e.indexChange,"on-page-size-change":e.sizeChange}})],1)])],1)},staticRenderFns:[]};var d=a("VU/8")(l,s,!1,function(e){a("Svir")},"data-v-011fc920",null);t.default=d.exports},Svir:function(e,t){}});
//# sourceMappingURL=36.cefdeca2396481ef93d0.js.map