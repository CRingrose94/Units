"""
Currently, this implementation creates a new Type which inherits any methods/attributes from
the original Type such as int, str, ndarray.
The new type also contains an associated unit.


A better implementation would be to define a metaclass.
Each new type would be a class, built through this metaclass.
The metaclass would add methods for converting units, as well as inheriting the original
class's methods/attributes.
"""

from functools import lru_cache
import inspect

import numpy as np


class TypedUnit:
    def __init__(self, value, unit=None):
        self.value = value
        self.unit = unit

    def __repr__(self):
        return '{}({!r})'.format(self.__class__.__name__, self.value)

    def __str__(self):
        return f'{self.value} {self.unit}'


def method_factory(method_name):
    """Returns methods extracted from type classes"""
    def method(self, other):
        if isinstance(other, TypedUnit):
            if self.unit != other.unit:
                raise TypeError('Cannot mix types!')
            other = other.value
        value = getattr(self.value, method_name)(other)
        unit = self.unit
        return TypedUnit(value, unit)
    return method


@lru_cache(maxsize=32, typed=True)
def type_container(type_):

    blacklist = frozenset([
        '__doc__',
        '__getattribute__',
        '__getnewargs__',
        '__init__',
        '__new__',
        '__repr__',
        '__setattr__',
        '__str__',
    ])

    name = f'Typed{type_.__name__.title()}'
    method_names = {
        method_name for method_name, _ in inspect.getmembers(type_, inspect.ismethoddescriptor) if
        method_name not in blacklist
    }
    return type(name, (TypedUnit,), {n: method_factory(n) for n in method_names})


def unit_container(value, unit=None):
    cls = type_container(type(value))
    return cls(value, unit)


# if __name__ == '__main__':
#     a = unit_container(np.array([1, 2, 3]), 'm')
#     b = unit_container(3, 'm')
#
#     print(a)
#     print(a * b)
#
#     print(a.dot(a))
#
#     c = unit_container([1, 2, 3])
#     c.append(5)
#
#     print(c)

class Metre:
    def __init__(self, value=None, unit='m'):
        self.value = value
        self.unit = unit

    def __mul__(self, other):
        return Metre(value=other)

    def __rmul__(self, other):
        return Metre(value=other)

    def __str__(self):
        return f'{self.value} {self.unit}'


m = Metre()

print(5 * m)
print(m * 5)
