import sys
import wave
import ffmpeg
import driver
from PyQt5.QtWidgets import (QWidget, QPushButton, QHBoxLayout, QVBoxLayout,
        QApplication, QLabel, QComboBox, QLineEdit, QFileDialog, QSpinBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot

class Worker(QThread):
    finished = pyqtSignal()
    def __init__(self, src, dst, threshold, margin):
        super().__init__()
        self.src = src
        self.dst = dst
        self.threshold = threshold
        self.margin = margin
    def run(self):
        driver.autoskip(self.src, self.dst, self.threshold, self.margin)
        self.finished.emit()


class AutoSkip(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        self.setGeometry(300,300,500,200)
        self.inLabel = QLabel('in:')
        self.inLineEdit = QLineEdit()
        self.inButton = QPushButton('...')
        self.inButton.clicked.connect(self.openButtonClicked)

        self.inHbox = QHBoxLayout()
        self.inHbox.addWidget(self.inLabel)
        self.inHbox.addWidget(self.inLineEdit)
        self.inHbox.addWidget(self.inButton)

        self.outLabel = QLabel('out:')
        self.outLineEdit = QLineEdit()
        self.outButton = QPushButton('...')
        self.outButton.clicked.connect(self.saveButtonClicked)

        self.outHbox = QHBoxLayout()
        self.outHbox.addWidget(self.outLabel)
        self.outHbox.addWidget(self.outLineEdit)
        self.outHbox.addWidget(self.outButton)

        self.threshLabel = QLabel('threshold:')
        self.threshSpinBox = QSpinBox()
        self.threshSpinBox.setMaximum(16383)
        self.threshSpinBox.setSingleStep(100)
        self.threshSpinBox.setValue(400)

        self.threshHbox = QHBoxLayout()
        self.threshHbox.addWidget(self.threshLabel)
        self.threshHbox.addWidget(self.threshSpinBox)

        self.marginLabel = QLabel('margin(ms):')
        self.marginSpinBox = QSpinBox()
        self.marginSpinBox.setMaximum(5000)
        self.marginSpinBox.setSingleStep(100)
        self.marginSpinBox.setValue(200)

        self.marginHbox = QHBoxLayout()
        self.marginHbox.addWidget(self.marginLabel)
        self.marginHbox.addWidget(self.marginSpinBox)

        self.startButton = QPushButton('start')
        self.startButton.clicked.connect(self.startProcessing)
        self.startHbox = QHBoxLayout()
        self.startHbox.addStretch(1)
        self.startHbox.addWidget(self.startButton)

        self.vbox = QVBoxLayout()
        self.vbox.addLayout(self.inHbox)
        self.vbox.addLayout(self.outHbox)
        self.vbox.addLayout(self.threshHbox)
        self.vbox.addLayout(self.marginHbox)
        self.vbox.addLayout(self.startHbox)
        self.vbox.addStretch(1)

        self.setLayout(self.vbox)
        self.show()
    def openButtonClicked(self):
        fname = QFileDialog.getOpenFileName(None, 'Load File', '', 'Video Files (*.mp4 *.avi *.mkv *.webm *.mov)')[0]
        if fname:
            self.inLineEdit.setText(fname)
        print(fname)
    def saveButtonClicked(self):
        fname = QFileDialog.getSaveFileName(None, 'Output File Name', '', 'Video Files (*.mkv)')[0]
        if fname:
            if fname[-4:] != '.mkv':
                fname += '.mkv'
            self.outLineEdit.setText(fname)
        print(fname)
    def startProcessing(self):
        self.startButton.setEnabled(False)
        self.startButton.setText('processing...')
        src = self.inLineEdit.text()
        dst = self.outLineEdit.text()
        threshold = self.threshSpinBox.value()
        margin = self.marginSpinBox.value()
        self.th = Worker(src, dst, threshold, margin)
        self.th.finished.connect(self.processingFinished)
        self.th.start()
    def processingFinished(self):
        self.startButton.setText('start')
        self.startButton.setEnabled(True)


if (__name__ == '__main__'):
    app = QApplication(sys.argv)
    ex = AutoSkip()
    sys.exit(app.exec_())
