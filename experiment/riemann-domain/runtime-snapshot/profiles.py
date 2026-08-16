"""Repository-scoped domain and reviewer profiles."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .contracts import SessionRef
from .runtime import RuntimeSettings


PROFILE_SCHEMA_VERSION = 1
PROFILE_DIR = "workspace-profiles"
DOMAINS = ("software", "riemann")
REVIEW_MODES = ("all", "stop_only")
RIEMANN_STAGES = ("frame", "explore", "attack", "prove")
CLOUD_PROVIDERS = ("anthropic", "openai")


@dataclass(frozen=True)
class WorkspaceProfile:
    domain: str = "software"
    stage: str = ""
    provider: str = ""
    model: str = ""
    review_mode: str = "all"
    workspace: str = ""
    source: str = "default"


def normalize_workspace(workspace: str | Path) -> str:
    raw = str(workspace or "").strip()
    if not raw:
        return ""
    try:
        resolved = str(Path(raw).expanduser().resolve())
    except OSError:
        resolved = str(Path(raw).expanduser().absolute())
    return os.path.normcase(resolved)


def session_workspace(session: SessionRef) -> str:
    return normalize_workspace(session.repo_root or session.cwd)


def workspace_profile_path(data_dir: Path, workspace: str | Path) -> Path:
    normalized = normalize_workspace(workspace)
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:24]
    return Path(data_dir) / PROFILE_DIR / f"{digest}.json"


def _validate(
    payload: object, *, expected_workspace: str = ""
) -> tuple[WorkspaceProfile, str]:
    if not isinstance(payload, dict):
        return WorkspaceProfile(), "workspace profile root must be an object"
    required = {
        "schema_version",
        "workspace",
        "domain",
        "stage",
        "provider",
        "model",
        "review_mode",
    }
    if set(payload) != required or payload.get("schema_version") != PROFILE_SCHEMA_VERSION:
        return WorkspaceProfile(), "workspace profile has an invalid shape"
    values = {key: payload.get(key) for key in required - {"schema_version"}}
    if any(not isinstance(value, str) for value in values.values()):
        return WorkspaceProfile(), "workspace profile values must be strings"
    workspace = normalize_workspace(str(values["workspace"]))
    if not workspace or (expected_workspace and workspace != expected_workspace):
        return WorkspaceProfile(), "workspace profile identity does not match"
    domain = str(values["domain"]).strip().lower()
    stage = str(values["stage"]).strip().lower()
    provider = str(values["provider"]).strip().lower()
    model = str(values["model"]).strip()
    review_mode = str(values["review_mode"]).strip().lower()
    if domain not in DOMAINS:
        return WorkspaceProfile(), f"unsupported domain: {domain}"
    if domain == "riemann" and stage not in RIEMANN_STAGES:
        return WorkspaceProfile(), f"unsupported Riemann stage: {stage}"
    if domain == "software" and stage:
        return WorkspaceProfile(), "software profile stage must stay empty"
    if provider not in CLOUD_PROVIDERS or not model:
        return WorkspaceProfile(), "workspace profile reviewer is invalid"
    if review_mode not in REVIEW_MODES:
        return WorkspaceProfile(), f"unsupported review mode: {review_mode}"
    return (
        WorkspaceProfile(
            domain,
            stage,
            provider,
            model,
            review_mode,
            workspace,
            "workspace_profile",
        ),
        "",
    )


def load_workspace_profile(
    data_dir: Path, session: SessionRef
) -> tuple[WorkspaceProfile, str]:
    workspace = session_workspace(session)
    if not workspace:
        return WorkspaceProfile(), ""
    path = workspace_profile_path(data_dir, workspace)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return WorkspaceProfile(workspace=workspace), ""
    except (OSError, ValueError) as exc:
        return WorkspaceProfile(workspace=workspace), f"cannot read workspace profile: {exc}"
    return _validate(payload, expected_workspace=workspace)


def configure_workspace_profile(
    data_dir: Path,
    workspace: str | Path,
    *,
    domain: str,
    stage: str,
    provider: str,
    model: str,
    review_mode: str,
) -> dict:
    normalized = normalize_workspace(workspace)
    payload = {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "workspace": normalized,
        "domain": str(domain).strip().lower(),
        "stage": str(stage).strip().lower(),
        "provider": str(provider).strip().lower(),
        "model": str(model).strip(),
        "review_mode": str(review_mode).strip().lower(),
    }
    profile, error = _validate(payload, expected_workspace=normalized)
    path = workspace_profile_path(data_dir, normalized)
    if error:
        return {"saved": False, "path": str(path), "error": error}
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".tmp",
        prefix="workspace-profile-",
        dir=path.parent,
        delete=False,
        encoding="utf-8",
    )
    temp_path = Path(handle.name)
    try:
        json.dump(payload, handle, ensure_ascii=False)
        handle.write("\n")
        handle.close()
        os.replace(temp_path, path)
    finally:
        try:
            handle.close()
        except Exception:
            pass
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass
    return {"saved": True, "path": str(path), "error": "", **profile.__dict__}


def reset_workspace_profile(data_dir: Path, workspace: str | Path) -> dict:
    path = workspace_profile_path(data_dir, workspace)
    try:
        existed = path.exists()
        path.unlink(missing_ok=True)
    except OSError as exc:
        return {"reset": False, "removed": False, "path": str(path), "error": str(exc)}
    return {"reset": True, "removed": existed, "path": str(path), "error": ""}


def resolve_reviewer(
    settings: RuntimeSettings,
    profile: WorkspaceProfile,
    *,
    environ: Mapping[str, str] | None = None,
) -> tuple[str, str, str]:
    """Apply a workspace reviewer below explicit environment overrides."""
    environment = os.environ if environ is None else environ
    explicit_provider = str(
        environment.get("MASTERS_NUDGE_PROVIDER")
        or environment.get("BUDDY_PROVIDER")
        or ""
    ).strip()
    explicit_model = str(
        environment.get("MASTERS_NUDGE_MODEL")
        or environment.get("BUDDY_MODEL")
        or ""
    ).strip()
    if profile.source != "workspace_profile":
        return settings.provider, settings.model, settings.configuration_source
    provider = explicit_provider.lower() or profile.provider
    model = explicit_model or profile.model
    source = "environment" if explicit_provider or explicit_model else profile.source
    return provider, model, source
