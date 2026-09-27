"""Inputs derived from the four restored methods' published docstrings."""
import ast
import inspect
import json
import sys
import typing
from metaflow.cmd.develop.stub_generator import StubGenerator


def gen():
    g=StubGenerator('/tmp/contract-stubs')
    g._current_module=sys.modules[__name__]
    g._current_module_name=__name__
    g._current_parent_module=sys.modules[__name__]
    g._current_name=None
    return g


def annotations():
    g=gen()
    assert g._exploit_annotation(None)==''
    assert g._exploit_annotation(inspect.Parameter.empty)==''
    assert g._exploit_annotation(int,starting=' -> ')==' -> int'
    for value in [typing.List[int],typing.Dict[str,typing.List[int]],typing.Union[str,int],
                  typing.Callable[[str],int],typing.NewType('UserId',int),typing.TypeVar('T')]:
        rendered=g._exploit_annotation(value,starting='')
        assert rendered
        ast.parse('x: '+rendered)
    g._current_name='Node'
    node=ast.parse(g._exploit_annotation('Node',starting=''),mode='eval').body
    assert isinstance(node,ast.Constant) and node.value=='Node'
    node=ast.parse(g._exploit_annotation('MissingType',starting=''),mode='eval').body
    assert isinstance(node,ast.Constant) and node.value=='MissingType'
    # The string is resolved using the module's published context.
    assert g._exploit_annotation('int',starting='')=='int'
    return True


def functions():
    def example(a:int,/,b:str='x',*args:float,k:bool=True,**kwargs:int)->str:
        """Documentation is preserved."""
    g=gen();text=g._generate_function_stub('example',example)
    tree=ast.parse(text);node=next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)))
    assert [p.arg for p in node.args.posonlyargs]==['a']
    assert [p.arg for p in node.args.args]==['b']
    assert node.args.vararg.arg=='args' and node.args.kwarg.arg=='kwargs'
    assert [p.arg for p in node.args.kwonlyargs]==['k']
    assert ast.literal_eval(node.args.defaults[0])=='x'
    assert ast.literal_eval(node.args.kw_defaults[0]) is True
    assert ast.get_docstring(node)==example.__doc__
    class Complex:pass
    def defaults(v=Complex()):pass
    n=ast.parse(g._generate_function_stub('defaults',defaults)).body[0]
    assert ast.literal_eval(n.args.defaults[0]) is Ellipsis
    signs=[inspect.Signature([inspect.Parameter('x',inspect.Parameter.POSITIONAL_OR_KEYWORD,annotation=t)],return_annotation=t) for t in (str,int)]
    out=g._generate_function_stub('overloaded',sign=signs,doc='overloaded docs')
    nodes=[n for n in ast.parse(out).body if isinstance(n,ast.FunctionDef)]
    assert len(nodes)==2 and all(any(ast.unparse(d).split('.')[-1]=='overload' for d in n.decorator_list) for n in nodes)
    assert g._generate_function_stub('ignored',example,doc='STUBGEN_IGNORE')==''
    try:g._generate_function_stub('absent')
    except RuntimeError:pass
    else:raise AssertionError('neither function nor signature must raise RuntimeError')
    # inspect.signature(dict) raises; the task requires an empty output in this case.
    assert g._generate_function_stub('uninspectable',dict)==''
    return True


def classes():
    class Meta(type):pass
    class Parent:pass
    class Child(Parent,metaclass=Meta):
        """Class docs."""
        field:int
        def __init__(self,value:str):pass
        @staticmethod
        def static(value:int)->str:pass
        @classmethod
        def factory(cls)->'Child':pass
        @property
        def value(self)->int:return 1
        @value.setter
        def value(self,value:int):pass
    text=gen()._generate_class_stub('Child',Child)
    node=next(n for n in ast.parse(text).body if isinstance(n,ast.ClassDef))
    assert any(ast.unparse(b).endswith('Parent') for b in node.bases)
    assert any(k.arg=='metaclass' and ast.unparse(k.value).endswith('Meta') for k in node.keywords)
    assert ast.get_docstring(node)==Child.__doc__
    methods={n.name:n for n in node.body if isinstance(n,ast.FunctionDef)}
    assert '__init__' in methods
    for name,deco in [('static','staticmethod'),('factory','classmethod')]:
        assert any(ast.unparse(d).split('.')[-1]==deco for d in methods[name].decorator_list)
    field=any(isinstance(n,ast.AnnAssign) and getattr(n.target,'id',None)=='field' for n in node.body)
    field=field or any(isinstance(n,ast.FunctionDef) and n.name=='field' and n.returns is not None
                      and any(ast.unparse(d).split('.')[-1]=='property' for d in n.decorator_list) for n in node.body)
    assert field
    return True


def reset():
    g=gen()
    g._exploit_annotation(typing.List[typing.TypeVar('T')])
    g._current_objects['old']=object();g._current_references.append('old');g._stubs.append('old')
    g._reset()
    for name in ('_imports','_typing_imports','_typevars','_current_objects','_current_references','_stubs',
                 '_sub_module_imports','_current_parent_module'):
        assert not getattr(g,name),name
    return True


name=sys.argv[1]
try:result={'passed':globals()[name](),'check':name}
except Exception as e:result={'passed':False,'check':name,'error':repr(e),'trace':__import__('traceback').format_exc()}
print('PROBE_RESULT '+json.dumps(result))
