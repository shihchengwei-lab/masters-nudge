import ast, json, sys, typing
from metaflow.cmd.develop.stub_generator import StubGenerator
from stub_semantics import namespace_for

def gen():
    result = StubGenerator('/tmp/probe-stubs')
    result._current_module = sys.modules[__name__]
    result._current_module_name = __name__
    result._current_parent_module = sys.modules[__name__]
    return result

Record = typing.TypedDict('Record', {'_id': int, 'name': str})
generator=gen()
text = generator._generate_class_stub('Record', Record)
namespace = namespace_for(generator, typing=typing, __main__=sys.modules[__name__])
exec(text,namespace)
names = list(namespace['Record'].__annotations__)
async def values() -> typing.AsyncIterator[int]:
    yield 1
async_text = gen()._generate_function_stub('values', values)
result = {'passed': set(Record.__annotations__).issubset(names), 'expected_fields': list(Record.__annotations__), 'emitted_fields': names, 'stub': text}
print('PROBE_RESULT '+json.dumps({'passed': result['passed'], 'cases': {'typed_dict_keys': result}, 'async_generator_observation_only': async_text}))
