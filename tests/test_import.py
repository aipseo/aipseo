import aipseo


def test_version_string():
    assert isinstance(aipseo.__version__, str)
    assert aipseo.__version__