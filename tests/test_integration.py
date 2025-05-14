import os
import pytest
from aipseo.utils import make_api_request


@pytest.mark.integration
def test_lookup_production():
    # Ensure we use the production manifest (aipseo.json) by setting the environment variable.
    os.environ["aipseo_manifest"] = os.path.abspath("aipseo.json")
    result = make_api_request("lookup", params={"url": "example.com"})
    assert "url" in result
    assert result["url"] == "example.com"
    # Optionally, check for additional keys if expected (e.g. "status" or "data"). 