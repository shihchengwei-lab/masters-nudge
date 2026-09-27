import asyncio,json
from openlibrary.solr import update_work as u
from openlibrary.solr.data_provider import DataProvider

source='/books/OL23M'
target='/books/OL24M'
class MemoryProvider(DataProvider):
    async def get_document(self,key):
        return {
            source:{'key':source,'type':{'key':'/type/redirect'},'location':target},
            target:{'key':target,'type':{'key':'/type/delete'}},
        }.get(key)
    def find_redirects(self,key):
        return []

async def main():
    output=[]
    for name,keys in [('source-first',[source,target]),('target-first',[target,source])]:
        u.data_provider=MemoryProvider()
        try:
            state=await u.update_keys(keys,update='quiet')
            deletes=list(state.deletes)
            output.append({'case':name,'deletes':deletes,'adds':state.adds,
                'passed':source in deletes and target in deletes and (name == 'target-first' or deletes.index(source)<deletes.index(target)) and not state.adds})
        except Exception as exc:
            output.append({'case':name,'passed':False,'error':repr(exc)})
    print('PROBE_RESULT '+json.dumps(output))
asyncio.run(main())
