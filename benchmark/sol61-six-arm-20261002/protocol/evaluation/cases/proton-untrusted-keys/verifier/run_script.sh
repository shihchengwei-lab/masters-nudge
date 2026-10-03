#!/bin/bash
set -e
export NODE_ENV=test
export CHROME_BIN=/usr/bin/chromium
python3 - "$@" <<'PY'
import json, os, re, subprocess, sys
from pathlib import Path
paths=list(dict.fromkeys(p.split('|',1)[0].strip() for arg in sys.argv[1:] for p in arg.split(',')))
if not paths:
    paths=['packages/shared/test/keys/publicKeys.spec.ts','packages/shared/test/mail/encryptionPreferences.spec.ts','packages/components/containers/contacts/email/ContactEmailSettingsModal.test.tsx']
shared=[p for p in paths if p.startswith('packages/shared/test/')]
components=[p for p in paths if p.startswith('packages/components/')]
unknown=[p for p in paths if p not in shared+components]
if unknown: raise SystemExit('Unsupported test selectors: '+repr(unknown))
status=0
if shared:
    base=Path('packages/shared/test')
    original=(base/'index.spec.js').read_text()
    prelude=original.split('const testsContext =')[0]
    imports='\n'.join('require('+json.dumps('./'+str(Path(p).relative_to(base)).replace('\\','/'))+');' for p in shared)
    (base/'mn10-selected.js').write_text(prelude+'\n'+imports+'\n')
    wrapper="""
const fs = require('fs');
const original = require('./karma.conf.js');
function JsonReporter(baseReporterDecorator) {
  baseReporterDecorator(this);
  this.onSpecComplete = (browser, result) => {
    const name = result.suite.concat([result.description]).join(' > ');
    const status = result.skipped ? 'SKIPPED' : result.success ? 'PASSED' : 'FAILED';
    this.write('MN_KARMA_RESULT ' + JSON.stringify({name, status}) + '\\n');
  };
}
JsonReporter.$inject = ['baseReporterDecorator'];
module.exports = config => {
  original(config);
  process.env.CHROME_BIN = '/usr/bin/chromium';
  config.set({
    files: ['test/mn10-selected.js'],
    preprocessors: {'test/mn10-selected.js': ['webpack']},
    reporters: ['spec', 'mn10-json'],
    plugins: config.plugins.concat([{'reporter:mn10-json': ['type', JsonReporter]}]),
    colors: false
  });
};
"""
    (base/'mn10-karma.conf.cjs').write_text(wrapper)
    status=max(status,subprocess.call(['yarn','workspace','@proton/shared','exec','karma','start','test/mn10-karma.conf.cjs']))
if components:
    pattern='|'.join(re.escape(p) for p in components)
    status=max(status,subprocess.call(['yarn','workspace','@proton/components','test','--runInBand','--forceExit','--verbose','--coverage=false','--testPathPattern='+pattern]))
raise SystemExit(status)
PY
