"""Recover only an unresolved execution review after its artifact tool failed.

Keep the first judge and provisional scores. Change only the read transport;
the original task, review prompt, schema, model and rules remain identical.
"""
import argparse,json,os,shutil,subprocess,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
import run,review,finish

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--case',required=True)
    parser.add_argument('--arm',required=True,choices=['C1','C2'])
    args=parser.parse_args();cid=args.case;arm=args.arm
    plan=run.prepare();assert cid in plan['cases']
    folder=run.artifact(cid,arm)
    old=run.read(folder/'execution-review.json')
    assert old['status']=='environment_error','Only unresolved infrastructure judgments may be recovered'
    original=run.ROOT/'execution-judges'/cid/arm
    assert 'MCP server startup failed' in (original/'stderr.txt').read_text(encoding='utf-8')
    directory=original.parent/(arm+'-recovery-1')
    assert not directory.exists(),'Preserve existing recovery; never redraw a judgment'
    directory.mkdir()
    prompt=(original/'prompt.txt').read_text(encoding='utf-8')
    helper=run.load_harness('recovery_helper')
    config={'command':sys.executable,'args':[str(run.ROOT/'transcript_reader.py'),'--root',str(folder),'--budget','400000','--audit',str(directory/'reads.jsonl')],
        'enabled':True,'startup_timeout_sec':30,'tool_timeout_sec':60,'default_tools_approval_mode':'approve','env':{'PYTHONIOENCODING':'utf-8'}}
    command=run.read(original/'launch.json')['command'][:]
    command=[('mcp_servers.transcript='+helper.toml(config)) if item.startswith('mcp_servers.transcript=') else item for item in command]
    for switch,target in [('-C',directory),('--output-schema',directory/'schema.json'),('-o',directory/'output.json')]:
        command[command.index(switch)+1]=str(target)
    (directory/'prompt.txt').write_text(prompt,encoding='utf-8')
    shutil.copy2(original/'schema.json',directory/'schema.json')
    run.save(directory/'launch.json',{'command':command,'prompt_sha256':run.textsha(prompt),'inventory_sha256':run.sha(folder/'execution-evidence.json'),
        'recovery_of':str(original),'reason':'Original repository reader rejects non-Git artifact directories; same prompt and criteria, artifact-only reader'})
    env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1',MASTERS_NUDGE_ACTIVE='0')
    started=time.monotonic()
    with (directory/'events.jsonl').open('w',encoding='utf-8') as stdout,(directory/'stderr.txt').open('w',encoding='utf-8') as stderr:
        process=subprocess.Popen(command,cwd=directory,env=env,stdin=subprocess.PIPE,stdout=stdout,stderr=stderr,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
        try:process.communicate(prompt,timeout=900)
        except subprocess.TimeoutExpired:
            subprocess.run(['taskkill.exe','/PID',str(process.pid),'/T','/F'],capture_output=True,timeout=30)
            raise
    run.save(directory/'transport.json',{'exit_code':process.returncode,'seconds':time.monotonic()-started,'usage':finish.usage(directory/'events.jsonl')})
    assert process.returncode==0 and (directory/'output.json').exists()
    judgment=run.read(directory/'output.json')
    assert judgment['status']!='environment_error',judgment
    reads=run.read(directory/'launch.json')
    assert (directory/'reads.jsonl').exists(),'Artifact reader did not initialize'
    decision={'status':judgment['status'],'reviewer':finish.EXECUTION_MODEL+' medium - semantic execution-contract review',
        'reason':judgment['reason'],'patch_sha256':run.sha(folder/'final.patch'),'execution_evidence_sha256':run.sha(folder/'execution-evidence.json'),
        'evidence':[{'file':'actor-events.jsonl','sha256':run.sha(folder/'actor-events.jsonl'),'observations':judgment['evidence']},
            {'file':str(directory/'output.json'),'sha256':run.sha(directory/'output.json')},
            {'file':str(directory/'reads.jsonl'),'sha256':run.sha(directory/'reads.jsonl')}],
        'infrastructure_recovery':{'original_judge':str(original),'same_prompt':run.textsha(prompt)==run.read(original/'launch.json')['prompt_sha256']}}
    preserved=run.ROOT/'infrastructure-recovery'/(cid+'-'+arm)
    assert not preserved.exists();preserved.mkdir(parents=True)
    for path in [folder/'execution-review.json',folder/'score-v3.json',run.evaluation_directory(folder)/'evidence.json']:
        shutil.copy2(path,preserved/path.name)
    run.save(preserved/'recovery.json',{'cause':'Original transcript MCP requires a Git root; result artifact folders are not repositories',
        'original_review_sha256':run.sha(preserved/'execution-review.json'),'original_score_sha256':run.sha(preserved/'score-v3.json'),
        'recovery_output':str(directory/'output.json'),'actor_and_fixed_checks_unchanged':True,'same_prompt_and_rules':True})
    (folder/'score-v3.json').unlink()
    run.save(folder/'execution-review.json',decision)
    score=review.score(cid,arm)
    run.emit({'stage':'execution_infrastructure_recovered',**score})

if __name__=='__main__':main()
