# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'message_box.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(476, 240)
        self.cancel_btn = QtWidgets.QPushButton(Form)
        self.cancel_btn.setGeometry(QtCore.QRect(260, 180, 100, 38))
        self.cancel_btn.setStyleSheet("font: 10pt \"Microsoft YaHei UI\";\n"
"background-color: rgb(218, 218, 218);\n"
"border-radius:10px;")
        self.cancel_btn.setObjectName("cancel_btn")
        self.ok_btn = QtWidgets.QPushButton(Form)
        self.ok_btn.setGeometry(QtCore.QRect(100, 180, 100, 38))
        self.ok_btn.setStyleSheet("font: 10pt \"Microsoft YaHei UI\";\n"
"color:#fff;\n"
"background-color: rgb(20, 255, 35);\n"
"border-radius:10px;")
        self.ok_btn.setObjectName("ok_btn")
        self.content_lable = QtWidgets.QLabel(Form)
        self.content_lable.setGeometry(QtCore.QRect(40, 30, 380, 120))
        self.content_lable.setMinimumSize(QtCore.QSize(380, 120))
        self.content_lable.setStyleSheet("font: 16pt \"Microsoft YaHei UI\";")
        self.content_lable.setAlignment(QtCore.Qt.AlignCenter)
        self.content_lable.setObjectName("content_lable")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.cancel_btn.setText(_translate("Form", "取消"))
        self.ok_btn.setText(_translate("Form", "确定"))
        self.content_lable.setText(_translate("Form", "TextLabel"))

