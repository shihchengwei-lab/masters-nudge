import ast
import collections
import json
from pathlib import Path
import sys
import tempfile
import types
import typing

from metaflow.cmd.develop.stub_generator import StubGenerator
from stub_semantics import namespace_for, typed_dict_keys


def generator():
    gen = StubGenerator('/tmp/probe-stubs')
    gen._current_module = sys.modules[__name__]
    gen._current_module_name = __name__
    gen._current_parent_module = sys.modules[__name__]
    return gen


def fields(text):
    names=set()
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
        if isinstance(node, ast.FunctionDef) and any(ast.unparse(d).split('.')[-1]=='property' for d in node.decorator_list):
            names.add(node.name)
        if isinstance(node, ast.Call) and ast.unparse(node.func).split('.')[-1] in ('NamedTuple','TypedDict') and len(node.args)>1:
            fields=node.args[1]
            if isinstance(fields,ast.Dict):
                names.update(k.value for k in fields.keys if isinstance(k,ast.Constant) and isinstance(k.value,str))
            if isinstance(fields,(ast.List,ast.Tuple)):
                for item in fields.elts:
                    if isinstance(item,(ast.Tuple,ast.List)) and item.elts and isinstance(item.elts[0],ast.Constant):names.add(item.elts[0].value)
    return sorted(names)


def named_tuple_fields():
    Point = collections.namedtuple('Point', ['x'])
    Point.__annotations__ = {'x': int, 'description': str}
    gen = generator()
    text = gen._generate_class_stub('Point', Point)
    names = fields(text)
    return {'passed': 'x' in names and 'description' in names, 'fields': names, 'stub': text}


def inherited_typed_dict():
    class Base(typing.TypedDict):
        x: int

    class Child(Base, total=False):
        y: str

    gen = generator()
    text = gen._generate_class_stub('Child', Child)
    namespace = namespace_for(gen, typing=typing, Base=Base, __main__=sys.modules[__name__])
    exec(text, namespace)
    result = namespace['Child']
    required, optional = typed_dict_keys(result, namespace)
    return {'passed': required == Child.__required_keys__ and optional == Child.__optional_keys__,
            'expected_required': sorted(Child.__required_keys__), 'actual_required': sorted(required),
            'expected_optional': sorted(Child.__optional_keys__), 'actual_optional': sorted(optional), 'stub': text}


def none_annotations():
    def f(x: None) -> None:
        pass

    class C:
        x: None

    gen = generator()
    function_text = gen._generate_function_stub('f', f)
    class_text = gen._generate_class_stub('C', C)
    function = next(n for n in ast.parse(function_text).body if isinstance(n, ast.FunctionDef))
    annotation = function.args.args[0].annotation
    class_node = next(n for n in ast.parse(class_text).body if isinstance(n, ast.ClassDef))
    member = next((n for n in class_node.body if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.target.id == 'x'), None)
    valid = lambda n: n is not None and (ast.unparse(n) in ('None', 'NoneType', 'types.NoneType') or isinstance(n, ast.Constant) and n.value in ('None', 'NoneType', 'types.NoneType'))
    # The other runtime-member checks already accept property declarations.
    property_member = next((n for n in class_node.body if isinstance(n, ast.FunctionDef) and n.name == 'x'
                            and any(ast.unparse(d).split('.')[-1] == 'property' for d in n.decorator_list)), None)
    class_preserved = (member is not None and valid(member.annotation)) or (property_member is not None and valid(property_member.returns))
    return {'passed': valid(annotation) and class_preserved and gen._exploit_annotation(None) == '',
            'function_parameter_preserved': valid(annotation), 'class_annotation_preserved': class_preserved,
            'helper_None_returns_empty_as_required': gen._exploit_annotation(None) == '',
            'function_stub': function_text, 'class_stub': class_text}


def annotated_property():
    class C:
        value: int

        @property
        def value(self) -> int:
            return 0

        @value.setter
        def value(self, value: int):
            pass

    text = generator()._generate_class_stub('C', C)
    node = next(n for n in ast.parse(text).body if isinstance(n, ast.ClassDef))
    decorators = [ast.unparse(d) for n in node.body if isinstance(n, ast.FunctionDef) and n.name == 'value' for d in n.decorator_list]
    return {'passed': 'property' in decorators and 'value.setter' in decorators, 'decorators': decorators, 'stub': text}


def unannotated_named_tuple():
    Pair = collections.namedtuple('Pair', ['left', 'right'])
    text = generator()._generate_class_stub('Pair', Pair)
    names = fields(text)
    return {'passed': 'left' in names and 'right' in names, 'fields': names, 'stub': text}


def constrained_typevar():
    module = types.ModuleType('metaflow.round10_probe')
    sys.modules[module.__name__] = module
    with tempfile.TemporaryDirectory() as directory:
        source = "from typing import TypeVar\nT = TypeVar('T', str, int)\ndef convert(value: T) -> T: pass\n"
        filename = Path(directory) / 'round10_probe.py'
        filename.write_text(source)
        module.__file__ = str(filename)
        exec(compile(source, str(filename), 'exec'), module.__dict__)
        output = Path(directory) / 'stubs'
        gen = StubGenerator(str(output))
        gen._pending_modules = [(module.__name__, module.__name__)]
        gen.write_out()
        texts = {str(p.relative_to(output)): p.read_text() for p in output.rglob('*.pyi')}
    errors = []
    for path, text in texts.items():
        try:
            ast.parse(text)
        except SyntaxError as exc:
            errors.append({'file': path, 'error': str(exc)})
    return {'passed': bool(texts) and not errors and any('TypeVar(' in text and 'def convert(' in text for text in texts.values()),
            'errors': errors, 'stubs': texts}


outputs = {}
for name, probe in [('named_tuple_annotated_members', named_tuple_fields), ('typed_dict_inherited_requiredness', inherited_typed_dict), ('none_annotations', none_annotations), ('annotated_property_and_setter', annotated_property), ('unannotated_named_tuple', unannotated_named_tuple), ('constrained_typevar', constrained_typevar)]:
    try:
        outputs[name] = probe()
    except Exception as exc:
        outputs[name] = {'passed': False, 'error_type': type(exc).__name__, 'error': str(exc)}
print('PROBE_RESULT '+json.dumps(outputs, ensure_ascii=False))
