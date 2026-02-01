from enum import Enum
from typing import Callable
from _operations import (
    add, sub, mul, truediv, floordiv, pow, mod,
    and_, or_, xor, lshift, rshift, invert,
    eq, ne, lt, le, gt, ge, is_, is_not, in_, not_in,
    and_op, or_op, not_op, pos, neg,
    operations
)




class ExprType(Enum):
    NORMAL = 0
    VARIABLE = 1
    OBJECT = 2


class _FuncInfo:
    def __init__(self, func:Callable, *args, **kwargs):
        self.func = func
        self.pos_para = args
        self.kw_para = kwargs

    def _get_precedence(self, func):
        precedence = {
            or_op: 1,
            and_op: 2,
            eq: 3,
            ne: 3,
            lt: 3,
            le: 3,
            gt: 3,
            ge: 3,
            is_: 3,
            is_not: 3,
            in_: 3,
            not_in: 3,
            or_: 4,
            xor: 5,
            and_: 6,
            lshift: 7,
            rshift: 7,
            add: 8,
            sub: 8,
            mul: 9,
            truediv: 9,
            floordiv: 9,
            mod: 9,
            pow: 10,
            invert: 11,
            pos: 11,
            neg: 11,
            not_op: 11
        }
        if func in precedence:
            return precedence[func]
        return 999

    def _is_unary(self, func):
        return func in (invert, pos, neg, not_op)

    def _needs_parens(self, para, parent_func, is_right=False):
        if not isinstance(para, _FuncInfo):
            return False
        para_precedence = self._get_precedence(para.func)
        parent_precedence = self._get_precedence(parent_func)
        if para_precedence < parent_precedence:
            return True
        if para_precedence == parent_precedence:
            if is_right and parent_func in (sub, truediv, floordiv, mod, pow, lshift, rshift):
                return True
            if parent_func == pow and not is_right:
                return True
            if parent_func in (eq, ne, lt, le, gt, ge, is_, is_not, in_, not_in):
                return True
            if parent_func in (and_op, or_op) and para.func in (and_op, or_op):
                return True
            if self._is_unary(parent_func) and self._is_unary(para.func):
                return True
        return False

    def __repr__(self):
        if self.func not in operations:
            if self.pos_para and not self.kw_para:
                return f'{self.func.__name__}({", ".join(str(i) for i in self.pos_para)})'
            elif self.kw_para and not self.pos_para:
                return f'{self.func.__name__}({", ".join(f"{k}={v}" for k, v in self.kw_para.items())})'
            elif self.pos_para and self.kw_para:
                return f'{self.func.__name__}({", ".join(str(i) for i in self.pos_para)}, {", ".join(f"{k}={v}" for k, v in self.kw_para.items())})'
            else:
                return f'{self.func.__name__}()'
        else:
            if self._is_unary(self.func):
                para = self.pos_para[0]
                para_str = f'({para})' if self._needs_parens(para, self.func, False) else str(para)
                return f'{operations[self.func]}{para_str}'
            else:
                left = self.pos_para[0]
                right = self.pos_para[1]
                left_str = f'({left})' if self._needs_parens(left, self.func, False) else str(left)
                right_str = f'({right})' if self._needs_parens(right, self.func, True) else str(right)
                return f'{left_str} {operations[self.func]} {right_str}'
    def __str__(self):
        return self.__repr__()


class _Expression:
    def __init__(self, struct):
        self._struct: _FuncInfo = struct

    def _get_paras(self, paras_set, struct):
        if isinstance(struct, _FuncInfo):
            for i in struct.pos_para:
                self._get_paras(paras_set, i)
            for i in struct.kw_para.keys():
                self._get_paras(paras_set, i)
        else:
            paras_set.add(struct)

    def calculate(self):
        """
        将值不为 None 的变量视为常量，返回新的表达式。
        """
        def _simplify_struct(struct):
            if isinstance(struct, Var) and struct.value is not None:
                # 变量有值，视为常量
                return struct.value
            if isinstance(struct, _FuncInfo):
                new_pos = [_simplify_struct(p) for p in struct.pos_para]
                new_kw = {k: _simplify_struct(v) for k, v in struct.kw_para.items()}
                # 如果所有参数都是常量，尝试直接计算
                if all(not isinstance(p, (_FuncInfo, Var)) for p in new_pos) and \
                   all(not isinstance(v, (_FuncInfo, Var)) for v in new_kw.values()):
                    try:
                        return struct.func(*new_pos, **new_kw)
                    except Exception:
                        # 计算失败则退回到表达式
                        pass
                return _FuncInfo(struct.func, *new_pos, **new_kw)
            return struct

        new_struct = _simplify_struct(self._struct)
        # 如果化简结果是常量，则封装为 OBJECT 类型表达式
        if not isinstance(new_struct, (_FuncInfo, Var)):
            return new_struct
        return _Expression(new_struct)

    @property
    def type(self):
        if isinstance(self._struct, Var):
            return ExprType.VARIABLE
        elif isinstance(self._struct, _FuncInfo):
            return ExprType.NORMAL
        else:
            return ExprType.OBJECT
    
    @property
    def vars(self):
        paras = set()
        self._get_paras(paras, self._struct)
        return tuple(i for i in paras if isinstance(i, Var))
    
    @property
    def var_num(self):
        return len(self.vars)

    def __repr__(self):
        return str(self._struct)
    def __str__(self):
        return str(self._struct)
    
    @property
    def content(self):
        return str(self._struct)

    def __add__(self, other):
        if isinstance(other, _Expression):
            return _Expression(_FuncInfo(add, self._struct, other._struct))
        else:
            return _Expression(_FuncInfo(add, self._struct, other))
    def __radd__(self, other):
        return _Expression(_FuncInfo(add, other, self._struct))

    def __sub__(self, other):
        if isinstance(other, _Expression):
            return _Expression(_FuncInfo(sub, self._struct, other._struct))
        else:
            return _Expression(_FuncInfo(sub, self._struct, other))
    def __rsub__(self, other):
        return _Expression(_FuncInfo(sub, other, self._struct))

    def __mul__(self, other):
        if isinstance(other, _Expression):
            return _Expression(_FuncInfo(mul, self._struct, other._struct))
        else:
            return _Expression(_FuncInfo(mul, self._struct, other))
    def __rmul__(self, other):
        return _Expression(_FuncInfo(mul, other, self._struct))
    
    def __truediv__(self, other):
        if isinstance(other, _Expression):
            return _Expression(_FuncInfo(truediv, self._struct, other._struct))
        else:
            return _Expression(_FuncInfo(truediv, self._struct, other))
    def __rtruediv__(self, other):
        return _Expression(_FuncInfo(truediv, other, self._struct))

    def __floordiv__(self, other):
        if isinstance(other, _Expression):
            return _Expression(_FuncInfo(floordiv, self._struct, other._struct))
        else:
            return _Expression(_FuncInfo(floordiv, self._struct, other))
    def __rfloordiv__(self, other):
        return _Expression(_FuncInfo(floordiv, other, self._struct))
    
    def __pow__(self, other):
        if isinstance(other, _Expression):
            return _Expression(_FuncInfo(pow, self._struct, other._struct))
        else:
            return _Expression(_FuncInfo(pow, self._struct, other))
    def __rpow__(self, other):
        return _Expression(_FuncInfo(pow, other, self._struct))
    
    def __mod__(self, other):
        if isinstance(other, _Expression):
            return _Expression(_FuncInfo(mod, self._struct, other._struct))
        else:
            return _Expression(_FuncInfo(mod, self._struct, other))
    def __rmod__(self, other):
        return _Expression(_FuncInfo(mod, other, self._struct))

    def __and__(self, other):
        if isinstance(other, _Expression):
            return _Expression(_FuncInfo(and_, self._struct, other._struct))
        else:
            return _Expression(_FuncInfo(and_, self._struct, other))
    def __rand__(self, other):
        return _Expression(_FuncInfo(and_, other, self._struct))

    def __or__(self, other):
        if isinstance(other, _Expression):
            return _Expression(_FuncInfo(or_, self._struct, other._struct))
        else:
            return _Expression(_FuncInfo(or_, self._struct, other))
    def __ror__(self, other):
        return _Expression(_FuncInfo(or_, other, self._struct))

    def __xor__(self, other):
        if isinstance(other, _Expression):
            return _Expression(_FuncInfo(xor, self._struct, other._struct))
        else:
            return _Expression(_FuncInfo(xor, self._struct, other))
    def __rxor__(self, other):
        return _Expression(_FuncInfo(xor, other, self._struct))

    def __lshift__(self, other):
        if isinstance(other, _Expression):
            return _Expression(_FuncInfo(lshift, self._struct, other._struct))
        else:
            return _Expression(_FuncInfo(lshift, self._struct, other))
    def __rlshift__(self, other):
        return _Expression(_FuncInfo(lshift, other, self._struct))

    def __rshift__(self, other):
        if isinstance(other, _Expression):
            return _Expression(_FuncInfo(rshift, self._struct, other._struct))
        else:
            return _Expression(_FuncInfo(rshift, self._struct, other))
    def __rrshift__(self, other):
        return _Expression(_FuncInfo(rshift, other, self._struct))

    def __invert__(self):
        return _Expression(_FuncInfo(invert, self._struct))

    def __eq__(self, other):
        if isinstance(other, _Expression):
            return _Expression(_FuncInfo(eq, self._struct, other._struct))
        else:
            return _Expression(_FuncInfo(eq, self._struct, other))

    def __ne__(self, other):
        if isinstance(other, _Expression):
            return _Expression(_FuncInfo(ne, self._struct, other._struct))
        else:
            return _Expression(_FuncInfo(ne, self._struct, other))

    def __lt__(self, other):
        if isinstance(other, _Expression):
            return _Expression(_FuncInfo(lt, self._struct, other._struct))
        else:
            return _Expression(_FuncInfo(lt, self._struct, other))

    def __le__(self, other):
        if isinstance(other, _Expression):
            return _Expression(_FuncInfo(le, self._struct, other._struct))
        else:
            return _Expression(_FuncInfo(le, self._struct, other))

    def __gt__(self, other):
        if isinstance(other, _Expression):
            return _Expression(_FuncInfo(gt, self._struct, other._struct))
        else:
            return _Expression(_FuncInfo(gt, self._struct, other))

    def __ge__(self, other):
        if isinstance(other, _Expression):
            return _Expression(_FuncInfo(ge, self._struct, other._struct))
        else:
            return _Expression(_FuncInfo(ge, self._struct, other))

    def __pos__(self):
        return _Expression(_FuncInfo(pos, self._struct))

    def __neg__(self):
        return _Expression(_FuncInfo(neg, self._struct))


class Var(_Expression):
    variables = {}
    def __init__(self, name: str, value=None):
        super().__init__(self)
        if name in Var.variables.values():
            raise Exception("Name already existed.")
        Var.variables[id(self)] = name
        self.value = value

    @property
    def name(self):
        return Var.variables[id(self)]
    @name.setter
    def name(self, value):
        if value in Var.variables.values():
            raise Exception("Name already existed.")
        Var.variables[id(self)] = value

    def __repr__(self):
        return self.name
    def __str__(self):
        return self.name

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return id(self) == id(other)


def operation(func:Callable):
    def wrapper(*args, **kwargs) -> _Expression:
        return _Expression(_FuncInfo(func, *args, **kwargs))
    return wrapper


class Equaltion:
    ...








__all__ = [
    'ExprType',
    'Var',
    'operation',
    'Equaltion'
]