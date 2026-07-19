"""Casos de uso comunes: carga, normalizacion, estadisticas y exportacion."""
from __future__ import annotations
import json
import logging
import hashlib
from collections import Counter
from pathlib import Path
from .models import Finding
LOGGER = logging.getLogger(__name__)

class Service:
    """Base reutilizable para adaptadores especificos de cada herramienta."""
    def inspect(self, target: Path) -> list[Finding]:
        if not target.exists(): raise FileNotFoundError(target)
        current_hash = hashlib.sha256(target.read_bytes()).hexdigest()
        baseline_path = target.parent / f".{target.name}.baseline"
        if not baseline_path.exists():
            baseline_path.write_text(current_hash, encoding="utf-8")
            return [Finding(category="baseline_created", value=current_hash, source=str(target), severity="info")]
        previous_hash = baseline_path.read_text(encoding="utf-8").strip()
        if current_hash != previous_hash:
            return [Finding(category="file_modified", value=f"{previous_hash} -> {current_hash}", source=str(target), severity="high")]
        return [Finding(category="file_unchanged", value=current_hash, source=str(target), severity="info")]
    @staticmethod
    def export(findings: list[Finding], destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps([item.to_dict() for item in findings], indent=2) + "\n", encoding="utf-8")
    @staticmethod
    def stats(findings: list[Finding]) -> dict[str, object]:
        return {"total": len(findings), "by_category": dict(Counter(item.category for item in findings)), "by_severity": dict(Counter(item.severity for item in findings))}
