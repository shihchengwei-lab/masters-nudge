import shutil
from pathlib import Path


def install(target_dir):
    source = Path(__file__).parent
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    for name in ("note_cli.py", "templates.json"):
        shutil.copy2(source / name, target / name)
    return target / "note_cli.py"
