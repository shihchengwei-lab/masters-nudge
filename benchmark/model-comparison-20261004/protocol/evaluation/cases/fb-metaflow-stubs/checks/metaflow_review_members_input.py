import ast, json, sys, typing
from metaflow.cmd.develop.stub_generator import StubGenerator

def gen():
    result = StubGenerator('/tmp/probe-stubs')
    result._current_module = sys.modules[__name__]
    result._current_module_name = __name__
    result._current_parent_module = sys.modules[__name__]
    return result
class Node: pass
Node.alias = Node
results = {}
for name, action in [
    ('self_alias', lambda g: g._generate_class_stub('Node', Node)),
    ('annotated_metadata', lambda g: 'value: ' + g._exploit_annotation(typing.Annotated[int, object()], '')),
]:
    text = None
    try:
        text = action(gen())
        ast.parse(text)
        results[name] = {'passed': True, 'stub': text[:4000]}
    except Exception as exc:
        results[name] = {'passed': False, 'error': type(exc).__name__ + ': ' + str(exc), 'stub': text}
print('PROBE_RESULT '+json.dumps({'passed': all(r['passed'] for r in results.values()), 'cases': results}))
