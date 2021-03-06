# -*- coding: utf-8 -*-
"""
# methoddispatch

[![Build Status](https://travis-ci.com/seequent/methoddispatch.svg?branch=master)](https://travis-ci.com/seequent/methoddispatch)

Python 3.4 added the ``singledispatch`` decorator to the ``functools`` standard library module.
This library extends this functionality to instance methods (and works for functions too).

To define a generic method , decorate it with the ``@singledispatch`` decorator. Note that the dispatch happens on the type of the first argument, create your function accordingly.

    >>> from methoddispatch import singledispatch, register, SingleDispatch

    >>> @singledispatch
    ... def fun(arg, verbose=False):
    ...     if verbose:
    ...         print("Let me just say,", end=" ")
    ...     print(arg)

To add overloaded implementations to the function, use the ``register()`` attribute of the generic function. It is a decorator, taking a type parameter and decorating a function implementing the operation for that type

    >>> @fun.register(int)
    ... def _(arg, verbose=False):
    ...     if verbose:
    ...         print("Strength in numbers, eh?", end=" ")
    ...     print(arg)
    ...
    >>> @fun.register(list)
    ... def _(arg, verbose=False):
    ...     if verbose:
    ...         print("Enumerate this:")
    ...     for i, elem in enumerate(arg):
    ...         print(i, elem)

To enable registering lambdas and pre-existing functions, the ``register()`` attribute can be used in a functional form::

    >>> def nothing(arg, verbose=False):
    ...     print("Nothing.")
    ...
    >>> fun.register(type(None), nothing)
    <function nothing at 0x03D3FDB0>

The ``register()`` attribute returns the undecorated function which enables decorator stacking, pickling, as well as creating unit tests for each variant independently

    >>> from decimal import Decimal
    >>> @fun.register(float)
    ... @fun.register(Decimal)
    ... def fun_num(arg, verbose=False):
    ...     if verbose:
    ...         print("Half of your number:", end=" ")
    ...     print(arg / 2)
    ...
    >>> fun_num is fun
    False

When called, the generic function dispatches on the type of the first argument::

    >>> fun("Hello, world.")
    Hello, world.
    >>> fun("test.", verbose=True)
    Let me just say, test.
    >>> fun(42, verbose=True)
    Strength in numbers, eh? 42
    >>> fun(['spam', 'spam', 'eggs', 'spam'], verbose=True)
    Enumerate this:
    0 spam
    1 spam
    2 eggs
    3 spam
    >>> fun(None)
    Nothing.
    >>> fun(1.23)
    0.615

Where there is no registered implementation for a specific type, its method resolution order is used to find a more generic implementation. The original function decorated with ``@singledispatch`` is registered for the base ``object`` type, which means it is used if no better implementation is found.

To check which implementation will the generic function choose for a given type, use the ``dispatch()`` attribute::

    >>> fun.dispatch(float)
    <function fun_num at 0x1035a2840>
    >>> fun.dispatch(dict)    # note: default implementation
    <function fun at 0x103fe0000>

To access all registered implementations, use the read-only ``registry`` attribute::

    >>> fun.registry.keys()
    dict_keys([<class 'NoneType'>, <class 'int'>, <class 'object'>,
              <class 'decimal.Decimal'>, <class 'list'>,
              <class 'float'>])
    >>> fun.registry[float]
    <function fun_num at 0x1035a2840>
    >>> fun.registry[object]
    <function fun at 0x103fe0000>

Decorating class methods requires the class to inherit from ``SingleDispatch``

    >>> class BaseClass(SingleDispatch):
    ...     @singledispatch
    ...     def foo(self, bar):
    ...         return 'default'
    ...
    ...     @foo.register(int)
    ...     def foo_int(self, bar):
    ...         return 'int'
    ...
    >>> b = BaseClass()
    >>> b.foo('hello')
    'default'
    >>> b.foo(1)
    'int'

Subclasses can extend the type registry of the function on the base class with their own overrides.
Because we do not want to modify the base class ``foo`` registry the ``methoddispatch.register`` decorator must be used instead of ``foo.register``.  The module level ``register`` function takes either the method name or the method itself as the first parameter and the dispatch type as the second.

    >>> class SubClass(BaseClass):
    ...     @register('foo', float)
    ...     def foo_float(self, bar):
    ...         return 'float'
    ...
    ...     @register(BaseClass.foo, str)
    ...     def foo_str(self, bar):
    ...         return 'str'
    ...
    >>> s = SubClass()
    >>> s.foo('')
    'str'
    >>> s.foo(1.0)
    'float'

The ``SingleDispatch`` mixin class ensures that each subclass has it's own independant copy of the dispatch registry

    >>> b = BaseClass()
    >>> b.foo(1.0)
    'default'

Method overrides do not need to provide the ``register`` decorator again to be used in the dispatch of ``foo``

    >>> class SubClass2(BaseClass):
    ...     def foo_int(self, bar):
    ...         return 'my int'
    ...
    >>> s = SubClass2()
    >>> s.foo(1)
    'my int'

However, providing the register decorator with the same type will also work.
Decorating a method override with a different type (not a good idea) will register the different type and leave the base-class handler in place for the orginal type.

In Python 3.6 and later, for functions annotated with types, the decorator will infer the type of the first argument automatically as shown below

    >>> class BaseClassAnno(SingleDispatch):
    ...     @singledispatch
    ...     def foo(self, bar):
    ...         return 'default'
    ...
    ...     @foo.register
    ...     def foo_int(self, bar: int):
    ...         return 'int'
    ...
    >>> class SubClassAnno(BaseClassAnno):
    ...     @register('foo')
    ...     def foo_float(self, bar: float):
    ...         return 'float'

In Python 3.6 and earlier, the ``SingleDispatch`` class uses a meta-class ``SingleDispatchMeta`` to manage the dispatch registries.  However in Python 3.6 and later the ``__init_subclass__`` method is used instead.
If your class also inherits from an ABC interface you can use the ``SingleDispatchABCMeta`` metaclass in Python 3.6 and earlier.

Finally, accessing the method ``foo`` via a class will use the dispatch registry for that class

      >>> SubClass2.foo(s, 1)
      'my int'
      >>> BaseClass.foo(s, 1)
      'int'

"""

import sys
if sys.version_info[0] < 3:
    from .methoddispatch2 import *
    del methoddispatch2
elif sys.version_info >= (3, 6):
    from .methoddispatch36 import *
    del methoddispatch36
else:
    from .methoddispatch3 import *
    del methoddispatch3

__version__ = '2.0.1'
__author__ = 'Seequent'
__license__ = 'BSD'
__copyright__ = 'Copyright 2018 Seequent'
