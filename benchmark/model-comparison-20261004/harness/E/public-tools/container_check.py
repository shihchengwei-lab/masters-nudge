"""Run the repository's public tests using the preinstalled Linux environment."""
import argparse
from pathlib import Path
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('case')
p.add_argument('tests',nargs='*')
a=p.parse_args()
cwd=Path.cwd().resolve()
if cwd != (ROOT/'cases'/a.case).resolve():
    raise SystemExit('Run this helper from the case repository root.')
subprocess.run(['git','add','-N','.'],cwd=cwd,check=True,capture_output=True)
patch=ROOT/'public-runs'/a.case/(str(time.time_ns())+'.patch')
patch.parent.mkdir(parents=True,exist_ok=True)
patch.write_bytes(subprocess.check_output(['git','diff','--binary','HEAD'],cwd=cwd))
args=['wsl.exe','-u','root','--exec','python3',
      '/mnt/d/masters-nudge-benchmark/round-10-calibration/pro_env.py','public',a.case,
      '--patch','/mnt/d/'+patch.as_posix()[3:],'--tests',*a.tests]
raise SystemExit(subprocess.run(args).returncode)
