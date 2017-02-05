#pylint: disable=E0611, w0614, R0903
#-*-coding: utf-8 -*-
import sys
import os.path
import logging
#from optparse import OptionParser
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from plus.web import MainView

class Window(QMainWindow):
    def __init__(self,file="index.html"):
        super().__init__()
        self.view = MainView()
        self._initUI()
        #self.view.load(QUrl.fromLocalFile(os.path.join(os.path.dirname( os.path.abspath( __file__ ) ), file)))
        self.view.load(QUrl('http:/localhost:8080'))
        
    def _initUI(self):
        self.setCentralWidget(self.view)
        self.setMinimumSize(1300, 900)
        self.setWindowTitle("Carpediem")

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message', "Are you sure to quit?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            #API 문제로 잠시 이용.
            self.view.kiwoom.quit()
            event.accept()
        else:
            event.ignore()   
        #event.accept() if reply == QMessageBox.Yes else event.ignore()

def main():
    #setup logger config
    logging.basicConfig(level=logging.DEBUG)

    #parsing command line arguments
    #parser = OptionParser()
    #parser.add_option("-p", "--port", action="store", type="string", dest="port", help="크롬 원격 디버깅 포트")
    #parser.add_option("-f", "--file", action="store", type="string", dest="file", help="시작 파일 경로", default="index.html")
    #(opt, args) = parser.parse_args()

    #if os.path.isfile(opt.file):
    os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "0.0.0.0: 9999"
    os.environ["QT_LOGGING_RULES"] = "js=false"

    app = QApplication(sys.argv)
    window = Window("view_source/dist/index.html")
    window.show()
    sys.exit(app.exec_())
    #else:
    #    parser.print_help()
    #    sys.exit()

if __name__ == "__main__":
    main()
