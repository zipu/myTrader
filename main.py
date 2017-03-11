#pylint: disable=E0611, w0614, R0903
#-*-coding: utf-8 -*-
import sys
import os.path
import logging
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from trader.view import MainView

class Window(QMainWindow):
    def __init__(self, mode="prod"):
        super().__init__()
        self.view = MainView()
        self._initUI()

        if mode == "prod":
            filename = "view_source/dist/index.html"
            self.view.load(QUrl.fromLocalFile(os.path.join(os.path.dirname( os.path.abspath( __file__ ) ), filename)))

        elif mode == "dev":
            self.view.load(QUrl('http:/localhost:8080'))

    def _initUI(self):
        self.setCentralWidget(self.view)
        self.setMinimumSize(1300, 900)
        self.setWindowTitle("Carpediem")

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message', "Are you sure to quit?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.view.kiwoom.quit()
            event.accept()
        else:
            event.ignore()

def main():
    #setup logger config
    logging.basicConfig(level=logging.DEBUG)

    #set environ variables
    os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "0.0.0.0: 9999"
    os.environ["QT_LOGGING_RULES"] = "js=false"

    #run app
    app = QApplication(sys.argv)
    window = Window("dev")
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
