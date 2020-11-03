import sys
import os
import datetime
import copy
import uuid

import xlrd
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QColor
# from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QCheckBox, QPushButton, QApplication, QDialog
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QWidget

from messageBox import Ui_Dialog


class MyMessageBox(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.reply = QMessageBox.Close
        self.content = ""
        self.setupUi(self)
        self.setWindowTitle('提示')
        self.ok_btn.clicked.connect(self.ok_click)
        self.cancel_btn.clicked.connect(self.cancel_click)

    def ok_click(self):
        self.reply = QMessageBox.Ok
        self.content = ""
        self.content_lable.setText(self.content)
        self.close()


    def cancel_click(self):
        self.reply = QMessageBox.Cancel
        self.content = ""
        self.content_lable.setText(self.content)
        self.close()

    def setContent(self, title, content):
        self.content = content
        self.setWindowTitle(title)
        self.content_lable.setText(self.content)