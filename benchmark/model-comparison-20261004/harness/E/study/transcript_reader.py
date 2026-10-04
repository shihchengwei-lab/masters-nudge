"""Read only archived Actor artifacts; these folders are not Git repositories."""
import argparse
from pathlib import Path
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'frozen-plugin'))
from masters_nudge import read_only_repo_mcp as base
ALLOWED={'actor-events.jsonl','final.patch','prompt.txt','launch.json','result.json','execution-evidence.json','execution-evidence.txt','actor-final.txt','actor-stderr.txt'}

class Artifacts(base.RepositoryTools):
    def __init__(self,root,budget,audit):
        self.root=Path(root).resolve(strict=True)
        assert self.root.parent.parent==ROOT/'runs' and self.root.name in ('D1','D2')
        self.budget=budget
        self.audit=audit
        self.audit.parent.mkdir(parents=True,exist_ok=True)

    def _allowed(self,path):
        if path.parent!=self.root or path.name not in ALLOWED or not path.is_file():
            raise base.ToolFault('mcp_path','Only the specified Actor artifacts may be read')

    def _search(self,args):
        if set(args)-{'query','path','max_results'}:
            raise base.ToolFault('mcp_input','Invalid search arguments')
        query=args.get('query');count=args.get('max_results',30)
        if not isinstance(query,str) or not query or type(count) is not int or not 1<=count<=50:
            raise base.ToolFault('mcp_input','Invalid query or result count')
        selected=args.get('path','')
        names=[selected] if selected else sorted(ALLOWED)
        found=0
        for name in names:
            path=self._path(name);self._allowed(path)
            for number,line in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
                if query in line:
                    yield base.MaterialLine('current_structure',name,number,line)
                    found+=1
                    if found>=count:return

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',required=True)
    parser.add_argument('--budget',type=int,required=True)
    parser.add_argument('--audit',type=Path,required=True)
    args=parser.parse_args()
    base.serve(Artifacts(args.root,args.budget,args.audit))
