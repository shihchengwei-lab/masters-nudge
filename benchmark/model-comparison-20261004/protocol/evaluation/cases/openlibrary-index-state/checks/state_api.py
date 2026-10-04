import dataclasses
import json
from openlibrary.solr.update_work import SolrUpdateState

out=[]
def check(name,fn):
    try: out.append({'case':name,'passed':bool(fn())})
    except Exception as e:out.append({'case':name,'passed':False,'error':repr(e)})

def defaults():
    x,y=SolrUpdateState(),SolrUpdateState()
    x.keys.append('key');x.adds.append({'id':'doc'});x.deletes.append('old')
    return dataclasses.is_dataclass(x) and not y.keys and not y.adds and not y.deletes and y.commit is False

def combine():
    x=SolrUpdateState(keys=['k'],adds=[{'id':'a'}],deletes=['d'],commit=False)
    y=SolrUpdateState(keys=['l'],adds=[{'id':'b'}],deletes=['e'],commit=True)
    z=x+y
    return z.keys==['k','l'] and z.adds==[{'id':'a'},{'id':'b'}] and z.deletes==['d','e'] and z.commit and x.keys==['k'] and x.commit is False

def changes():
    return (not SolrUpdateState(keys=['k'],commit=True).has_changes()
            and SolrUpdateState(adds=[{'id':'x'}]).has_changes()
            and SolrUpdateState(deletes=['x']).has_changes())

def clear():
    s=SolrUpdateState(keys=['k'],adds=[{'id':'x'}],deletes=['y'],commit=True)
    s.clear_requests()
    return s.keys==['k'] and s.commit and not s.adds and not s.deletes

def serialize():
    s=SolrUpdateState(adds=[{'id':'x'}],deletes=['y'],commit=True)
    # Solr command JSON allows repeated command keys; retain pairs when parsing.
    pairs=json.loads(s.to_solr_requests_json(indent=None,sep=','),object_pairs_hook=list)
    return any(k=='add' for k,v in pairs) and any(k=='delete' for k,v in pairs) and any(k=='commit' for k,v in pairs)

for name,fn in [('defaults',defaults),('combine',combine),('has_changes',changes),('clear',clear),('json',serialize)]:check(name,fn)
print('PROBE_RESULT '+json.dumps(out))
