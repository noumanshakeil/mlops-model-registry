"""Filesystem model registry MVP."""
from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path

ROOT = Path("registry")

def register(name: str, artifact: Path, stage: str = "staging") -> Path:
    assert artifact.exists()
    ver = int(time.time())
    dest = ROOT / name / f"v{{ver}}"
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(artifact, dest / artifact.name)
    meta = {"name": name, "version": ver, "stage": stage, "file": artifact.name}
    (dest / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (ROOT / name / "latest.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return dest

def promote(name: str, stage: str = "production") -> None:
    latest = json.loads((ROOT / name / "latest.json").read_text(encoding="utf-8"))
    latest["stage"] = stage
    ver_dir = ROOT / name / f"v{{latest['version']}}"
    (ver_dir / "meta.json").write_text(json.dumps(latest, indent=2), encoding="utf-8")
    (ROOT / name / "latest.json").write_text(json.dumps(latest, indent=2), encoding="utf-8")
    print(json.dumps(latest, indent=2))

def main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("register")
    r.add_argument("name")
    r.add_argument("artifact", type=Path)
    pr = sub.add_parser("promote")
    pr.add_argument("name")
    pr.add_argument("--stage", default="production")
    args = p.parse_args()
    if args.cmd == "register":
        print(register(args.name, args.artifact))
    else:
        promote(args.name, args.stage)

if __name__ == "__main__":
    main()
