from utils.errorhandler import handle_error
from utils.http import get_html


if __name__ == '__main__':
    body, ok = get_html(url="http://www.google.com")
    print(ok)
    print(body)
