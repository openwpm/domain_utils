from domain_utils import get_port


def test_no_port():
    assert get_port('domain.net') == None

def test_port_in_ip():
    assert get_port('10.0.0.1:80/path/to/index.html') == None

def test_port_in_url():
    assert get_port('example.com:80/path/to/index.html') == None

def test_port_in_domain():
    assert get_port('example.com:5000') == None
    
def test_port_in_ip_strict():
    assert get_port('10.0.0.1:80/path/to/index.html', strict=True) == 80

def test_port_in_url_strict():
    assert get_port('example.com:80/path/to/index.html', strict=True) == 80

def test_port_in_domain_strict():
    assert get_port('example.com:5000', strict=True) == 5000

def test_url_with_protocol_strict():
    assert get_port('ws://example.com:5000', strict=True) == 5000

def test_url_with_protocol():
    assert get_port('ws://example.com:5000') == 5000

def test_no_port_strict():
    assert get_port('domain.net', strict=True) == None

def test_no_port_strict_protocol():
    assert get_port('https://domain.net', strict=True) == None
