import asyncio,json
from openlibrary.solr import update_work as u
from openlibrary.tests.solr.test_update_work import FakeDataProvider,make_edition
async def main():
    output=[]
    for name,keys in [('orphan-only',['/books/OL1M']),('missing-synthetic-first',['/works/OL1M','/books/OL1M']),('orphan-first',['/books/OL1M','/works/OL1M'])]:
        u.data_provider=FakeDataProvider([make_edition(key='/books/OL1M',title='Probe title')])
        error=None;adds=[];deletes=[]
        try:
            state=await u.update_keys(keys,update='quiet')
            adds=[{'key':x.get('key'),'title':x.get('title')} for x in state.adds];deletes=list(state.deletes)
        except Exception as exc:error=repr(exc)
        output.append({'case':name,'adds':adds,'deletes':deletes,'error':error,'passed':error is None and any(x['key']=='/works/OL1M' and x['title']=='Probe title' for x in adds)})
    print('PROBE_RESULT '+json.dumps(output))
asyncio.run(main())
