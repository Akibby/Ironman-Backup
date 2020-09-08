#! /usr/bin/env python3
# pylint: disable=C0103

import sys
import time
import threading
from threading import Event
from PyQt5.QtWidgets import QApplication, QTextEdit, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QMainWindow, QAction, QInputDialog, QMessageBox
from PyQt5.QtGui import QIcon
from backup import Backup


class App(QMainWindow):
    """Main window class"""

    def __init__(self, backup):
        super().__init__()

        self.timer = 300
        self.backup = backup
        self.cWidget = QWidget(self)
        self.isRunning = False
        self.exit = Event()
        self.text = QTextEdit(self)
        self.text.setReadOnly(True)
        self.ssBtn = QPushButton('Start')
        self.ldBtn = QPushButton('Load')
        self.vLayout = QVBoxLayout()
        self.hLayout = QHBoxLayout()
        self.curGame = ''

        self.initUI()

    def initUI(self):
        """Initialize UI"""
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        timeMenu = QAction('Set Interval', self)
        lastMenu = QAction('Load Last', self)
        timeMenu.triggered.connect(self.setTimer)
        lastMenu.triggered.connect(self.loadLast)
        fileMenu.addAction(timeMenu)
        fileMenu.addAction(lastMenu)

        self.vLayout.addWidget(self.text)
        self.hLayout.addWidget(self.ssBtn)
        self.hLayout.addWidget(self.ldBtn)
        self.vLayout.addLayout(self.hLayout)
        self.ssBtn.clicked.connect(self.updateSSBtn)
        self.ldBtn.clicked.connect(self.load)

        self.cWidget.setLayout(self.vLayout)
        self.setCentralWidget(self.cWidget)
        self.setWindowIcon(QIcon('.\\res\\Ironman.png'))
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
        self.lw = LoadWindow(self.backup, self.curGame)
        self.lw.initUI()

        self.lw.show()

    def setTimer(self):
        """Set a the time interval for saves"""
        newTime, i = QInputDialog.getInt(
            self, "New Timer", "Enter a time in minutes", (self.timer/60), 1, 60, 1)
        if i:
            if self.timer != (newTime * 60):
                self.timer = (newTime * 60)
                if self.isRunning:
                    self.ssBtn.click()
                    time.sleep(.5)
                    self.ssBtn.click()

    def loadLast(self):
        """Load the latest backup save for the current game"""
        self.curGame = self.backup.currentGame()
        if self.curGame == 'Issue detecting the game, trying again.':
            self.loadLast()
        elif self.curGame == 'Stellaris':
            runList = self.backup.loadList(self.curGame)
            if runList:
                run = runList[0]
                saveList = self.backup.loadList(self.curGame + '\\' + run)
                if saveList:
                    save = saveList[0]
                    self.backup.stellarisLoad(self.curGame, run, save)
                    QMessageBox.information(
                        self, 'Load Last', 'The latest backup for ' + self.curGame + ' has been loaded.')
                    return
        elif self.curGame != '':
            runList = self.backup.loadList(self.curGame)
            if runList:
                run = runList[0]
                saveList = self.backup.loadList(self.curGame + '\\' + run)
                if saveList:
                    save = saveList[0]
                    self.backup.genLoad(self.curGame, run, save)
                    QMessageBox.information(
                        self, 'Load Last', 'The latest backup for ' + self.curGame + ' has been loaded.')
                    return
        else:
            QMessageBox.warning(self, 'Load Last',
                                'A game must be running to use this feature.')
            return
        QMessageBox.warning(self, 'Load Last', self.curGame + ' has no backups.')


class LoadWindow(QWidget):
    """Load window class"""

    def __init__(self, backup, curGame):
        QWidget.__init__(self)
        self.backup = backup
        self.curGame = backup.currentGame()
        self.gameList = backup.loadList('')
        self.gameCB = QComboBox(self)
        self.runCB = QComboBox(self)
        self.saveCB = QComboBox(self)
        self.loadBtn = QPushButton('Load')

    def initUI(self):
        """Initialize UI"""
        self.resize(250, 200)
        self.setWindowTitle('Saved Games')

        for game in self.gameList:
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
        self.setWindowIcon(QIcon('.\\res\\Ironman.png'))
        self.chooseFirst()
        self.gameSelect()
        self.show()
        self.focusWidget()

    def chooseFirst(self):
        """Set the current game as chosen"""
        if self.curGame in self.gameList:
            self.gameCB.setCurrentText(self.curGame)

    def gameSelect(self):
        """Handle a game being selected"""
        runList = self.backup.loadList(self.gameCB.currentText())
        self.runCB.clear()
        for run in runList:
            self.runCB.addItem(run)
        self.runSelect()

    def runSelect(self):
        """Handle a run being selected"""
        run = self.runCB.currentText()
        saveList = self.backup.loadList(self.gameCB.currentText() + '\\' + run)
        self.saveCB.clear()
        for save in saveList:
            self.saveCB.addItem(save)

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
            QMessageBox.information(
                self, 'Load Last', 'The backup '+ self.saveCB.currentText() + ' for ' + self.gameCB.currentText() + ' has been loaded.')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App(Backup())
    sys.exit(app.exec_())
