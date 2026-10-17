# src/memory.py
"""
IE3 — Memoria de contenido de largo plazo por sesión/caso.

Complementa el historial corto (conversation.py) con hechos, temas y tickets
persistidos en disco para flujos prolongados (EP2).
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from src.config import CASE_MEMORY_DIR, ORG_CASE


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CaseMemory:
    session_id: str
    colaborador: str = ""
    rut: str = ""
    tema: str = ""
    facts: list[str] = field(default_factory=list)
    ticket_ids: list[str] = field(default_factory=list)
    updated_at: str = field(default_factory=_now_iso)

    def to_prompt_block(self) -> str:
        if not any([self.colaborador, self.tema, self.facts, self.ticket_ids]):
            return "Sin memoria de caso previa en esta sesión."
        lines = [
            f"Sesión: {self.session_id}",
            f"Colaborador: {self.colaborador or 'no indicado'}",
            f"RUT: {self.rut or 'no indicado'}",
            f"Tema activo: {self.tema or 'general RRHH'}",
        ]
        if self.facts:
            lines.append("Hechos registrados:")
            for fact in self.facts[-8:]:
                lines.append(f"- {fact}")
        if self.ticket_ids:
            lines.append("Tickets RRHH: " + ", ".join(self.ticket_ids))
        lines.append(f"Última actualización: {self.updated_at}")
        return "\n".join(lines)


class CaseMemoryStore:
    def __init__(self, base_dir: str = CASE_MEMORY_DIR) -> None:
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _path(self, session_id: str) -> str:
        safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in session_id)
        return os.path.join(self.base_dir, f"{safe}.json")

    def load(self, session_id: str) -> CaseMemory:
        path = self._path(session_id)
        if not os.path.isfile(path):
            return CaseMemory(session_id=session_id)
        with open(path, encoding="utf-8") as handle:
            data: dict[str, Any] = json.load(handle)
        return CaseMemory(
            session_id=session_id,
            colaborador=data.get("colaborador", ""),
            rut=data.get("rut", ""),
            tema=data.get("tema", ""),
            facts=list(data.get("facts") or []),
            ticket_ids=list(data.get("ticket_ids") or []),
            updated_at=data.get("updated_at") or _now_iso(),
        )

    def save(self, memory: CaseMemory) -> None:
        memory.updated_at = _now_iso()
        path = self._path(memory.session_id)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(asdict(memory), handle, ensure_ascii=False, indent=2)

    def append_fact(self, session_id: str, fact: str, *, tema: str = "") -> CaseMemory:
        memory = self.load(session_id)
        text = fact.strip()
        if text and text not in memory.facts:
            memory.facts.append(text[:500])
        if tema.strip():
            memory.tema = tema.strip()[:120]
        self.save(memory)
        return memory

    def register_ticket(self, session_id: str, ticket_id: str) -> CaseMemory:
        memory = self.load(session_id)
        if ticket_id not in memory.ticket_ids:
            memory.ticket_ids.append(ticket_id)
        self.save(memory)
        return memory

    def update_profile(
        self,
        session_id: str,
        *,
        colaborador: str = "",
        rut: str = "",
    ) -> CaseMemory:
        memory = self.load(session_id)
        if colaborador.strip():
            memory.colaborador = colaborador.strip()[:120]
        if rut.strip():
            memory.rut = rut.strip()[:32]
        self.save(memory)
        return memory


def default_session_label(session_id: str) -> str:
    return f"Caso {session_id[:8]} · {ORG_CASE.area}"
