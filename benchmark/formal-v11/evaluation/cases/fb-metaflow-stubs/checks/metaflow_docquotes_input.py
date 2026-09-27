import ast
import json
import sys
from metaflow.cmd.develop.stub_generator import StubGenerator

def function():
    pass

class Example:
    pass

function.__doc__ = Example.__doc__ = 'Ends with "'
results = {}
for kind, name, value in [('function', 'function', function), ('class', 'Example', Example)]:
    gen = StubGenerator('/tmp/probe-stubs')
    gen._current_module = sys.modules[__name__]
    gen._current_module_name = __name__
    gen._current_parent_module = sys.modules[__name__]
    try:
        text = getattr(gen, '_generate_' + kind + '_stub')(name, value)
        tree = ast.parse(text)
        doc = ast.get_docstring(tree.body[0])
        results[kind] = {'passed': doc == value.__doc__, 'stub': text, 'doc': doc}
    except Exception as exc:
        results[kind] = {'passed': False, 'error': type(exc).__name__ + ': ' + str(exc), 'stub': locals().get('text')}
print('PROBE_RESULT '+json.dumps({'passed': all(r['passed'] for r in results.values()), 'cases': results}))
