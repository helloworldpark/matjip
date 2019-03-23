import requests
from utils.errorhandler import handle_error


def get_html(url):

    ok = False
    body = ''

    def request():
        res = requests.get(url=url)
        nonlocal body
        nonlocal ok
        ok = res.ok
        body = res.text

    handle_error(request)

    return body, ok


def get_json(url):

    ok = False
    body = ''

    def request():
        res = requests.get(url=url)
        nonlocal body
        nonlocal ok
        ok = res.ok
        body = res.json()

    handle_error(request)

    return body, ok


