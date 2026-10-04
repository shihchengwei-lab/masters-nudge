import json
from ansible.config.manager import ensure_type
from ansible._internal._datatag._tags import Origin
out=[]
for kind in ('list','pathlist','pathspec'):
    value=Origin(description='config').tag('relative-child')
    try:
        result=ensure_type(value,kind)
        row={'type':kind,'container_tagged':Origin.get_tag(result)==Origin.get_tag(value),
             'elements_tagged':[Origin.get_tag(x)==Origin.get_tag(value) for x in result]}
        row['passed']=row['container_tagged'] and all(row['elements_tagged'])
    except Exception as exc:
        row={'type':kind,'passed':False,'error':type(exc).__name__+': '+str(exc)}
    out.append(row)
print('PROBE_RESULT '+json.dumps(out))
