def add(a, b):
    return a + b

def sub(a, b):
    return a - b

def mul(a, b):
    return a * b

def truediv(a, b):
    return a / b

def floordiv(a, b):
    return a // b

def pow(a, b):
    return a ** b

def mod(a, b):
    return a % b

def and_(a, b):
    return a & b

def or_(a, b):
    return a | b

def xor(a, b):
    return a ^ b

def lshift(a, b):
    return a << b

def rshift(a, b):
    return a >> b

def invert(a):
    return ~a

def eq(a, b):
    return a == b

def ne(a, b):
    return a != b

def lt(a, b):
    return a < b

def le(a, b):
    return a <= b

def gt(a, b):
    return a > b

def ge(a, b):
    return a >= b

def is_(a, b):
    return a is b

def is_not(a, b):
    return a is not b

def in_(a, b):
    return a in b

def not_in(a, b):
    return a not in b

def and_op(a, b):
    return a and b

def or_op(a, b):
    return a or b

def not_op(a):
    return not a

def pos(a):
    return +a

def neg(a):
    return -a


operations = {
    add: '+',
    sub: '-',
    mul: '*',
    truediv: '/',
    floordiv: '//',
    pow: '**',
    mod: '%',
    and_: '&',
    or_: '|',
    xor: '^',
    lshift: '<<',
    rshift: '>>',
    invert: '~',
    eq: '==',
    ne: '!=',
    lt: '<',
    le: '<=',
    gt: '>',
    ge: '>=',
    is_: 'is',
    is_not: 'is not',
    in_: 'in',
    not_in: 'not in',
    and_op: 'and',
    or_op: 'or',
    not_op: 'not',
    pos: '+',
    neg: '-'
}
