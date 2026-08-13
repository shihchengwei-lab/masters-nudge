import shutil
from pathlib import Path


def install(target_dir):
    source = Path(__file__).parent
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    for path in source.iterdir():
        if path.name == "note_cli.py" or path.suffix == ".json":
            shutil.copy2(path, target / path.name)
    return target / "note_cli.py"
