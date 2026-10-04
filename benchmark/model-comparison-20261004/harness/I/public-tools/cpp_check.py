"""Build the current fmt checkout with the installed WSL C++ compiler.

This public helper reads only the current checkout, never reference patches.
The source list and flags mirror fmt's bundled format-test CMake target.
"""
from pathlib import Path
import os
import subprocess
import sys


def linux_path(path):
    path = Path(path).resolve()
    return '/mnt/' + path.drive[0].lower() + str(path)[2:].replace('\\', '/')


if os.name == 'nt':
    command = ['wsl.exe', '--exec', 'python3', linux_path(__file__),
               linux_path(Path.cwd()), *sys.argv[1:]]
    sys.exit(subprocess.call(command))

checkout = Path(sys.argv[1]).resolve()
args = sys.argv[2:]
root = Path(__file__).resolve().parent.parent
build = root / 'cpp-build' / checkout.name
build.mkdir(parents=True, exist_ok=True)
sources = ['src/format.cc', 'src/os.cc', 'test/test-main.cc',
           'test/gtest-extra.cc', 'test/util.cc',
           'test/gtest/gmock-gtest-all.cc', 'test/format-test.cc']
binary = build / 'format-test'
compile_args = ['g++', '-std=c++17', '-O0', '-pthread',
                '-DGTEST_HAS_STD_WSTRING=1', '-fno-delete-null-pointer-checks',
                '-Iinclude', '-Itest/gtest', *sources, '-o', str(binary)]
print('Building the current checkout with installed g++...', flush=True)
code = subprocess.call(compile_args, cwd=checkout)
if code:
    sys.exit(code)
sys.exit(subprocess.call([str(binary), '--gtest_color=no', *args], cwd=checkout))
