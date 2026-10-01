"""
ThSyr God's Eye View Bridge & Planetary Telemetry Connector
Interface de integracao sensorial entre a mente do ThSyr e o console 3D Gods Eye View
Localizacao padrao: ~/gods-eye-view
"""

import json
import subprocess
from pathlib import Path
from typing import Any

from .config import setup_logger

logger = setup_logger("gods_eye_bridge")

def resolve_gods_eye_path() -> Path:
    candidates = [
        Path.home() / "gods-eye-view",
        Path.home() / "projetos" / "gods-eye-view",
        Path.home() / "projects" / "gods-eye-view",
    ]
    for c in candidates:
        if (c / "package.json").exists():
            return c
    return candidates[0]


DEFAULT_GODS_EYE_PATH = resolve_gods_eye_path()


class GodsEyeBridge:
    def __init__(self, repo_path: Path | None = None):
        self.repo_path = repo_path or resolve_gods_eye_path()

    def is_installed(self) -> bool:
        """Verifica se o repositorio local do Gods Eye View existe e contem os arquivos essenciais."""
        if not self.repo_path.exists():
            return False
        package_json = self.repo_path / "package.json"
        vite_config = self.repo_path / "vite.config.js"
        return package_json.exists() and vite_config.exists()

    def get_metadata(self) -> dict[str, Any]:
        """Obtem informacoes de versao, scripts e dependencias do projeto."""
        if not self.is_installed():
            return {
                "installed": False,
                "path": str(self.repo_path),
                "error": "Repositorio nao localizado no caminho especificado."
            }

        package_json = self.repo_path / "package.json"
        try:
            with open(package_json, "r", encoding="utf-8") as f:
                pkg = json.load(f)

            return {
                "installed": True,
                "name": pkg.get("name", "gods-eye-view"),
                "version": pkg.get("version", "unknown"),
                "description": pkg.get("description", ""),
                "scripts": list(pkg.get("scripts", {}).keys()),
                "path": str(self.repo_path)
            }
        except Exception as e:
            logger.error(f"Erro ao ler metadata do Gods Eye View: {e}")
            return {
                "installed": True,
                "path": str(self.repo_path),
                "error": str(e)
            }

    def list_sensory_layers(self) -> list[dict[str, str]]:
        """Lista as camadas de telemetria e fluxos de dados mapeados pelo console."""
        return [
            {
                "layer_id": "adsb_aviation",
                "name": "Trafego Aereo Global (ADS-B)",
                "source": "OpenSky Network / FlightRadar feeds",
                "status": "active"
            },
            {
                "layer_id": "ais_maritime",
                "name": "Trafego Maritimo Global (AIS)",
                "source": "Balizas nauticas e frotas de carga",
                "status": "active"
            },
            {
                "layer_id": "satellites_sgp4",
                "name": "Constelacoes e Mecanica Orbital (SGP4)",
                "source": "Celestrak / NORAD TLEs via satellite.js",
                "status": "active"
            },
            {
                "layer_id": "seismic_usgs",
                "name": "Sismologia Planetaria",
                "source": "USGS Earthquakes Feed",
                "status": "active"
            },
            {
                "layer_id": "thermal_firms",
                "name": "Anomalias Termicas e Focos de Calor",
                "source": "NASA FIRMS",
                "status": "active"
            },
            {
                "layer_id": "cctv_nodes",
                "name": "Malha de CFTV Publico",
                "source": "Streams publicos georreferenciados",
                "status": "active"
            }
        ]

    def has_dependencies(self) -> bool:
        """Verifica se a pasta node_modules existe."""
        return (self.repo_path / "node_modules").exists()

    def get_status(self) -> dict[str, Any]:
        """Gera relatorio diagnostico de status da integracao sensorial."""
        installed = self.is_installed()
        deps_installed = self.has_dependencies() if installed else False
        meta = self.get_metadata() if installed else {}
        layers = self.list_sensory_layers()

        return {
            "status": "OPERATIONAL" if installed else "MISSING",
            "installed": installed,
            "dependencies_installed": deps_installed,
            "path": str(self.repo_path),
            "version": meta.get("version", "N/A"),
            "total_layers": len(layers),
            "layers": layers,
            "telemetry_engine": "Cesium 3D Tiles + WebGL Shaders"
        }

    def launch(self, port: int = 4173) -> dict[str, Any]:
        """Dispara o servidor de desenvolvimento do console 3D em segundo plano."""
        if not self.is_installed():
            return {"success": False, "error": "Repositorio nao localizado."}
        if not self.has_dependencies():
            return {"success": False, "error": "Dependencias (node_modules) ausentes. Execute 'npm install' no console."}

        try:
            proc = subprocess.Popen(
                ["npm", "run", "dev", "--", "--port", str(port)],
                cwd=str(self.repo_path),
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return {"success": True, "pid": proc.pid, "url": f"http://localhost:{port}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

