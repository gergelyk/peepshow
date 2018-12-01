x = 123
y = {'name': 'John', 'age': 123}
z = "Hello World!"

# show all variables in scope
show()

# or only selected variables
show(x, y)

# you can also rename them
show(my_var=x)

# use 'show_' to specify variable names as a string
show_('x')

# expressions and renaming are also allowed
show_('x + 321', zet='z')
