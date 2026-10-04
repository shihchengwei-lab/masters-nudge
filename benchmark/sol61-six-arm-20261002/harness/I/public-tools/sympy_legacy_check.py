"""Map the repository's legacy bool result to a conventional process exit code."""
import sys
from sympy.testing.runtests import test

sys.exit(0 if test(*sys.argv[1:], colors=False) else 1)
