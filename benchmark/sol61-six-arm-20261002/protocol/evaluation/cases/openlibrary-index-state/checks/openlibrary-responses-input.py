import json,time,httpx
from openlibrary.solr import update_work as u
time.sleep=lambda seconds:None
output=[]
for name,status,body in [('ok',200,'{}'),('non-json',400,'not json'),('json-list',400,'[]'),('null-header',400,'{"responseHeader":null}')]:
    calls=[]
    def post(url,**kwargs):
        calls.append(url)
        return httpx.Response(status,content=body.encode(),request=httpx.Request('POST',url))
    u.httpx.post=post
    error=None
    try:
        u.solr_update(u.SolrUpdateState(commit=True),solr_base_url='http://solr.test')
    except Exception as exc:error=type(exc).__name__+': '+str(exc)
    output.append({'case':name,'calls':len(calls),'error':error,'passed':error is None})
print('PROBE_RESULT '+json.dumps(output))
