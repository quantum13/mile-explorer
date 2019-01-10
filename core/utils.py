from urllib.parse import urlparse, parse_qs, urlencode


def url_without_qs_param(url, remove_params=None, replace_params: dict = None):
    url_parsed = urlparse(url)
    qs = parse_qs(url_parsed.query)
    if remove_params:
        for param in (remove_params if type(remove_params) is list else [remove_params]):
            qs.pop(param, None)
    if replace_params:
        for k, v in replace_params.items():
            qs[k] = v
    return f"{url_parsed.path}?{urlencode(qs, True)}"
