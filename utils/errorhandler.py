import traceback
import sys


def handle_error(f):
    """
    예외를 출력하고 더 이상의 예외 전파는 막는다.
    :param f: 인자 없는 함수.
    :type f: Callable[[]]
    """
    try:
        f()
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
