import pytest
from tldextract import TLDExtract


@pytest.fixture
def custom_extractor(tmp_path):
    local_list_location = tmp_path / "list.txt"
    local_list_location.write_text('moz.illa')
    return TLDExtract(
        suffix_list_urls=[local_list_location.as_uri()],
        cache_dir=(tmp_path / "cache").as_posix(),
        # Without this a suffix list that failed to load would quietly fall
        # back to the bundled snapshot, and the test would pass against the
        # real public suffix list instead of the contrived one.
        fallback_to_snapshot=False
    )


@pytest.fixture
def extractor():
    return TLDExtract()
