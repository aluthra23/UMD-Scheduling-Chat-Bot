from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from term_utils import TERM_PATTERN


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], *, cwd: Path, env: dict[str, str]) -> None:
    print(f"Running {' '.join(command)} in {cwd}", flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape and upload one UMD term.")
    parser.add_argument("term_id", help="UMD term ID in YYYY01 or YYYY08 format")
    parser.add_argument("--recreate", action="store_true", help="Replace an existing collection")
    args = parser.parse_args()

    if not TERM_PATTERN.fullmatch(args.term_id):
        parser.error("term_id must have the format YYYY01 or YYYY08")

    env = os.environ.copy()
    env["UMD_TERM_ID"] = args.term_id
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    python = sys.executable

    run([python, "main_soc_scraper.py"], cwd=ROOT / "schedule_of_classes_scraper", env=env)
    run([python, "main_catalog_scraper.py"], cwd=ROOT / "course_catalog_scraper", env=env)
    run([python, "main_gen_ed.py"], cwd=ROOT / "gen_eds", env=env)

    upload_command = [python, "main.py", "--collection", args.term_id]
    if args.recreate:
        upload_command.append("--recreate")
    run(upload_command, cwd=ROOT, env=env)


if __name__ == "__main__":
    main()
