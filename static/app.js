const $=id=>document.getElementById(id);
const demos=["not vegetarian","veg","vegetarian","Burger","fast food in Noida","chicken pizza","non-veg","Paneer Tikka"];
$("chips").innerHTML=demos.map(d=>`<span class="chip" onclick="setQ('${d}')">${d}</span>`).join("");
function setQ(v){$("q").value=v;doSearch();}
function toast(m){const t=$("toast");t.textContent=m;t.style.display="block";setTimeout(()=>t.style.display="none",2200);}
function badge(veg){return veg.toLowerCase().includes("non")?`<span class="ftype nonveg">🔴 NON-VEG</span>`:`<span class="ftype veg">🟢 VEG</span>`;}
function card(p,s){return `<div class="card"><div class="rhead"><span class="rname">🍽️ ${p.restaurant||"-"}</span><span class="pid">pid ${p.pid}</span></div><div class="food">${p.food||""}</div>${badge(p.food_type||"")}<div class="kv">📍 <b>${p.location||"-"}</b> • ${p.landmark||"no landmark"} • ${p.pincode||""}</div><div class="kv">🗺️ Zone: <b>${p.zone||"-"}</b> • ☎️ ${p.phone||"-"}</div><div class="scorebar"><div class="scorefill" style="width:${Math.min(100,Math.round(s*100))}%"></div></div><div class="scoreRow"><span>score: <b style="color:#22d3ee">${s}</b></span><span>sheet ${p.sheet||"-"}</span></div></div>`;}
async function doSearch(){const q=$("q").value.trim();if(!q)return toast("Query likho pehle!");
const body={query:q,method:$("method").value,threshold:parseFloat($("thr").value||0.05),top_k:parseInt($("topk").value||5)};
$("resMeta").textContent="Searching...";
try{const r=await fetch("/api/search",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});const j=await r.json();
if(!r.ok)throw new Error(j.detail||"error");
$("timing").textContent=`⚡ ${j.time_ms} ms • ${j.method}`;
$("resMeta").textContent=`${j.count} result(s) for “${j.query}”`;
$("grid").innerHTML=j.results.length?j.results.map(x=>card(x.poi,x.score)).join(""):`<div class="empty">😕 No match — threshold kam karke try karo.</div>`;
}catch(e){toast("Error: "+e.message);}}
async function loadAll(){try{const r=await fetch("/api/pois");const j=await r.json();
$("countBadge").textContent=j.count+" POIs";$("resMeta").textContent=`All ${j.count} POIs`;
$("grid").innerHTML=j.pois.map(p=>card(p,1.0)).join("");
$("tbody").innerHTML=j.pois.map(p=>`<tr><td>${p.pid}</td><td>${p.restaurant}</td><td>${p.food}</td><td>${p.food_type}</td><td><button onclick="delPoi(${p.pid})" style="background:none;border:none;cursor:pointer">🗑️</button></td></tr>`).join("");
$("apiMeta").textContent="GET /api/pois • POST /api/search • /docs";}catch(e){toast(e.message);}}
async function addPoi(){const b={restaurant:$("f_rest").value,food:$("f_food").value,location:$("f_loc").value,food_type:$("f_ft").value||"veg",landmark:$("f_land").value,zone:$("f_zone").value,pincode:$("f_pin").value,phone:$("f_phone").value};
if(!b.restaurant||!b.food)return toast("Restaurant + Food required!");
const r=await fetch("/api/pois",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(b)});const j=await r.json();toast("Added pid "+j.poi.pid);loadAll();}
async function delPoi(pid){if(!confirm("Delete pid "+pid+"?"))return;await fetch("/api/pois/"+pid,{method:"DELETE"});loadAll();}
async function q2(q,m){const r=await fetch("/api/search",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query:q,method:m,threshold:0.0,top_k:20})});return r.json();}
async function compareVeg(){$("cmp").textContent="comparing...";const a=await q2("veg","keyword"),b=await q2("veg","semantic");
$("cmp").innerHTML=`Old keyword pids: <b>${a.results.map(x=>x.poi.pid).join(",")}</b> (bug: 2 included) <br/>Semantic pids: <b style="color:#4ade80">${b.results.map(x=>x.poi.pid).join(",")}</b> (correct)`;}
async function compareNonVeg(){$("cmp").textContent="comparing...";const a=await q2("not vegetarian","semantic"),b=await q2("not vegetarian","keyword");
$("cmp").innerHTML=`Semantic pids: <b style="color:#4ade80">${a.results.map(x=>x.poi.pid).join(",")||"none"}</b> <br/>Old keyword pids: <b>${b.results.map(x=>x.poi.pid).join(",")||"none"}</b> (fails!)`;}
document.getElementById("q").addEventListener("keydown",e=>{if(e.key==="Enter")doSearch();});
loadAll();doSearch();
