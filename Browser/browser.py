from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *
import sys
import re

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.visitedUrls = {}
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.closeTab)
        self.tab1 = QWidget()
        self.tabWebEngine = []
        self.lNameLine = []
        self.tabs.addTab(self.tab1, "New Tab")
        self.tabUI(self.tab1)
        self.setWindowTitle("PyBrowser")
        self.setCentralWidget(self.tabs)
        self.showMaximized()
        QShortcut(QKeySequence("Ctrl+T"), self, self.addTab)

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu("File")
        self.historyMenu = mainMenu.addMenu("History")

        newTabAction = QAction("New Tab", self)
        newTabAction.setShortcut("Ctrl+T")
        fileMenu.addAction(newTabAction)
        newTabAction.triggered.connect(self.addTab)

        closeTabAction = QAction("Close Tab", self)
        closeTabAction.setShortcut("Ctrl+Shift+Backspace")
        fileMenu.addAction(closeTabAction)
        closeTabAction.triggered.connect(self.closeTab)
        fileMenu.addSeparator()

        openAction = QAction("Open File", self)
        openAction.setShortcut("Ctrl+O")
        fileMenu.addAction(openAction)
        openAction.triggered.connect(self.openFile)

        saveAction = QAction("Save File", self)
        saveAction.setShortcut("Ctrl+S")
        fileMenu.addAction(saveAction)
        saveAction.triggered.connect(self.saveFile)

        goBackAction = QAction("Go Back", self)
        goBackAction.setShortcut("Ctrl+Backspace")
        self.historyMenu.addAction(goBackAction)
        goBackAction.triggered.connect(self.goBack)

        frwrdAction = QAction("Go Next", self)
        frwrdAction.setShortcut("Ctrl+Return")
        self.historyMenu.addAction(frwrdAction)
        frwrdAction.triggered.connect(self.goNext)

        reloadAction = QAction("Relaod", self)
        reloadAction.setShortcut("Ctrl+R")
        self.historyMenu.addAction(reloadAction)
        reloadAction.triggered.connect(self.goRefresh)

        goToPageAction = QAction("Go to Page", self)
        goToPageAction.setShortcut("Return")
        self.historyMenu.addAction(goToPageAction)
        goToPageAction.triggered.connect(self.requestUrl)

        self.historyMenu.addSeparator()
        showHistoryAction = QAction("Show Full History", self)
        self.historyMenu.addAction(showHistoryAction)
        showHistoryAction.triggered.connect(self.showFullHistory)

        clearHistoryAction = QAction("Clear History", self)
        self.historyMenu.addAction(clearHistoryAction)
        clearHistoryAction.triggered.connect(self.clearHistory)
        self.historyMenu.addSeparator()

    def clearHistory(self):
        for i in self.visitedUrls.values():
            self.historyMenu.removeAction(i)

    def openFile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Open File", "", "HTML Files (*.html or *.htm) ;; All Files (*.*)")
        if filePath == "":
            return
        with open(filePath, 'r') as f:
            self.tabWebEngine[self.tabs.currentIndex()].setHtml(f.read())
            self.lNameLine[self.tabs.currentIndex()].setText(filePath)

    def saveFile(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save File", "", "HTML Files (*.html or *.htm) :: All Files (*.*)")
        if filePath == "":
            return
        self.tabWebEngine[self.tabs.currentIndex()].page().save(filePath)

    def addTab(self):
        tab = QWidget()
        self.tabs.addTab(tab, "New Tab")
        self.tabUI(tab)

        index = self.tabs.currentIndex()
        self.tabs.setCurrentIndex(index + 1)
    
    def goBack(self):
        index = self.tabs.currentIndex()
        self.tabWebEngine[index].back()

    def goNext(self):
        index = self.tabs.currentIndex()
        self.tabWebEngine[index].forward()

    def goRefresh(self):
        index = self.tabs.currentIndex()
        self.tabWebEngine[index].reload()

    def loadStarted(self):
        return

    def changePage(self):
        index = self.tabs.currentIndex()
        pageTitle = self.tabWebEngine[index].title()
        self.tabs.setTabText(index, pageTitle[:15])
        url = self.tabWebEngine[index].url().url()
        self.lNameLine[index].setText(url)
        self.tabs.setTabIcon(index, self.tabWebEngine[index].icon())
        print(pageTitle)
        if "http" not in pageTitle:
            self.visitedUrls[url] = QAction(pageTitle, self)
            self.historyMenu.addAction(self.visitedUrls[url])

    def tabUI(self, tab):
        backButton = QToolButton()
        backIcon = QIcon()
        backIcon.addPixmap(QPixmap("./icons/backward.png"))
        backButton.setIcon(backIcon)

        nextButton = QToolButton()
        nextIcon = QIcon()
        nextIcon.addPixmap(QPixmap("./icons/forward.png"))
        nextButton.setIcon(nextIcon)

        refreshButton = QToolButton()
        refreshIcon = QIcon()
        refreshIcon.addPixmap(QPixmap("./icons/reload.png"))
        refreshButton.setIcon(refreshIcon)

        backButton.clicked.connect(self.goBack)
        refreshButton.clicked.connect(self.goRefresh)
        nextButton.clicked.connect(self.goNext)

        self.newTabButton = QToolButton()
        newTabIcon = QIcon()
        newTabIcon.addPixmap(QPixmap("./icons/plus.png"))
        self.newTabButton.setIcon(newTabIcon)
        self.destroyButton = QPushButton("x")
        self.tabWidget = QTabWidget()

        urlLine = QLineEdit()
        urlLine.returnPressed.connect(self.requestUrl)
        self.newTabButton.clicked.connect(self.addTab)

        tabGrid = QGridLayout()
        tabGrid.setContentsMargins(0, 0, 0, 0)

        navigationFrame = QWidget()
        navigationFrame.setMaximumHeight(20)

        navigationGrid = QGridLayout(navigationFrame)
        navigationGrid.setSpacing(0)
        navigationGrid.setContentsMargins(0, 0, 0, 0)
        navigationGrid.addWidget(self.newTabButton, 0, 1)
        navigationGrid.addWidget(backButton, 0, 2)
        navigationGrid.addWidget(refreshButton, 0, 3)
        navigationGrid.addWidget(nextButton, 0, 4)
        navigationGrid.addWidget(urlLine, 0, 5)
        
        tabGrid.addWidget(navigationFrame, 0, 0)
        QWebEngineProfile.defaultProfile().downloadRequested.connect(self.on_downloadRequested)
        
        if self.tabs.count() == 1:
            self.tabs.setTabsClosable(False)
        else:
            self.tabs.setTabsClosable(True)

        self.webEngineView = QWebEngineView()
        global_settings = QWebEngineSettings.globalSettings()

        for attr in (QWebEngineSettings.PluginsEnabled, QWebEngineSettings.FullScreenSupportEnabled, ):
            global_settings.setAttribute(attr, True)
        self.webEngineView.load(QUrl("https://www.google.com/"))
        self.webEngineView.titleChanged.connect(self.changePage)
        self.webEngineView.page().fullScreenRequested.connect(self.FullScreenRequest)
        self.webEngineView.page().windowCloseRequested.connect(self.closeTab)
       
        frame = QFrame()
        frame.setFrameStyle(QFrame.Panel)

        self.gridLayout = QGridLayout(frame)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.addWidget(self.webEngineView, 0, 0, 1, 1)
        frame.setLayout(self.gridLayout)
        
        self.tabWebEngine.append(self.webEngineView)
        self.tabWidget.setCurrentWidget(self.webEngineView)
        self.lNameLine.append(urlLine)
        tabGrid.addWidget(frame)
        tab.setLayout(tabGrid)

    def requestUrl(self):
        if self.tabs.count() != 0:
            url = QUrl(self.lNameLine[self.tabs.currentIndex()].text())
            if check(url.toString()):
                url = QUrl("https://www.google.com/?#q=" + self.lNameLine[self.tabs.currentIndex()].text())
            else:
                if url.toString() == "":
                    url = QUrl("https://www.google.com")
                if url.scheme() == "":
                    url.setScheme("http")
            self.tabWebEngine[self.tabs.currentIndex()].load(url)
        else:
            exit()

    def closeTab(self, tabId):
        print(tabId)
        del self.lNameLine[tabId]
        self.tabWebEngine[tabId].load(QUrl("https://www.google.com"))
        self.tabWebEngine[tabId].destroy()
        self.tabWebEngine.pop(tabId)
        self.tabs.removeTab(tabId)
        if self.tabs.count() == 1:
            self.tabs.setTabsClosable(False)
        else:
            self.tabs.setTabsClosable(True)

    @pyqtSlot("QWebEngineFullScreenRequest")
    def FullScreenRequest(self, request):
        request.accept()
        if request.toggleOn():
            self.webEngineView.setParent(None)
            self.webEngineView.showFullScreen()
        else:
            self.gridLayout.addWidget(self.webEngineView, 0, 0, 1, 1)
            self.webEngineView.showNormal()

    @pyqtSlot("QWebEngineDownloadItem*")
    def on_downloadRequested(self, download):
        old_path = download.path()
        suffix = QFileInfo(old_path).suffix()
        path, _ = QFileDialog.getSaveFileName(self, "Save File", old_path, "*."+suffix)
        if path:
            download.setPath(path)
            download.accept()

    def showFullHistory(self):
        history = '<html><head><title>History</title></head><body><table align="center" cellspacing="0px" border="2px">'
        for i in self.visitedUrls:
            history += "<tr><td>" + self.visitedUrls[i].text() + "</td><td>" + i + "</td></tr>"
        history += "</table></body></html>"
        self.tabWebEngine[self.tabs.currentIndex()].setHtml(history)

def check(string):
    reUrl = "(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+"
    url = re.match(reUrl, string)
    return not url
        
if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())