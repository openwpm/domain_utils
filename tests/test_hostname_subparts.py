from domain_utils import hostname_subparts


def test_returns_ip_address():
    assert hostname_subparts('http://127.0.0.1/foo.html') == ['127.0.0.1']


def test_returns_an_empty_list_on_relative_url():
    assert hostname_subparts('/my/path/is.html') == []


def test_returns_vanilla_url():
    result = hostname_subparts('http://www.google.com')
    assert result == ['www.google.com', 'google.com']


def test_returns_when_path():
    result = hostname_subparts('http://www.google.com/has/path.html')
    assert result == ['www.google.com', 'google.com']


def test_returns_when_anchor():
    result = hostname_subparts('http://www.google.com#anchor')
    assert result == ['www.google.com', 'google.com']


def test_returns_vanilla_url_include_ps():
    result = hostname_subparts('http://www.google.com', include_ps=True)
    assert result == ['www.google.com', 'google.com', 'com']


def test_complex_private_domain():
    result = hostname_subparts('cn-north-1.eb.amazonaws.com.cn')
    assert result == []


def test_complex_private_domain_with_ps():
    result = hostname_subparts('cn-north-1.eb.amazonaws.com.cn', include_ps=True)
    assert result == ['cn-north-1.eb.amazonaws.com.cn']


def test_complex_private_domain_with_subdomain():
    result = hostname_subparts('mydomain.cn-north-1.eb.amazonaws.com.cn')
    assert result == ['mydomain.cn-north-1.eb.amazonaws.com.cn']


def test_complex_private_domain_with_subdomain_with_ps():
    result = hostname_subparts('mydomain.cn-north-1.eb.amazonaws.com.cn', include_ps=True)
    assert result == ['mydomain.cn-north-1.eb.amazonaws.com.cn', 'cn-north-1.eb.amazonaws.com.cn']
