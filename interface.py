# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'interface.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1319, 828)
        MainWindow.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"margin: 0px;")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_5 = QtWidgets.QFrame(self.centralwidget)
        self.frame_5.setMinimumSize(QtCore.QSize(0, 80))
        self.frame_5.setStyleSheet("background-color: rgb(69, 90, 179);\n"
"border-top-left-radius:15px;\n"
"border-top-right-radius:15px;")
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.data_get_btn = QtWidgets.QPushButton(self.frame_5)
        self.data_get_btn.setGeometry(QtCore.QRect(410, 30, 141, 51))
        self.data_get_btn.setStyleSheet("background-color: rgb(80, 103, 203);\n"
"font: 75 12pt \"微软雅黑\";\n"
"background-color: rgb(255, 255, 255);\n"
"color:#455ab3;\n"
"border-top-left-radius:15px;\n"
"border-top-right-radius:15px")
        self.data_get_btn.setObjectName("data_get_btn")
        self.data_analysis_btn = QtWidgets.QPushButton(self.frame_5)
        self.data_analysis_btn.setGeometry(QtCore.QRect(570, 30, 141, 51))
        self.data_analysis_btn.setStyleSheet("background-color: rgb(80, 103, 203);\n"
"font: 75 12pt \"微软雅黑\";\n"
"color: rgb(255, 255, 255);\n"
"border-top-left-radius:15px;\n"
"border-top-right-radius:15px;")
        self.data_analysis_btn.setObjectName("data_analysis_btn")
        self.choice_btn = QtWidgets.QPushButton(self.frame_5)
        self.choice_btn.setGeometry(QtCore.QRect(740, 30, 141, 51))
        self.choice_btn.setStyleSheet("background-color: rgb(80, 103, 203);\n"
"font: 75 12pt \"微软雅黑\";\n"
"color: rgb(255, 255, 255);\n"
"border-top-left-radius:15px;\n"
"border-top-right-radius:15px;")
        self.choice_btn.setObjectName("choice_btn")
        self.label_3 = QtWidgets.QLabel(self.frame_5)
        self.label_3.setGeometry(QtCore.QRect(30, 20, 350, 40))
        self.label_3.setStyleSheet("borde1r-width: 1px;border-style: solid;\n"
"border-top-left-radius:0px;\n"
"border-top-right-radius:0px;")
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.frame_5)
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setEnabled(True)
        self.frame.setMinimumSize(QtCore.QSize(0, 180))
        self.frame.setMaximumSize(QtCore.QSize(16777215, 180))
        self.frame.setStyleSheet("margin: 0px;\n"
"border-width: 1px;border-style: solid;")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.label_8 = QtWidgets.QLabel(self.frame)
        self.label_8.setGeometry(QtCore.QRect(290, 115, 15, 30))
        self.label_8.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_8.setObjectName("label_8")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(10, 10, 101, 31))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(14)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(9)
        self.label.setFont(font)
        self.label.setStyleSheet("color:#455ab3;\n"
"font: 75 14pt \"Microsoft YaHei UI\";\n"
"border:0px;")
        self.label.setObjectName("label")
        self.crawl_btn = QtWidgets.QPushButton(self.frame)
        self.crawl_btn.setGeometry(QtCore.QRect(1060, 115, 93, 30))
        self.crawl_btn.setStyleSheet("font: 10pt \"Microsoft YaHei UI\";\n"
"background-color:#455ab3;\n"
"color:#fff;")
        self.crawl_btn.setObjectName("crawl_btn")
        self.model_edit = QtWidgets.QLineEdit(self.frame)
        self.model_edit.setGeometry(QtCore.QRect(550, 70, 140, 30))
        self.model_edit.setObjectName("model_edit")
        self.password_edit = QtWidgets.QLineEdit(self.frame)
        self.password_edit.setGeometry(QtCore.QRect(320, 70, 140, 30))
        self.password_edit.setObjectName("password_edit")
        self.username_edit = QtWidgets.QLineEdit(self.frame)
        self.username_edit.setGeometry(QtCore.QRect(110, 70, 140, 30))
        self.username_edit.setStyleSheet("font: 12pt \"Microsoft YaHei UI\";")
        self.username_edit.setObjectName("username_edit")
        self.upload_excel_btn = QtWidgets.QPushButton(self.frame)
        self.upload_excel_btn.setGeometry(QtCore.QRect(870, 115, 121, 30))
        self.upload_excel_btn.setStyleSheet("font: 10pt \"Microsoft YaHei UI\";\n"
"background-color: rgb(226,226,226);")
        self.upload_excel_btn.setObjectName("upload_excel_btn")
        self.label_6 = QtWidgets.QLabel(self.frame)
        self.label_6.setGeometry(QtCore.QRect(30, 115, 72, 30))
        self.label_6.setStyleSheet("border:0px;font: 10pt \"Microsoft YaHei UI\";")
        self.label_6.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName("label_6")
        self.end_time_edit = QtWidgets.QDateTimeEdit(self.frame)
        self.end_time_edit.setGeometry(QtCore.QRect(310, 115, 170, 30))
        self.end_time_edit.setStyleSheet("font: 10pt \"Microsoft YaHei UI\";")
        self.end_time_edit.setDateTime(QtCore.QDateTime(QtCore.QDate(2020, 10, 12), QtCore.QTime(0, 0, 0)))
        self.end_time_edit.setObjectName("end_time_edit")
        self.label_7 = QtWidgets.QLabel(self.frame)
        self.label_7.setGeometry(QtCore.QRect(260, 70, 51, 30))
        self.label_7.setStyleSheet("border:0px;font: 10pt \"Microsoft YaHei UI\";")
        self.label_7.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_7.setObjectName("label_7")
        self.label_5 = QtWidgets.QLabel(self.frame)
        self.label_5.setGeometry(QtCore.QRect(480, 70, 61, 30))
        self.label_5.setStyleSheet("border:0px;font: 10pt \"Microsoft YaHei UI\";")
        self.label_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName("label_5")
        self.create_time_edit = QtWidgets.QDateTimeEdit(self.frame)
        self.create_time_edit.setGeometry(QtCore.QRect(110, 115, 170, 30))
        self.create_time_edit.setStyleSheet("font: 10pt \"Microsoft YaHei UI\";")
        self.create_time_edit.setDateTime(QtCore.QDateTime(QtCore.QDate(2020, 10, 11), QtCore.QTime(0, 0, 0)))
        self.create_time_edit.setObjectName("create_time_edit")
        self.excel_path_edit = QtWidgets.QLineEdit(self.frame)
        self.excel_path_edit.setGeometry(QtCore.QRect(510, 115, 371, 30))
        self.excel_path_edit.setStyleSheet("font: 9pt \"Microsoft YaHei UI\";")
        self.excel_path_edit.setObjectName("excel_path_edit")
        self.label_4 = QtWidgets.QLabel(self.frame)
        self.label_4.setGeometry(QtCore.QRect(30, 70, 72, 30))
        self.label_4.setStyleSheet("border:0px;font: 10pt \"Microsoft YaHei UI\";")
        self.label_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.frame)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setMinimumSize(QtCore.QSize(120, 50))
        self.label_2.setMaximumSize(QtCore.QSize(120, 50))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(14)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(9)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet("color:#455ab3;\n"
"font: 75 14pt \"Microsoft YaHei UI\";\n"
"border:0px;\n"
"margin: 8px;")
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.fileinfo_table = QtWidgets.QTableWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fileinfo_table.sizePolicy().hasHeightForWidth())
        self.fileinfo_table.setSizePolicy(sizePolicy)
        self.fileinfo_table.setStyleSheet("font: 10pt \"Microsoft YaHei UI\";\n"
"")
        self.fileinfo_table.setAutoScrollMargin(16)
        self.fileinfo_table.setObjectName("fileinfo_table")
        self.fileinfo_table.setColumnCount(11)
        self.fileinfo_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.fileinfo_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileinfo_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileinfo_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileinfo_table.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileinfo_table.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileinfo_table.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileinfo_table.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileinfo_table.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileinfo_table.setHorizontalHeaderItem(8, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileinfo_table.setHorizontalHeaderItem(9, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileinfo_table.setHorizontalHeaderItem(10, item)
        self.fileinfo_table.horizontalHeader().setDefaultSectionSize(110)
        self.verticalLayout.addWidget(self.fileinfo_table)
        self.frame_2 = QtWidgets.QFrame(self.centralwidget)
        self.frame_2.setMinimumSize(QtCore.QSize(0, 60))
        self.frame_2.setMaximumSize(QtCore.QSize(16777215, 60))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.report_docx_btn = QtWidgets.QPushButton(self.frame_2)
        self.report_docx_btn.setGeometry(QtCore.QRect(850, 20, 100, 30))
        self.report_docx_btn.setStyleSheet("background-color:#455ab3;color:#fff;\n"
"font: 10pt \"Microsoft YaHei UI\";")
        self.report_docx_btn.setObjectName("report_docx_btn")
        self.auto_choice_btn = QtWidgets.QPushButton(self.frame_2)
        self.auto_choice_btn.setGeometry(QtCore.QRect(730, 20, 100, 30))
        self.auto_choice_btn.setStyleSheet("background-color:#455ab3;color:#fff;\n"
"font: 10pt \"Microsoft YaHei UI\";")
        self.auto_choice_btn.setObjectName("auto_choice_btn")
        self.select_all_btn = QtWidgets.QPushButton(self.frame_2)
        self.select_all_btn.setGeometry(QtCore.QRect(610, 20, 100, 30))
        self.select_all_btn.setStyleSheet("background-color:#455ab3;color:#fff;\n"
"font: 10pt \"Microsoft YaHei UI\";")
        self.select_all_btn.setObjectName("select_all_btn")
        self.label_9 = QtWidgets.QLabel(self.frame_2)
        self.label_9.setGeometry(QtCore.QRect(10, 20, 121, 31))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(14)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(9)
        self.label_9.setFont(font)
        self.label_9.setStyleSheet("color:#455ab3;\n"
"font: 75 14pt \"Microsoft YaHei UI\";\n"
"border:0px;")
        self.label_9.setObjectName("label_9")
        self.verticalLayout.addWidget(self.frame_2)
        self.fileinfo_table_2 = QtWidgets.QTableWidget(self.centralwidget)
        self.fileinfo_table_2.setStyleSheet("font: 10pt \"Microsoft YaHei UI\";")
        self.fileinfo_table_2.setObjectName("fileinfo_table_2")
        self.fileinfo_table_2.setColumnCount(13)
        self.fileinfo_table_2.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.fileinfo_table_2.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileinfo_table_2.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileinfo_table_2.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileinfo_table_2.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileinfo_table_2.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileinfo_table_2.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileinfo_table_2.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileinfo_table_2.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileinfo_table_2.setHorizontalHeaderItem(8, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileinfo_table_2.setHorizontalHeaderItem(9, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileinfo_table_2.setHorizontalHeaderItem(10, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileinfo_table_2.setHorizontalHeaderItem(11, item)
        item = QtWidgets.QTableWidgetItem()
        self.fileinfo_table_2.setHorizontalHeaderItem(12, item)
        self.fileinfo_table_2.horizontalHeader().setDefaultSectionSize(95)
        self.verticalLayout.addWidget(self.fileinfo_table_2)
        self.frame_3 = QtWidgets.QFrame(self.centralwidget)
        self.frame_3.setMinimumSize(QtCore.QSize(0, 60))
        self.frame_3.setMaximumSize(QtCore.QSize(16777215, 60))
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.label_10 = QtWidgets.QLabel(self.frame_3)
        self.label_10.setGeometry(QtCore.QRect(20, 10, 101, 31))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(14)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(9)
        self.label_10.setFont(font)
        self.label_10.setStyleSheet("color:#455ab3;\n"
"font: 75 14pt \"Microsoft YaHei UI\";\n"
"border:0px;")
        self.label_10.setObjectName("label_10")
        self.verticalLayout.addWidget(self.frame_3)
        self.l_widget = QtWidgets.QWidget(self.centralwidget)
        self.l_widget.setObjectName("l_widget")
        self.verticalLayout.addWidget(self.l_widget)
        self.r_widget = QtWidgets.QWidget(self.centralwidget)
        self.r_widget.setObjectName("r_widget")
        self.verticalLayout.addWidget(self.r_widget)
        self.frame_4 = QtWidgets.QFrame(self.centralwidget)
        self.frame_4.setMinimumSize(QtCore.QSize(0, 60))
        self.frame_4.setMaximumSize(QtCore.QSize(16777215, 60))
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.save_change_btn = QtWidgets.QPushButton(self.frame_4)
        self.save_change_btn.setGeometry(QtCore.QRect(670, 20, 100, 30))
        self.save_change_btn.setStyleSheet("background-color:#455ab3;color:#fff;\n"
"font: 10pt \"Microsoft YaHei UI\";")
        self.save_change_btn.setObjectName("save_change_btn")
        self.edit_btn = QtWidgets.QPushButton(self.frame_4)
        self.edit_btn.setGeometry(QtCore.QRect(310, 20, 100, 30))
        self.edit_btn.setStyleSheet("background-color:#455ab3;color:#fff;\n"
"font: 10pt \"Microsoft YaHei UI\";")
        self.edit_btn.setObjectName("edit_btn")
        self.delete_btn = QtWidgets.QPushButton(self.frame_4)
        self.delete_btn.setGeometry(QtCore.QRect(430, 20, 100, 30))
        self.delete_btn.setStyleSheet("background-color:#455ab3;color:#fff;\n"
"font: 10pt \"Microsoft YaHei UI\";")
        self.delete_btn.setObjectName("delete_btn")
        self.undo_btn = QtWidgets.QPushButton(self.frame_4)
        self.undo_btn.setGeometry(QtCore.QRect(550, 20, 100, 30))
        self.undo_btn.setStyleSheet("background-color:#455ab3;color:#fff;\n"
"font: 10pt \"Microsoft YaHei UI\";")
        self.undo_btn.setObjectName("undo_btn")
        self.verticalLayout.addWidget(self.frame_4)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.data_get_btn.setText(_translate("MainWindow", "数据获取"))
        self.data_analysis_btn.setText(_translate("MainWindow", "数据分析"))
        self.choice_btn.setText(_translate("MainWindow", "手动剔野"))
        self.label_3.setText(_translate("MainWindow", "TextLabel"))
        self.label_8.setText(_translate("MainWindow", "--"))
        self.label.setText(_translate("MainWindow", "参数信息"))
        self.crawl_btn.setText(_translate("MainWindow", "开始爬取"))
        self.upload_excel_btn.setText(_translate("MainWindow", "参数名上传"))
        self.label_6.setText(_translate("MainWindow", "时间段:"))
        self.label_7.setText(_translate("MainWindow", "密码:"))
        self.label_5.setText(_translate("MainWindow", "型号名:"))
        self.label_4.setText(_translate("MainWindow", "用户名:"))
        self.label_2.setText(_translate("MainWindow", "文件信息"))
        item = self.fileinfo_table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "爬取状态"))
        item = self.fileinfo_table.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "遥测名称"))
        item = self.fileinfo_table.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "遥测代号"))
        item = self.fileinfo_table.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "在轨正常范围"))
        item = self.fileinfo_table.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "遥测量来源"))
        item = self.fileinfo_table.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "制图序号"))
        item = self.fileinfo_table.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "制表序号"))
        item = self.fileinfo_table.horizontalHeaderItem(7)
        item.setText(_translate("MainWindow", "参数1"))
        item = self.fileinfo_table.horizontalHeaderItem(8)
        item.setText(_translate("MainWindow", "参数2"))
        item = self.fileinfo_table.horizontalHeaderItem(9)
        item.setText(_translate("MainWindow", "参数3"))
        item = self.fileinfo_table.horizontalHeaderItem(10)
        item.setText(_translate("MainWindow", "参数4"))
        self.report_docx_btn.setText(_translate("MainWindow", "数据导出"))
        self.auto_choice_btn.setText(_translate("MainWindow", "自动剔野"))
        self.select_all_btn.setText(_translate("MainWindow", "全选"))
        self.label_9.setText(_translate("MainWindow", "选择性剔野"))
        item = self.fileinfo_table_2.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "选择"))
        item = self.fileinfo_table_2.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "剔野状态"))
        item = self.fileinfo_table_2.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "遥测名称"))
        item = self.fileinfo_table_2.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "遥测代号"))
        item = self.fileinfo_table_2.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "在轨正常范围"))
        item = self.fileinfo_table_2.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "遥测量来源"))
        item = self.fileinfo_table_2.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "制图序号"))
        item = self.fileinfo_table_2.horizontalHeaderItem(7)
        item.setText(_translate("MainWindow", "制表序号"))
        item = self.fileinfo_table_2.horizontalHeaderItem(8)
        item.setText(_translate("MainWindow", "参数1"))
        item = self.fileinfo_table_2.horizontalHeaderItem(9)
        item.setText(_translate("MainWindow", "参数2"))
        item = self.fileinfo_table_2.horizontalHeaderItem(10)
        item.setText(_translate("MainWindow", "参数3"))
        item = self.fileinfo_table_2.horizontalHeaderItem(11)
        item.setText(_translate("MainWindow", "参数4"))
        item = self.fileinfo_table_2.horizontalHeaderItem(12)
        item.setText(_translate("MainWindow", "查看数据"))
        self.label_10.setText(_translate("MainWindow", "手动剔野"))
        self.save_change_btn.setText(_translate("MainWindow", "保存数据"))
        self.edit_btn.setText(_translate("MainWindow", "编辑模式"))
        self.delete_btn.setText(_translate("MainWindow", "批量删除"))
        self.undo_btn.setText(_translate("MainWindow", "撤销"))

