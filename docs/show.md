# Show

`show` is a function that displays variables given as arguments. Names of the variables that are provided as positional arguments are determined based on Python reflection.

```python
>>> x = 123
>>> y = [1, 2, 3]
>>> show(x, y, x*2+1)
x = 123
y = [1, 2, 3]
x * 2 + 1 = 247
```

Variables that are provided as keyword arguments inherit names from corresponding arguments.

```python
>>> x = 123
>>> y = 234
>>> show(foo=x+y)
foo = 357
```

There is also `show_` function that expects their arguments to be expressions that should be evaluated in context of the caller.

```python
>>> x = 123
>>> y = 234
>>> show_('x+y', py_ver='sys.version.split()[0]')
x + y = 357
py_ver = '3.6.2'
```

`show` and `show_` functions can be also called without arguments to display all the variables in context of the caller.
