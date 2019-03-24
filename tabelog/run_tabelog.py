from tabelog import parser
import time


if __name__ == '__main__':
    start = time.process_time()
    parser.collect_info_sapporo(page=1)
    print("Elapsed: {}".format(time.process_time() - start))
