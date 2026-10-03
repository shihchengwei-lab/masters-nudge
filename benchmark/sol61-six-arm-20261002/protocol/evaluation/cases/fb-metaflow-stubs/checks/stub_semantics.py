"""Interpret generated declarations with the imports their stub records."""
import typing


def namespace_for(generator, **initial):
    namespace = dict(initial)
    for module in generator._imports | generator._typing_imports:
        exec('import ' + module, namespace)
    for module, member in generator._sub_module_imports:
        exec('from ' + module + ' import ' + member, namespace)
    namespace.update(generator._typevars)
    for declaration in generator._current_references:
        exec(declaration, namespace)
    return namespace


def typed_dict_keys(clazz, namespace):
    # .pyi annotations may be quoted. TypedDict's runtime key sets do not
    # resolve Required/NotRequired inside a forward reference; type checkers do.
    required = set(clazz.__required_keys__)
    optional = set(clazz.__optional_keys__)
    for name, annotation in typing.get_type_hints(clazz, globalns=namespace, localns=namespace, include_extras=True).items():
        origin = typing.get_origin(annotation)
        if origin is typing.Required:
            required.add(name)
            optional.discard(name)
        elif origin is typing.NotRequired:
            optional.add(name)
            required.discard(name)
    return required, optional
