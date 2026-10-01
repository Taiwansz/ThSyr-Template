"""
ThSyr Interaction Layer - Conversation Object Registry
Rastreia e indexa objetos concretos referenciados na conversa:
opcoes numeradas, arquivos, planos, metas, mudancas, commits e ferramentas.
Permite resolucao deterministica para expressoes como 'o segundo' ou '1'.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class ConversationObject:
    id: str
    label: str
    category: str  # 'option', 'file', 'plan', 'goal', 'commit', 'change', 'action', 'result', 'tool'
    value: Any
    shortcut: Optional[str] = None
    created_at: str = ""
    expires_turns: int = 5
    turns_alive: int = 0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "category": self.category,
            "value": str(self.value),
            "shortcut": self.shortcut,
            "created_at": self.created_at,
            "expires_turns": self.expires_turns,
            "turns_alive": self.turns_alive,
        }


class ConversationObjectRegistry:
    def __init__(self):
        self._objects: dict[str, ConversationObject] = {}
        self._shortcut_map: dict[str, str] = {}  # shortcut -> object_id
        self._category_index: dict[str, list[str]] = {}  # category -> list of object_id (latest last)
        self._active_options: list[str] = []  # IDs of active numbered options

    def register(
        self,
        id: str,
        label: str,
        category: str,
        value: Any,
        shortcut: Optional[str] = None,
        expires_turns: int = 5,
    ) -> ConversationObject:
        obj = ConversationObject(
            id=id,
            label=label,
            category=category,
            value=value,
            shortcut=shortcut,
            expires_turns=expires_turns,
        )
        self._objects[id] = obj

        if shortcut:
            self._shortcut_map[str(shortcut)] = id

        if category not in self._category_index:
            self._category_index[category] = []
        if id in self._category_index[category]:
            self._category_index[category].remove(id)
        self._category_index[category].append(id)

        return obj

    def register_options(self, options: list[dict[str, Any]]) -> list[ConversationObject]:
        """
        Registra um lote de alternativas apresentadas ao usuario,
        atribuindo atalhos numericos ("1", "2", "3") e IDs estaveis.
        """
        self._active_options.clear()
        registered = []
        for idx, opt in enumerate(options, 1):
            opt_id = opt.get("id") or f"option_{idx}"
            label = opt.get("label") or f"Opcao {idx}"
            shortcut = str(idx)
            val = opt.get("command") or opt.get("value") or label
            obj = self.register(
                id=opt_id,
                label=label,
                category="option",
                value=val,
                shortcut=shortcut,
                expires_turns=3,
            )
            self._active_options.append(opt_id)
            registered.append(obj)
        return registered

    def get_by_id(self, object_id: str) -> Optional[ConversationObject]:
        return self._objects.get(object_id)

    def get_by_shortcut(self, shortcut: str) -> Optional[ConversationObject]:
        obj_id = self._shortcut_map.get(str(shortcut).strip())
        if obj_id:
            return self.get_by_id(obj_id)
        return None

    def get_latest_by_category(self, category: str) -> Optional[ConversationObject]:
        items = self._category_index.get(category, [])
        if items:
            return self.get_by_id(items[-1])
        return None

    def get_active_options(self) -> list[ConversationObject]:
        res = []
        for opt_id in self._active_options:
            obj = self.get_by_id(opt_id)
            if obj:
                res.append(obj)
        return res

    def tick_turn(self) -> None:
        """Avanca um turno conversacional e expira objetos antigos."""
        to_delete = []
        for obj_id, obj in self._objects.items():
            obj.turns_alive += 1
            if obj.turns_alive >= obj.expires_turns:
                to_delete.append(obj_id)

        for obj_id in to_delete:
            self._remove(obj_id)

    def _remove(self, object_id: str) -> None:
        obj = self._objects.pop(object_id, None)
        if not obj:
            return
        if obj.shortcut and self._shortcut_map.get(obj.shortcut) == object_id:
            del self._shortcut_map[obj.shortcut]
        cat = obj.category
        if cat in self._category_index and object_id in self._category_index[cat]:
            self._category_index[cat].remove(object_id)
        if object_id in self._active_options:
            self._active_options.remove(object_id)

    def clear(self) -> None:
        self._objects.clear()
        self._shortcut_map.clear()
        self._category_index.clear()
        self._active_options.clear()
