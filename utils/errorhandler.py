import traceback
import sys


def handle_error(f):
    try:
        f()
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
