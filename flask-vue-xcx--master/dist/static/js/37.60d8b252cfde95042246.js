webpackJsonp([37],{PFpv:function(t,e,a){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var i={data:function(){return{step:1,loading:!1,wxapayconfig:{mchid:"",signkey:""},ruleValidate:{mchid:[{required:!0,message:"请输入微信支付商户号！",trigger:"blur"}],signkey:[{required:!0,message:"请输入API 密钥！",trigger:"blur"}]}}},mounted:function(){this.$sitemap.prvname="小程序管理",this.$sitemap.currname="微信支付配置",this.$menuactive.open=["SystemBlock"],this.$menuactive.active="WxaPayConfig",this.getPayconfigDetail()},methods:{handleSubmit:function(t){var e=this,a=this.$refs[t];this.$refs[t].validate(function(t){t?(e.loading=!0,e.postPayconfigSave(a)):e.$Message.error("还没有完整的信息输入！")})},handleReset:function(t){this.$refs[t].resetFields()},getPayconfigDetail:function(){var t=this;this.$http.post(this.$api.payconfig_detail,{}).then(function(e){e.data.data?(t.wxapayconfig.mchid=e.data.data.mchid,t.wxapayconfig.signkey=e.data.data.signkey,t.step=2):t.step=1}).catch(function(t){})},postPayconfigSave:function(t){var e=this,a=this;this.$http.post("/payconfig/save",{mchid:this.wxapayconfig.mchid,signkey:this.wxapayconfig.signkey}).then(function(e){1==e.data.result?(t.resetFields(),a.$Message.success("小程序参数配置成功!")):a.$Message.error("操作失败，请检查原因！")}).catch(function(t){a.$Message.error("操作失败！"+t)}).then(function(){e.loading=!1})}}},n={render:function(){var t=this,e=t.$createElement,a=t._self._c||e;return a("div",{staticStyle:{margin:"20px"}},[a("Steps",{attrs:{current:t.step}},[a("Step",{attrs:{title:"申请微信支付",content:"通过微信小程序后台申请开通"}}),t._v(" "),a("Step",{attrs:{title:"微信支付参数配置",content:"填写微信支付商户号和API密钥"}}),t._v(" "),a("Step",{attrs:{title:"完成配置",content:"完成配置后即可使用微信支付"}})],1),t._v(" "),a("div",{staticStyle:{"margin-top":"60px"}}),t._v(" "),a("Form",{ref:"formValidate",attrs:{model:t.wxapayconfig,rules:t.ruleValidate,"label-position":"left","label-width":180}},[a("FormItem",{attrs:{label:"微信支付商户号",prop:"mchid"}},[a("Input",{attrs:{placeholder:"请输入微信支付商户号！",size:"large"},model:{value:t.wxapayconfig.mchid,callback:function(e){t.$set(t.wxapayconfig,"mchid",e)},expression:"wxapayconfig.mchid"}})],1),t._v(" "),a("FormItem",{attrs:{label:"API 密钥",prop:"signkey"}},[a("Input",{attrs:{placeholder:"请输入API 密钥！",size:"large"},model:{value:t.wxapayconfig.signkey,callback:function(e){t.$set(t.wxapayconfig,"signkey",e)},expression:"wxapayconfig.signkey"}})],1),t._v(" "),a("FormItem",[a("Button",{staticStyle:{width:"120px"},attrs:{type:"primary",loading:t.loading,size:"large"},on:{click:function(e){t.handleSubmit("formValidate")}}},[t.loading?a("span",[t._v("正在保存..")]):a("span",[t._v(t._s(1==t.step?"提交配置":"保存修改"))])]),t._v(" "),a("Button",{staticStyle:{"margin-left":"8px",width:"80px"},attrs:{type:"ghost",size:"large"},on:{click:function(e){t.handleReset("formValidate")}}},[t._v("取消")])],1)],1)],1)},staticRenderFns:[]},s=a("VU/8")(i,n,!1,null,null,null);e.default=s.exports}});
//# sourceMappingURL=37.60d8b252cfde95042246.js.map