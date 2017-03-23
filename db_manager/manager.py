# -*- coding: utf-8 -*-
import sys
import argparse
import logging
from datetime import datetime

def main():
    logging.basicConfig(filename="manager.log", format="%(levelname)s: %(message)s",
                        level=logging.INFO)
    logging.info('====================================================')
    logging.info('  %s', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logging.info('====================================================')


    parser = argparse.ArgumentParser(description='database manager')
    parser.add_argument('--update', help='update data')
    parser.add_argument('--calc', help='data visualization')
    args = parser.parse_args()

    if args.update:
        from PyQt5.QtWidgets import QApplication
        from update import Update

        if args.update in ['marketinfo', 'OHLC', 'minute']:
            app = QApplication(sys.argv)
            kiwoom = Update(args.update)
            kiwoom.CommConnect(0)
            sys.exit(app.exec_())
        else:
            raise NameError(args.update)


    elif args.calc:
        from calc import Calc
        calc = Calc()
        if args.calc == 'density':
            calc.density()


if __name__ == "__main__":
    main()

