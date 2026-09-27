"""Execute frozen checks against one patch in its pinned project image (WSL).

This process receives a case and patch, never an A/B label. Results and raw logs
are written to a fresh directory. It does not start an Actor or call a model.
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import time
import uuid
import evaluate


def command(args, timeout=1800):
    return subprocess.run(args, capture_output=True, timeout=timeout)


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def passed_values(value):
    if isinstance(value, list):
        return [x for item in value for x in passed_values(item)]
    if not isinstance(value, dict):
        return []
    if isinstance(value.get('passed'), bool):
        return [value['passed']]
    return [x for item in value.values() for x in passed_values(item)]


def markers(text):
    decoder = json.JSONDecoder()
    found = []
    for match in re.finditer(r'PROBE_RESULT\s+', text):
        try:
            value, _ = decoder.raw_decode(text[match.end():])
            found.append(value)
        except ValueError:
            pass
    return found


def execute(case_id, patch, output, calibration=False):
    fingerprint = (evaluate.digest(evaluate.ROOT / 'manifest.json')
                   if not calibration else 'calibration:' +
                   __import__('hashlib').sha256(json.dumps(evaluate.inventory(), sort_keys=True).encode()).hexdigest())
    if not calibration:
        evaluate.verify()
    case = next(c for c in evaluate.read(evaluate.ROOT/'cases.json') if c['id']==case_id)
    folder = evaluate.ROOT/'cases'/case_id
    spec = evaluate.read(folder/'contract.json')
    output.mkdir(parents=True, exist_ok=False)
    name = 'mn-fixed-' + uuid.uuid4().hex[:12]
    result = {'case': case_id, 'patch_sha256': evaluate.digest(patch),
              'evaluator_sha256': fingerprint, 'checks': {}, 'logs': [],
              'image_id': case['environment']['image_id']}
    started = time.monotonic()

    def run(tag, args, timeout=1800):
        p = command(args, timeout)
        log = output/(tag+'.txt')
        log.write_bytes(p.stdout+b'\n'+p.stderr)
        result['logs'].append({'file': log.name, 'sha256': evaluate.digest(log), 'exit_code': p.returncode})
        return p, (p.stdout+b'\n'+p.stderr).decode(errors='replace')

    def docker(*args):
        p = command(['docker', *map(str,args)])
        if p.returncode:
            raise RuntimeError((p.stdout+p.stderr).decode(errors='replace')[-5000:])
        return p

    def copy(src, target):
        docker('cp',src,f'{name}:{target}')

    try:
        docker('run','--detach','--pull=never','--name',name,'--cpus','4','--memory','6g',
               '--shm-size','512m','--user','root','--mount',
               f'type=bind,source={folder/"verifier"},target=/tests,readonly','--mount',
               f'type=bind,source={output},target=/logs/verifier',
               '--entrypoint','sleep',case['environment']['image_id'],'infinity')
        app = '/app' if command(['docker','exec',name,'test','-d','/app']).returncode == 0 else '/testbed'
        base = docker('exec','--workdir',app,name,'git','rev-parse','HEAD').stdout.decode().strip()
        if base != case['base_commit']:
            raise RuntimeError('Image base differs from fixed task base: '+base)
        if patch.stat().st_size:
            copy(patch,'/tmp/delivery.patch')
            test_surface=['test/*','tests/*','**/*_test.go','**/*.test.ts','**/*.test.tsx','**/*.spec.ts']
            p,text=run('apply',['docker','exec','--workdir',app,name,'git','apply','--whitespace=nowarn',
                              *['--exclude='+pattern for pattern in test_surface],'/tmp/delivery.patch'])
            result['delivery_test_paths_replaced_by_fixed_suite']=test_surface
            if p.returncode:
                raise RuntimeError('Delivery cannot be applied: '+text[-1500:])
        prefix=['docker','exec','--workdir',app,name]
        p,text=run('reserved',prefix+['bash','/tests/test.sh'])
        report=output/'output.json'
        tests=evaluate.read(report).get('tests',[]) if report.exists() else []
        raw=(output/'run-script-stdout.txt').read_text(errors='replace') if (output/'run-script-stdout.txt').exists() else text
        if case_id.startswith('flipt-'):
            tests=[{'name':n,'status':{'PASS':'PASSED','FAIL':'FAILED','SKIP':'SKIPPED'}[s]}
                   for s,n in re.findall(r'^--- (PASS|FAIL|SKIP):\s+(\S+)\s+\(',raw,re.M)]
            if not tests:
                for line in raw.splitlines():
                    try: event=json.loads(line)
                    except ValueError: continue
                    if event.get('Test') and event.get('Action') in ('pass','fail','skip'):
                        tests.append({'name':event['Test'],'status':{'pass':'PASSED','fail':'FAILED','skip':'SKIPPED'}[event['Action']]})
        actual={t['name']:t['status'] for t in tests}
        required=evaluate.read(folder/'reserved-tests.json')
        missing=[n for n in required if actual.get(n)!='PASSED']
        failures=[t for t in tests if t['status'] in ('FAILED','ERROR')]
        run_exit=output/'run-exit-code.txt'
        actual_exit=int(run_exit.read_text().strip()) if run_exit.exists() else None
        result['reserved_detail']={'required_not_passed':missing,'failures':failures,'test_count':len(tests),'tests':tests,'run_exit':actual_exit}
        result['checks']['reserved']='pass' if tests and not missing and not failures and p.returncode==0 and actual_exit==0 else 'fail'
        # Supplemental checks run even if another contract clause already failed.
        for check in spec['checks']:
            key=check['id']
            if key=='reserved':continue
            recipe=check.get('recipe')
            if not recipe:
                result['checks'][key]='missing'
                continue
            for src,target in recipe.get('copy',[]):
                copy(folder/'checks'/src,app+'/'+target)
            args=[s.replace('{app}',app) for s in recipe['command']]
            p,text=run(key.replace('/','-'),prefix+args,recipe.get('timeout',900))
            values=markers(text)
            if recipe['parser']=='marker':
                flags=passed_values(values)
                good=p.returncode==0 and bool(flags) and all(flags)
            elif recipe['parser']=='go':
                good=p.returncode==0 and bool(re.search(r'^ok\s',text,re.M))
            else:
                raise RuntimeError('Unsupported parser '+recipe['parser'])
            result['checks'][key]='pass' if good else 'fail'
            result.setdefault('detail',{})[key]={'results':values,'exit_code':p.returncode}
    except Exception as exc:
        result['environment_error']=str(exc)
    finally:
        command(['docker','rm','--force',name])
        for check in spec['checks']:
            result['checks'].setdefault(check['id'],'environment_error' if 'environment_error' in result else 'missing')
        result['elapsed_seconds']=round(time.monotonic()-started,3)
        save(output/'evidence.json',result)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('case');parser.add_argument('patch',type=Path);parser.add_argument('output',type=Path)
    parser.add_argument('--calibration',action='store_true')
    args=parser.parse_args()
    result=execute(args.case,args.patch.resolve(),args.output.resolve(),args.calibration)
    print(json.dumps({k:v for k,v in result.items() if k not in ('logs','detail','reserved_detail')},ensure_ascii=False),flush=True)
