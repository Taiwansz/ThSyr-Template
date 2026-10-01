"""
ThSyr Host Hardware Telemetry & Silicon Perception
Mapeia em tempo real a computacao fisica do operador:
- Utilizacao e nucleos de CPU
- Memoria RAM total, em uso e disponivel
- Armazenamento em disco da unidade primária
- Deteccao de GPU NVIDIA, VRAM alocada e temperatura (via nvidia-smi)
- Telemetria de runtime Python e plataforma
"""

import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import setup_logger

logger = setup_logger("host_telemetry")


class HostTelemetryObserver:
    def __init__(self, target_drive: str | None = None):
        self.target_drive = target_drive or (Path.home().anchor if sys.platform.startswith("win") else "/")

    def _get_cpu_metrics(self) -> dict[str, Any]:
        """Obtem metricas de CPU com fallback robusto."""
        cpu_data: dict[str, Any] = {
            "cores_logical": os.cpu_count() or 1,
            "usage_percent": 0.0,
            "architecture": platform.machine()
        }

        # 1. Tentar via psutil se disponivel
        try:
            import psutil
            cpu_data["usage_percent"] = float(psutil.cpu_percent(interval=0.1))
            cpu_data["cores_physical"] = psutil.cpu_count(logical=False) or cpu_data["cores_logical"]
            return cpu_data
        except ImportError:
            pass

        # 2. Fallback Windows via wmic
        if sys.platform.startswith("win"):
            try:
                out = subprocess.check_output(
                    ["wmic", "cpu", "get", "loadpercentage"],
                    text=True,
                    timeout=2,
                    stderr=subprocess.DEVNULL,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
                )
                lines = [line.strip() for line in out.splitlines() if line.strip() and line.strip().isdigit()]
                if lines:
                    cpu_data["usage_percent"] = float(lines[0])
            except Exception:
                pass
        # 3. Fallback Linux via /proc/loadavg
        elif Path("/proc/loadavg").exists():
            try:
                with open("/proc/loadavg", "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    parts = content.split()
                    if parts:
                        load1 = float(parts[0])
                        cores = int(cpu_data["cores_logical"])
                        cpu_data["usage_percent"] = round(min(100.0, (load1 / max(1, cores)) * 100), 1)
            except Exception:
                pass
        return cpu_data

    def _get_ram_metrics(self) -> dict[str, Any]:
        """Obtem metricas de memoria RAM."""
        ram_data = {
            "total_gb": 0.0,
            "used_gb": 0.0,
            "free_gb": 0.0,
            "percent": 0.0
        }

        # 1. Tentar psutil
        try:
            import psutil
            vm = psutil.virtual_memory()
            ram_data["total_gb"] = round(vm.total / (1024 ** 3), 2)
            ram_data["used_gb"] = round(vm.used / (1024 ** 3), 2)
            ram_data["free_gb"] = round(vm.available / (1024 ** 3), 2)
            ram_data["percent"] = round(vm.percent, 1)
            return ram_data
        except ImportError:
            pass

        # 2. Fallback Windows via ctypes GlobalMemoryStatusEx
        if sys.platform.startswith("win"):
            try:
                import ctypes

                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]

                stat = MEMORYSTATUSEX()
                stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
                    total = stat.ullTotalPhys
                    avail = stat.ullAvailPhys
                    used = total - avail
                    ram_data["total_gb"] = round(total / (1024 ** 3), 2)
                    ram_data["used_gb"] = round(used / (1024 ** 3), 2)
                    ram_data["free_gb"] = round(avail / (1024 ** 3), 2)
                    ram_data["percent"] = float(stat.dwMemoryLoad)
                    return ram_data
            except Exception:
                pass

        # 3. Fallback Linux via /proc/meminfo
        if Path("/proc/meminfo").exists():
            try:
                meminfo = {}
                with open("/proc/meminfo", "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.split(":")
                        if len(parts) == 2:
                            key = parts[0].strip()
                            val_str = parts[1].strip().split()[0]
                            if val_str.isdigit():
                                meminfo[key] = int(val_str)
                total_kb = meminfo.get("MemTotal", 0)
                avail_kb = meminfo.get("MemAvailable", meminfo.get("MemFree", 0))
                if total_kb > 0:
                    used_kb = total_kb - avail_kb
                    ram_data["total_gb"] = round(total_kb / (1024 ** 2), 2)
                    ram_data["used_gb"] = round(used_kb / (1024 ** 2), 2)
                    ram_data["free_gb"] = round(avail_kb / (1024 ** 2), 2)
                    ram_data["percent"] = round((used_kb / total_kb) * 100, 1)
                    return ram_data
            except Exception:
                pass

        return ram_data

    def _get_disk_metrics(self) -> dict[str, Any]:
        """Obtem dados de utilizacao do disco primario via standard library."""
        try:
            usage = shutil.disk_usage(self.target_drive)
            return {
                "drive": self.target_drive,
                "total_gb": round(usage.total / (1024 ** 3), 2),
                "used_gb": round(usage.used / (1024 ** 3), 2),
                "free_gb": round(usage.free / (1024 ** 3), 2),
                "percent": round((usage.used / usage.total) * 100, 1) if usage.total > 0 else 0.0
            }
        except Exception as e:
            logger.debug(f"Falha ao checar disco: {e}")
            return {
                "drive": self.target_drive,
                "total_gb": 0.0,
                "used_gb": 0.0,
                "free_gb": 0.0,
                "percent": 0.0
            }

    def _get_gpu_metrics(self) -> dict[str, Any]:
        """Detecta GPUs NVIDIA e telemetria de VRAM via nvidia-smi."""
        gpu_info = {
            "available": False,
            "model": "N/D",
            "vram_total_mb": 0,
            "vram_used_mb": 0,
            "vram_free_mb": 0,
            "temperature_c": 0,
            "utilization_percent": 0
        }

        try:
            cmd = [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.used,memory.free,temperature.gpu,utilization.gpu",
                "--format=csv,noheader,nounits"
            ]
            flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform.startswith("win") else 0
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
                creationflags=flags
            )
            if proc.returncode == 0 and proc.stdout.strip():
                line = proc.stdout.strip().splitlines()[0]
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 6:
                    gpu_info["available"] = True
                    gpu_info["model"] = parts[0]
                    gpu_info["vram_total_mb"] = int(float(parts[1]))
                    gpu_info["vram_used_mb"] = int(float(parts[2]))
                    gpu_info["vram_free_mb"] = int(float(parts[3]))
                    gpu_info["temperature_c"] = int(float(parts[4]))
                    gpu_info["utilization_percent"] = int(float(parts[5]))
        except Exception:
            pass

        return gpu_info

    def get_telemetry(self) -> dict[str, Any]:
        """Consolida toda a telemetria do hospedeiro."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "node": platform.node(),
                "python_version": sys.version.split()[0],
                "python_executable": sys.executable
            },
            "cpu": self._get_cpu_metrics(),
            "ram": self._get_ram_metrics(),
            "disk": self._get_disk_metrics(),
            "gpu": self._get_gpu_metrics()
        }

    def render_report(self) -> str:
        """Renderiza o relatorio de silicio em formato tabular limpo."""
        t = self.get_telemetry()
        cpu = t["cpu"]
        ram = t["ram"]
        disk = t["disk"]
        gpu = t["gpu"]
        plat = t["platform"]

        lines = [
            "==================================================",
            "        THSYR HOST TELEMETRY & SILICON MONITOR    ",
            "==================================================",
            f"Host / OS:           {plat['node']} | {plat['system']} {plat['release']}",
            f"Python Runtime:      {plat['python_version']} ({plat['python_executable']})",
            "--------------------------------------------------",
            f"CPU [{cpu['architecture']}]:         {cpu['usage_percent']:.1f}% em uso ({cpu['cores_logical']} nucleos logicos)",
            f"Memoria RAM:         {ram['used_gb']} GB / {ram['total_gb']} GB ({ram['percent']}%) | Livre: {ram['free_gb']} GB",
            f"Disco [{disk['drive']}]:           {disk['used_gb']} GB / {disk['total_gb']} GB ({disk['percent']}%) | Livre: {disk['free_gb']} GB",
            "--------------------------------------------------",
        ]

        if gpu["available"]:
            lines.extend([
                f"GPU Dedicada:        {gpu['model']}",
                f"VRAM Alocada:        {gpu['vram_used_mb']} MB / {gpu['vram_total_mb']} MB (Livre: {gpu['vram_free_mb']} MB)",
                f"Termal / Carga GPU:  {gpu['temperature_c']} C | {gpu['utilization_percent']}% utilizacao"
            ])
        else:
            lines.append("GPU Dedicada:        Nenhuma GPU NVIDIA detectada via nvidia-smi")

        lines.append("==================================================")
        return "\n".join(lines)
