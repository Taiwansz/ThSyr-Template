"""3D holographic brain renderer for the ThSyr knowledge graph."""

from __future__ import annotations

import json
import math
import webbrowser
from pathlib import Path
from typing import Any

from .config import settings
from .knowledge_ingestor import extract_ecosystem_graph
from .readme_stats import update_readme_graph_stats

THREE_D_OUTPUT = settings.brain.brain_dir / "neural_canvas_3d.html"

LOBE_LAYOUT = {
    "regra": ((0, 0, 0), "#ffb52e"),
    "tech": ((0, 0, 0), "#ffd66b"),
    "sessao": ((0, 0, 0), "#e58b20"),
    "design": ((0, 0, 0), "#ffc04d"),
    "limbico": ((0, 0, 0), "#ff8b1f"),
    "cortex": ((0, 0, 0), "#ffe29a"),
    "analitica": ((0, 0, 0), "#f6a928"),
    "projeto": ((0, 0, 0), "#ffca57"),
    "conceito": ((0, 0, 0), "#d88a1c"),
    "operador": ((0, 0, 0), "#fff0bd"),
}


def _coordinates(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for global_index, node in enumerate(nodes):
        group = str(node.get("group", "conceito"))
        center, color = LOBE_LAYOUT.get(group, LOBE_LAYOUT["conceito"])
        workspace = str(node.get("workspace", "brain"))
        depth = int(node.get("depth", 0))
        fraction = (global_index + 0.5) / max(len(nodes), 1)
        longitude = global_index * 2.3999632297
        latitude = math.acos(1 - 2 * fraction)
        direction = (
            math.sin(latitude) * math.cos(longitude),
            math.cos(latitude),
            math.sin(latitude) * math.sin(longitude),
        )
        if node.get("kind") == "project":
            radius = 1.25 + (global_index % 7) * 0.12
        elif node.get("kind") == "directory":
            radius = 2.15 + min(depth, 4) * 0.48
        elif workspace == "brain":
            radius = 3.05 + min(depth, 4) * 0.4
        else:
            radius = 4.15 + min(depth, 4) * 0.48
        radius += ((global_index % 5) - 2) * 0.06
        result.append(
            {
                **node,
                "x": direction[0] * radius,
                "y": direction[1] * radius,
                "z": direction[2] * radius,
                "color": color,
                "lobe": group,
            }
        )
    return result


HTML_TEMPLATE = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ThSyr // Holographic Neural Brain</title>
<style>
*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:radial-gradient(circle at 53% 50%,#241808 0%,#080b10 32%,#03070d 72%);color:#dce8f5;font:12px "Geist","Segoe UI",sans-serif}
#scene{position:fixed;inset:0}#hud{position:fixed;inset:24px;pointer-events:none;display:flex;justify-content:space-between}
.panel{pointer-events:auto;background:rgba(3,12,22,.58);border:1px solid rgba(111,224,255,.22);border-radius:16px;padding:15px;backdrop-filter:blur(18px);box-shadow:0 0 45px rgba(0,155,210,.08),inset 0 1px 0 rgba(190,245,255,.08)}
.eyebrow{font-size:10px;letter-spacing:.22em;color:#73d8ff;text-transform:uppercase}.title{font-size:18px;letter-spacing:.08em;margin:8px 0 14px}.metric{display:flex;justify-content:space-between;gap:28px;margin-top:8px;color:#7f94aa}.metric b{color:#eef7ff;font-weight:500}
#inspector{min-width:220px;align-self:flex-start;opacity:0;transform:translateY(-8px);transition:opacity .55s cubic-bezier(.32,.72,0,1),transform .55s cubic-bezier(.32,.72,0,1)}
#inspector.visible{opacity:1;transform:translateY(0)}#status{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);color:#6e8296;letter-spacing:.16em;font-size:10px}
#tools{position:fixed;left:24px;bottom:24px;width:250px}#tools input{width:100%;background:rgba(3,12,22,.7);border:1px solid rgba(111,224,255,.22);border-radius:10px;color:#eef7ff;padding:9px 11px;outline:none}#tools input:focus{border-color:#73d8ff}.filters{display:flex;flex-wrap:wrap;gap:5px;margin-top:8px}.filters button{padding:5px 8px;font-size:9px}.filters button.active{background:rgba(255,181,46,.2);border-color:#ffb52e;color:#ffe09a}.events{margin-top:10px;max-height:90px;overflow:auto;color:#91a6b8;font-size:10px;line-height:1.5}.events div{border-top:1px solid rgba(145,210,255,.1);padding:4px 0}.connections{margin-top:10px;color:#91a6b8;font-size:10px;line-height:1.5;max-width:220px}
button{background:rgba(77,205,235,.08);border:1px solid rgba(115,216,255,.35);color:#dce8f5;border-radius:99px;padding:8px 13px;cursor:pointer;letter-spacing:.08em;text-transform:uppercase;font-size:10px}
button:hover{background:rgba(77,205,235,.16);border-color:#73d8ff;color:#73d8ff}
</style>
</head>
<body><div id="scene"></div><div id="hud">
<section class="panel"><div class="eyebrow">ThSyr // cognitive core</div><div class="title">HOLOGRAPHIC CORE</div>
<div class="metric"><span>nodes</span><b id="nodes">0</b></div><div class="metric"><span>synapses</span><b id="links">0</b></div>
<div class="metric"><span>runtime</span><b id="runtime-status">OFFLINE</b></div><div class="metric"><span>events</span><b id="event-count">0</b></div><br><button id="reset">recenter</button></section>
<section id="inspector" class="panel"><div class="eyebrow">selected node</div><div class="title" id="node-name">—</div><div class="metric"><span>kind</span><b id="node-kind">—</b></div><div class="metric"><span>parent</span><b id="node-parent">—</b></div><div class="metric"><span>path</span><b id="node-path">—</b></div><div class="connections" id="connections">Select a node to inspect connections.</div></section>
</div><section id="tools" class="panel"><div class="eyebrow">cortex controls</div><input id="search" placeholder="Search nodes..." autocomplete="off"><div class="filters" id="filters"></div><div class="events" id="events">No runtime events received.</div></section><div id="status">COGNITIVE REACTOR // WAITING FOR RUNTIME TELEMETRY</div>
<script src="../assets/three.min.js"></script>
<script src="../assets/OrbitControls.js"></script>
<script>
const GRAPH=__GRAPH_JSON__, scene=new THREE.Scene(), camera=new THREE.PerspectiveCamera(45,innerWidth/innerHeight,.1,100);
camera.position.set(0,.25,24);const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(innerWidth,innerHeight);renderer.setClearColor(0x03070d,1);document.getElementById("scene").appendChild(renderer.domElement);
const controls=new THREE.OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.06;controls.minDistance=8;controls.maxDistance=48;controls.target.set(0,0,.35);
const root=new THREE.Group();root.rotation.set(.04,-.18,0);const nodes=new Map();scene.add(root);
scene.add(new THREE.AmbientLight(0x8ccfe5,.5));const keyLight=new THREE.PointLight(0x38d8ff,3.5,22);keyLight.position.set(2,3,7);scene.add(keyLight);
const gold=0xffb52e,hot=0xffe09a;
const lobeColors={},nodeById={},edges=[];GRAPH.nodes=GRAPH.nodes.map(n=>{nodeById[n.id]=n;return n});
GRAPH.nodes.forEach(n=>{lobeColors[n.group]=n.color||"#8ba3bb";const size=.022+Math.min(n.degree||0,18)*.0038;const geo=new THREE.SphereGeometry(size,n.is_hub?12:7,n.is_hub?9:5);const mat=new THREE.MeshBasicMaterial({color:n.color||"#8ba3bb"});const mesh=new THREE.Mesh(geo,mat);mesh.position.set(n.x,n.y,n.z);mesh.userData={...n,baseColor:n.color||"#8ba3bb"};root.add(mesh);nodes.set(n.id,mesh)});
GRAPH.links.forEach(l=>{const a=nodes.get(l.source),b=nodes.get(l.target);if(!a||!b)return;const geo=new THREE.BufferGeometry().setFromPoints([a.position,b.position]);const line=new THREE.Line(geo,new THREE.LineBasicMaterial({color:0xffb52e,transparent:true,opacity:.045}));line.userData={a,b,source:l.source,target:l.target};root.add(line);edges.push(line)});
document.getElementById("nodes").textContent=GRAPH.nodes.length;document.getElementById("links").textContent=GRAPH.links.length;
const ray=new THREE.Raycaster(),pointer=new THREE.Vector2();let selected=null,activeLobe="all",query="";
function inspect(n){selected=n;document.getElementById("node-name").textContent=n.label;document.getElementById("node-kind").textContent=n.kind||n.lobe||"semantic";document.getElementById("node-parent").textContent=n.parent_id||n.workspace||"root";document.getElementById("node-path").textContent=n.path||"inferred link target";const linked=GRAPH.links.filter(l=>l.source===n.id||l.target===n.id).map(l=>l.source===n.id?l.target:l.source).slice(0,12);document.getElementById("connections").textContent=linked.length?`connections: ${linked.join(", ")}`:"No recorded connections.";document.getElementById("inspector").classList.add("visible")}
renderer.domElement.addEventListener("click",e=>{pointer.x=e.clientX/innerWidth*2-1;pointer.y=-(e.clientY/innerHeight)*2+1;ray.setFromCamera(pointer,camera);const hit=ray.intersectObjects([...nodes.values()])[0];if(hit)inspect(hit.object.userData)});
function applyFilters(){nodes.forEach(mesh=>{const n=mesh.userData;const visible=(activeLobe==="all"||n.group===activeLobe)&&(!query||n.label.toLowerCase().includes(query)||n.id.toLowerCase().includes(query));mesh.visible=visible});edges.forEach(edge=>{edge.visible=edge.userData.a.visible&&edge.userData.b.visible})}
const filterRoot=document.getElementById("filters"),lobes=["all",...new Set(GRAPH.nodes.map(n=>n.group))];lobes.forEach(lobe=>{const button=document.createElement("button");button.textContent=lobe;button.className=lobe==="all"?"active":"";button.onclick=()=>{activeLobe=lobe;filterRoot.querySelectorAll("button").forEach(item=>item.classList.remove("active"));button.classList.add("active");applyFilters()};filterRoot.appendChild(button)});document.getElementById("search").oninput=e=>{query=e.target.value.trim().toLowerCase();applyFilters()};
function normalize(value){return String(value||"").replaceAll("\\\\","/").toLowerCase()}
function matchEventToNodes(payload){const stats=payload.file_stats||[];const matched=[];nodes.forEach(mesh=>{const path=normalize(mesh.userData.path);if(path&&stats.some(item=>{const changed=normalize(item.path);return changed.endsWith(path)||path.endsWith(changed)})){matched.push(mesh)}});return matched}
function connectRuntime(){const status=document.getElementById("runtime-status"),eventLog=document.getElementById("events"),source=new EventSource("http://127.0.0.1:7474/events");source.onopen=()=>{status.textContent="ONLINE";status.style.color="#71e7a5";document.getElementById("status").textContent="COGNITIVE REACTOR // LIVE RUNTIME TELEMETRY"};source.onerror=()=>{status.textContent="OFFLINE";status.style.color="";document.getElementById("status").textContent="COGNITIVE REACTOR // RUNTIME UNAVAILABLE"};source.addEventListener("workspace_mutation",event=>{const data=JSON.parse(event.data),payload=data.payload||{};document.getElementById("event-count").textContent=String(Number(document.getElementById("event-count").textContent)+1);const row=document.createElement("div");row.textContent=`${payload.workspace||"workspace"} // ${(payload.files||[]).slice(0,2).join(", ")}`;eventLog.prepend(row);while(eventLog.children.length>5)eventLog.lastElementChild.remove();const matched=matchEventToNodes(payload);matched.forEach(mesh=>{mesh.material.color.set(0xffffff);if(mesh.userData.path)inspect(mesh.userData)});if(payload.high_signal)document.getElementById("status").textContent="COGNITIVE REACTOR // HIGH-SIGNAL MUTATION DETECTED"})}
connectRuntime();
document.getElementById("reset").onclick=()=>{camera.position.set(0,.25,24);controls.target.set(0,0,.35)};
function animate(){requestAnimationFrame(animate);controls.update();renderer.render(scene,camera)}animate();addEventListener("resize",()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight)});
</script></body></html>"""


def generate_3d_canvas(data: dict[str, Any], output_path: Path = THREE_D_OUTPUT) -> Path:
    graph = {"nodes": _coordinates(data.get("nodes", [])), "links": data.get("links", [])}
    update_readme_graph_stats(
        graph,
        settings.project_root / "README.md",
        source_label="brain/knowledge_ecosystem.json + brain/**/*.md",
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(HTML_TEMPLATE.replace("__GRAPH_JSON__", json.dumps(graph, ensure_ascii=False)), encoding="utf-8")
    return output_path


def render_and_open_3d(open_browser: bool = True) -> Path:
    data = extract_ecosystem_graph(
        settings.brain.brain_dir,
        settings.brain.brain_dir / "knowledge_ecosystem.json",
    )
    output = generate_3d_canvas(data)
    if open_browser:
        webbrowser.open(output.as_uri())
    return output
