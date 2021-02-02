webpackJsonp([11],{TYYy:function(t,a,e){"use strict";Object.defineProperty(a,"__esModule",{value:!0});var r=e("fZjL"),s=e.n(r),o={data:function(){return{formData:{catename:"",catepic:"",sortvalue:0,isrecommend:0,parentid:"",ishidden:0,id:""},rules:{catename:{required:!0,message:"分类名称不能为空！",trigger:"blur"},catepic:{required:!0,message:"分类图片不能为空！",trigger:"blur"}},loading:!1,parentData:{}}},methods:{handleImgChange:function(t){this.formData.catepic=t.url},handleEdit:function(t){var a=this,e=this;this.$refs[t].validate(function(t){if(t)return a.$http.post(a.$api.category_edit,a.formData).then(function(t){1==t.data.result?(e.$Message.success("修改成功"),a.$router.push("/category/list")):e.$Message.error(t.data.msg)}).catch(function(t){e.$Message.error("服务器异常")});a.$Message.error("请检查数据是否填充完整！")})},handleReset:function(){this.$router.push("/category/list")},getCategoryDetail:function(t){var a=this;return this.loading=!0,this.$http.post(this.$api.category_detail,{cateid:t}).then(function(t){s()(a.formData).forEach(function(e){a.formData[e]=t.data.data[e]});var e=t.data.data.parentid;0==e?a.parentData={id:0,catename:"根级分类"}:a.$http.post(a.$api.category_detail,{cateid:e}).then(function(t){a.parentData=t.data.data}).catch(function(t){})}).catch(function(t){}).then(function(){a.loading=!1})}},components:{"single-uploader":e("dc86").a},mounted:function(){this.$sitemap.prvname="商品分类",this.$sitemap.currname="编辑分类",this.getCategoryDetail(this.$route.query.cateid)}},n={render:function(){var t=this,a=t.$createElement,e=t._self._c||a;return e("div",{staticStyle:{position:"relative",padding:"20px"}},[e("Spin",{directives:[{name:"show",rawName:"v-show",value:t.loading,expression:"loading"}],attrs:{fix:""}},[e("Icon",{staticClass:"demo-spin-icon-load",attrs:{type:"load-c",size:"18"}}),t._v(" "),e("div",[t._v("正在获取数据...")])],1),t._v(" "),e("Form",{ref:"cateDetial",attrs:{model:t.formData,rules:t.rules,"label-position":"left","label-width":120}},[e("FormItem",{attrs:{label:"父级分类：",prop:"parentid"}},[e("Input",{attrs:{disabled:!0},model:{value:t.parentData.catename,callback:function(a){t.$set(t.parentData,"catename",a)},expression:"parentData.catename"}})],1),t._v(" "),e("FormItem",{attrs:{label:"分类名称：",prop:"catename"}},[e("Input",{attrs:{placeholder:"请输入分类名称"},model:{value:t.formData.catename,callback:function(a){t.$set(t.formData,"catename",a)},expression:"formData.catename"}})],1),t._v(" "),e("FormItem",{attrs:{label:"显示顺序：",prop:"sortvalue"}},[e("Row",[e("Col",{attrs:{span:"4"}},[e("InputNumber",{attrs:{min:0},model:{value:t.formData.sortvalue,callback:function(a){t.$set(t.formData,"sortvalue",a)},expression:"formData.sortvalue"}})],1),t._v(" "),e("Col",{attrs:{span:"10"}},[e("span",{staticStyle:{color:"silver"}},[t._v("数值越大，在父级分类中的顺序越靠前")])])],1)],1),t._v(" "),e("FormItem",{attrs:{label:"分类图片：",prop:"catepic"}},[e("single-uploader",{attrs:{image:t.formData.catepic},on:{change:t.handleImgChange}})],1),t._v(" "),e("FormItem",{attrs:{label:"首页推荐",prop:"isrecommend"}},[e("i-Switch",{attrs:{size:"large","true-value":1,"false-value":0},model:{value:t.formData.isrecommend,callback:function(a){t.$set(t.formData,"isrecommend",a)},expression:"formData.isrecommend"}},[e("span",{attrs:{slot:"open"},slot:"open"},[t._v("是")]),t._v(" "),e("span",{attrs:{slot:"close"},slot:"close"},[t._v("否")])])],1),t._v(" "),e("FormItem",{attrs:{label:"是否显示",prop:"ishidden"}},[e("Row",[e("Col",{attrs:{span:6}},[e("i-Switch",{attrs:{size:"large","true-value":0,"false-value":1},model:{value:t.formData.ishidden,callback:function(a){t.$set(t.formData,"ishidden",a)},expression:"formData.ishidden"}},[e("span",{attrs:{slot:"open"},slot:"open"},[t._v("是")]),t._v(" "),e("span",{attrs:{slot:"close"},slot:"close"},[t._v("否")])])],1),t._v(" "),e("Col",{attrs:{span:18}},[e("span",{staticStyle:{color:"#ccc"}},[t._v("用于控制这个分类在小程序端的显示与否，请慎重选择")])])],1)],1),t._v(" "),e("FormItem",[e("Button",{staticStyle:{width:"100px"},attrs:{type:"primary",size:"large"},on:{click:function(a){t.handleEdit("cateDetial")}}},[t._v("保存")]),t._v(" "),e("Button",{staticStyle:{"margin-left":"8px",width:"80px"},attrs:{type:"ghost",size:"large"},on:{click:t.handleReset}},[t._v("取消")])],1)],1)],1)},staticRenderFns:[]};var i=e("VU/8")(o,n,!1,function(t){e("ui61")},null,null);a.default=i.exports},ui61:function(t,a){}});
//# sourceMappingURL=11.f1329c1441f7d216a846.js.map