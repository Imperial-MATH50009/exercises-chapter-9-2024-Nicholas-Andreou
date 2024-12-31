"""Doc."""
import numbers
from functools import singledispatch


class Expression:
    """Doc."""

    def __init__(self, *operands):
        """Doc."""
        self.operands = operands

    def __add__(self, other):
        """Doc."""
        if isinstance(other, numbers.Number):
            other = Number(other)
        return Add(self, other)

    def __radd__(self, other):
        """Doc."""
        if isinstance(other, numbers.Number):
            other = Number(other)
        return Add(other, self)

    def __sub__(self, other):
        """Doc."""
        if isinstance(other, numbers.Number):
            other = Number(other)
        return Sub(self, other)

    def __rsub__(self, other):
        """Doc."""
        if isinstance(other, numbers.Number):
            other = Number(other)
        return Sub(other, self)

    def __mul__(self, other):
        """Doc."""
        if isinstance(other, numbers.Number):
            other = Number(other)
        return Mul(self, other)

    def __rmul__(self, other):
        """Doc."""
        if isinstance(other, numbers.Number):
            other = Number(other)
        return Mul(other, self)

    def __truediv__(self, other):
        """Doc."""
        if isinstance(other, numbers.Number):
            other = Number(other)
        return Div(self, other)

    def __rtruediv__(self, other):
        """Doc."""
        if isinstance(other, numbers.Number):
            other = Number(other)
        return Div(other, self)

    def __pow__(self, other):
        """Doc."""
        if isinstance(other, numbers.Number):
            other = Number(other)
        return Pow(self, other)

    def __rpow__(self, other):
        """Doc."""
        if isinstance(other, numbers.Number):
            return Pow(Number(other), self)
        return NotImplemented


class Operator(Expression):
    """Doc."""

    def __repr__(self):
        """Doc."""
        return type(self).__name__ + repr(self.operands)

    def __str__(self):
        """Doc."""

        def brack(expr):
            if expr.prec < self.prec:
                return f"({expr!s})"
            else:
                return str(expr)

        return " ".join((brack(self.operands[0]),
                        self.symbol, brack(self.operands[1])))


class Add(Operator):
    """Doc."""

    prec = 0
    symbol = "+"


class Sub(Operator):
    """Doc."""

    prec = 0
    symbol = "-"


class Mul(Operator):
    """Doc."""

    prec = 1
    symbol = "*"


class Div(Operator):
    """Doc."""

    prec = 1
    symbol = "/"


class Pow(Operator):
    """Doc."""

    prec = 2
    symbol = "^"


class Terminal(Expression):
    """Doc."""

    prec = 3

    def __init__(self, value):
        """Doc."""
        self.value = value
        super().__init__()

    def __repr__(self):
        """Doc."""
        return repr(self.value)

    def __str__(self):
        """Doc."""
        return str(self.value)


class Symbol(Terminal):
    """Doc."""

    def __init__(self, value):
        """Doc."""
        if isinstance(value, str):
            super().__init__(value)


class Number(Terminal):
    """Doc."""

    def __init__(self, value):
        """Doc."""
        if isinstance(value, numbers.Number):
            super().__init__(value)


def postvisitor(expr, fn, **kwargs):
    """Doc."""
    stack = []
    visited = {}
    stack.append(expr)
    while stack:
        e = stack[-1]
        stack = stack[:-1]
        unvisited_children = []
        for o in e.operands:
            if o not in visited:
                unvisited_children.append(o)

        if unvisited_children:
            stack.append(e)
            for u in unvisited_children:
                stack.append(u)
        else:
            visited[e] = fn(e, *(visited[o] for o in e.operands), **kwargs)

    return visited[expr]


@singledispatch
def differentiate(expr, *o, **kwargs):
    """Doc."""
    raise NotImplementedError(
        f"Cannot diff a {type(expr).__name__}")


@differentiate.register(Number)
def _(expr, *o, **kwargs):
    return 0.0


@differentiate.register(Symbol)
def _(expr, *o, **kwargs):
    if kwargs['var'] == expr.value:
        return 1.0
    else:
        return 0.0


@differentiate.register(Add)
def _(expr, *o, **kwargs):
    return o[0] + o[1]


@differentiate.register(Sub)
def _(expr, *o, **kwargs):
    return o[0] - o[1]


@differentiate.register(Mul)
def _(expr, *o, **kwargs):
    return (o[0]*expr.operands[1] + o[1]*expr.operands[0])


@differentiate.register(Div)
def _(expr, *o, **kwargs):
    return (o[0] * expr.operands[1] - expr.operands[0]
            * o[1]) / (expr.operands[1]**2)


@differentiate.register(Pow)
def _(expr, *o, **kwargs):
    return expr.operands[1] * \
            (expr.operands[0] ** (expr.operands[1] - 1)) * o[0]
