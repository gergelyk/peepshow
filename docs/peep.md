# Peep

`peep` function provides an interactive interface to access properties of the target object given as an argument. When called without arguments, `peep` starts from inspecting a dictionary that consists of all the variables in scope of the caller. There is also `peep_` function which expects an expression instead of variable to be provided as an argument. Such expression is evaluated in context of the caller and the result becomes a target object.

```python
>>> x = [1, 2, 3]  # target object
>>> peep(x)        # target provided explicitly
>>> peep()         # all the variables in this context a assembly to a target
>>> peep_('x')     # target provided as an expression
```

## Navigating

After invoking `peep` an interactive prompt appears on the screen. User can call one of the commands using either its full name or and alias. Alias consists only of capital letters form the full name. Use *Help* command to get full list of commands or invoke *help <COMMAND>* to get help on specific command <COMMAND>.

```
> help        # provides list of commands
> h           # the same as above
> help manual # provides help on 'manual' command
> h man       # the same as above
```

It is also possible to execute suggested command that is displayed in the prompt simply by hitting Enter key.

Prompt also provides type name of the target. This applies only to selected Python built-in types.


## Basic Inspection

Regardless of the target type, command *Info* (executed at startup) can be used for displaying basic summary. More detailed information are provided by *Features* command.

*PrettyPrint* command attempts to show target recursively in a recursive manner.

Commans *?* and *??* display target's docstring and source code respectively.

Whenever there is too much information on the screen, *CLear* command or CTRL+L can be used.

Typically there is a need of inspecting of target's attributes. This can be done by using *Dir* command. Optionally one can enter an integer number to select corresponding attribute. Such attribute becomes a new target. Beside *Dir*, there are also *DirAll* and *DirPublic* that help to specify if private or built-in attributes should be considered. Note that peepshow distinguish between public/private/built-in attributes by looking at the underscores in the name.

While *Dir* commands inspect by using `dir()` function, there are also *Vars* and *VarsPublic* commands that use `vars()` function instead.

*.<ATTRIB>* is a command that can be used to access attributes without listing them.

Commands *Bases*, *Mro*, *Self*, *Type* can be invoked to understand relations between the type of the target and other types. For more details use *help*.

Example:

```
> t           # take type of the target
> .__name__   # take name of the type above
> d           # list attributes of the string above
> 5           # select 5-th attribute
```

## History

Peepshow keeps track of the targets that are examined. One can display history and traverse through it by using following commands:

```
> .    # display history
> ..   # go one step backward
> -    # go one step forward
> /    # go to the very beginning
```

## Expressions

For clarity, in the title bar target is described in a functional language that is not necessarily a valid Python expression. This language extends Python by:

* `->` to denote passing target to a function. E.g. `x -> func` corresponds to `func(x)` in pure Python.
* `=>` to denote passing target to an expression. E.g. `x => _ + 5` corresponds to `(lambda _: _ + 5)(x)` in pure Python.
* `<>` to denote taking n-th element of iterable. E.g. `range(30, 40)<5>` could be replaced by `[*range(30, 40)][5]` in pure Python.
* `<*>` to denote all the variables in context of the caller. Note that peepshow have access to locals, globals and built-ins, but not to enclosed variables.

*eXpression* prints a valid Python expression which evaluates to the target. The same expression can be passed to underlying IPython by *Export* command.

It is possible to evaluate an expression and consider result to be a new target. For instance:

```
> $range(100)  # take generator object as a new target
> $list(_)     # converts target to a list and takes it as a new target
```

Following predefined symbols are available:

* `_` - current target
* `nth` - function that returns n-th element from an iterable
* `catch` - wrapper that returns exception raised by wrapped function. For instance:

```
> catch(divmod)(1, 0)  # returns ZeroDivisionError
```

Next to *$* (dollar) there is also *!* (exclamation mark) which evaluates expression and prints the result without replacing current target. For example:

```
> !import re                      # import 're' module
> !m = re.match('\d*', '123abc')  # assign 'm'
> $m.group()                      # execute 'group' method and take result as a target
```

## Iterables

Elements of iterables can be listed by *\** (asterisk). Optional offset can be provided to skip given number of initial elements. Items from cache (last items visible on the screen) can be selected from by providing an integer numner. Cache can be recalled any time by *ShowCache*. Example:

```
> $range(1000)
> *100          # show items starting from 100-th
> 105           # pick 105-th item
```

It is important to know that generator objects are drained by listing their elements. In many cases this can influence execution of underlying application.

In case of dictionaries, only keys are iterated by invoking *\**. Alternatively *\*\** can be used to display keys and corresponding values. Optional offset can be specified.


## Subscribables

Target can be subscribed by using square brackets. Slicing an other expressions are allowed. Examples:

```
> $[1, 22, 333]
> ..
> [2]     # select 333
> ..
> [1:]    # select [22, 333]
> ..
> [_[0]]  # select [22]
```


## Callables

Targets can be called by using round brackets. All kinds of Python-compatible expressions are allowed inside. Examples:

```
> !x = (123,)
> $str
> ()                # empty string
> ..
> (*x)              # '123'
> ..
> (b'abc', 'utf8')  # 'abc'
```

Command *Pass* can be used for passing target to a function and executing this function:

```
> $"abcdef"
> pass len  # equivalent of $len(_)
```

## Exiting

Use *Quit* or CTRL+C to quit peepshow and terminate underlying application. Use *Continue* or CTRL+D to return to underlying application. Additionally *Export* command continues underlying IPython session and provides it with an expression that evaluates to current target.
