from tabelog import parser
from utils.excel import to_excel
import time


if __name__ == '__main__':
    start = time.process_time()
    ok, page, infos = parser.collect_info_sapporo(page=1)
    to_excel(infos[0], 'test2.xlsx')
    print("Elapsed: {}".format(time.process_time() - start))
