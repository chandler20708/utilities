"""This is a runtime typechecker decorator"""
from typing import Callable, Any, get_origin #, get_args
from types import GenericAlias
from inspect import signature, _empty
from itertools import chain
from functools import wraps

def _typehint_converter(typehint: Any) -> type:
    """recursively get the type of the typehint"""
    if type(typehint) is type:
        return typehint
    if type(typehint) is GenericAlias: 
        return get_origin(typehint)
    return object

def check_type(method: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to check type of the input arguments and returned values"""
    sig = signature(method)
    arg_types = sig.parameters
    return_anno = sig.return_annotation
    arg_messsage = (
        "Expected type {expected!r} for argument {argument}, "
        "but got type {got!r} with value {value!r}"
    )
    retr_message = (
        "Expected return type {expected!r}, "
        "but got type {got!r} with value {value!r}"
    )

    @wraps(method)
    def wrapper(*args, **kwargs):

        # arg type check
        check_list = chain(args, kwargs.values())
        for arg, (arg_name_anno, arg_type) in zip(check_list, arg_types.items()):
            arg_type_anno = arg_type.annotation
            if arg_type_anno is _empty:
                continue
            arg_type_anno = _typehint_converter(arg_type_anno)
            # checking
            if not isinstance(arg, arg_type_anno):
                argerror = arg_messsage.format(
                    expected=arg_type_anno, argument=arg_name_anno,
                    got=type(arg), value=arg,
                )
                raise TypeError(argerror)

        # return type check
        result = method(*args, **kwargs)
        if return_anno is not _empty and result is not None:
            return_type = _typehint_converter(return_anno)
            # checking
            if not isinstance(result, return_type):
                reterror = retr_message.format(
                    expected=return_type,
                    got=type(result), value=result
                )
                raise TypeError(reterror)

        return result

    return wrapper

