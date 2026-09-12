/* AEGIS next-generation geospatial + track intelligence layer. */
const AEGIS_GEO_URL='https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json';
const aegisHistory=new Map();
let aegisGeo=null;
let aegisIntel=null;
let aegisGeoReady=false;

function aegisRememberTracks(payload){
  const now=Date.now();
  [...(payload.aircraft||[]),...(payload.vessels||[])].forEach(t=>{
    const id=t.id||t.callsign||t.name;
    if(!id||!Number.isFinite(Number(t.lat))||!Number.isFinite(Number(t.lon)))return;
    const h=aegisHistory.get(id)||[];
    const last=h[h.length-1];
    if(!last||now-last.time>3500||Math.abs(last.lat-Number(t.lat))>0.00005||Math.abs(last.lon-Number(t.lon))>0.00005){
      h.push({lat:Number(t.lat),lon:Number(t.lon),time:now});
      while(h.length>36)h.shift();
      aegisHistory.set(id,h);
    }
  });
}

function aegisEnsureIntel(){
  if(aegisIntel)return aegisIntel;
  aegisIntel=document.createElement('aside');
  aegisIntel.id='aegisIntelDrawer';
  aegisIntel.innerHTML='<div class="aid-head"><span>TRACK INTELLIGENCE</span><button id="aidClose" aria-label="Close">×</button></div><div id="aidBody"><div class="aid-muted">SELECT A TRACK TO OPEN INTELLIGENCE</div></div>';
  Object.assign(aegisIntel.style,{position:'fixed',top:'78px',right:'18px',width:'320px',maxWidth:'calc(100vw - 36px)',zIndex:'50',padding:'0',background:'rgba(3,10,7,.96)',border:'1px solid rgba(99,255,155,.35)',boxShadow:'0 20px 70px rgba(0,0,0,.55),0 0 35px rgba(99,255,155,.08)',backdropFilter:'blur(14px)',transform:'translateX(115%)',transition:'transform .25s ease',fontFamily:'ui-monospace, SFMono-Regular, Menlo, monospace',color:'#d8f5e3'});
  document.body.appendChild(aegisIntel);
  const style=document.createElement('style');
  style.textContent=`#aegisIntelDrawer.open{transform:translateX(0)}#aegisIntelDrawer .aid-head{display:flex;justify-content:space-between;align-items:center;padding:14px 16px;border-bottom:1px solid rgba(99,255,155,.18);font-size:11px;letter-spacing:.14em;color:#63ff9b}#aegisIntelDrawer #aidClose{background:none;border:0;color:#8bb49a;font-size:24px;cursor:pointer}#aegisIntelDrawer #aidBody{padding:16px}.aid-title{font-size:20px;color:#fff;margin-bottom:4px}.aid-type{display:inline-block;font-size:10px;padding:4px 7px;border:1px solid rgba(84,231,255,.35);color:#54e7ff;margin-bottom:14px}.aid-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.aid-cell{padding:9px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.05)}.aid-cell span{display:block;font-size:9px;color:#6f927e;letter-spacing:.1em;margin-bottom:4px}.aid-cell b{font-size:12px;color:#dff7e8}.aid-source{margin-top:12px;font-size:10px;color:#89a998}.aid-history{margin-top:15px;height:4px;background:rgba(99,255,155,.08);position:relative}.aid-history i{display:block;height:100%;background:#63ff9b;box-shadow:0 0 10px #63ff9b}.aid-muted{font-size:11px;color:#6f927e;line-height:1.6}@media(max-width:700px){#aegisIntelDrawer{top:64px!important;right:10px!important;width:calc(100vw - 20px)!important}}`;
  document.head.appendChild(style);
  document.getElementById('aidClose').onclick=()=>aegisIntel.classList.remove('open');
  return aegisIntel;
}

function aegisOpenIntel(t){
  const drawer=aegisEnsureIntel();
  if(!t){drawer.classList.remove('open');return;}
  const id=t.id||t.callsign||t.name||'UNKNOWN';
  const h=aegisHistory.get(id)||[];
  const body=document.getElementById('aidBody');
  body.innerHTML=`<div class="aid-title">${esc(t.callsign||t.name||t.id||'UNKNOWN')}</div><div class="aid-type">${esc((t.type||'TRACK').toUpperCase())}</div><div class="aid-grid"><div class="aid-cell"><span>LATITUDE</span><b>${Number(t.lat).toFixed(5)}°</b></div><div class="aid-cell"><span>LONGITUDE</span><b>${Number(t.lon).toFixed(5)}°</b></div><div class="aid-cell"><span>ALTITUDE</span><b>${Number(t.altitude_ft||0).toLocaleString()} FT</b></div><div class="aid-cell"><span>SPEED</span><b>${t.speed_kt??0} KT</b></div><div class="aid-cell"><span>HEADING</span><b>${t.heading??0}°</b></div><div class="aid-cell"><span>TRACK ID</span><b>${esc(id)}</b></div></div><div class="aid-source">SOURCE: ${esc(t.source||'UNKNOWN')} · UPDATED: ${esc(t.updated||new Date().toISOString())}</div><div class="aid-history" title="${h.length} recorded positions"><i style="width:${Math.min(100,Math.max(4,h.length/36*100))}%"></i></div><div class="aid-source">TRACK HISTORY: ${h.length} POSITION${h.length===1?'':'S'} RECORDED</div>`;
  drawer.classList.add('open');
}

async function aegisLoadGeo(){
  if(aegisGeoReady)return;
  try{const r=await fetch(AEGIS_GEO_URL);if(!r.ok)throw Error(r.status);aegisGeo=await r.json();aegisGeoReady=true;toast('Geographic layer online');aegisDrawOverlay();}catch(e){aegisGeoReady=true;console.warn('Aegis geographic layer unavailable',e)}
}

function aegisSvg(){
  const map=document.getElementById('map');if(!map)return null;
  let svg=document.getElementById('aegisGeoOverlay');
  if(!svg){svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.id='aegisGeoOverlay';Object.assign(svg.style,{position:'absolute',inset:'0',width:'100%',height:'100%',pointerEvents:'none',zIndex:'2'});map.appendChild(svg)}
  return svg;
}
function aegisGeoPath(coords,w,h){
  let d='',pen=false;
  coords.forEach(q=>{const p=project(Number(q[1]),Number(q[0]),w,h);if(p.z<-.12){pen=true;return}d+=(pen||!d?'M':'L')+p.x.toFixed(1)+' '+p.y.toFixed(1);pen=false});
  return d;
}
function aegisDrawGeo(svg,w,h){
  if(!aegisGeo?.features)return;
  const frag=document.createDocumentFragment();
  aegisGeo.features.forEach(f=>{
    const g=f.geometry;if(!g)return;
    const polys=g.type==='Polygon'?[g.coordinates]:g.type==='MultiPolygon'?g.coordinates:[];
    polys.forEach(poly=>poly.forEach(ring=>{const p=document.createElementNS('http://www.w3.org/2000/svg','path');p.setAttribute('d',aegisGeoPath(ring,w,h));p.setAttribute('fill','rgba(99,255,155,.045)');p.setAttribute('stroke','rgba(99,255,155,.28)');p.setAttribute('stroke-width','0.7');frag.appendChild(p)}));
  });
  svg.appendChild(frag);
}
function aegisDrawTrails(svg,w,h){
  aegisHistory.forEach((history,id)=>{
    if(history.length<2)return;
    const points=history.map(x=>project(x.lat,x.lon,w,h)).filter(p=>p.visible);
    if(points.length<2)return;
    const p=document.createElementNS('http://www.w3.org/2000/svg','path');
    p.setAttribute('d',points.map((x,i)=>(i?'L':'M')+x.x.toFixed(1)+' '+x.y.toFixed(1)).join(' '));
    const t=[...(latestTracks.aircraft||[]),...(latestTracks.vessels||[])].find(x=>(x.id||x.callsign||x.name)===id);
    p.setAttribute('fill','none');p.setAttribute('stroke',t?.type==='aircraft'?'#54e7ff':'#ffc65c');p.setAttribute('stroke-width','1.2');p.setAttribute('stroke-opacity','.48');p.setAttribute('stroke-dasharray','3 4');
    svg.appendChild(p);
  });
}
function aegisDrawOverlay(){
  const svg=aegisSvg();if(!svg)return;
  const r=document.getElementById('globeCanvas')?.getBoundingClientRect();if(!r)return;
  svg.setAttribute('viewBox',`0 0 ${r.width} ${r.height}`);svg.innerHTML='';aegisDrawGeo(svg,r.width,r.height);aegisDrawTrails(svg,r.width,r.height);
}

const aegisBaseRenderTracks=window.renderTracks;
window.renderTracks=function(payload){
  aegisRememberTracks(payload);
  aegisBaseRenderTracks(payload);
  aegisDrawOverlay();
  if(selectedTrack)aegisOpenIntel(selectedTrack);
};
const aegisBaseShowIntel=window.showTrackIntel;
window.showTrackIntel=function(t){aegisBaseShowIntel(t);aegisOpenIntel(t)};
const aegisBaseDrawAll=window.drawAllMaps;
window.drawAllMaps=function(){aegisBaseDrawAll();aegisDrawOverlay()};

/* Start over Türkiye / Europe for the first operator view. */
globe.yaw=35*Math.PI/180;globe.pitch=.08;globe.zoom=1.08;
aegisEnsureIntel();
aegisLoadGeo();
window.addEventListener('resize',aegisDrawOverlay);
