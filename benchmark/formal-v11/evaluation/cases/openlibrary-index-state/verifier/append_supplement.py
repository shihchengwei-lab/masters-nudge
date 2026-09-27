from pathlib import Path
p=Path('/app/openlibrary/tests/solr/test_update_work.py')
p.write_text(p.read_text()+'\n'+Path('/tests/supplement.txt').read_text())
