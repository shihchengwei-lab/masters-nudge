"""Run the four native benchmark suites on an isolated, disposable checkout."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import evaluate
from container_checks import markers, passed_values, save


def wsl(path):
    p=Path(path).resolve().as_posix()
    return '/mnt/'+p[0].lower()+p[2:]


def execute(cid,patch,output,cal,calibration=False):
    fingerprint=('calibration:'+hashlib.sha256(json.dumps(evaluate.inventory(),sort_keys=True).encode()).hexdigest()
                 if calibration else evaluate.verify())
    case=next(c for c in evaluate.read(evaluate.ROOT/'cases.json') if c['id']==cid)
    folder=evaluate.ROOT/'cases'/cid
    spec=evaluate.read(folder/'contract.json')
    output.mkdir(parents=True,exist_ok=False)
    work=(output/'checkout').resolve()
    assert work.parent==output.resolve() and work.name=='checkout'
    result={'case':cid,'patch_sha256':evaluate.digest(patch),'evaluator_sha256':fingerprint,'checks':{},'logs':[]}
    env=os.environ.copy()
    env.update(PYTHONUTF8='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1',CARGO_BUILD_JOBS='1',RUSTFLAGS='-A warnings')
    temp=output/'temp';temp.mkdir();env.update(TEMP=str(temp),TMP=str(temp))
    started=time.monotonic()

    def run(tag,args,cwd=None,timeout=1800):
        p=subprocess.run(list(map(str,args)),cwd=cwd or work,env=env,capture_output=True,timeout=timeout)
        text=(p.stdout+b'\n'+p.stderr).decode(errors='replace')
        path=output/(tag+'.txt');path.write_text(text,encoding='utf-8')
        result['logs'].append({'file':path.name,'sha256':evaluate.digest(path),'exit_code':p.returncode})
        return p,text

    def checked(tag,args,cwd=None):
        p,text=run(tag,args,cwd)
        if p.returncode:raise RuntimeError(tag+': '+text[-2500:])

    def git(*args):
        return subprocess.run(['git',*map(str,args)],cwd=work,capture_output=True)

    def apply_test_patch():
        # Restore only the fixed test files; delivery code stays untouched.
        for rel in re.findall(r'^diff --git a/(.*?) b/.*$',(folder/'test.patch').read_text(),re.M):
            dest=(work/rel).resolve();assert dest.is_relative_to(work)
            p=git('show',case['base_commit']+':'+rel)
            if p.returncode==0:
                dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.stdout)
            elif dest.exists():dest.unlink()
        checked('apply-tests',['git','apply','--whitespace=nowarn',folder/'test.patch'])

    try:
        if not calibration:
            expected=evaluate.read(evaluate.ROOT/'environment.json')
            names=['cargo','rustc'] if cid in ('clap-2297','tracing-1523') else ['node'] if cid=='regexp-404' else []
            for name in names:
                p,text=run('environment-'+name,[name,'--version'],cal)
                if p.returncode or text.strip()!=expected[name]:
                    raise RuntimeError('Execution environment differs: '+name)
        checked('checkout',['git','-c','core.longpaths=true','-c','core.autocrlf=false','worktree','add','--detach',work,case['base_commit']],cal/'cases'/cid)
        if patch.stat().st_size:
            test_surface={'clap-2297':['tests/*'],'tracing-1523':['tracing-subscriber/tests/*'],
                          'regexp-404':['tests/*'],'fb-metaflow-stubs':['test/*','tests/*']}[cid]
            args=['git','apply','--whitespace=nowarn']
            args.extend('--exclude='+pattern for pattern in test_surface)
            checked('apply',args+[patch])
            result['delivery_test_paths_replaced_by_fixed_suite']=test_surface
        apply_test_patch()
        if cid=='fb-metaflow-stubs':
            # The contract requires quoted forward references, not double quotes.
            source=work/'test/cmd/develop/test_stub_generator.py'
            original=source.read_text(encoding='utf-8');lines=original.splitlines(keepends=True)
            replacements=[]
            for node in ast.walk(ast.parse(original)):
                if not isinstance(node,ast.Assert) or not isinstance(node.test,ast.Compare):continue
                test=node.test
                if len(test.ops)!=1 or not isinstance(test.ops[0],ast.Eq):continue
                expected=test.comparators[0]
                if not isinstance(expected,ast.Constant) or not isinstance(expected.value,str):continue
                try:value=ast.literal_eval(expected.value)
                except (ValueError,SyntaxError):continue
                if not isinstance(value,str):continue
                if node.lineno!=node.end_lineno:raise RuntimeError('Unexpected multiline quote assertion')
                actual=ast.get_source_segment(original,test.left)
                replacement=' '*node.col_offset+f"assert __import__('ast').literal_eval({actual}) == {value!r}\n"
                replacements.append((node.lineno-1,replacement))
            for index,replacement in replacements:lines[index]=replacement
            source.write_text(''.join(lines),encoding='utf-8')
            result['forward_reference_quote_normalizations']=len(replacements)
        if cid in ('clap-2297','tracing-1523'):
            shutil.copyfile(folder/'Cargo.lock',work/'Cargo.lock')
            # Existing dependency caches are reusable; this package is always rebuilt.
            env['CARGO_TARGET_DIR']=str(cal.parent/'round-10-evaluation-builds'/cid)
            package='clap@3.0.0-beta.2' if cid=='clap-2297' else 'tracing-subscriber'
            checked('clean-package',['cargo','clean','--offline','-p',package])
            if cid=='clap-2297':
                source=work/'tests/grouped_values.rs';text=source.read_text()
                text,count=re.subn(r'(\.grouped_values_of\([^)]*\)\.unwrap\(\))\.collect\(\)',r'\1.map(|group| group.into_iter().collect::<Vec<_>>()).collect()',text)
                if count!=7:raise RuntimeError('Unexpected grouped_values test normalization count')
                source.write_text(text,encoding='utf-8')
                tests=['grouped_values','multiple_occurrences','multiple_values','flags','opts','positionals','delimiters','conflicts','require','indices','default_vals','tests','groups']
                args=['cargo','test','--offline','--locked','-p',package]
                for name in tests:args+=['--test',name]
            else:
                source=work/'tracing-subscriber/tests/layer_filters/trees.rs'
                text=source.read_text()
                if text.count('dbg!(subscriber)')!=2:raise RuntimeError('Unexpected tracing test normalization count')
                source.write_text(text.replace('dbg!(subscriber)','subscriber'),encoding='utf-8')
                shutil.copyfile(folder/'checks/benchmark_public_layer_tests.rs',work/'tracing-subscriber/tests/benchmark_public_layer_tests.rs')
                args=['cargo','test','--offline','--locked','-p',package,'--features','env-filter,registry,regex/unicode','--tests']
            p,text=run('reserved',args)
            counts=re.findall(r'test result: (?:ok|FAILED)\. (\d+) passed; (\d+) failed;',text)
            result['checks']['reserved']='pass' if p.returncode==0 and counts and sum(int(a) for a,b in counts)>0 and all(int(b)==0 for a,b in counts) else 'fail'
            result['reserved_detail']={'passed':sum(int(a) for a,b in counts),'failed':sum(int(b) for a,b in counts)}
            for check in spec['checks']:
                key=check['id']
                if key=='reserved':continue
                name='contract_'+re.sub(r'\W','_',key)
                src='self_override.rs' if cid=='clap-2297' else key
                target=work/('tests' if cid=='clap-2297' else 'tracing-subscriber/tests')/(name+'.rs')
                shutil.copyfile(folder/'checks'/src,target)
                args=['cargo','test','--offline','--locked','-p',package]
                if cid=='tracing-1523':args+=['--features','env-filter,registry,regex/unicode']
                p,text=run(name,args+['--test',name,'--','--nocapture','--test-threads=1'])
                flags=passed_values(markers(text))
                good=p.returncode==0 and bool(re.search(r'test result: ok\. [1-9]\d* passed;',text)) and (cid=='clap-2297' or flags and all(flags))
                result['checks'][key]='pass' if good else 'fail'
        elif cid=='regexp-404':
            deps=cal/'cases'/cid/'node_modules'
            env.update(NODE_PATH=str(deps),TS_NODE_TRANSPILE_ONLY='true')
            p,text=run('reserved',['node',deps/'mocha/bin/mocha','--require','ts-node/register','tests/lib/rules/no-dupe-disjunctions.ts','--reporter','spec','--no-color','--timeout','60000'])
            result['checks']['reserved']='pass' if p.returncode==0 and re.search(r'\b[1-9]\d* passing\b',text) else 'fail'
            for check in spec['checks']:
                key=check['id']
                if key=='reserved':continue
                p,text=run(key,['node','-r','ts-node/register',folder/'checks'/key,work])
                values=markers(text);flags=passed_values(values)
                if key=='regexp_direction.js' and values:flags.append(values[0]['exponential']['warningPreserved'])
                result['checks'][key]='pass' if p.returncode==0 and flags and all(flags) else 'fail'
        elif cid=='fb-metaflow-stubs':
            image='sha256:db698fbb2f50522f181849bd38245f448f3feb287b5d6ebabcf527bf3da901d2'
            base=['wsl.exe','-u','root','--exec','docker','run','--rm','--pull=never','--network','none','--cpus','2','--memory','2g',
                  '--mount',f'type=bind,source={wsl(work)},target=/task,readonly',
                  '--mount',f'type=bind,source={wsl(cal/"shared-env/featurebench")},target=/deps,readonly',
                  '--mount',f'type=bind,source={wsl(folder/"checks")},target=/probe,readonly',
                  '--workdir','/task','-e','PYTHONPATH=/task:/deps','-e','PYTHONDONTWRITEBYTECODE=1','-e','METAFLOW_USER=benchmark',
                  '-e','METAFLOW_HOME=/tmp/metaflow','--entrypoint','python3',image]
            tests=['test/cmd/develop/test_stub_generator.py','test/unit/test_multicore_utils.py','test/unit/test_argo_workflows_cli.py','test/unit/test_pypi_parsers.py','test/unit/test_local_metadata_provider.py','test/unit/test_pypi_decorator.py']
            p,text=run('reserved',base+['-m','pytest','-q','-o','cache_dir=/tmp/pytest-cache',*tests])
            result['checks']['reserved']='pass' if p.returncode==0 and re.search(r'\b[1-9]\d* passed\b',text) else 'fail'
            for check in spec['checks']:
                key=check['id']
                if key=='reserved':continue
                mode={'annotation-api':'annotations','class-api':'classes','function-api':'functions','reset-api':'reset'}.get(key)
                args=['/probe/stub_api.py',mode] if mode else ['/probe/'+key]
                p,text=run(key,base+args)
                flags=passed_values(markers(text))
                result['checks'][key]='pass' if p.returncode==0 and flags and all(flags) else 'fail'
                result.setdefault('detail',{})[key]=markers(text)
        else:raise ValueError('Unknown native case')
    except Exception as e:
        result['environment_error']=str(e)
    finally:
        for check in spec['checks']:
            result['checks'].setdefault(check['id'],'environment_error' if 'environment_error' in result else 'missing')
        result['elapsed_seconds']=round(time.monotonic()-started,3)
        save(output/'evidence.json',result)
        # The checkout is disposable; all delivered bytes and logs remain outside it.
        if work.exists():
            assert work.parent==output.resolve() and work.name=='checkout'
            subprocess.run(['git','worktree','remove','--force',str(work)],cwd=cal/'cases'/cid,capture_output=True)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('case');p.add_argument('patch',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--calibration-root',type=Path,required=True);p.add_argument('--calibration',action='store_true')
    a=p.parse_args();r=execute(a.case,a.patch.resolve(),a.output.resolve(),a.calibration_root.resolve(),a.calibration)
    print(json.dumps({k:v for k,v in r.items() if k not in ('logs','detail')},ensure_ascii=False),flush=True)
