from pathlib import Path

from app.core.config import settings


def resolve_path(path: str) -> Path:
    backend_root = Path(__file__).resolve().parent.parent.parent
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return (backend_root / candidate).resolve()


def configure_media_dirs() -> tuple[str, str, str]:
    media_root = resolve_path(settings.media_root)
    logos_dir = resolve_path(settings.logos_dir)
    exports_dir = resolve_path(settings.exports_dir)

    settings.media_root = str(media_root)
    settings.logos_dir = str(logos_dir)
    settings.exports_dir = str(exports_dir)

    try:
        for directory in (media_root, logos_dir, exports_dir):
            directory.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        fallback_root = Path("/tmp/invoice-media")
        media_root = fallback_root
        logos_dir = fallback_root / "logos"
        exports_dir = fallback_root / "exports"

        for directory in (media_root, logos_dir, exports_dir):
            directory.mkdir(parents=True, exist_ok=True)

        settings.media_root = str(media_root)
        settings.logos_dir = str(logos_dir)
        settings.exports_dir = str(exports_dir)

    return settings.media_root, settings.logos_dir, settings.exports_dir
