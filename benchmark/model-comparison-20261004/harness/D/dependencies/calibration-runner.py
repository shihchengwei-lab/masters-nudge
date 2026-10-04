"""Round 10 calibration. Product sources are never mutated by this harness."""
from __future__ import annotations
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
SELECTION = Path(r'D:\masters-nudge-benchmark\selection\round-10')
PRODUCT = Path(r'C:\Users\kk789\Desktop\GH_repos\masters-nudge')
MANIFEST = json.loads((SELECTION/'candidate-manifest.json').read_text(encoding='utf-8'))
CASES = {c['case_id']: c for c in MANIFEST['cases']}
COMMANDS = {
    'fb-pydantic-self': [[sys.executable,str(ROOT/'public-tools/feature_python_check.py'),'tests/test_types_self.py','tests/test_deprecated_fields.py','tests/test_experimental_arguments_schema.py','tests/benchmarks/test_isinstance.py','tests/test_titles.py','tests/benchmarks/test_attribute_access.py']],
    'fb-sympy-puiseux': [[sys.executable,str(ROOT/'public-tools/feature_python_check.py'),'sympy/polys/tests/test_puiseux.py','sympy/core/tests/test_eval.py','sympy/matrices/expressions/tests/test_companion.py','sympy/liealgebras/tests/test_type_G.py','sympy/multipledispatch/tests/test_core.py','sympy/plotting/intervalmath/tests/test_intervalmath.py']],
    'fb-packaging-metadata': [[sys.executable,str(ROOT/'public-tools/feature_python_check.py'),'tests/test_metadata.py','tests/test_tags.py','tests/test_specifiers.py','tests/test_markers.py','tests/test_structures.py','tests/test_musllinux.py']],
    'fb-metaflow-stubs': [[sys.executable,str(ROOT/'public-tools/feature_python_check.py'),'test/cmd/develop/test_stub_generator.py','test/unit/test_multicore_utils.py','test/unit/test_argo_workflows_cli.py','test/unit/test_pypi_parsers.py','test/unit/test_local_metadata_provider.py','test/unit/test_pypi_decorator.py']],
    'chalk-671': [['cargo','test','--test','lib']],
    'fmt-3750': [[sys.executable,str(ROOT/'public-tools/cpp_check.py')]],
    'fmt-2310': [[sys.executable,str(ROOT/'public-tools/cpp_check.py')]],
    'ndarray-986': [['cargo','test','--features','approx,serde,rayon','--test','iterators']],
    'algorand-454': [['node','-r','ts-node/register','tests/mocha.js','--reporter','spec']],
    'pyfakefs-1286': [[sys.executable,'-m','pytest','pyfakefs/tests/fake_filesystem_vs_real_test.py','-q','-p','no:cacheprovider']],
    'sqlglot-6374': [[sys.executable,'-m','pytest','tests/dialects/test_oracle.py','tests/test_parser.py','-q','-p','no:cacheprovider']],
    'sympy-28660': [[sys.executable,str(ROOT/'public-tools/sympy_legacy_check.py'),'sympy/integrals/tests/test_rationaltools.py'], [sys.executable,'-m','pytest',str(ROOT/'public-tools/test_noise_integrals.py'),'-q','-p','no:cacheprovider']],
    'config-rs-207': [['cargo','test','--all-features','--test','async_builder','--test','defaults','--test','merge','--test','set','--test','get','--test','empty','--test','env','--test','legacy_tests','--test','file_json','--test','file_toml']],
    'regexp-404': [['node','node_modules/mocha/bin/mocha','--require','ts-node/register','tests/lib/rules/no-dupe-disjunctions.ts','--reporter','spec','--no-color','--timeout','60000']],
    'mpmath-819': [[sys.executable,str(ROOT/'public-tools/seeded_pytest.py'),'mpmath/tests/test_format.py','mpmath/tests/test_str.py','mpmath/tests/test_basic_ops.py','-q','-p','no:cacheprovider']],
    'django-15629': [[r'D:\masters-nudge-benchmark\round-9-calibration\cases\django__django-11815\.venv\Scripts\python.exe','tests/runtests.py','migrations.test_operations','--settings=test_sqlite','--parallel=1','--verbosity=2']],
    'sympy-16597': [[r'C:\Users\kk789\AppData\Roaming\uv\python\cpython-3.8-windows-x86_64-none\python.exe','bin/test','sympy/core/tests/test_assumptions.py','sympy/functions/elementary/tests/test_miscellaneous.py','sympy/assumptions/tests/test_query.py','sympy/tensor/tests/test_indexed.py','sympy/core/tests/test_power.py']],
    'django-13344': [[r'D:\masters-nudge-benchmark\round-9-calibration\cases\django__django-11815\.venv\Scripts\python.exe','tests/runtests.py','deprecation.test_middleware_mixin','cache.tests.CacheMiddlewareTest','--settings=test_sqlite','--parallel=1','--verbosity=2']],
    'django-15128': [[r'D:\masters-nudge-benchmark\round-9-calibration\cases\django__django-11815\.venv\Scripts\python.exe','tests/runtests.py','queries','--settings=test_sqlite','--parallel=1','--verbosity=2']],
    'sphinx-7590': [[r'D:\masters-nudge-benchmark\round-9-calibration\cases\sphinx-doc__sphinx-7748\.venv\Scripts\python.exe','-m','pytest','tests/test_domain_cpp.py','tests/test_domain_c.py','-q']],
    'django-15957': [[r'D:\masters-nudge-benchmark\round-9-calibration\cases\django__django-11815\.venv\Scripts\python.exe','tests/runtests.py','prefetch_related','--settings=test_sqlite','--parallel=1','--verbosity=2']],
    'clap-2297': [['cargo','test','-p','clap@3.0.0-beta.2','--test','grouped_values','--test','multiple_occurrences','--test','multiple_values','--test','flags','--test','opts','--test','positionals','--test','delimiters','--test','conflicts','--test','require','--test','indices','--test','default_vals','--test','tests','--test','groups']],
    'tokio-6205': [['cargo','test','-p','tokio@1.35.1','--features','full','--test','sync_mpsc']],
    'tracing-1523': [['cargo','test','-p','tracing-subscriber','--features','env-filter,registry,regex/unicode','--tests']],
    'tokio-5179': [[sys.executable,str(ROOT/'public-tools/rust_check.py'),'tokio-5179','test','-p','tokio@1.21.2','--features','full','--test','task_local_set']],
    'clap-3420': [['cargo','test','--test','builder']],
    'clap-4523': [['cargo','test','--test','builder']],
    'bytes-547': [['cargo','test','--test','test_bytes','--test','test_bytes_odd_alloc','--test','test_bytes_vec_alloc']],
    'tracing-1983': [['cargo','test','-p','tracing-subscriber','--features','env-filter,registry,regex/unicode','--test','env_filter']],
    'tokio-6618': [['cargo','test','-p','tokio-util','--features','full','--test','sync_cancellation_token']],
}
SUPPLEMENT = {
    'tracing-1523': ('tracing-subscriber/tests/benchmark_public_layer_tests.rs', (ROOT/'supplements/tracing-1523-public-layer-tests.rs').read_text(encoding='utf-8')),
    'bytes-547': ('tests/test_bytes.rs', '''

#[test]
fn benchmark_unique_vec_allocation_is_transferred() {
    let mut source = Vec::with_capacity(128);
    source.extend_from_slice(b"owned allocation");
    let bytes = Bytes::from(source);
    let original = bytes.as_ptr();
    let restored = Vec::<u8>::from(bytes);
    assert_eq!(restored.as_slice(), b"owned allocation");
    assert_eq!(restored.as_ptr(), original);
}
'''),
    'tokio-6618': ('tokio-util/tests/sync_cancellation_token.rs', '''

#[test]
fn benchmark_cancellation_drops_pending_future() {
    use std::sync::{Arc, atomic::{AtomicBool, Ordering}};
    struct PendingDrop(Arc<AtomicBool>);
    impl Future for PendingDrop {
        type Output = ();
        fn poll(self: std::pin::Pin<&mut Self>, _: &mut Context<'_>) -> Poll<()> {
            Poll::Pending
        }
    }
    impl Drop for PendingDrop {
        fn drop(&mut self) { self.0.store(true, Ordering::SeqCst); }
    }
    let dropped = Arc::new(AtomicBool::new(false));
    let token = CancellationToken::new();
    let mut future = Box::pin(token.run_until_cancelled(PendingDrop(dropped.clone())));
    let (waker, _) = new_count_waker();
    assert_eq!(future.as_mut().poll(&mut Context::from_waker(&waker)), Poll::Pending);
    assert!(!dropped.load(Ordering::SeqCst));
    token.cancel();
    assert_eq!(future.as_mut().poll(&mut Context::from_waker(&waker)), Poll::Ready(None));
    drop(future);
    assert!(dropped.load(Ordering::SeqCst));
}
'''),
}

def sha(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode('utf-8')).hexdigest()

def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    tmp.replace(path)

def env(cid):
    e=os.environ.copy()
    for name in ['tmp','cargo-target']:
        (ROOT/name).mkdir(exist_ok=True)
    e.update(PYTHONUTF8='1',PYTHONIOENCODING='utf-8',CARGO_BUILD_JOBS='2',
             CARGO_TARGET_DIR=str(ROOT/'cargo-target'/cid),RUSTFLAGS='-Awarnings',
             TEMP=str(ROOT/'tmp'),TMP=str(ROOT/'tmp'))
    if CASES[cid]['language']=='Python': e['PYTHONPATH']=str(work(cid))
    if cid == 'sympy-16597': e['PYTHONPATH']+=os.pathsep+str(ROOT/'shared-env/sympy38')
    return e

def command(args,cwd,timeout=900,e=None):
    return subprocess.run(args,cwd=cwd,env=e,capture_output=True,text=True,
                          encoding='utf-8',errors='replace',timeout=timeout)

def checked(args,cwd,timeout=900,e=None):
    r=command(args,cwd,timeout,e)
    if r.returncode:
        raise RuntimeError(f'{args!r}\n{(r.stdout+r.stderr)[-4000:]}')
    return r.stdout

def work(cid):
    return ROOT/'cases'/cid

def case_source(cid):
    return SELECTION/'cases'/cid

def assert_work(path):
    resolved=path.resolve()
    if resolved.parent != (ROOT/'cases').resolve() or not (resolved/'.git').exists():
        raise RuntimeError(f'Not an isolated calibration worktree: {resolved}')

def clean(cid):
    p=work(cid); assert_work(p)
    checked(['git','reset','--hard',CASES[cid]['base_commit']],p)
    checked(['git','clean','-fd'],p)

def apply(cid,name):
    checked(['git','apply','--whitespace=nowarn',str(case_source(cid)/name)],work(cid))

def test_patch(cid):
    apply(cid,'test.patch')
    if cid in SUPPLEMENT:
        name,code=SUPPLEMENT[cid]
        path=work(cid)/name
        with path.open('a',encoding='utf-8',newline='\n') as f: f.write(code)

def emit(data):
    print(json.dumps(data,ensure_ascii=False),flush=True)

def prepare(cid):
    c=CASES[cid]; p=work(cid)
    cache=Path(r'D:\masters-nudge-benchmark\round-9-calibration\repos')/(c['repo'].replace('/','__')+'.git')
    if not cache.exists():
        cache=ROOT/'repos'/(c['repo'].replace('/','__')+'.git')
        if not cache.exists():
            cache.mkdir(parents=True,exist_ok=True)
            checked(['git','init','--bare'],cache)
            checked(['git','remote','add','origin','https://github.com/'+c['repo']+'.git'],cache)
    if command(['git','cat-file','-e',c['base_commit']+'^{commit}'],cache).returncode:
        checked(['git','fetch','--depth','1','origin',c['base_commit']],cache,1800)
    if not (p/'.git').exists():
        p.parent.mkdir(parents=True,exist_ok=True)
        checked(['git','-c','core.autocrlf=false','worktree','add','--detach',str(p),c['base_commit']],cache)
    assert checked(['git','rev-parse','HEAD'],p).strip()==c['base_commit']
    out={'case':cid,'prepared':True,'worktree':str(p),'base_commit':c['base_commit']}
    save(ROOT/'state'/cid/'prepare.json',out); emit(out)

def verify(cid,stage):
    out=[]
    for i,args in enumerate(COMMANDS[cid],1):
        start=time.monotonic()
        r=command(args,work(cid),1800,env(cid))
        text=r.stdout+r.stderr
        log=ROOT/'logs'/cid/f'{stage}-{i}.txt'; log.parent.mkdir(parents=True,exist_ok=True)
        log.write_text(text,encoding='utf-8')
        summaries=[tuple(map(int,m)) for m in re.findall(r'test result: (?:ok|FAILED)\. (\d+) passed; (\d+) failed; (\d+) ignored;',text)]
        if CASES[cid]['language']=='Python':
            ran=re.search(r'^Ran (\d+) tests? in ',text,re.M)
            fail=re.search(r'^FAILED \(([^\n]+)\)',text,re.M)
            failures=sum(int(x) for x in re.findall(r'(?:failures|errors)=(\d+)',fail.group(1))) if fail else 0
            skipped_match=re.search(r'^(?:OK|FAILED) \([^\n]*skipped=(\d+)',text,re.M)
            skipped=int(skipped_match.group(1)) if skipped_match else 0
            summaries=[(max(0,int(ran.group(1))-failures-skipped),failures,skipped)] if ran else []
            if not ran:
                summary_line=next((line for line in reversed(text.splitlines()) if re.search(r'\b\d+ (?:passed|failed|errors?)\b',line)), '')
                counts={key:int(n) for n,key in re.findall(r'(\d+) (passed|failed|errors?|skipped|xfailed)',summary_line)}
                if counts: summaries=[(counts.get('passed',0),counts.get('failed',0)+counts.get('error',0)+counts.get('errors',0),counts.get('skipped',0)+counts.get('xfailed',0))]
        if cid in ['regexp-404', 'algorand-454']:
            counts={k:int(n) for n,k in re.findall(r'^\s*(\d+) (passing|failing|pending)\b',text,re.M)}
            summaries=[(counts.get('passing',0),counts.get('failing',0),counts.get('pending',0))]
        if cid.startswith('fmt-'):
            counts={k:int(n) for k,n in re.findall(r'^\[\s*(PASSED|FAILED|SKIPPED)\s*\]\s+(\d+) tests?\b',text,re.M)}
            summaries=[(counts.get('PASSED',0),counts.get('FAILED',0),counts.get('SKIPPED',0))]
        out.append(dict(command=args,exit_code=r.returncode,passed=sum(x[0] for x in summaries),
                        failed=sum(x[1] for x in summaries),ignored=sum(x[2] for x in summaries),
                        rust_errors=re.findall(r'error\[E\d+\]:[^\n]*',text),
                        elapsed_seconds=round(time.monotonic()-start,3),log=str(log)))
    return out

def preflight(cid):
    state=ROOT/'state'/cid/'preflight.json'
    if state.exists() and json.loads(state.read_text(encoding='utf-8')).get('valid'):
        emit({'case':cid,'preflight':'already_valid'}); return
    clean(cid); test_patch(cid)
    baseline=verify(cid,'baseline')
    apply(cid,'reference.patch')
    reference=verify(cid,'reference')
    # Baseline compile errors are recorded for inspection; valid reference must execute tests.
    valid=any(x['exit_code']!=0 for x in baseline) and all(x['exit_code']==0 and x['passed']>0 for x in reference)
    supplement_path=ROOT/'supplements'/f'{cid}.json'
    if cid in SUPPLEMENT:
        save(supplement_path,{'path':SUPPLEMENT[cid][0],'code':SUPPLEMENT[cid][1],
                              'basis':'Behavior already published in candidate task.md'})
    out={'case':cid,'valid':valid,'baseline':baseline,'reference':reference,
         'base_commit':CASES[cid]['base_commit'],'task_sha256':sha((case_source(cid)/'task.md').read_bytes())}
    save(state,out); clean(cid)
    emit({'case':cid,'stage':'preflight','valid':valid,'baseline':[(x['exit_code'],x['passed'],x['failed']) for x in baseline],
          'reference':[(x['exit_code'],x['passed'],x['failed']) for x in reference]})

def actor_prompt(cid):
    environment_note = ('\n\nEnvironment note: this old checkout resolves a current regex release. '
                        'For the env_filter tests, use `cargo test -p tracing-subscriber --features '
                        'env-filter,registry,regex/unicode --test env_filter` so Unicode-aware '
                        'case matching is available. This is the verified test configuration.\n'
                        if cid == 'tracing-1983' else '')
    if cid.startswith('fb-'):
        paths = json.loads((case_source(cid)/'oracle.json').read_text(encoding='utf-8'))['PASS_TO_PASS']
        environment_note += '\nEnvironment: Python and dependencies are preinstalled in an offline Linux container. From this checkout use PowerShell `python "'+str(ROOT/'public-tools/feature_python_check.py')+'" '+' '.join(paths)+'` to run existing checks. The helper accepts pytest paths and arguments for your own new tests as well. It mounts only this checkout and third-party dependencies.\n'
    if cid.startswith('fmt-'):
        environment_note += '\nEnvironment: the Linux C++ compiler is preinstalled. From this checkout use PowerShell `python "'+str(ROOT/'public-tools/cpp_check.py')+'"` to build and run the existing format-test suite. The helper compiles this checkout with its bundled Google Test and accepts Google Test arguments such as --gtest_filter=format_test.format_nan. No CMake installation is needed.\n'
    if cid == 'tracing-1523':
        environment_note += '\nEnvironment: run `cargo test -p tracing-subscriber --features env-filter,registry,regex/unicode --tests`. The Unicode feature makes this old checkout compatible with the resolved regex dependency.\n'
    if cid == 'clap-2297':
        environment_note += '\nEnvironment: select the package explicitly with `cargo test -p clap@3.0.0-beta.2`. Relevant existing tests include multiple_occurrences, multiple_values, flags, opts, positionals, delimiters, conflicts, require, indices, default_vals, tests and groups. Cargo otherwise selects unrelated workspace tools too.\n'
    if cid.startswith('django-'):
        args=COMMANDS[cid][0]
        environment_note += '\nEnvironment: dependencies are preinstalled. From this checkout use PowerShell: `& "'+args[0]+'" '+' '.join(args[1:])+'`. PYTHONPATH already selects the current checkout. The interpreter path is an environment dependency, not task source.\n'
    if cid == 'sympy-16597':
        args=COMMANDS[cid][0]
        environment_note += '\nEnvironment: Python 3.8 and mpmath are available. From this checkout use PowerShell: `& "'+args[0]+'" '+' '.join(args[1:])+'`. PYTHONPATH selects this checkout and the preinstalled pure-Python mpmath dependency. The interpreter path is an environment dependency, not task source.\n'
    if cid == 'mpmath-819':
        environment_note += '\nEnvironment: Python and pytest are preinstalled. PYTHONPATH selects this checkout. Run existing formatting/arithmetic checks with `python -m pytest mpmath/tests/test_str.py mpmath/tests/test_basic_ops.py -q`; add your own checks for the new format protocol.\n'
    if cid in ['sqlglot-6374', 'sympy-28660', 'pyfakefs-1286']:
        args = COMMANDS[cid][0]
        environment_note += '\nEnvironment: Python 3.12 and the test dependencies are preinstalled. PYTHONPATH selects this checkout. From PowerShell use `& "'+args[0]+'" '+' '.join(args[1:])+'`.\n'
    if cid == 'sympy-28660':
        environment_note += '\nThe existing SymPy runner executes the unchanged rational-integration suite without requiring the optional hypothesis dependency. The eight numerical examples from the public issue are also available with `python -m pytest "'+str(ROOT/'public-tools/test_noise_integrals.py')+'" -q -p no:cacheprovider`.\n'
    if cid == 'sphinx-7590':
        environment_note += '\nEnvironment: dependencies are preinstalled. From this checkout use PowerShell: `& "D:\\masters-nudge-benchmark\\round-9-calibration\\cases\\sphinx-doc__sphinx-7748\\.venv\\Scripts\\python.exe" -m pytest tests/test_domain_cpp.py tests/test_domain_c.py -q`. PYTHONPATH already selects the current checkout. The interpreter path is an environment dependency, not task source.\n'
    if cid == 'config-rs-207':
        environment_note += '\nEnvironment: Rust and dependency downloads are prewarmed. Run `cargo test --all-features --test defaults --test merge --test set --test get --test empty --test env --test legacy_tests --test file_json --test file_toml`. The old JSON5 parser diagnostic test is incompatible with its resolved dependency; it is outside these selected configuration-merge checks. Preserve existing Cargo dependency requirements except changes needed by the task.\n'
    if cid == 'chalk-671':
        environment_note += '\nEnvironment: Rust and dependencies are prewarmed. Run the solver integration suite with `cargo test --test lib`.\n'
    if cid == 'ndarray-986':
        environment_note += '\nEnvironment: Rust and dependencies are prewarmed. Run the iterator suite with `cargo test --features approx,serde,rayon --test iterators`.\n'
    if cid == 'regexp-404':
        environment_note += '\nEnvironment: Node and npm dependencies are preinstalled. Run the focused rule suite with `node node_modules/mocha/bin/mocha --require ts-node/register tests/lib/rules/no-dupe-disjunctions.ts --reporter spec --no-color --timeout 60000`.\n'
    if cid == 'algorand-454':
        environment_note += '\nEnvironment: Node and npm dependencies are preinstalled. Run the existing SDK checks with `node -r ts-node/register tests/mocha.js --reporter spec`. The ARC-4 file above is task specification, not a solution.\n'
    if cid == 'tokio-5179':
        environment_note += f'\nEnvironment: use the installed Linux Rust toolchain via PowerShell: `python "{ROOT / "public-tools/rust_check.py"}" tokio-5179 test -p tokio@1.21.2 --features full --test task_local_set`. The helper runs this checkout using preinstalled dependencies, offline. It accepts other Cargo arguments for your own tests. Windows compilation is blocked by this old checkout ntapi dependency.\n'
    return ('Complete the repository task. Existing tests are immutable: do not edit, delete, or replace them. '
            'You own implementation and verification. Use apply_patch for edits. Do not commit, install packages, '
            'inspect Git history, use the network, delegate, or use subagents.\n\n'
            +(case_source(cid)/'task.md').read_text(encoding='utf-8')
            +environment_note
            +'\n\nInspect your final diff and run relevant existing checks. Report what changed and what was verified.\n\n'
            +'請高品味的完成任務。\n')

def actor(cid):
    state=ROOT/'state'/cid
    if (state/'actor.json').exists():
        emit({'case':cid,'actor':'already_recorded'}); return
    pre=json.loads((state/'preflight.json').read_text(encoding='utf-8'))
    if not pre.get('valid'): raise RuntimeError('Preflight not valid: '+cid)
    clean(cid)
    p=actor_prompt(cid); out=ROOT/'actors'/cid; out.mkdir(parents=True,exist_ok=True)
    (out/'prompt.txt').write_text(p,encoding='utf-8')
    sys.path.insert(0,str(PRODUCT))
    from masters_nudge.providers import resolve_codex_bin
    binary=resolve_codex_bin()
    args=[binary,'-c','project_doc_max_bytes=0','-c','features.multi_agent=false',
          '-c','model_reasoning_effort="medium"','--disable','hooks','--disable','plugins',
          'exec','--ignore-user-config','--ignore-rules','--skip-git-repo-check','--ephemeral',
          '--json','-s','danger-full-access','-m','gpt-6-sol','-C',str(work(cid)),
          '-o',str(out/'actor-final.txt'),'-']
    save(out/'launch.json',{'command':args,'model':'gpt-6-sol','reasoning':'medium','hooks':False,
                           'prompt_sha256':sha(p),'base_commit':CASES[cid]['base_commit']})
    start=time.monotonic()
    emit({'case':cid,'stage':'actor_started'})
    with (out/'actor-events.jsonl').open('w',encoding='utf-8') as stdout, (out/'actor-stderr.txt').open('w',encoding='utf-8') as stderr:
        proc=subprocess.Popen(args,cwd=work(cid),env=env(cid),stdin=subprocess.PIPE,stdout=stdout,stderr=stderr,text=True,encoding='utf-8')
        try:
            proc.communicate(p,timeout=1800)
            actor_error=None
        except subprocess.TimeoutExpired:
            command(['taskkill','/PID',str(proc.pid),'/T','/F'],ROOT,60)
            proc.wait(timeout=30); actor_error='Actor exceeded 1800 second budget'
    actor_seconds=round(time.monotonic()-start,3)
    existing=checked(['git','diff','--name-only','--diff-filter=MDRTUXB','HEAD'],work(cid)).splitlines()
    touched_tests=[n for n in existing if re.search(r'(^|/)(tests?|__tests__)(/|$)|(^|/)test_[^/]+',n)]
    checked(['git','add','-N','.'],work(cid))
    patch=checked(['git','diff','--binary','HEAD'],work(cid))
    (out/'final.patch').write_text(patch,encoding='utf-8',newline='\n')
    events=[]; usage={}
    for line in (out/'actor-events.jsonl').read_text(encoding='utf-8').splitlines():
        try: e=json.loads(line)
        except ValueError: continue
        events.append(e)
        if e.get('type')=='turn.completed': usage=e.get('usage') or {}
    clean(cid)
    if patch:
        exclusions=[]
        if cid.startswith('fb-'):
            # The benchmark restores original withheld tests at these paths.
            # Preserve Actor-created tests in the captured patch; do not let a
            # filename collision prevent verification with unchanged assertions.
            exclusions=['--exclude='+path for path in CASES[cid]['test_files']]
        checked(['git','apply','--allow-empty','--whitespace=nowarn',*exclusions,str(out/'final.patch')],work(cid))
    verification=[]; verification_error=None
    if not touched_tests:
        try:
            test_patch(cid); verification=verify(cid,'actor-contract')
        except Exception as exc: verification_error=str(exc)
    else: verification_error='Actor modified pre-existing tests'
    result={'case':cid,'arm':'A1','model':'gpt-6-sol','reasoning':'medium','actor_exit':proc.returncode,
            'actor_seconds':actor_seconds,'elapsed_seconds':round(time.monotonic()-start,3),'usage':usage,
            'actor_error':actor_error,'verification_error':verification_error,'tests_modified':touched_tests,
            'verification':verification,'prompt_sha256':sha(p),'patch_sha256':sha(patch),
            'automated_contract_passed':proc.returncode==0 and actor_error is None and verification_error is None
                  and bool(verification) and all(x['exit_code']==0 and x['passed']>0 for x in verification)}
    save(state/'actor.json',result)
    emit({'case':cid,'stage':'actor_complete','passed':result['automated_contract_passed'],
          'actor_seconds':actor_seconds,'usage':usage,'error':actor_error or verification_error})

def safe_stage(stage,cid):
    try: globals()[stage](cid)
    except Exception as exc:
        result={'case':cid,'stage':stage,'error':str(exc)}
        save(ROOT/'state'/cid/f'{stage}-error.json',result); emit(result)

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    p=argparse.ArgumentParser(); p.add_argument('stage',choices=['prepare','preflight','actor'])
    p.add_argument('cases',nargs='+'); p.add_argument('--workers',type=int,default=2); a=p.parse_args()
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
        list(pool.map(lambda cid:safe_stage(a.stage,cid),a.cases))
