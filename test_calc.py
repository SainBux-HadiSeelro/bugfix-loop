import pytest

from calc import divide


def test_divide_normal():
    assert divide(10, 2) == 5
    assert divide(-6, 3) == -2
    assert divide(7, 2) == 3.5


def test_divide_by_zero_raises_value_error():
    with pytest.raises(ValueError, match="cannot divide by zero"):
        divide(10, 0)