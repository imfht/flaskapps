(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-4ed6"],{"26f4":function(t,e,a){},4497:function(t,e,a){"use strict";var n=a("26f4"),i=a.n(n);i.a},"619f":function(t,e,a){},"73ae":function(t,e,a){"use strict";a.d(e,"d",function(){return i}),a.d(e,"a",function(){return r}),a.d(e,"b",function(){return s}),a.d(e,"c",function(){return o}),a.d(e,"e",function(){return l});var n=a("66df"),i=function(t){return n["a"].request({url:"/v1/cron/job/",method:"get",params:t})},r=function(t,e){return n["a"].request({url:"/v1/cron/job/".concat(e),method:"post",data:t})},s=function(t,e){return n["a"].request({url:"/v1/cron/job/".concat(e),method:"post",data:t})},o=function(t){return n["a"].request({url:"/v1/cron/job/remove",method:"delete",data:t})},l=function(t){return n["a"].request({url:"/v1/cron/job/log",method:"get",params:t})}},8913:function(t,e,a){"use strict";var n=a("619f"),i=a.n(n);i.a},f0ef:function(t,e,a){"use strict";a.r(e);var n=function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("Card",[a("div",{staticClass:"search-con search-con-top"},[a("Select",{staticClass:"search-col",model:{value:t.searchKey,callback:function(e){t.searchKey=e},expression:"searchKey"}},t._l(t.columns,function(e){return"handle"!==e.key&&"status"!==e.key&&""!==e.key?a("Option",{key:"search-col-"+e.key,attrs:{value:e.key}},[t._v(t._s(e.title))]):t._e()})),a("Input",{staticClass:"search-input",attrs:{clearable:"",placeholder:"输入关键字搜索"},on:{"on-change":t.handleClear},model:{value:t.searchValue,callback:function(e){t.searchValue=e},expression:"searchValue"}}),a("Button",{staticClass:"search-btn",attrs:{type:"primary"},on:{click:t.handleSearch}},[t._v("搜索")]),t._t("new_btn",[a("Button",{staticClass:"search-btn",attrs:{type:"primary"},on:{click:function(e){t.editModal("","add","新建任务")}}},[t._v("新建")])])],2),a("Table",{ref:"selection",attrs:{size:"small",border:"",columns:t.columns,data:t.tableData}}),a("div",{staticStyle:{margin:"10px",overflow:"hidden"}},[a("div",{staticStyle:{float:"left"}},[a("Page",{attrs:{total:t.pageTotal,current:t.getParams.pageNum,"page-size":t.getParams.pageSize,"page-size-opts":[25,50,100],"show-sizer":"","show-total":""},on:{"on-change":t.changePage,"on-page-size-change":t.handlePageSize}})],1)]),a("Modal",{attrs:{title:t.modalMap.modalTitle,loading:!0,"footer-hide":!0},model:{value:t.modalMap.modalVisible,callback:function(e){t.$set(t.modalMap,"modalVisible",e)},expression:"modalMap.modalVisible"}},[a("form-group",{attrs:{list:t.formList},on:{"on-submit-success":t.handleSubmit}})],1)],1)},i=[],r=function(){var t=this,e=t.$createElement,a=t._self._c||e;return Object.keys(t.valueList).length?a("Form",{ref:"form",attrs:{"label-width":t.labelWidth,model:t.valueList,rules:t.rules}},[t._l(t.list,function(e,n){return a("FormItem",{key:t._uid+"_"+n,attrs:{label:e.label,"label-position":"left",prop:e.name,error:t.errorStore[e.name]},nativeOn:{click:function(a){t.handleFocus(e.name)}}},[a(e.type,{tag:"component",attrs:{range:e.range,placeholder:e.placeholder?e.placeholder:"",maxlength:"i-input"===e.type&&e.maxlength?e.maxlength:50,type:"i-input"===e.type&&e.type1?e.type1:"text"},model:{value:t.valueList[e.name],callback:function(a){t.$set(t.valueList,e.name,a)},expression:"valueList[item.name]"}},[e.children?t._l(e.children.list,function(i,r){return a(e.children.type,{key:t._uid+"_"+n+"_"+r,tag:"component",attrs:{label:i.label,value:i.value}},[t._v(t._s(i.title))])}):t._e()],2)],1)}),a("FormItem",[t._t("right-btn"),a("Button",{attrs:{type:"primary",loading:t.loading},on:{click:t.handleSubmit}},[t._v("提交")]),a("Button",{staticStyle:{"margin-left":"8px"},on:{click:t.handleReset}},[t._v("重置")]),t._t("left-btn")],2)],2):t._e()},s=[],o=(a("7f7f"),a("ac6a"),a("c5f6"),a("cadf"),a("551c"),a("097d"),{name:"FormGroup",data:function(){return{loading:!1,initValueList:[],rules:{},valueList:{},errorStore:{}}},props:{list:{type:Array,default:function(){return[]}},labelWidth:{type:Number,default:110}},watch:{list:function(){this.setInitValue()}},methods:{setInitValue:function(){var t={},e={},a={},n={};this.list.forEach(function(i){t[i.name]=i.rule,e[i.name]=i.value,a[i.name]=i.value,n[i.name]=""}),this.rules=t,this.valueList=e,this.initValueList=a,this.errorStore=n},handleSubmit:function(){var t=this;this.$refs.form.validate(function(e){e&&(t.$emit("on-submit-success",{data:t.valueList}),t.loading=!0,setTimeout(function(){t.loading=!1},1e3))})},handleReset:function(){var t=JSON.parse(JSON.stringify(this.initValueList));this.valueList=JSON.stringify(t)},handleFocus:function(t){this.errorStore[t]=""}},mounted:function(){this.setInitValue()}}),l=o,u=(a("8913"),a("2877")),c=Object(u["a"])(l,r,s,!1,null,null,null);c.options.__file="form-group.vue";var d=c.exports,h=d,m=a("73ae"),p={components:{FormGroup:h},data:function(){var t=this;return{columns:[{type:"selection",key:"",width:60,align:"center"},{title:"job id",key:"id",align:"center",sortable:!0},{title:"可执行命令",key:"cmd"},{title:"定时器（秒 分 时 日 月 周）",key:"cron"},{title:"下一次执行时间",key:"next_run_time"},{title:"状态",key:"status",width:80,align:"center",render:function(e,a,n){return e("div",[e("i-switch",{props:{size:"large",value:"running"===a.row.status},style:{marginRight:"5px"},scopedSlots:{open:function(){return e("span","正常")},close:function(){return e("span","暂停")}},on:{"on-change":function(){t.onSwitch(a)}}})])}},{title:"操作",key:"handle",width:150,align:"center",render:function(e,a){return e("div",[e("Button",{props:{type:"primary",size:"small"},style:{marginRight:"5px"},on:{click:function(){t.editModal(a.index,"edit","编辑任务")}}},"编辑"),e("Button",{props:{type:"error",size:"small"},on:{click:function(){t.delData(a)}}},"删除")])}}],tableData:[],pageTotal:0,getParams:{pageNum:1,pageSize:25},modalMap:{modalVisible:!1,modalTitle:"创建任务"},formList:[],hand_method:"",searchKey:"",searchValue:""}},methods:{getCronJobsList:function(){var t=this;Object(m["d"])(this.getParams).then(function(e){t.tableData=e.data.data})},editModal:function(t,e,a){this.modalMap.modalVisible=!0,this.modalMap.modalTitle=a,this.hand_method=e,this.formList=[{name:"id",type:"i-input",value:"edit"===e?this.tableData[t].id:"",label:"job id",placeholder:"请输入定时任务ID，建议使用有意义的英文命名，名且不要更改",rule:[{required:!0,message:"job_id不能为空",trigger:"blur"}]},{name:"cmd",type:"i-input",value:"edit"===e?this.tableData[t].cmd:"",label:"可执行命令",placeholder:"请输入要执行的命令，必须为可执行，注意环境变量",rule:[{required:!0,message:"执行命令不能为空",trigger:"blur"}]},{name:"cron",type:"i-input",value:"edit"===e?this.tableData[t].cron:"",label:"任务定时器",placeholder:"定时器，参考linux crontab，（秒 分 时 日 月 周）",rule:[{required:!0,message:"定时器不能为空",trigger:"blur"}]}]},handleSubmit:function(t){var e=this;setTimeout(function(){Object(m["a"])(t.data,e.hand_method).then(function(t){var a="add"==e.hand_method?"任务添加成功":"任务修改成功";0===t.data.status?(e.$Message.success({content:a,duration:5}),e.getCronJobsList(e.getParams),e.modalMap.modalVisible=!1):e.$Message.error({content:t.data.msg,duration:5})})},1e3)},delData:function(t){var e=this;confirm("确定要删除 ".concat(t.row.id))&&Object(m["c"])({id:t.row.id}).then(function(a){0===a.data.status?(e.$Message.success({content:"任务删除成功",duration:5}),e.tableData.splice(t.index,1)):e.$Message.error({content:a.data.msg,duration:5})})},onSwitch:function(t){var e=this,a="running"==t.row.status?"/pause":"/resume",n="running"==t.row.status?"任务暂停成功":"任务恢复成功";Object(m["b"])({id:t.row.id},a).then(function(t){0===t.data.status?e.$Message.success({content:n,duration:5}):e.$Message.error({content:t.data.msg,duration:5})})},changePage:function(t){this.pageNum=t,this.getCronJobsList(this.getParams)},handlePageSize:function(t){this.pageSize=t,this.getCronJobsList(1,this.pageSize,this.searchKey,this.searchValue)},handleClear:function(t){""===t.target.value&&(this.tableData=this.value)},handleSearch:function(){this.getCronJobsList(this.pageNum,this.pageSize,this.searchKey,this.searchValue)}},mounted:function(){this.getCronJobsList()}},f=p,g=(a("4497"),Object(u["a"])(f,n,i,!1,null,"487a932a",null));g.options.__file="List.vue";e["default"]=g.exports}}]);
//# sourceMappingURL=chunk-4ed6.ff83e9a9.js.map