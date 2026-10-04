import json
from ansible.config.manager import ensure_type
class NoneLike:
    def __eq__(self, other): return other == 'None'
    def __repr__(self): return 'NoneLike()'
try:
    result=ensure_type(NoneLike(),'none')
    row={'passed':False,'result':repr(result)}
except ValueError as exc:
    expected="Invalid value provided for 'none': NoneLike()"
    row={'passed':str(exc)==expected,'error':str(exc),'expected':expected}
except Exception as exc:
    row={'passed':False,'error':type(exc).__name__+': '+str(exc)}
print('PROBE_RESULT '+json.dumps([row]))
