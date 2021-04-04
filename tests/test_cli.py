import pytest

from b2c2.cli import validate_quantity, rfq
import click


def test_validate_quantity():
    with pytest.raises(click.exceptions.BadParameter):
        validate_quantity(None, None, "def")
    with pytest.raises(click.exceptions.BadParameter):
        assert validate_quantity(None, None, "14.42445") == '14.42445'

    assert validate_quantity(None, None, "14.42") == '14.42'
    assert validate_quantity(None, None, "14.4244") == '14.4244'