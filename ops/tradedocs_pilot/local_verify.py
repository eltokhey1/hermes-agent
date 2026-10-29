"""Single-command TradeDocs pilot verification with non-vacuous unittest discovery."""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent


def verify(root=ROOT):
    suite = unittest.defaultTestLoader.discover(str(root), pattern="test_*.py")
    if suite.countTestCases() == 0:
        raise ValueError("No unittest test cases discovered")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    try:
        raise SystemExit(verify())
    except ValueError as exc:
        raise SystemExit(str(exc)) from None
