webpackJsonp([39],{"6rdE":function(t,e,s){"use strict";Object.defineProperty(e,"__esModule",{value:!0});var n=s("mtWM"),r=s.n(n),a={name:"my-first-vue",data:function(){return{serverResponse:"resp"}},methods:{getData:function(){var t=this;r.a.get("http://127.0.0.1:5000/getMsg").then(function(e){var s=e.data.msg;t.serverResponse=s,alert("Success "+e.status+", "+e.data+", "+s)}).catch(function(t){alert("Error "+t)})}}},i={render:function(){var t=this.$createElement,e=this._self._c||t;return e("div",[e("span",[this._v(this._s(this.serverResponse)+" ")]),this._v(" "),e("button",{on:{click:this.getData}},[this._v("GET DATA")])])},staticRenderFns:[]},u=s("VU/8")(a,i,!1,null,null,null);e.default=u.exports}});
//# sourceMappingURL=39.3759028929d1b0961cd9.js.map