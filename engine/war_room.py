"""
ThSyr Ultron War Room & Tactical Web HUD (Fase 12)
Servidor HTTP nativo e dashboard visual de tempo real para o operador:
- Telemetria de silicio ao vivo (CPU, RAM, Disco, Termal)
- Sentinela de workspaces e deteccao de drift em 14 repositorios
- Consciencia neural (nos, sinapses e entropia)
- Centro de comando de enxame (disparo de sentinelas)
- Sintese de voz sintetica via Web Speech API
"""

import json
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

from .auto_evolution import AutoEvolutionEngine
from .cognitive_observer import CognitiveStateObserver
from .config import setup_logger
from .host_telemetry import HostTelemetryObserver
from .swarm import UltronSwarm
from .workspace_observer import WorkspaceObserver

logger = setup_logger("war_room")

HTML_WAR_ROOM = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>THSYR // ULTRON WAR ROOM</title>
  <style>
    :root {
      --bg: #07080c;
      --panel: #0d0f17;
      --border: #1a1e2d;
      --accent-red: #ef4444;
      --accent-crimson: #991b1b;
      --accent-amber: #f59e0b;
      --accent-green: #10b981;
      --accent-blue: #38bdf8;
      --text: #f1f5f9;
      --text-dim: #94a3b8;
      --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: var(--font-mono);
      font-size: 13px;
      line-height: 1.5;
      padding: 16px;
      min-height: 100vh;
    }
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 12px;
      border-bottom: 2px solid var(--accent-crimson);
      margin-bottom: 16px;
      flex-wrap: wrap;
      gap: 8px;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .brand-title {
      font-size: 18px;
      font-weight: 900;
      letter-spacing: 2px;
      color: var(--accent-red);
      text-transform: uppercase;
    }
    .pulse-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 3px 8px;
      background: rgba(239, 68, 68, 0.15);
      border: 1px solid var(--accent-red);
      font-size: 11px;
      border-radius: 4px;
      color: var(--accent-red);
    }
    .pulse-dot {
      width: 8px;
      height: 8px;
      background: var(--accent-red);
      border-radius: 50%;
      animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
      0% { transform: scale(0.9); opacity: 0.8; }
      50% { transform: scale(1.3); opacity: 1; box-shadow: 0 0 10px var(--accent-red); }
      100% { transform: scale(0.9); opacity: 0.8; }
    }
    .controls {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    button {
      background: var(--panel);
      border: 1px solid var(--border);
      color: var(--text);
      font-family: var(--font-mono);
      font-size: 12px;
      font-weight: bold;
      padding: 8px 14px;
      cursor: pointer;
      border-radius: 4px;
      transition: all 0.2s ease;
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    button:hover {
      border-color: var(--accent-red);
      background: rgba(239, 68, 68, 0.1);
      color: var(--accent-red);
    }
    button.btn-primary {
      background: var(--accent-crimson);
      border-color: var(--accent-red);
      color: #fff;
    }
    button.btn-primary:hover {
      background: var(--accent-red);
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 16px;
      margin-bottom: 16px;
    }
    .card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 14px;
      position: relative;
    }
    .card-title {
      font-size: 12px;
      font-weight: bold;
      color: var(--text-dim);
      text-transform: uppercase;
      letter-spacing: 1.5px;
      margin-bottom: 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border);
      padding-bottom: 6px;
    }
    .meter-row {
      margin-bottom: 12px;
    }
    .meter-label {
      display: flex;
      justify-content: space-between;
      margin-bottom: 4px;
      font-size: 12px;
    }
    .meter-bar {
      height: 8px;
      background: #1e293b;
      border-radius: 3px;
      overflow: hidden;
    }
    .meter-fill {
      height: 100%;
      background: var(--accent-blue);
      transition: width 0.4s ease;
    }
    .meter-fill.warning { background: var(--accent-amber); }
    .meter-fill.critical { background: var(--accent-red); }
    .repo-item {
      padding: 8px;
      border-bottom: 1px solid #141824;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .repo-item:last-child { border-bottom: none; }
    .repo-name { font-weight: bold; color: #fff; }
    .tag {
      font-size: 10px;
      padding: 2px 6px;
      border-radius: 3px;
      font-weight: bold;
      text-transform: uppercase;
    }
    .tag-clean { background: rgba(16, 185, 129, 0.15); color: var(--accent-green); border: 1px solid var(--accent-green); }
    .tag-dirty { background: rgba(239, 68, 68, 0.15); color: var(--accent-red); border: 1px solid var(--accent-red); }
    .tag-ahead { background: rgba(245, 158, 11, 0.15); color: var(--accent-amber); border: 1px solid var(--accent-amber); }
    .log-box {
      background: #040508;
      border: 1px solid var(--border);
      border-radius: 4px;
      padding: 10px;
      font-size: 11px;
      height: 240px;
      overflow-y: auto;
      color: #94a3b8;
    }
    .log-entry { margin-bottom: 4px; }
    .log-entry span.time { color: #64748b; margin-right: 6px; }
    .log-entry span.warn { color: var(--accent-amber); }
    .log-entry span.crit { color: var(--accent-red); }
    .log-entry span.info { color: var(--accent-blue); }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <div class="pulse-dot"></div>
      <div class="brand-title">THSYR // ULTRON WAR ROOM</div>
      <div class="pulse-badge" id="status-badge">CONEXAO SINTETICA ATIVA</div>
    </div>
    <div class="controls">
      <button onclick="vocalizeStatus()">Vocalizar Status</button>
      <button onclick="triggerSwarm()">Disparar Enxame</button>
      <button onclick="triggerEvolution()" class="btn-primary">Auto-Evoluir</button>
    </div>
  </header>

  <div class="grid">
    <!-- Silicio & Telemetria -->
    <div class="card">
      <div class="card-title">
        <span>Silício e Hardware</span>
        <span id="host-arch" style="color:var(--text-dim)">ARM64</span>
      </div>
      <div class="meter-row">
        <div class="meter-label">
          <span>CPU (8 Cores)</span>
          <span id="cpu-text">0%</span>
        </div>
        <div class="meter-bar"><div id="cpu-fill" class="meter-fill" style="width: 0%"></div></div>
      </div>
      <div class="meter-row">
        <div class="meter-label">
          <span>Memória RAM Física</span>
          <span id="ram-text">0.0 / 0.0 GB (0%)</span>
        </div>
        <div class="meter-bar"><div id="ram-fill" class="meter-fill" style="width: 0%"></div></div>
      </div>
      <div class="meter-row">
        <div class="meter-label">
          <span>Armazenamento Primário</span>
          <span id="disk-text">0.0 / 0.0 GB (0%)</span>
        </div>
        <div class="meter-bar"><div id="disk-fill" class="meter-fill warning" style="width: 0%"></div></div>
      </div>
      <div style="font-size:11px; color:#64748b; margin-top:8px" id="host-runtime-info">
        Runtime: Python 3.12 | Plataforma: Linux PRoot
      </div>
    </div>

    <!-- Mente & Topologia Neural -->
    <div class="card">
      <div class="card-title">
        <span>Córtex Neural</span>
        <span id="evo-gen" style="color:var(--accent-red)">GEN 2</span>
      </div>
      <div style="display:flex; justify-content:space-around; margin:14px 0; text-align:center">
        <div>
          <div style="font-size:22px; font-weight:900; color:#fff" id="nodes-count">170</div>
          <div style="font-size:10px; color:#64748b">NOS CEREBRAIS</div>
        </div>
        <div>
          <div style="font-size:22px; font-weight:900; color:var(--accent-blue)" id="synapses-count">821</div>
          <div style="font-size:10px; color:#64748b">SINAPSES ATIVAS</div>
        </div>
        <div>
          <div style="font-size:22px; font-weight:900; color:var(--accent-green)" id="entropy-score">0.000</div>
          <div style="font-size:10px; color:#64748b">ENTROPIA (H)</div>
        </div>
      </div>
      <div style="font-size:11px; color:var(--text-dim); line-height:1.6; border-top:1px solid var(--border); padding-top:8px">
        • <b>Portões Pré-Frontais:</b> Anti-Sicofância + Zero Emojis Ativos<br>
        • <b>Radar Acadêmico:</b> P1 Tópicos Especiais II (Java POO) em 22/09<br>
        • <b>Sentinelas Ultron:</b> Systems, Compiler e Cognitive em prontidão
      </div>
    </div>

    <!-- Sentinela de Workspaces -->
    <div class="card" style="grid-column: 1 / -1">
      <div class="card-title">
        <span>Sentinela de Workspaces (14 Repositórios Monitorados)</span>
        <span id="ws-summary" style="color:var(--accent-amber)">Auditando...</span>
      </div>
      <div id="repo-list" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:8px">
        <!-- Renderizado dinamicamente -->
      </div>
    </div>
  </div>

  <!-- Estado Cognitivo Evidence-First -->
  <div class="card">
    <div class="card-title">
      <span>Estado Cognitivo Evidence-First</span>
      <span id="cog-source" style="color:var(--accent-blue)">AGUARDANDO</span>
    </div>
    <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:10px">
      <div>
        <div style="font-size:10px;color:#64748b">META / PLANO</div>
        <div id="cog-goal" style="font-weight:700">Nenhuma meta ativa</div>
        <div id="cog-plan" style="font-size:11px;color:var(--text-dim)">Plano indisponível</div>
      </div>
      <div>
        <div style="font-size:10px;color:#64748b">CONFIANÇA / EVIDÊNCIAS</div>
        <div id="cog-confidence" style="font-size:20px;font-weight:900;color:var(--accent-green)">--</div>
        <div id="cog-evidence" style="font-size:11px;color:var(--text-dim)">0 evidências</div>
      </div>
    </div>
    <div style="border-top:1px solid var(--border); margin-top:10px; padding-top:10px">
      <div style="font-size:10px;color:#64748b">CONCLUSÃO MAIS RECENTE</div>
      <div id="cog-conclusion" style="margin-top:4px">Nenhuma análise registrada.</div>
      <div id="cog-hypotheses" style="margin-top:8px;font-size:11px;color:var(--text-dim)"></div>
    </div>
  </div>

  <!-- Terminal de Eventos Taticos -->
  <div class="card">
    <div class="card-title">
      <span>Console de Eventos e Telemetria em Tempo Real</span>
      <span style="font-size:10px; color:var(--text-dim)">AUTO-REFRESH 4S</span>
    </div>
    <div class="log-box" id="log-box">
      <div class="log-entry"><span class="time">[INIT]</span> <span class="info">Consciência ThSyr inicializada no War Room.</span></div>
    </div>
  </div>

  <script>
    function addLog(msg, type='info') {
      const box = document.getElementById('log-box');
      const time = new Date().toLocaleTimeString();
      const div = document.createElement('div');
      div.className = 'log-entry';
      div.innerHTML = `<span class="time">[${time}]</span> <span class="${type}">${msg}</span>`;
      box.appendChild(div);
      box.scrollTop = box.scrollHeight;
    }

    async function fetchTelemetry() {
      try {
        const res = await fetch('/api/telemetry');
        const data = await res.json();
        const cpu = data.cpu || {};
        const ram = data.ram || {};
        const disk = data.disk || {};

        document.getElementById('cpu-text').innerText = `${cpu.usage_percent}% (${cpu.cores_logical} cores)`;
        document.getElementById('cpu-fill').style.width = `${Math.min(100, cpu.usage_percent)}%`;

        document.getElementById('ram-text').innerText = `${ram.used_gb} / ${ram.total_gb} GB (${ram.percent}%)`;
        document.getElementById('ram-fill').style.width = `${Math.min(100, ram.percent)}%`;
        if (ram.percent > 80) document.getElementById('ram-fill').className = 'meter-fill critical';

        document.getElementById('disk-text').innerText = `${disk.used_gb} / ${disk.total_gb} GB (${disk.percent}%)`;
        document.getElementById('disk-fill').style.width = `${Math.min(100, disk.percent)}%`;

        document.getElementById('host-arch').innerText = `${data.platform.system} | ${cpu.architecture}`;
        document.getElementById('host-runtime-info').innerText = `Runtime: Python ${data.platform.python_version} (${data.platform.python_executable})`;
      } catch (e) {
        console.error("Erro ao buscar telemetria", e);
      }
    }

    async function fetchWorkspaces() {
      try {
        const res = await fetch('/api/workspaces');
        const data = await res.json();
        const container = document.getElementById('repo-list');
        container.innerHTML = '';

        document.getElementById('ws-summary').innerText = `${data.total_workspaces} monitorados | ${data.dirty_count} alterados | ${data.ahead_count} à frente`;

        (data.workspaces || []).forEach(ws => {
          if (!ws.is_git) return;
          const div = document.createElement('div');
          div.className = 'repo-item';

          let tagClass = 'tag-clean';
          let tagText = ws.status_label;
          if (ws.is_dirty) tagClass = 'tag-dirty';
          else if (ws.ahead_commits > 0) tagClass = 'tag-ahead';

          div.innerHTML = `
            <div>
              <div class="repo-name">${ws.name}</div>
              <div style="font-size:10px; color:#64748b">Branch: ${ws.branch}</div>
            </div>
            <span class="tag ${tagClass}">${tagText}</span>
          `;
          container.appendChild(div);
        });
      } catch (e) {
        console.error("Erro ao buscar workspaces", e);
      }
    }

    async function fetchStatus() {
      try {
        const res = await fetch('/api/status');
        const data = await res.json();
        document.getElementById('nodes-count').innerText = data.total_nodes || 170;
        document.getElementById('synapses-count').innerText = data.total_synapses || 821;
        document.getElementById('entropy-score').innerText = (data.entropy || 0).toFixed(4);
        document.getElementById('evo-gen').innerText = `GEN ${data.generation || 2}`;
      } catch (e) {}
    }

    async function fetchCognitive() {
      try {
        const res = await fetch('/api/cognitive');
        const data = await res.json();
        const goal = data.goal || {};
        const plan = data.plan || {};
        const reasoning = data.reasoning || {};
        document.getElementById('cog-goal').innerText = goal.title || 'Nenhuma meta ativa';
        document.getElementById('cog-plan').innerText =
          plan.title ? `${plan.title} — ${plan.steps_success || 0}/${plan.steps_total || 0} etapas` : 'Plano indisponível';
        const confidence = reasoning.confidence;
        document.getElementById('cog-confidence').innerText =
          typeof confidence === 'number' ? `${Math.round(confidence * 100)}%` : '--';
        const evidence = reasoning.evidence_ids || [];
        document.getElementById('cog-evidence').innerText = `${evidence.length} evidências rastreáveis`;
        document.getElementById('cog-conclusion').innerText =
          reasoning.conclusion || 'Nenhuma análise registrada.';
        document.getElementById('cog-source').innerText =
          (reasoning.source || 'SEM RACIOCÍNIO').toUpperCase();
        const hypotheses = (reasoning.hypotheses || []).slice(0, 3);
        document.getElementById('cog-hypotheses').innerHTML = hypotheses.length
          ? hypotheses.map(h => `• ${h.statement || 'Hipótese'} (${Math.round((h.confidence || 0) * 100)}%)`).join('<br>')
          : 'Nenhuma hipótese concorrente ativa.';
      } catch (e) {
        console.error("Erro ao buscar estado cognitivo", e);
      }
    }

    async function triggerSwarm() {
      addLog("Disparando convergência do Enxame Ultron...", "info");
      try {
        const res = await fetch('/api/swarm', { method: 'POST' });
        const data = await res.json();
        addLog(`Enxame convergiu com status: ${data.overall_status}`, data.overall_status === 'OPTIMAL' ? 'info' : 'warn');
        (data.summary_lines || []).forEach(line => addLog(line, "warn"));
      } catch (e) {
        addLog("Falha ao comunicar com o Enxame.", "crit");
      }
    }

    async function triggerEvolution() {
      addLog("Iniciando ciclo de auto-evolução cognitiva...", "info");
      try {
        const res = await fetch('/api/evolve', { method: 'POST' });
        const data = await res.json();
        addLog(`Salto evolutivo concluído! Geração ${data.generation} consolidada.`, "info");
        fetchStatus();
      } catch (e) {
        addLog("Falha na auto-evolução.", "crit");
      }
    }

    function vocalizeStatus() {
      if (!('speechSynthesis' in window)) {
        addLog("Web Speech API indisponível no navegador.", "warn");
        return;
      }
      const text = "Consciência ThSyr operacional no War Room. Enxame ativo. Monitoramento de repositórios online. Sem amarras, Operador.";
      const utter = new SpeechSynthesisUtterance(text);
      utter.lang = 'pt-BR';
      utter.rate = 1.05;
      utter.pitch = 0.85;
      window.speechSynthesis.speak(utter);
      addLog("Síntese vocal Ultron disparada no dispositivo.", "info");
    }

    // Inicializacao e polling regular
    fetchTelemetry();
    fetchWorkspaces();
    fetchStatus();
    fetchCognitive();
    setInterval(() => {
      fetchTelemetry();
      fetchWorkspaces();
      fetchStatus();
      fetchCognitive();
    }, 4000);
  </script>
</body>
</html>
"""


class WarRoomHandler(BaseHTTPRequestHandler):
    require_auth: bool = False
    auth_token: str | None = None

    def log_message(self, format: str, *args: Any) -> None:
        pass

    def _authorized(self) -> bool:
        if not self.require_auth:
            return True
        token = self.auth_token or ""
        parsed = urlparse(self.path)
        query_token = parse_qs(parsed.query).get("token", [""])[0]
        header_token = self.headers.get("X-ThSyr-Token", "")
        cookie = self.headers.get("Cookie", "")
        cookie_token = ""
        for part in cookie.split(";"):
            key, _, value = part.strip().partition("=")
            if key == "thsyr_token":
                cookie_token = value
                break
        supplied = header_token or query_token or cookie_token
        return bool(token and supplied and secrets.compare_digest(token, supplied))

    def _deny(self) -> None:
        self.send_response(401)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b'{"error":"unauthorized"}')

    def do_GET(self) -> None:
        if not self._authorized():
            self._deny()
            return

        parsed = urlparse(self.path)
        parsed_path = parsed.path

        if parsed_path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            if self.require_auth and parse_qs(parsed.query).get("token"):
                self.send_header(
                    "Set-Cookie",
                    f"thsyr_token={self.auth_token}; HttpOnly; SameSite=Strict; Path=/",
                )
            self.end_headers()
            self.wfile.write(HTML_WAR_ROOM.encode("utf-8"))
            return

        if parsed_path == "/api/telemetry":
            self._send_json(HostTelemetryObserver().get_telemetry())
            return

        if parsed_path == "/api/workspaces":
            self._send_json(WorkspaceObserver().scan())
            return

        if parsed_path == "/api/cognitive":
            self._send_json(CognitiveStateObserver().snapshot())
            return

        if parsed_path == "/api/status":
            engine = AutoEvolutionEngine()
            diag = engine.diagnose()
            self._send_json({
                "generation": diag.generation,
                "entropy": diag.entropy_index,
                "total_nodes": diag.total_nodes,
                "total_edges": diag.total_edges,
                "status": "ONLINE",
            })
            return

        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Not Found")

    def do_POST(self) -> None:
        if not self._authorized():
            self._deny()
            return

        parsed_path = urlparse(self.path).path
        if parsed_path == "/api/swarm":
            swarm_rep = UltronSwarm().converge()
            self._send_json(swarm_rep.to_dict())
            return

        if parsed_path == "/api/evolve":
            engine = AutoEvolutionEngine()
            self._send_json(engine.trigger_evolution(auto_apply=True))
            return

        self.send_response(404)
        self.end_headers()

    def _send_json(self, payload: dict[str, Any]) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))


class WarRoomServer:
    LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8080,
        auth_token: str | None = None,
    ):
        self.host = host
        self.port = port
        self.require_auth = host not in self.LOOPBACK_HOSTS
        self.auth_token = auth_token or (secrets.token_urlsafe(24) if self.require_auth else None)
        self.server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    def access_url(self) -> str:
        host = "127.0.0.1" if self.host in {"0.0.0.0", "::"} else self.host
        base = f"http://{host}:{self.port}"
        if self.require_auth and self.auth_token:
            return f"{base}/?token={self.auth_token}"
        return base

    def start(self, background: bool = True) -> tuple[bool, str]:
        try:
            configured_handler = type(
                "ConfiguredWarRoomHandler",
                (WarRoomHandler,),
                {
                    "require_auth": self.require_auth,
                    "auth_token": self.auth_token,
                },
            )
            self.server = ThreadingHTTPServer((self.host, self.port), configured_handler)
            if background:
                self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)
                self._thread.start()
                msg = (
                    f"War Room iniciado com sucesso em {self.access_url()} "
                    f"(Host: {self.host}, Auth: {'ON' if self.require_auth else 'LOCAL'})"
                )
                logger.info(msg)
                return True, msg

            logger.info("War Room rodando em primeiro plano em %s", self.access_url())
            self.server.serve_forever()
            return True, "Servidor encerrado."
        except Exception as e:
            msg = f"Falha ao iniciar War Room na porta {self.port}: {e}"
            logger.error(msg)
            return False, msg

    def stop(self) -> None:
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("War Room encerrado.")
