const $=i=>document.getElementById(i), RED="#e50914";
const st={q:"",g:"",y:"",page:1};
const qs=()=>new URLSearchParams({q:st.q,genre:st.g,year:st.y}).toString();
const api=async(p,x="")=>{const r=await fetch(`/api/${p}?${qs()}${x}`);if(!r.ok)throw new Error(r.status);return r.json()};
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

// animated counters
const cur={};
function count(id,to){const el=$(id);if(to==null||isNaN(to)){el.textContent="–";cur[id]=0;return}
 const from=cur[id]||0,t0=performance.now();cur[id]=to;
 (function f(t){const k=Math.min(1,(t-t0)/450),e=1-Math.pow(1-k,3);el.textContent=Math.round(from+(to-from)*e).toLocaleString();if(k<1)requestAnimationFrame(f)})(t0)}

// tooltip
const tip=$("tip");
document.addEventListener("mousemove",e=>{const t=e.target.closest("[data-tip]");
 if(!t){tip.style.opacity=0;return}tip.textContent=t.dataset.tip;tip.style.opacity=1;tip.style.left=e.clientX+14+"px";tip.style.top=e.clientY+14+"px"});

function donut(m,t){const tot=m+t;if(!tot)return'<svg viewBox="0 0 300 220"><text x="150" y="110" fill="#999" text-anchor="middle">No titles match</text></svg>';
 const C=2*Math.PI*70,p=m/tot,lab=(a,v)=>`<text x="${150+112*Math.cos(a)}" y="${114+112*Math.sin(a)}" fill="#fff" font-weight="700" font-size="14" text-anchor="${Math.cos(a)>0?"start":"end"}">${(v*100).toFixed(2)}%</text>`;
 let s=`<svg viewBox="0 0 300 220"><g transform="translate(150,110) rotate(-90)"><circle r="70" fill="none" stroke="#fff" stroke-width="36" data-tip="TV Shows: ${t.toLocaleString()}"/>`;
 if(p>0)s+=`<circle r="70" fill="none" stroke="${RED}" stroke-width="36" stroke-dasharray="${p*C} ${C}" data-tip="Movies: ${m.toLocaleString()}"/>`;
 s+="</g>";if(m)s+=lab(-Math.PI/2+p*Math.PI,p);if(t)s+=lab(-Math.PI/2+p*2*Math.PI+(1-p)*Math.PI,1-p);return s+"</svg>"}

function genres(rows){if(!rows.length)return'<svg viewBox="0 0 420 100"><text x="210" y="50" fill="#999" text-anchor="middle">No titles match</text></svg>';
 const mx=Math.max(...rows.map(r=>r.movies+r.tv)),sc=250/mx;let s=`<svg viewBox="0 0 420 ${rows.length*34+10}">`;
 rows.forEach((r,i)=>{const y=6+i*34,a=r.movies*sc,b=r.tv*sc;
  s+=`<text x="136" y="${y+19}" fill="#fff" font-size="12" text-anchor="end">${esc(r.genre)}</text><rect class="bar" x="144" y="${y}" width="${a}" height="26" fill="${RED}" data-tip="${esc(r.genre)} – Movies: ${r.movies}"/><rect class="bar" x="${144+a}" y="${y}" width="${b}" height="26" fill="#fff" data-tip="${esc(r.genre)} – TV Shows: ${r.tv}"/>`;
  if(r.movies)s+=`<text x="${144+a/2}" y="${y+18}" fill="#fff" font-size="12" text-anchor="middle" pointer-events="none">${r.movies}</text>`;
  if(r.tv)s+=`<text x="${144+a+b/2}" y="${y+18}" fill="#000" font-size="12" text-anchor="middle" pointer-events="none">${r.tv}</text>`});return s+"</svg>"}

function map(rows){let s='<svg viewBox="0 0 720 340" style="background:#1b1b1b">';
 for(let lo=-150;lo<=150;lo+=30)s+=`<line x1="${(lo+180)*2}" x2="${(lo+180)*2}" y1="0" y2="340" stroke="#2a2a2a"/>`;
 for(let la=-60;la<=75;la+=15)s+=`<line y1="${(90-la)*2-10}" y2="${(90-la)*2-10}" x1="0" x2="720" stroke="#2a2a2a"/>`;
 [["NORTH AMERICA",-100,52],["SOUTH AMERICA",-60,-22],["EUROPE",15,58],["AFRICA",20,5],["ASIA",90,55],["OCEANIA",135,-38]].forEach(([n,lo,la])=>s+=`<text x="${(lo+180)*2}" y="${(90-la)*2-10}" fill="#555" font-size="13" text-anchor="middle">${n}</text>`);
 rows.filter(r=>r.lat!=null).forEach(r=>s+=`<circle class="dot" cx="${(r.lon+180)*2}" cy="${(90-r.lat)*2-10}" r="${Math.min(30,3+Math.sqrt(r.n)*.95)}" fill="${RED}" fill-opacity=".65" stroke="#ff5a5a" stroke-opacity=".6" data-tip="${esc(r.country)}: ${r.n} titles"/>`);
 return s+"</svg>"}

function years(rows){const Y=[];for(let y=2010;y<=2021;y++)Y.push(y);const by=Object.fromEntries(rows.map(r=>[r.year,r]));
 const m=Y.map(y=>by[y]?.movies||0),t=Y.map(y=>by[y]?.tv||0),mx=Math.max(10,...m,...t),X=i=>40+i*(540/(Y.length-1)),H=v=>220-v/mx*180;
 const area=(a,f)=>{const p=a.map((v,i)=>`${X(i)},${H(v)}`).join(" ");return`<polygon points="${X(0)},220 ${p} ${X(a.length-1)},220" fill="${f}" fill-opacity=".35"/><polyline points="${p}" fill="none" stroke="${f}" stroke-width="3"/>`};
 let s='<svg viewBox="0 0 600 250"><line x1="40" x2="580" y1="220" y2="220" stroke="#444"/>'+area(m,RED)+area(t,"#fff");
 Y.forEach((y,i)=>{s+=`<text x="${X(i)}" y="240" fill="#bbb" font-size="11" text-anchor="middle">${y}</text><text x="${X(i)}" y="${H(m[i])-6}" fill="#fff" font-size="11" text-anchor="middle">${m[i]}</text>`;if(t[i])s+=`<text x="${X(i)}" y="${H(t[i])+14}" fill="#fff" font-size="11" text-anchor="middle">${t[i]}</text>`;
  s+=`<rect x="${X(i)-20}" y="30" width="40" height="190" fill="transparent" data-tip="${y}: ${m[i]} movies, ${t[i]} TV shows"/>`});return s+"</svg>"}

function table(d){$("count").textContent=`(${d.total.toLocaleString()} matches)`;
 $("rows").innerHTML=d.rows.length?d.rows.map(r=>`<tr><td>${esc(r.title)}</td><td><span class="badge ${r.type==="TV Show"?"tv":""}">${r.type}</span></td><td>${r.year}</td><td>${esc(r.rating)}</td><td>${esc(r.country)}</td><td>${esc(r.genre)}</td></tr>`).join(""):'<tr><td colspan="6" style="color:#999">No titles match these filters. Try clearing a filter.</td></tr>';
 $("pg").textContent=`Page ${d.page} of ${d.pages}`;$("prev").disabled=d.page<=1;$("next").disabled=d.page>=d.pages}

let seq=0;
async function load(){const my=++seq;document.querySelector(".grid").classList.add("loading");
 try{const [s,g,c,y,t]=await Promise.all([api("summary"),api("genres"),api("countries"),api("years"),api("titles",`&page=${st.page}`)]);
  if(my!==seq)return;
  count("k1",s.avg_runtime);count("k2",s.movies);count("k3",s.tv);count("k4",s.countries);
  $("donut").innerHTML=donut(s.movies,s.tv);$("genres").innerHTML=genres(g);$("map").innerHTML=map(c);$("years").innerHTML=years(y);table(t);
 }catch(e){$("status").className="bad";$("status").innerHTML="<i></i>API error – is the server running?"}
 document.querySelector(".grid").classList.remove("loading")}
const reload=(resetPage=true)=>{if(resetPage)st.page=1;load()};

async function init(){
 try{const h=await (await fetch("/api/health")).json();$("status").className="ok";$("status").innerHTML=`<i></i>API online · ${h.titles.toLocaleString()} titles in database`;
  const f=await (await fetch("/api/filters")).json();
  $("g").innerHTML='<option value="">All</option>'+f.genres.map(g=>`<option>${esc(g)}</option>`).join("");
  $("y").innerHTML='<option value="">All</option>'+f.years.map(y=>`<option>${y}</option>`).join("");
 }catch(e){$("status").className="bad";$("status").innerHTML="<i></i>API offline – run: python backend/app.py"}
 load()}
let deb;$("q").oninput=e=>{clearTimeout(deb);deb=setTimeout(()=>{st.q=e.target.value.trim();reload()},250)};
$("g").onchange=e=>{st.g=e.target.value;reload()};$("y").onchange=e=>{st.y=e.target.value;reload()};
$("prev").onclick=()=>{st.page--;reload(false)};$("next").onclick=()=>{st.page++;reload(false)};
$("reset").onclick=()=>{st.q=st.g=st.y="";st.page=1;$("q").value=$("g").value=$("y").value="";load()};
init();
