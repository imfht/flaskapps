webpackJsonp([26],{QN4Y:function(t,i,a){"use strict";Object.defineProperty(i,"__esModule",{value:!0});var e={name:"repair-detail",data:function(){return{repairid:"",item:"",piclist:"",img:"",visible:!1,viewSrc:""}},mounted:function(){var t=this,i=this.$route.query.repairid||"";this.repairid=i,this.$http.post(this.$api.repair_get,{repairid:i}).then(function(i){if(1==i.data.result&&i.data.data){t.item=i.data.data,t.piclist=i.data.data.faultimg;var a=t.piclist.split(",");t.img=a}else t.$Message.error(i.data.msg)})},methods:{handleView:function(t){this.viewSrc=t,this.visible=!0}}},s={render:function(){var t=this,i=t.$createElement,a=t._self._c||i;return a("div",[a("div",{staticClass:"all"},[a("div",[t._v("维修人姓名：")]),t._v(" "),a("div",[t._v(t._s(t.item.realname))])]),t._v(" "),a("div",{staticClass:"all"},[a("div",[t._v("维修人手机：")]),t._v(" "),a("div",[t._v(t._s(t.item.telphone))])]),t._v(" "),1==t.item.repairtype?a("div",{staticClass:"all"},[a("div",[t._v("故障类型：")]),t._v(" "),a("div",{staticStyle:{"margin-left":"54px"}},[t._v("手机")])]):t._e(),t._v(" "),1==t.item.repairtype?a("div",{staticClass:"all"},[a("div",[t._v("手机型号：")]),t._v(" "),a("div",{staticStyle:{"margin-left":"54px"}},[t._v(t._s(t.item.brand))])]):t._e(),t._v(" "),2==t.item.repairtype?a("div",{staticClass:"all"},[a("div",[t._v("故障类型：")]),t._v(" "),a("div",{staticStyle:{"margin-left":"54px"}},[t._v("电脑")])]):t._e(),t._v(" "),3==t.item.repairtype?a("div",{staticClass:"all"},[a("div",[t._v("故障类型：")]),t._v(" "),a("div",{staticStyle:{"margin-left":"54px"}},[t._v("宽带")])]):t._e(),t._v(" "),a("div",{staticClass:"all"},[a("div",[t._v("故障说明：")]),t._v(" "),a("div",{staticStyle:{"margin-left":"54px"}},[t._v(t._s(t.item.malfunction))])]),t._v(" "),a("div",{staticClass:"all"},[a("div",{staticClass:"title"},[t._v("故障图片：")]),t._v(" "),a("div",{staticClass:"main",staticStyle:{"margin-left":"-20px"}},t._l(t.img,function(i,e){return a("div",{staticClass:"upload-list"},[a("img",{attrs:{src:i,alt:""}}),t._v(" "),a("div",{staticClass:"action-cover"},[a("dir",{staticClass:"action-cover"},[a("Icon",{staticClass:"ico",attrs:{type:"ios-eye-outline",title:"查看大图"},nativeOn:{click:function(a){t.handleView(i)}}})],1)],1)])}))]),t._v(" "),a("Modal",{attrs:{title:"预览"},model:{value:t.visible,callback:function(i){t.visible=i},expression:"visible"}},[t.viewSrc?a("img",{staticStyle:{width:"100%"},attrs:{src:t.viewSrc}}):t._e()])],1)},staticRenderFns:[]};var l=a("VU/8")(e,s,!1,function(t){a("UaMU")},null,null);i.default=l.exports},UaMU:function(t,i){}});
//# sourceMappingURL=26.53565abeda8c2e5e9d65.js.map