"""Simple decorator that applies f-string formatting to docstrings
To use, simply apply `@fmydocstring` to your function
Only global variables are accessible for interpolation.
Credits:
https://gist.github.com/RhetTbull/47366e42fd593762e7d28db2ca160b07

Modification credits:
https://stackoverflow.com/questions/5929107/decorators-with-parameters
"""

import functools


def fmydocstring(g, l):
    # docstrings_dict = docstrings_dict
    def decorator(func):
        """Simple decorator to treat docstrings as f-strings"""
        # globals()["docstrings_dict"] = docstrings_dict
        func.__doc__ = (
            eval(f'f"""{func.__doc__}"""', g, l) if func.__doc__ is not None else None
        )

        # func.__doc__ = eval(f'f"""{func.__doc__}"""', globals()) if func.__doc__ is not None else None
        @functools.wraps(func)
        def func_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return func_wrapper

    return decorator
