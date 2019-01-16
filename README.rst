PeepShow
========

Provides following utilities for debugging Python applications:

* show - lightweight function that prints name and value of your variable(s) to the console.
* peep - featured, interactive interface for data inspection.

.. image:: https://user-images.githubusercontent.com/11185582/51219128-b3127780-192f-11e9-8618-ecfff642b87f.gif

Installation
------------

Install ``peepshow`` package:

.. code-block:: bash

    pip install peepshow

PeepShow uses ``clear``, ``vim``, ``man`` commands which are available in most of Linux distributions. Users of other operating systems need to install them on their own.

Built-Ins
^^^^^^^^^

If you expect to use peepshow often, consider adding ``peep`` and ``show`` commands to Python's built-ins. Edit either ``{site-packages}/sitecustomize.py`` or ``{user-site-packages}/usercustomize.py`` and append the following:

.. code-block:: python

    import peepshow
    import builtins
    builtins.peep = peepshow.peep
    builtins.show = peepshow.show
    builtins.peep_ = peepshow.peep_
    builtins.show_ = peepshow.show_

Alternatively let the installer do it for you:

.. code-block:: bash

        pip install peepshow --upgrade --force-reinstall --no-deps --install-option="--add-builtins"

Note that ``pip uninstall peepshow`` command will not undo this change. You need to do it manually.

Breakpoint
^^^^^^^^^^

It is also possible to invoke ``peep()`` as a result of calling built-in function ``breakpoint()``. To enable such behaviour use ``PYTHONBREAKPOINT`` system variable:

.. code-block:: bash

    export PYTHONBREAKPOINT=peepshow.peep

Compatibility
-------------

* This software is expected to work with Python 3.6, 3.7 and compatible.
* It has never been tested under operating systems other than Linux.
* It works fine when started in a plain Python script, in ipython or ptipython
* In these environments like interactive python console, in pdb and ipdb, peep and show cannot infer names of the variables in the user context, so they need to be provided explicitely (e.g. use `peep_`` and ``show_``).

Usage
-----

show
^^^^

Running this script:

.. code-block:: python

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


will result in following output:

.. code-block::

    x = 123
    y = {'age': 123, 'name': 'John'}
    z = 'Hello World!'
    x = 123
    y = {'age': 123, 'name': 'John'}
    my_var = 123
    x = 123
    x + 321 = 444
    zet = 'Hello World!'


peep
^^^^

Try to run the following script:

.. code-block:: python

    x = 123
    y = {'name': 'John', 'age': 123}
    z = "Hello World!"

    # inspect dictionary that consists of all the variables in the scope
    peep()

    # or inspect variable of your choice directly
    peep(x)

    # use 'peep_' to specify variable name as a string
    peep_('x')


When interactive interface pops up:

* hit ENTER to see list of available variables
* type ``10`` and hit ENTER to select ``y``
* hit ENTER again to see items of your dictionary
* type ``dir`` and hit ENTER to list attributes of ``y`` (excluding built-ins)
* type ``continue`` and hit ENTER to proceed or type ``quit`` and hit ENTER to terminate your script

Note that all the commands have their short aliases. E.g. ``quit`` and ``q`` is the same.

For more help:

* type ``help`` and hit ENTER to see list of available commands
* type ``man`` and hit ENTER to read the manual, hit ``q`` when you are done


Development
-----------

Preparing Environment
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    ./setup.sh
    source venv/bin/activate


Modifying Dependencies
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # edit setup.py
    # edit requirements*.in
    pip-compile
    pip-sync
    # git add... commit... push...

Testing
^^^^^^^

.. code-block:: bash

    pytest

Releasing
^^^^^^^^^

.. code-block:: bash

    # update version in setup.py
    python setup.py sdist
    twine upload dist/peepshow-$VERSION.tar.gz
    git tag $VERSION
    git push --tags



