#!/usr/bin/env python3
"""Validate integrity-critical fields in the committed Supertonic catalog."""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = ROOT / "catalog" / "bundles.json"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REV_RE = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_MODELS = {"duration_predictor", "text_encoder", "vector_estimator", "vocoder"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    args = parser.parse_args()
    data = json.loads(args.catalog.read_text(encoding="utf-8"))
    errors: list[str] = []
    source = data.get("source") or {}
    revision = source.get("revision")
    if not isinstance(revision, str) or REV_RE.fullmatch(revision) is None:
        errors.append("source.revision must be a lowercase 40-character SHA")
    bundles = data.get("bundles")
    if not isinstance(bundles, dict) or not bundles:
        errors.append("bundles must be a non-empty mapping")
        bundles = {}
    if source.get("bundle_count") != len(bundles):
        errors.append("source.bundle_count does not match bundles")
    artifact_count = 0
    for bundle_id, bundle in bundles.items():
        seen: set[tuple[str, str | None]] = set()
        components: set[str] = set()
        style_components: set[str] = set()
        for i, artifact in enumerate(bundle.get("artifacts") or []):
            artifact_count += 1
            label = f"{bundle_id}.artifacts[{i}]"
            key = (artifact.get("role"), artifact.get("component"))
            if key in seen:
                errors.append(f"{label}: duplicate role/component {key!r}")
            seen.add(key)
            size = artifact.get("size")
            if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
                errors.append(f"{label}: size must be a positive integer")
            sha = artifact.get("sha256")
            if not isinstance(sha, str) or SHA256_RE.fullmatch(sha) is None:
                errors.append(f"{label}: invalid sha256")
            url = artifact.get("url")
            if not isinstance(url, str) or not revision or f"/resolve/{revision}/" not in url:
                errors.append(f"{label}: URL is not pinned to source revision")
            if artifact.get("role") == "model" and isinstance(artifact.get("component"), str):
                components.add(artifact["component"])
            if artifact.get("role") == "voice_style" and isinstance(artifact.get("component"), str):
                style_components.add(artifact["component"])
        if components != REQUIRED_MODELS:
            errors.append(f"{bundle_id}: model components {sorted(components)} != {sorted(REQUIRED_MODELS)}")
        if ("config", None) not in seen or ("unicode_indexer", None) not in seen:
            errors.append(f"{bundle_id}: config/unicode_indexer artifacts are required")
        voices = bundle.get("voices") or []
        voice_names = {v.get("name") for v in voices if isinstance(v, dict)}
        for voice in voices:
            component = voice.get("artifact_component") if isinstance(voice, dict) else None
            if component not in style_components:
                errors.append(f"{bundle_id}: voice {voice!r} has no style artifact")
        if bundle.get("default_voice") not in voice_names:
            errors.append(f"{bundle_id}: default_voice is not declared")
        if bundle.get("default_language") not in set(bundle.get("languages") or []):
            errors.append(f"{bundle_id}: default_language is not declared")
        if bundle.get("runtime", {}).get("sample_rate") != bundle.get("sample_rate"):
            errors.append(f"{bundle_id}: runtime/sample_rate mismatch")
    if errors:
        print("Catalog integrity check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Catalog integrity check passed: bundles={len(bundles)} artifacts={artifact_count}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
