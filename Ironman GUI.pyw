#! /usr/bin/env python3
# pylint: disable=C0103

import sys
import threading
from threading import Event
from PyQt5.QtWidgets import QApplication, QTextEdit, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QComboBox
from backup import Backup

class App(QWidget):
    """Main window class"""

    def __init__(self, backup):
        super(App, self).__init__()
        self.timer = 300
        self.backup = backup
        self.isRunning = False
        self.exit = Event()
        self.text = QTextEdit(self)
        self.text.setReadOnly(True)
        self.ssBtn = QPushButton('Start')
        self.ldBtn = QPushButton('Load')
        self.vLayout = QVBoxLayout()
        self.hLayout = QHBoxLayout()

        self.initUI()

    def initUI(self):
        """Initialize UI"""
        self.vLayout.addWidget(self.text)
        self.hLayout.addWidget(self.ssBtn)
        self.hLayout.addWidget(self.ldBtn)
        self.vLayout.addLayout(self.hLayout)
        self.ssBtn.clicked.connect(self.updateSSBtn)
        self.ldBtn.clicked.connect(self.load)

        self.setLayout(self.vLayout)
        self.setWindowTitle('Ironman Backup')

        self.show()

    def updateSSBtn(self, done):
        """Update the Start/Stop button"""
        if self.isRunning:
            self.ssBtn.setText('Stopping')
            self.ssBtn.setEnabled(False)
            self.stopRun()
        elif done:
            self.ssBtn.setText('Start')
            self.ssBtn.setEnabled(True)
        else:
            self.ssBtn.setText('Stop')
            self.startRun()
        self.show()

    def startRun(self):
        """Start running"""
        if not self.isRunning:
            self.text.append('Starting...')
            self.t = threading.Thread(target=self.writeText, name='backup')
            self.t.daemon = True
            self.isRunning = True
            self.exit.clear()
            self.t.start()

    def stopRun(self):
        """Stop running"""
        if self.isRunning:
            self.isRunning = False
            self.exit.set()

    def writeText(self):
        """Write text to screen"""
        while not self.exit.is_set():
            message = self.backup.startup()
            self.text.append(message)
            app.processEvents()
            if self.isRunning:
                self.exit.wait(self.timer)
        self.t._stop
        self.text.append('Process stopped.')
        self.updateSSBtn(True)

    def load(self):
        """Open a load window"""
        self.lw = LoadWindow(self.backup)
        self.lw.initUI()

        self.lw.show()


class LoadWindow(QWidget):
    """Load window class"""

    def __init__(self, backup):
        QWidget.__init__(self)
        self.backup = backup
        self.gameCB = QComboBox(self)
        self.runCB = QComboBox(self)
        self.saveCB = QComboBox(self)
        self.loadBtn = QPushButton('Load')

    def initUI(self):
        """Initialize UI"""
        gameList = self.backup.loadList('')
        self.resize(250, 200)
        self.setWindowTitle('Saved Games')

        for game in gameList:
            self.gameCB.addItem(game)
        self.gameCB.currentIndexChanged.connect(self.gameSelect)
        self.runCB.activated.connect(self.runSelect)
        self.loadBtn.clicked.connect(self.loadFile)
        vBox = QVBoxLayout()
        vBox.addWidget(self.gameCB)
        vBox.addWidget(self.runCB)
        vBox.addWidget(self.saveCB)
        vBox.addWidget(self.loadBtn)
        self.setLayout(vBox)
        self.gameSelect()

    def gameSelect(self):
        """Handle a game being selected"""
        runList = self.backup.loadList(self.gameCB.currentText())
        self.runCB.clear()
        for run in runList:
            self.runCB.addItem(run)
        self.show()
        self.runSelect()

    def runSelect(self):
        """Handle a run being selected"""
        run = self.runCB.currentText()
        saveList = self.backup.loadList(self.gameCB.currentText() + '\\' + run)
        self.saveCB.clear()
        for save in saveList:
            self.saveCB.addItem(save)
        self.show()

    def loadFile(self):
        """Load a file"""
        if self.saveCB.currentText() != '':
            if self.gameCB.currentText() != 'Stellaris':
                self.backup.genLoad(self.gameCB.currentText(
                ), self.runCB.currentText(), self.saveCB.currentText())
            else:
                self.backup.stellarisLoad(self.gameCB.currentText(
                ), self.runCB.currentText(), self.saveCB.currentText())
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App(Backup())
    sys.exit(app.exec_())
