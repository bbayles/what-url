from ada_cffi._ada_cffi_wrapper import ffi, lib

URL_ATTRIBUTES = (
    'href',
    'username',
    'password',
    'protocol',
    'host',
    'port',
    'hostname',
    'pathname',
    'search',
    'hash',
)


def _get_str(c_value):
    return ffi.string(c_value.data, c_value.length).decode('utf-8')


def check_url(s):
    """
    Returns ``True`` if *s* represents a valid URL, and ``False`` otherwise.
    """
    s_bytes = s.encode('utf-8')
    return lib.ada_is_valid(s_bytes, len(s_bytes))  


def join_url(base_url, s):
    """
    Return the URL that results from joining *base_url* to *s*.
    Raises ``ValueError`` if no valid URL can be constructed.
    """
    base_bytes = base_url.encode('utf-8')
    s_bytes = s.encode('utf-8')
    ada_url = lib.ada_parse_with_base(
        s_bytes, len(s_bytes), base_bytes, len(base_bytes)
    )
    try:
        if not lib.ada_is_valid(ada_url):
            raise ValueError('Invalid URL') from None
        
        return _get_str(lib.ada_get_href(ada_url))
    finally:
        lib.ada_free(ada_url)


def normalize_url(s):
    """
    Returns a "normalized" URL with all ``'..'`` and ``'/'`` characters resolved.
    """
    return parse_url(s)['href']


def parse_url(s):
    """
    Returns a dictionary with the parsed components of the URL represented by *s*.
    
    For the URL ``'https://user_1:password_1@example.org:8080/dir/../api?q=1#frag'``,
    the dictionary will have:

    * ``href`` -  ``'https://user_1:password_1@example.org:8080/api?q=1#frag'``
    * ``username`` - ``'user_1'``
    * ``password`` - ``'password_1'``
    * ``protocol`` - ``'https:'``
    * ``host`` - ``'example.org:8080'``
    * ``port`` - ``'8080'``
    * ``hostname`` - ``'example.org'``
    * ``pathname`` - ``'/dir/api'``
    * ``search`` - ``'?q=1'``
    * ``hash`` - ``'frag'``
    """
    s_bytes = s.encode('utf-8')
    ada_url = lib.ada_parse(s_bytes, len(s_bytes))
    ret = {}
    try:
        if not lib.ada_is_valid(ada_url):
            raise ValueError('Invalid URL') from None
        
        for attr in URL_ATTRIBUTES:
            get_func = getattr(lib, f'ada_get_{attr}')
            ret[attr] = _get_str(get_func(ada_url))
    finally:
        lib.ada_free(ada_url)
    
    return ret


def replace_url(s, **kwargs):
    """
    Start with the URL represented by *s*, replace the components given in the *kwargs*
    mapping, and return a normalized URL with the result.
    
    Raises ``ValueError`` if the input URL or one of the components is not valid.
    """
    s_bytes = s.encode('utf-8')
    ada_url = lib.ada_parse(s_bytes, len(s_bytes))
    try:
        if not lib.ada_is_valid(ada_url):
            raise ValueError('Invalid URL') from None
        
        for attr in URL_ATTRIBUTES:
            value = kwargs.get(attr)
            if not value:
                continue

            set_func = getattr(lib, f'ada_set_{attr}')
            value_bytes = value.encode()
            set_result = set_func(ada_url, value_bytes, len(value_bytes))
            if (set_result is not None) and (not set_result):
                raise ValueError(f'Invalid value for {attr}') from None
            
        return _get_str(lib.ada_get_href(ada_url))
    finally:
        lib.ada_free(ada_url)
