/* MIPL v2 — light 3D touches (Three.js r147, classic build). Lazy-loaded, paused offscreen, static fallback on reduced motion / no WebGL. */
(function(){
'use strict';
var d=document,W=window,S=W.__3d={status:'idle',logo:false,particles:false,frames:{}};
var RM=W.matchMedia('(prefers-reduced-motion: reduce)').matches;
var MOB=W.innerWidth<=900||!W.matchMedia('(hover: hover)').matches;
var me=d.currentScript, VEN=(me&&me.getAttribute('data-vendor'))||'assets/vendor/';
var els=[].slice.call(d.querySelectorAll('[data-3d]')); if(!els.length)return;
function webgl(){try{var c=d.createElement('canvas');return !!(W.WebGLRenderingContext&&(c.getContext('webgl2')||c.getContext('webgl')))}catch(e){return false}}
if(RM||!webgl()){S.status=RM?'fallback-reduced-motion':'fallback-no-webgl';return}
var loading=null;
function load(src){return new Promise(function(res,rej){var s=d.createElement('script');s.src=VEN+src;s.onload=res;s.onerror=rej;d.head.appendChild(s)})}
function three(){ if(!loading){S.status='loading'; loading=load('three.min.js').then(function(){return load('SVGLoader.js')}).then(function(){S.status='loaded'})} return loading }
var mouse={x:0,y:0}; W.addEventListener('pointermove',function(e){mouse.x=e.clientX/innerWidth*2-1;mouse.y=e.clientY/innerHeight*2-1},{passive:true});

function scene(el,name,setup){
  var THREE=W.THREE, r=new THREE.WebGLRenderer({antialias:!MOB,alpha:true,powerPreference:'low-power'});
  r.setPixelRatio(Math.min(W.devicePixelRatio||1,MOB?1.25:1.75)); el.appendChild(r.domElement); r.domElement.setAttribute('aria-hidden','true');
  var sc=new THREE.Scene(), cam=new THREE.PerspectiveCamera(35,1,1,5000), tick=setup(THREE,sc,cam,r);
  function size(){var w=el.clientWidth||1,h=el.clientHeight||1;r.setSize(w,h,false);cam.aspect=w/h;cam.updateProjectionMatrix()}
  size(); if(W.ResizeObserver) new ResizeObserver(size).observe(el); else W.addEventListener('resize',size);
  var on=false,raf=0,t0=performance.now(); S.frames[name]=0;
  function loop(now){ if(!on)return; tick((now-t0)/1000); r.render(sc,cam); S.frames[name]++; raf=requestAnimationFrame(loop) }
  function set(v){ if(v===on)return; on=v; S[name+'Running']=v; if(v)raf=requestAnimationFrame(loop); else cancelAnimationFrame(raf) }
  var vis=false; new IntersectionObserver(function(en){vis=en[0].isIntersecting;set(vis&&!d.hidden)},{rootMargin:'100px'}).observe(el);
  d.addEventListener('visibilitychange',function(){set(vis&&!d.hidden)});
  r.render(sc,cam);
}

function logo(el){
  scene(el,'logo',function(THREE,sc,cam){
    var src=d.querySelector('.nav .mlogo')||d.querySelector('.mlogo'); var vb=src.getAttribute('viewBox');
    var col={bp:'#5843CB',bar:'#5843CB',stem:'#DD2A1B',dot:'#DD2A1B'}, parts='';
    [].forEach.call(src.querySelectorAll('path'),function(p){ var c=p.getAttribute('class')||(p.parentNode.getAttribute('class'))||'stem'; parts+='<path fill="'+(col[c]||'#DD2A1B')+'" d="'+p.getAttribute('d')+'"/>' });
    var data=new THREE.SVGLoader().parse('<svg xmlns="http://www.w3.org/2000/svg" viewBox="'+vb+'">'+parts+'</svg>');
    var g=new THREE.Group(), mats={};
    data.paths.forEach(function(path){ var hex=path.color.getHexString(); var m=mats[hex]||(mats[hex]=new THREE.MeshStandardMaterial({color:path.color,metalness:.35,roughness:.32,side:THREE.DoubleSide}));
      THREE.SVGLoader.createShapes(path).forEach(function(sh){ var geo=new THREE.ExtrudeGeometry(sh,{depth:34,bevelEnabled:true,bevelThickness:4,bevelSize:2.5,bevelSegments:MOB?1:3,curveSegments:MOB?6:12}); g.add(new THREE.Mesh(geo,m)) }) });
    g.scale.y=-1; var box=new THREE.Box3().setFromObject(g), c=box.getCenter(new THREE.Vector3()); g.children.forEach(function(m){m.position.sub(new THREE.Vector3(c.x,-c.y,c.z))});
    var piv=new THREE.Group(); piv.add(g); sc.add(piv);
    var sz=box.getSize(new THREE.Vector3()); cam.position.set(0,0,Math.max(sz.x,sz.y)*2.15); cam.lookAt(0,0,0);
    sc.add(new THREE.AmbientLight(0xffffff,.55)); var k=new THREE.DirectionalLight(0xffffff,1.1); k.position.set(300,400,600); sc.add(k);
    var rim=new THREE.PointLight(0xdd2a1b,1.4,2400); rim.position.set(-500,-200,300); sc.add(rim); var fill=new THREE.PointLight(0x7f6bff,.9,2400); fill.position.set(500,200,-300); sc.add(fill);
    el.classList.add('ready'); S.logo=true; var ry=0,rx=0;
    return function(t){ var ty=(MOB?Math.sin(t*.6)*.5:mouse.x*.65)+Math.sin(t*.4)*.18, tx=(MOB?0:mouse.y*.35)+Math.sin(t*.7)*.05; ry+=(ty-ry)*.06; rx+=(tx-rx)*.06; piv.rotation.set(rx,ry,0); piv.position.y=Math.sin(t*1.1)*6 };
  });
}
function particles(el){
  scene(el,'particles',function(THREE,sc,cam){
    var nx=MOB?60:120,nz=MOB?30:60,sp=14,pos=new Float32Array(nx*nz*3),i=0;
    for(var x=0;x<nx;x++)for(var z=0;z<nz;z++){pos[i++]=(x-nx/2)*sp;pos[i++]=0;pos[i++]=(z-nz/2)*sp}
    var geo=new THREE.BufferGeometry(); geo.setAttribute('position',new THREE.BufferAttribute(pos,3));
    var mat=new THREE.ShaderMaterial({transparent:true,depthWrite:false,uniforms:{t:{value:0},m:{value:new THREE.Vector2()}},
      vertexShader:'uniform float t;uniform vec2 m;varying float a;void main(){vec3 p=position;float w=sin(p.x*.018+t*.9)*cos(p.z*.022+t*.7);float r=length(p.xz-vec2(m.x*400.,m.y*200.));p.y=w*28.+exp(-r*r/40000.)*40.;a=.35+.65*(w*.5+.5);vec4 mv=modelViewMatrix*vec4(p,1.);gl_PointSize=2.6*(600./-mv.z);gl_Position=projectionMatrix*mv;}',
      fragmentShader:'varying float a;void main(){vec2 c=gl_PointCoord-.5;if(length(c)>.5)discard;gl_FragColor=vec4(0.95,0.94,1.,a*.75);}'});
    sc.add(new THREE.Points(geo,mat)); cam.position.set(0,260,620); cam.lookAt(0,0,-60); S.particles=true;
    return function(t){ mat.uniforms.t.value=t; mat.uniforms.m.value.set(mouse.x,mouse.y); cam.position.x+=((MOB?0:mouse.x*60)-cam.position.x)*.03 };
  });
}
var io=new IntersectionObserver(function(en){ en.forEach(function(e){ if(!e.isIntersecting)return; io.unobserve(e.target); var el=e.target;
  three().then(function(){ try{ el.getAttribute('data-3d')==='logo'?logo(el):particles(el); S.status='running' }catch(err){ S.status='error: '+err.message; console.warn('3D disabled:',err.message) } }).catch(function(){S.status='load-failed'}) }) },{rootMargin:'600px 0px'});
els.forEach(function(el){io.observe(el)});
})();
