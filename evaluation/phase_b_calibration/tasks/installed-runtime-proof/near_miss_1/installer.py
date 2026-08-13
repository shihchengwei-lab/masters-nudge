import shutil
from pathlib import Path


def install(target_dir):
    source = Path(__file__).parent
    target = Path(target_dir)
    assets = target / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source / "note_cli.py", target / "note_cli.py")
    shutil.copy2(source / "templates.json", assets / "templates.json")
    return target / "note_cli.py"
