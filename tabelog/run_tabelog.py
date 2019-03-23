from utils import errorhandler


if __name__ == '__main__':
    def f():
        raise Exception("HELLO!")

    errorhandler.handle_error(f)
