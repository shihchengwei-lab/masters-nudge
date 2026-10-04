import asyncio,json
from openlibrary.solr import update_work as u
from openlibrary.solr.data_provider import BetterDataProvider
class Probe(BetterDataProvider):
    def __init__(self): self.cache={}; self.seen=[]
    def preload_documents0(self, keys): self.seen.extend(keys)
    def _preload_works(self): pass
    def _preload_authors(self): pass
    def _preload_editions(self): pass
    async def _preload_metadata_of_editions(self): pass
    def preload_redirects(self, keys): pass
async def main():
    rows=[]
    for cls,key in [(u.AuthorSolrUpdater,'/authors/OL1A'),(u.EditionSolrUpdater,'/books/OL1M')]:
        provider=Probe();u.data_provider=provider;error=None
        try: await cls().preload_keys(iter([key]))
        except Exception as exc: error=repr(exc)
        rows.append({'updater':cls.__name__,'seen':provider.seen,'error':error,'passed':error is None and key in provider.seen})
    print('PROBE_RESULT '+json.dumps(rows))
asyncio.run(main())
