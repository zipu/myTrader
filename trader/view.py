# -*-coding: utf-8 -*-

import logging
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QShortcut, QDialog, QGridLayout
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebChannel import QWebChannel

from .kiwoom import Kiwoom
from .record import Record

class MainView(QWebEngineView):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        #initialize utilities
        self._initShortcuts()
        self._debuggingMode()

        #setting up page and register kiwoom object into the javascript context
        self.kiwoom = Kiwoom()
        self.record = Record()

        #for i in range(16):
        #    self.settings().setAttribute(i, True)
        #    print(self.settings().testAttribute(i))

        webchannel = QWebChannel(self.page())
        self.page().setWebChannel(webchannel)

        webObjects = {
            "kiwoom" : self.kiwoom,
            "record" : self.record
        }
        #webchannel.registerObject("kiwoom", self.history)
        webchannel.registerObjects(webObjects)

    def _initShortcuts(self):
        self.shortcut = {}
        #F5 - Page reloading
        self.shortcut['F5'] = QShortcut(self)
        self.shortcut['F5'].setKey(Qt.Key_F5)
        self.shortcut['F5'].activated.connect(self.reload)
        #F12 - Development tool
        self.shortcut['F12'] = QShortcut(self)
        self.shortcut['F12'].setContext(Qt.ApplicationShortcut)
        self.shortcut['F12'].setKey(Qt.Key_F12)
        self.shortcut['F12'].activated.connect(self._toggleDevTool)

    def _debuggingMode(self):
        self.devTool = QDialog(self)
        self.devTool.setWindowTitle("Development Tool")
        self.devTool.resize(950, 400)
        self.devView = DevToolView("9999")

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.devView)
        self.devTool.setLayout(layout)

    def _toggleDevTool(self):
        #F12를 누르면 개발자 도구가 열림
        if not self.devTool.isVisible():
            self.devView.removeDevTool()
        self.devTool.setVisible(not self.devTool.isVisible())


class DevToolView(QWebEngineView):
    """
    QWebEngineView 커스터마이징
    """
    def __init__(self, port):
        super().__init__()
        self.setPage(QWebEnginePage(self))
        self.load(QUrl("http://127.0.0.1:"+ port))

    def removeDevTool(self):
        # 리모트 디버그에서 자동으로 이동하는 스크립트
        loadScript = """
        var items = Array.prototype.slice.call(document.querySelectorAll(".item"));
        if (items.length) {
            document.body.style.opacity = "0.001";
            items = items.filter(v => {
                if(v.title === "QtWebEngine Remote Debugging") {
                    v.style.display = "none";
                    return false;
                } else {
                    return true;
                }
            });
            if(items.length === 1) {
                location.href = items[0].href;
            } else {
                document.body.style.opacity=1;
            }
        }
        """
        self.page().runJavaScript(loadScript)