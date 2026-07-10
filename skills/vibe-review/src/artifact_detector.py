from pathlib import Path


_DEFAULT_TYPE_MAP = {
    "md": "markdown",
    "markdown": "markdown",
    "json": "json",
    "yaml": "yaml",
    "yml": "yaml",
}

_FALLBACK = "unsupported"


def detect_type(artifact_path: str, type_map: dict[str, str] | None = None) -> str:
    ext = Path(artifact_path).suffix.lstrip(".")
    if not ext:
        return _FALLBACK
    mapping = type_map if type_map is not None else _DEFAULT_TYPE_MAP
    return mapping.get(ext, _FALLBACK)
