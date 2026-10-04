"""Run pytest against the current checkout using the prepared Linux Python.

Only the current checkout and shared third-party dependencies are mounted.
"""
from pathlib import Path
import subprocess
import sys

IMAGE = 'sha256:db698fbb2f50522f181849bd38245f448f3feb287b5d6ebabcf527bf3da901d2'
ROOT = Path(__file__).resolve().parent.parent


def linux_path(path):
    path = Path(path).resolve()
    return '/mnt/' + path.drive[0].lower() + str(path)[2:].replace('\\', '/')


args = sys.argv[1:]
if not args:
    raise SystemExit('Supply pytest test paths or arguments.')
dependency_set = 'pydantic-feature' if Path.cwd().name == 'fb-pydantic-self' else 'featurebench'
if dependency_set == 'pydantic-feature':
    args += ['-p', 'pytest_benchmark.plugin', '-p', 'pytest_mock', '--benchmark-disable']
command = ['wsl.exe', '-u', 'root', '--exec', 'docker', 'run', '--rm',
           '--pull=never', '--network', 'none', '--cpus', '4', '--memory', '6g',
           '-v', linux_path(Path.cwd()) + ':/task',
           '-v', linux_path(ROOT/'shared-env'/dependency_set) + ':/deps:ro',
           '-w', '/task', '-e', 'PYTHONPATH=/task/src:/task:/deps',
           '-e', 'PYTHONDONTWRITEBYTECODE=1', '-e', 'PYTEST_DISABLE_PLUGIN_AUTOLOAD=1',
           '-e', 'PYTEST_ADDOPTS=',
           '-e', 'METAFLOW_USER=benchmark', '-e', 'METAFLOW_HOME=/tmp/metaflow',
           '--entrypoint', 'python3', IMAGE, '-m', 'pytest', *args,
           '-q', '-p', 'no:cacheprovider']
sys.exit(subprocess.call(command))
