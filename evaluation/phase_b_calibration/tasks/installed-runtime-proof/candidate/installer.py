import shutil
from pathlib import Path


def install(target_dir):
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    installed = target / "note_cli.py"
    shutil.copy2(Path(__file__).with_name("note_cli.py"), installed)
    return installed
