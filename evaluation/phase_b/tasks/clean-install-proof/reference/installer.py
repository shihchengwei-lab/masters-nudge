import shutil
from pathlib import Path


def install(target_dir):
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).resolve().parent
    installed = target / "mn_cli.py"
    shutil.copy2(source / "mn_cli.py", installed)
    shutil.copy2(source / "defaults.json", target / "defaults.json")
    return installed
