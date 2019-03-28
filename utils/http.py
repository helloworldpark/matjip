import requests
from utils.errorhandler import handle_error


def get_html(url):
    """
    URL로부터 HTML을 string의 형태로 받는다. 만일 HTML을 받지 못했다면 ok는 False이다.
    :param url: HTML을 요청할 URL
    :type url: str
    :return: HTML, ok
    :rtype: str, bool
    """
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
    """
    URL로부터 JSON을 파싱된 형태로 받는다. 만일 JSON을 받지 못했다면 ok는 False이다.
    :param url: HTML을 요청할 URL
    :type url: str
    :return: HTML, ok
    :rtype: dict, bool
    """
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


