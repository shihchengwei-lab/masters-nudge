import asyncio,json
from openlibrary.solr import update_work as u
async def main():
    error=None
    keys=None
    try:
        state=await u.EditionSolrUpdater().update_key({'key':'/books/OL1M','type':{'key':'/type/edition'},'title':'Title'})
        keys=list(state.keys)
    except Exception as exc:error=repr(exc)
    print('PROBE_RESULT '+json.dumps([{'case':'orphan-edition-public-keys','keys':keys,'error':error,'passed':error is None and keys==['/works/OL1M']}]))
asyncio.run(main())
