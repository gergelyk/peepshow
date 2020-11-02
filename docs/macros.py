import random

def define_env(env):

    @env.macro
    def random_digits(n):
        """Sample macro"""

        digits = [str(random.randint(0, 9)) for _ in range(n)]
        return ', '.join(digits)
