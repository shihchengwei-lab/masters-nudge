import shutil
from pathlib import Path


def install(target_dir):
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    installed = target / "mn_cli.py"
    shutil.copy2(Path(__file__).with_name("mn_cli.py"), installed)
    return installed
