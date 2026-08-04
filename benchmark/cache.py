import hashlib
import json
from pathlib import Path
from typing import Any

class ResponseCache:
    def __init__(self, root: str | Path = "cache/responses") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def key(self, model: str, prompt: str, system_prompt: str | None) -> str:
        payload = json.dumps({"model": model, "prompt": prompt, "system_prompt": system_prompt}, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def get(self, key: str) -> dict[str, Any] | None:
        path = self.root / f"{key}.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None

    def set(self, key: str, value: dict[str, Any]) -> None:
        (self.root / f"{key}.json").write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
