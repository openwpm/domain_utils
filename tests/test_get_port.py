from domain_utils import get_port


def test_no_port():
    assert get_port('domain.net') is None


def test_port_in_ip():
    assert get_port('10.0.0.1:80/path/to/index.html') == 80


def test_port_in_url():
    assert get_port('example.com:80/path/to/index.html') == 80


def test_port_in_domain():
    assert get_port('example.com:5000') == 5000


def test_port_in_ip_no_path():
    assert get_port('10.0.0.1:80') == 80


def test_port_no_tld():
    assert get_port('localhost:8000') == 8000


def test_url_with_protocol():
    assert get_port('ws://example.com:5000') == 5000
