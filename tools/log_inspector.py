"""Pretty-print a Delta table's _delta_log."""

import json
import sys
from pathlib import Path


def summarize(action: str, obj: dict) -> str:
    if action == "add":
        path = obj.get("path", "")
        size = obj.get("size", "?")
        stats = obj.get("stats", {})
        return f"add path={path[:70]} size={size} stats={len(str(stats))}b"
    if action == "remove":
        path = obj.get("path", "")
        return f"remove path={path[:70]}"
    if action == "metaData":
        schema = obj.get("schemaString", "")
        return f"metaData schema_len={len(schema)}"
    if action == "protocol":
        return f"protocol reader={obj.get('minReaderVersion')} writer={obj.get('minWriterVersion')}"
    if action == "commitInfo":
        return f"commitInfo op={obj.get('operation')} ts={obj.get('timestamp')}"
    return f"{action} keys={list(obj.keys())}"


def inspect(table_path: Path) -> None:
    log_dir = Path(table_path) / "_delta_log"
    if not log_dir.exists():
        print(f"No _delta_log found at {log_dir}")
        sys.exit(1)

    print(f"Delta log for: {table_path}\n")

    version_files = sorted(log_dir.glob("*.json"))
    for vf in version_files:
        print(f"--- {vf.name} ---")
        for line in vf.read_text(encoding="utf-8").splitlines():
            obj = json.loads(line)
            for action, payload in obj.items():
                print(f"  {summarize(action, payload)}")
        print()

    checkpoints = sorted(log_dir.glob("*.checkpoint*.parquet"))
    if checkpoints:
        print("Checkpoints:")
        for cp in checkpoints:
            print(f"  {cp.name}")


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <delta-table-path>")
        sys.exit(1)
    inspect(Path(sys.argv[1]))


if __name__ == "__main__":
    main()
