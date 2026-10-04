import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
cid=sys.argv[1]
work=(ROOT/'cases'/cid).resolve()
assert work.parent==(ROOT/'cases').resolve() and (work/'.git').exists()
cmd=['wsl.exe','--cd','/mnt/d/'+work.as_posix()[3:],'--exec','env',
     'CARGO_TARGET_DIR=/home/kk789/masters-nudge-rust-target/'+cid,
     'CARGO_BUILD_JOBS=2','RUSTFLAGS=-Awarnings','CARGO_NET_OFFLINE=true',
     '/home/kk789/.cargo/bin/cargo',*sys.argv[2:]]
raise SystemExit(subprocess.call(cmd))
