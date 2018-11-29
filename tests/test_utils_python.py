import pytest
from peepshow.utils.python import caller_gloloc
from peepshow.utils.python import arg_names
from peepshow.utils.python import CheckInvocation, InvocationError
from peepshow.utils.python import catch, NoException
from peepshow.utils.python import nth, prettify_expr, exc_to_str

class TestCallerGloloc:
    def test_locals(self):
        def foo():
            gloloc = caller_gloloc()
            loc = gloloc.loc
            assert loc['x'] == 123
            assert loc['y'] == 234
            assert loc['foo'] == foo

        def bar():
            x = 123
            y = 234
            foo()

        bar()

    def test_globals(self):
        def foo():
            gloloc = caller_gloloc()
            glo = gloloc.glo
            assert glo['caller_gloloc'] == caller_gloloc
            assert glo['TestCallerGloloc'] == TestCallerGloloc

        def bar():
            x = 123
            y = 234
            foo()

        bar()


class TestArgNames:
    def test_locals(self):
        def foo(a, b, c=321, d=432):
            anames = arg_names()
            assert anames == ['x', 'y']

        def bar():
            x = 123
            y = 234
            z = 345
            foo(x, y, d=z)

        bar()


class TestCheckInvocation:

    def test_incorrect_invocation(self):
        def foo(x, y, z):
            pass

        with pytest.raises(InvocationError):
            with CheckInvocation():
                foo()

    def test_function_raises(self):
        def foo(x, y, z):
            raise RuntimeError

        with pytest.raises(RuntimeError):
            with CheckInvocation():
                foo(1, 2, 3)

    def test_successfull_call(self):
        def foo(x, y, z):
            return x + y + z

        with CheckInvocation():
            ret = foo(1, 2, 3)

        assert ret == 6


class TestCatch:

    def test_target_raises(self):
        def foo(x, y):
            return x / y

        exc = catch(foo)(1, 0)
        assert isinstance(exc, ZeroDivisionError)

    def test_target_doesnt_raise(self):
        def foo(x, y):
            return x / y

        with pytest.raises(NoException) as exc_inf:
            catch(foo)(6, 2)

        assert exc_inf.value.return_value == 3


class TestNth:

    def test_tuple(self):
        t = (11, 22, 33, 44)
        assert nth(t, 2) == 33

    def test_gen_expr(self):
        g = (x**2 for x in range(10))
        assert nth(g, 3) == 9

    def test_gen_func(self):
        def f():
            yield from [11, 22, 33, 44]
        g = f()
        assert nth(g, 2) == 33

    def test_index_out_of_range(self):
        t = (11, 22, 33, 44)
        with pytest.raises(IndexError):
            nth(t, 5)


class TestPrettifyExpr:

    def test_arithmetic(self):
        assert prettify_expr('123+234//5') == '123 + 234 // 5'
        assert prettify_expr('123+-234%5  ') == '123 + -234 % 5'
        assert prettify_expr('123   *3   #qq') == '123 * 3'
        assert prettify_expr('qwe =  asd =  234 == None') == 'qwe = asd = 234 == None'

    def test_parentheses(self):
        assert prettify_expr('(  12*23)+ 34') == '12 * 23 + 34'
        assert prettify_expr('34 + (( 12*  (23+23)))') == '34 + 12 * (23 + 23)'

    def test_list(self):
        assert prettify_expr('x = [     ]  ') == 'x = []'
        assert prettify_expr('[1] +[ ] / [1,2,] + [3,4]  ') == '[1] + [] / [1, 2] + [3, 4]'
        assert prettify_expr('[ [],[[],[]]]') == '[[], [[], []]]'

    def test_tuple(self):
        assert prettify_expr('func  ( (1,2,3,) )') == 'func((1, 2, 3))'
        assert prettify_expr('func(  *(x, y   ,z) )') == 'func(*(x, y, z))'
        assert prettify_expr('foo[(1,2,3)]') == 'foo[1, 2, 3]'

    def test_dict(self):
        assert prettify_expr('{"x" : 123, \'yy\': 234, 567:...}') == "{'x': 123, 'yy': 234, (567): ...}"
        # note: parentheses could be skipped                                                ^   ^
        assert prettify_expr('{"x" : {}, **{"y":set()}, **abc}') == "{'x': {}, **{'y': set()}, **abc}"
        assert prettify_expr('dict (   abc=  123,qwe=x)') == 'dict(abc=123, qwe=x)'


class TestExcToStr:

    def test_regular(self):
        try:
            123/0
        except Exception as ex:
            exc = ex

        assert exc_to_str(exc) == 'division by zero'
        assert exc_to_str(exc, True) == 'ZeroDivisionError: division by zero'

    def test_no_msg(self):
        try:
            raise RuntimeError
        except Exception as ex:
            exc = ex

        assert exc_to_str(exc) == 'RuntimeError'
        assert exc_to_str(exc, True) == 'RuntimeError'
