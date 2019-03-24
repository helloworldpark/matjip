from utils.errorhandler import handle_error
from utils.http import get_html
from tabelog import parser


if __name__ == '__main__':
    parser.collect_info_sapporo(page=30)
