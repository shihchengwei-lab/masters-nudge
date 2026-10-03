"""Reproducible standard-library random state for randomized project tests."""
import random
import sys
import pytest

random.seed(0)
raise SystemExit(pytest.main(sys.argv[1:]))
