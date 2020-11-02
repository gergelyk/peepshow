# peepshow

Provides following utilities for debugging Python applications:

* show - lightweight function that prints name and value of your variable(s) to the console.
* peep - featured, interactive interface for data inspection.

![](https://user-images.githubusercontent.com/11185582/51219128-b3127780-192f-11e9-8618-ecfff642b87f.gif)

## Resources

* Documentation: <https://gergelyk.github.io/peepshow>
* Repository: <https://github.com/gergelyk/peepshow>
* Package: <https://pypi.python.org/pypi/peepshow>
* Author: [Grzegorz Krasoń](mailto:grzegorz.krason@gmail.com)
* License: [MIT](LICENSE)

## Installation

Install `peepshow` package:

```sh
pip install peepshow
```

PeepShow uses `clear`, `vim`, `man` commands which are available in most of Linux distributions. Users of other operating systems need to install them on their own.

### Built-Ins

If you expect to use peepshow often, consider adding `peep` and `show` commands to Python's built-ins and enabling except hook. Edit either `{site-packages}/sitecustomize.py` or `{user-site-packages}/usercustomize.py` and append the following:

```python
import peepshow
import builtins
builtins.peep = peepshow.peep
builtins.show = peepshow.show
builtins.peep_ = peepshow.peep_
builtins.show_ = peepshow.show_
peepshow.enable_except_hook(consider_env=True)
```

### Breakpoint

It is also possible to invoke `peep()` as a result of calling built-in function `breakpoint()`. To enable such behavior use `PYTHONBREAKPOINT` system variable:

```sh
export PYTHONBREAKPOINT=peepshow.peep
```

## Compatibility

* This software is expected to work with Python 3.6, 3.7, 3.8 and compatible.
* It has never been tested under operating systems other than Linux.
* It works fine when started in a plain Python script, in ipython or ptipython.
* In these environments like interactive python console, in pdb and ipdb, peep and show cannot infer names of the variables in the user context, so they need to be provided explicitly (e.g. use `peep_` and `show_`).

## Usage

### `show`

Running this script:

```python
x = 123
y = {'name': 'John', 'age': 123}
z = "Hello World!"

# show all the variables in the scope
show()

# or only variables of your choice
show(x, y)

# you can also rename them
show(my_var=x)

# use 'show_' to specify variable names as a string
show_('x')

# expressions and renaming are also allowed
show_('x + 321', zet='z')
```

will result in following output:

```
x = 123
y = {'age': 123, 'name': 'John'}
z = 'Hello World!'
x = 123
y = {'age': 123, 'name': 'John'}
my_var = 123
x = 123
x + 321 = 444
zet = 'Hello World!'
```

### `peep`

Try running the following script:

```python
x = 123
y = {'name': 'John', 'age': 123}
z = "Hello World!"

# inspect dictionary that consists of all the variables in the scope
peep()

# or inspect variable of your choice directly
peep(x)

# use 'peep_' to specify variable name as a string
peep_('x')
```

When interactive interface pops up:

* Hit ENTER to see list of available variables.
* Type `10` and hit ENTER to select `y`.
* Hit ENTER again to see items of your dictionary.
* Type `dir` and hit ENTER to list attributes of `y` (excluding built-ins).
* Type `continue` and hit ENTER to proceed or type `quit` and hit ENTER to terminate your script.

Note that all the commands have their short aliases. E.g. `quit` and `q` is the same.

For more help:

* Type `help` and hit ENTER to see list of available commands.
* Type `man` and hit ENTER to read the manual, hit `q` when you are done.

### excepthook

Before running your script, set environment variable `PYTHON_PEEP_EXCEPTIONS` to `1`. Now run the script and see what happens when an exception is raised.

## Development

```sh
# Preparing environment
pip install --user poetry  # unless already installed
poetry install

# Auto-formatting
poetry run docformatter -ri peepshow tests
poetry run isort -rc peepshow tests
poetry run yapf -r -i peepshow tests

# Checking coding style
poetry run flake8 peepshow tests

# Checking composition and quality
poetry run vulture peepshow tests
poetry run mypy peepshow tests
poetry run pylint peepshow tests
poetry run bandit peepshow tests
poetry run radon cc peepshow tests
poetry run radon mi peepshow tests

# Testing with coverage
poetry run pytest --cov peepshow --cov tests

# Rendering documentation
poetry run mkdocs serve

# Building package
poetry build

# Releasing
poetry version minor  # increment selected component
git commit -am "bump version"
git push
git tag ${$(poetry version)[2]}
git push --tags
poetry build
poetry publish
poetry run mkdocs build
poetry run mkdocs gh-deploy -b gh-pages
```

## Donations

If you find this software useful and you would like to repay author's efforts you are welcome to use following button:

[![Donate](https://www.paypalobjects.com/en_US/PL/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=D9KUJD9LTKJY8&source=url)

