from tabelog import parser
import time

# https://beomi.github.io/gb-crawling/posts/2017-07-05-HowToMakeWebCrawler-with-Multiprocess.html


if __name__ == '__main__':
    start = time.time()
    parser.collect_info_sapporo_all(pools=4, total_pages=60)
    print("Elapsed: {}".format(time.time() - start))
