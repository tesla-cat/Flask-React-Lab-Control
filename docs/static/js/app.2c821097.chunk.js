(this.webpackJsonp=this.webpackJsonp||[]).push([[0],{197:function(e,t,n){"use strict";n.d(t,"a",(function(){return _}));var a=n(198),r=n(0),o=n.n(r),c=n(279),i=n(5),l=n.n(i),s=n(7),f=n.n(s),u=n(8),m=n.n(u),g=n(277),p=n(278),d=n(128);function b(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);t&&(a=a.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,a)}return n}function h(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?b(Object(n),!0).forEach((function(t){f()(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):b(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}var y=n(160),x=n(158),E=n(68),O=n(275),w=n(3),v=n(31),S=n(56),j=n(4);function T(e){var t=e.navigation;return r.createElement(j.a,{style:k.container},r.createElement(v.a,{style:k.title},"This screen doesn't exist."),r.createElement(S.a,{onPress:function(){return t.replace("Root")},style:k.link},r.createElement(v.a,{style:k.linkText},"Go to home screen!")))}var k=w.a.create({container:{flex:1,backgroundColor:"#fff",alignItems:"center",justifyContent:"center",padding:20},title:{fontSize:20,fontWeight:"bold"},link:{marginTop:15,paddingVertical:15},linkText:{fontSize:14,color:"#2e78b7"}}),I=n(22),z=n.n(I),C=n(276),D={light:{text:"#000",background:"#fff",tint:"#2f95dc",tabIconDefault:"#ccc",tabIconSelected:"#2f95dc"},dark:{text:"#fff",background:"#000",tint:"#fff",tabIconDefault:"#ccc",tabIconSelected:"#fff"}},P=n(58),L=n(187),N=n(188),H=n(26),B=n(123),A=(n(269),n(185)),R=n.n(A);B.a.initializeApp({apiKey:"AIzaSyDuNZv1DauGOJWmbemUzCkXajt5La0wN-A",authDomain:"qcrew2021.firebaseapp.com",projectId:"qcrew2021",storageBucket:"qcrew2021.appspot.com",messagingSenderId:"197393268910",appId:"1:197393268910:web:e9a8c373956c84b9ddad3f",measurementId:"G-80EYHZ0BF4"});var W=B.a.firestore().collection("data"),M=H.a.get("window"),V=M.width>M.height;function q(){var e=Object(r.useState)({}),t=m()(e,2),n=t[0],a=t[1];Object(r.useEffect)((function(){!function(e){W.doc("qcrew").onSnapshot((function(t){var n=t.data();n&&e(n)}))}(a)}),[]);var c=function(e){if(e.json)return JSON.parse(e.json)}(n);return c?o.a.createElement(P.a,{contentContainerStyle:{flexDirection:"row",flexWrap:"wrap",justifyContent:"center"}},c.ys.map((function(e,t){var n=c.xs[e.x];return o.a.createElement(F,{id:"fig"+t,x:n.x,y:e.y,xl:n.l,yl:e.l})}))):null}function F(e){var t=Object(r.useState)(!0),n=m()(t,2),a=n[0],c=n[1],i=Object(r.useState)(!1),l=m()(i,2),s=l[0],f=l[1];Object(r.useEffect)((function(){c(!1)}),[]);var u,g,p=[{x:e.x,y:s?(u=e.y,u.map((function(e){return Math.log10(e)}))):e.y}],d={family:"Courier New, monospace",size:18,color:"#7f7f7f"},b={xaxis:{title:{text:e.xl,font:d}},yaxis:{title:{text:e.yl,font:d}}};return o.a.createElement(j.a,{style:{width:V?"30%":"100%",margin:V?10:0}},o.a.createElement(j.a,{style:{flexDirection:"row",padding:10,alignItems:"center"}},o.a.createElement(v.a,{style:{flex:1,fontSize:20,fontWeight:"bold",marginLeft:10}},e.yl),o.a.createElement(v.a,{style:{flex:1,fontSize:20,fontWeight:"bold",marginLeft:10,color:"blue"}},(g=e.y)[g.length-1]),o.a.createElement(j.a,{style:{alignItems:"center",marginHorizontal:20}},o.a.createElement(L.a,{value:s,onValueChange:f}),o.a.createElement(v.a,null,"log10")),o.a.createElement(N.a,{title:a?"hide":"show",onPress:function(){c(!a)}})),o.a.createElement(j.a,{style:{flex:1,display:a?"flex":"none"}},o.a.createElement(R.a,{data:p,layout:b})))}n(200),n(9);w.a.create({container:{flex:1,backgroundColor:"#fff"},developmentModeText:{marginBottom:20,fontSize:14,lineHeight:19,textAlign:"center"},contentContainer:{paddingTop:30},welcomeContainer:{alignItems:"center",marginTop:10,marginBottom:20},welcomeImage:{width:100,height:80,resizeMode:"contain",marginTop:3,marginLeft:-10},getStartedContainer:{alignItems:"center",marginHorizontal:50},homeScreenFilename:{marginVertical:7},codeHighlightText:{color:"rgba(96,100,109, 0.8)"},codeHighlightContainer:{borderRadius:3,paddingHorizontal:4},getStartedText:{fontSize:17,lineHeight:24,textAlign:"center"},helpContainer:{marginTop:15,marginHorizontal:20,alignItems:"center"},helpLink:{paddingVertical:15},helpLinkText:{textAlign:"center"}});w.a.create({container:{flex:1,alignItems:"center",justifyContent:"center"},title:{fontSize:20,fontWeight:"bold"},separator:{marginVertical:30,height:1,width:"80%"}});var J=Object(C.a)();function G(){return r.createElement(J.Navigator,{initialRouteName:"TabOne",tabBarOptions:{activeTintColor:D.light.tint}},r.createElement(J.Screen,{name:"TabOne",component:Q,options:{tabBarIcon:function(e){var t=e.color;return r.createElement(Z,{name:"ios-code",color:t})}}}),null)}function Z(e){return r.createElement(g.a,z()({size:30,style:{marginBottom:-3}},e))}var K=Object(O.a)();function Q(){return r.createElement(K.Navigator,null,r.createElement(K.Screen,{name:"TabOneScreen",component:q,options:{headerTitle:"Qcrew Lab Monitor"}}))}Object(O.a)();var U={prefixes:[n(199).a("https://tesla-cat.github.io/LabTools")],config:{screens:{Root:{screens:{TabOne:{screens:{TabOneScreen:"LabTools"}},TabTwo:{screens:{TabTwoScreen:"LabTools/two"}}}},NotFound:"*"}}};function X(e){var t=e.colorScheme;return r.createElement(y.a,{linking:U,theme:"dark"===t?x.a:E.a},r.createElement($,null))}var Y=Object(O.a)();function $(){return r.createElement(Y.Navigator,{screenOptions:{headerShown:!1}},r.createElement(Y.Screen,{name:"Root",component:G}),r.createElement(Y.Screen,{name:"NotFound",component:T,options:{title:"Oops!"}}))}function _(){return function(){var e=r.useState(!1),t=m()(e,2),a=t[0],o=t[1];return r.useEffect((function(){l.a.async((function(e){for(;;)switch(e.prev=e.next){case 0:return e.prev=0,d.b(),e.next=4,l.a.awrap(p.b(h(h({},g.a.font),{},{"space-mono":n(226)})));case 4:e.next=9;break;case 6:e.prev=6,e.t0=e.catch(0),console.warn(e.t0);case 9:return e.prev=9,o(!0),d.a(),e.finish(9);case 13:case"end":return e.stop()}}),null,null,[[0,6,9,13]],Promise)}),[]),a}()?o.a.createElement(c.b,null,o.a.createElement(X,{colorScheme:"light"}),o.a.createElement(a.a,null)):null}},208:function(e,t,n){e.exports=n(268)},226:function(e,t,n){e.exports=n.p+"./fonts/SpaceMono-Regular.ttf"}},[[208,1,2]]]);
//# sourceMappingURL=app.2c821097.chunk.js.map