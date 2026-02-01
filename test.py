from expression import Var, operation


@operation
def func(a, b, c, *, d):
    return a+b+c+d

x = Var('x')
y = Var('y')

A = (x + y + 5 + 6)**5
B = x + 3

x.value = 2;y.value = 4


print(A.calculate(), B.calculate())
