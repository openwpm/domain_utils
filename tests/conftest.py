import pytest
from tldextract import TLDExtract


@pytest.fixture
def custom_extractor(tmp_path):
    local_list_location = tmp_path / "list.txt"
    local_list_location.write_text('moz.illa')
    return TLDExtract(
        suffix_list_urls=[local_list_location.as_uri()],
        cache_file=local_list_location.as_posix(),
        fallback_to_snapshot=True
    )


@pytest.fixture
def extractor():
    return TLDExtract()
