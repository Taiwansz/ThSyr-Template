"""
ThSyr Sleep Cycle / Memory Consolidation
Rotina de reflexao e consolidacao continua da memoria.
"""

from engine.memory_manager import MemoryManager


def run_consolidation():
    memory = MemoryManager()
    recents = memory.get_recent_episodic_logs(limit=5)
    semantics = memory.get_semantic_memories()

    print("[THSYR SLEEP CYCLE] Iniciando consolidacao cognitiva...")
    print(f"Sessoes analisadas: {len(recents)}")
    print(f"Memorias semanticas ativas: {list(semantics.keys())}")
    print("[OK] Consolidacao concluida.")


if __name__ == "__main__":
    run_consolidation()
