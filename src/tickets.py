# src/tickets.py
"""Escritura de tickets RRHH (mock local) — herramienta del agente EP2."""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TICKETS_DIR = Path("tickets_local")
TICKETS_FILE = TICKETS_DIR / "tickets_rrhh.jsonl"


@dataclass
class HRTicket:
    id: str
    asunto: str
    descripcion: str
    categoria: str
    prioridad: str
    colaborador: str = ""
    rut: str = ""
    estado: str = "abierto"
    origen: str = "IntegraBot"
    creado_en: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "asunto": self.asunto,
            "categoria": self.categoria,
            "prioridad": self.prioridad,
            "estado": self.estado,
            "origen": self.origen,
            "creado_en": self.creado_en,
        }


def _next_id() -> str:
    TICKETS_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    if TICKETS_FILE.exists():
        count = sum(1 for line in TICKETS_FILE.read_text(encoding="utf-8").splitlines() if line.strip())
    return f"INT-{count + 1:05d}"


class HRTicketClient:
    def get(self, ticket_id: str) -> HRTicket | None:
        """Recupera un ticket mock por id (INT-xxxxx)."""
        if not TICKETS_FILE.is_file():
            return None
        needle = ticket_id.strip().upper()
        for line in TICKETS_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            if str(data.get("id", "")).upper() == needle:
                return HRTicket(
                    id=str(data.get("id", "")),
                    asunto=str(data.get("asunto", "")),
                    descripcion=str(data.get("descripcion", "")),
                    categoria=str(data.get("categoria", "otro")),
                    prioridad=str(data.get("prioridad", "media")),
                    colaborador=str(data.get("colaborador", "")),
                    rut=str(data.get("rut", "")),
                    estado=str(data.get("estado", "abierto")),
                    origen=str(data.get("origen", "IntegraBot")),
                    creado_en=str(data.get("creado_en", "")),
                )
        return None

    def create(
        self,
        *,
        asunto: str,
        descripcion: str,
        categoria: str = "otro",
        prioridad: str = "media",
        colaborador: str = "",
        rut: str = "",
    ) -> HRTicket:
        ticket = HRTicket(
            id=_next_id(),
            asunto=(asunto or "Consulta derivada desde IntegraBot").strip()[:200],
            descripcion=descripcion.strip()[:2000],
            categoria=(categoria or "otro").strip().lower(),
            prioridad=(prioridad or "media").strip().lower(),
            colaborador=colaborador.strip()[:120],
            rut=rut.strip()[:32],
        )
        TICKETS_DIR.mkdir(parents=True, exist_ok=True)
        with TICKETS_FILE.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(ticket), ensure_ascii=False) + "\n")
        return ticket
