import os

def test_manifest(temp_path):
    os.environ["aipseo_manifest"] = temp_path

    # Cleanup
    os.environ.pop("aipseo_manifest", None) 