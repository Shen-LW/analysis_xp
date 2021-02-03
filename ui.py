import sys
import os
import math
import datetime
import time
import copy
import uuid
import collections
from threading import Thread, Lock

import xlrd
from PIL import Image
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QCheckBox, QPushButton, QApplication, \
    QHeaderView, QAbstractItemView, QSplashScreen
import pyqtgraph as pg
from pyqtgraph.exporters import ImageExporter
from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml.ns import qn

from interface import Ui_MainWindow
from crawl import crawl, check_login, crawl_test
from myMessage import MyMessageBox
from MyPlotWidget import MyPlotWidget
from crawlThread import CrawlThread
from settings import Settings
from draw_win import DrawWindow

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')


class UiTest(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(UiTest, self).__init__(parent)
        self.region = pg.RectROI([0, 0], [0, 0], pen=pg.mkPen('g', width=1))  # 框选
        self.raw_data = []  # 爬取的原始数据
        self.excel_data = []  # 所有excel爬取的数据, 修改记录在这里
        self.crawl_status_list = []  # 暂存所有列的爬取状态
        self.manual_item = {}  # 当前操作的数据
        self.choice_data = []  # 剔野暂存数据
        self.select_indexs = []  # 自动剔野选择行数组
        self.l_plot_data = None  # 左侧绘图数据
        self.r_plot_data = None  # 右侧绘图数据
        self.undo_list = []  # undo队列
        self.undo_base_point_list = []  # 变化率剔野基准点undo队列
        self.crawl_status = False
        self.setupUi(self)
        self.bing_signal()
        self.extar_control()
        self.create_dir(['tmp', 'source'])
        self.config = Settings()
        self.init_style()

    def bing_signal(self):
        self.upload_excel_btn.clicked.connect(self.choose_excel)
        self.crawl_btn.clicked.connect(self.crawl)
        self.report_docx_btn.clicked.connect(self.report_excel)
        self.fileinfo_table_2.itemChanged.connect(self.table_update)
        self.manual_btn.clicked.connect(lambda: self.edit_model(77))  # 77: M
        self.rate_btn.clicked.connect(lambda: self.edit_model(82))  # 82: R
        self.delete_btn.clicked.connect(self.delete_data)
        self.undo_btn.clicked.connect(self.delete_undo)
        self.undo_base_btn.clicked.connect(self.undo_base_point)
        self.save_change_btn.clicked.connect(self.save_chaneg)
        self.select_all_btn.clicked.connect(self.select_all)
        self.auto_choice_btn.clicked.connect(self.auto_choice)
        self.auto_choices_cbbox.currentIndexChanged.connect(self.change_auto_choice_index)
        self.save_auto_choice_config_btn.clicked.connect(self.save_auto_choice_config)
        self.data_get_btn.clicked.connect(lambda: self.select_tab('data_get'))
        self.data_analysis_btn.clicked.connect(lambda: self.select_tab('data_analysis'))
        self.choice_btn.clicked.connect(lambda: self.select_tab('choice'))

    def init_style(self):
        # self.setWindowFlags(Qt.FramelessWindowHint)
        # self.fileinfo_table_2.setSelectionBehavior(QAbstractItemView.SelectRows);
        logo = QtGui.QPixmap('source/logo.png')
        self.label_3.setPixmap(logo)
        self.label_3.setScaledContents(True)
        self.hidden_frame('data_get')

        # 加载默认设置
        login_config = self.config.get_login()
        if login_config['username']:
            self.username_edit.setText(login_config['username'])
            self.password_edit.setText(login_config['password'])
        auto_choices = self.config.get_auto_choice_list()
        if auto_choices:
            choice_items = [str([item + 1 for item in indexs]) for indexs in auto_choices]
            choice_items.insert(0, '[]')
            self.auto_choices_cbbox.addItems(choice_items)

        self.undo_base_btn.setEnabled(False)
        self.undo_base_btn.setStyleSheet(
            'font: 10pt "Microsoft YaHei UI";background-color:rgb(156,156,156);;color:#fff;')

    def hidden_frame(self, tab):
        style_1 = 'font: 75 12pt "微软雅黑";background-color: rgb(255, 255, 255);color:#455ab3;border-top-left-radius:15px;border-top-right-radius:15px;'
        style_2 = 'background-color: rgb(80, 103, 203);font: 75 12pt "微软雅黑";color: rgb(255, 255, 255);border-top-left-radius:15px;border-top-right-radius:15px;'
        if tab == "data_get":
            self.frame.setHidden(False)
            self.fileinfo_table.setHidden(False)
            self.label_2.setHidden(False)

            self.frame_2.setHidden(True)
            self.fileinfo_table_2.setHidden(True)

            self.frame_3.setHidden(True)
            self.l_widget.setHidden(True)
            self.r_widget.setHidden(True)
            self.frame_4.setHidden(True)
            self.frame_6.setHidden(True)

            self.data_get_btn.setStyleSheet(style_1)
            self.data_analysis_btn.setStyleSheet(style_2)
            self.choice_btn.setStyleSheet(style_2)
        elif tab == 'data_analysis':
            self.frame.setHidden(True)
            self.fileinfo_table.setHidden(True)
            self.label_2.setHidden(True)

            self.frame_2.setHidden(False)
            self.fileinfo_table_2.setHidden(False)

            self.frame_3.setHidden(True)
            self.l_widget.setHidden(True)
            self.r_widget.setHidden(True)
            self.frame_4.setHidden(True)
            self.frame_6.setHidden(True)

            self.data_get_btn.setStyleSheet(style_2)
            self.data_analysis_btn.setStyleSheet(style_1)
            self.choice_btn.setStyleSheet(style_2)

        elif tab == 'choice':
            if not self.manual_item:
                message_box = MyMessageBox()
                message_box.setContent("暂无数据", "请先选择要填充的数据")
                message_box.exec_()
                return

            self.frame.setHidden(True)
            self.fileinfo_table.setHidden(True)
            self.label_2.setHidden(True)

            self.frame_2.setHidden(True)
            self.fileinfo_table_2.setHidden(True)

            self.frame_3.setHidden(False)
            self.l_widget.setHidden(False)
            self.r_widget.setHidden(False)
            self.frame_4.setHidden(False)
            self.frame_6.setHidden(False)

            self.data_get_btn.setStyleSheet(style_2)
            self.data_analysis_btn.setStyleSheet(style_2)
            self.choice_btn.setStyleSheet(style_1)

    def create_dir(slef, path_list):
        for path in path_list:
            if not os.path.exists(path):
                os.makedirs(path)

    def reset_data(self):
        # 重置软件数据状态
        self.raw_data = []  # 爬取的原始数据
        self.excel_data = []  # 所有excel爬取的数据, 修改记录在这里
        self.crawl_status_list = []
        self.manual_item = {}  # 当前操作的数据
        self.choice_data = []  # 剔野暂存数据
        self.select_indexs = []  # 自动剔野选择行数组
        self.undo_list = []  # undo列表
        self.crawl_status = False
        # self.l_plot_data = None  # 左侧绘图数据
        # self.r_plot_data = None  # 右侧绘图数据
        if self.l_plot_data:
            self.l_plot_data.setData(x=[], y=[], pen=pg.mkPen('g', width=1))
        if self.r_plot_data:
            self.r_plot_data.setData(x=[], y=[], pen=pg.mkPen('r', width=1))
        self.l_pw.reset_rate_edit()

    def extar_control(self):
        # 左边框
        l_plot_layout = QtWidgets.QGridLayout()  # 实例化一个网格布局层
        self.l_widget.setLayout(l_plot_layout)  # 设置K线图部件的布局层
        l_date_axis = TimeAxisItem(orientation='bottom')
        self.l_pw = MyPlotWidget(self, axisItems={'bottom': l_date_axis})  # 创建一个绘图控件
        self.l_pw.showGrid(x=True, y=True)
        # 要将pyqtgraph的图形添加到pyqt5的部件中，我们首先要做的就是将pyqtgraph的绘图方式由window改为widget。PlotWidget方法就是通过widget方法进行绘图的
        self.l_widget.layout().addWidget(self.l_pw)

        # 右边框
        r_plot_layout = QtWidgets.QGridLayout()  # 实例化一个网格布局层
        self.r_widget.setLayout(r_plot_layout)  # 设置K线图部件的布局层
        r_date_axis = TimeAxisItem(orientation='bottom')
        self.r_pw = MyPlotWidget(self, axisItems={'bottom': r_date_axis})  # 创建一个绘图控件
        self.r_pw.showGrid(x=True, y=True)
        # 要将pyqtgraph的图形添加到pyqt5的部件中，我们首先要做的就是将pyqtgraph的绘图方式由window改为widget。PlotWidget方法就是通过widget方法进行绘图的
        self.r_widget.layout().addWidget(self.r_pw)
        self.r_pw.region = self.region
        self.r_pw.l_widget = self.l_widget
        self.r_pw.position_lable = self.position_lable
        vLine = pg.InfiniteLine(angle=90, movable=False)
        hLine = pg.InfiniteLine(angle=0, movable=False)
        self.r_pw.addItem(vLine, ignoreBounds=True)
        self.r_pw.addItem(hLine, ignoreBounds=True)
        self.r_pw.vLine = vLine
        self.r_pw.hLine = hLine
        self.r_pw.undo_base_point_list = self.undo_base_point_list

    def resizeEvent(self, *args, **kwargs):
        self.fileinfo_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.fileinfo_table_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def choose_excel(self):
        if self.crawl_status:
            message_box = MyMessageBox()
            message_box.setContent("请等待", "请等待数据读取完成")
            message_box.exec_()
            return
        fileName_choose, filetype = QtWidgets.QFileDialog.getOpenFileName(self,
                                                                          "选取文件",
                                                                          os.getcwd(),  # 起始路径
                                                                          "Execl Files (*.xlsx;*.xls)")  # 设置文件扩展名过滤,用双分号间隔

        if fileName_choose == "":
            return
        # 重置软件状态
        self.reset_data()

        self.excel_path_edit.setText(fileName_choose)
        # 解析excel文件，填充内容
        self.parse_excel(fileName_choose)

    # 解析excel
    def parse_excel(self, file_path):
        # 清除原有数据
        self.excel_data = []

        # 打开上传 excel 表格
        file = xlrd.open_workbook(file_path)
        # 打开文件
        sheet_1 = file.sheet_by_index(0)  # 根据sheet页的排序选取sheet
        row_content = sheet_1.row_values(0)  # 获取指定行的数据，返回列表，排序自0开始
        row_number = sheet_1.nrows  # 获取有数据的最大行
        for i in range(1, row_number):
            telemetry_name = sheet_1.cell(i, 0).value
            telemetry_num = sheet_1.cell(i, 1).value
            normal_range = sheet_1.cell(i, 2).value
            telemetry_source = sheet_1.cell(i, 3).value
            img_num = sheet_1.cell(i, 4).value
            table_num = sheet_1.cell(i, 5).value
            params_one = sheet_1.cell(i, 6).value
            params_two = sheet_1.cell(i, 7).value
            params_three = sheet_1.cell(i, 8).value
            params_four = sheet_1.cell(i, 9).value
            item = {
                "status": '未读取',
                'telemetry_name': telemetry_name,
                'telemetry_num': telemetry_num,
                'normal_range': normal_range,
                'telemetry_source': telemetry_source,
                'img_num': img_num,
                'table_num': table_num,
                'params_one': params_one,
                'params_two': params_two,
                'params_three': params_three,
                "params_four": params_four,
                "data": []
            }
            self.excel_data.append(item)
        self.crawl_status_list = [None for i in range(len(self.excel_data))]
        self.update_talbe1()
        self.crawl_btn.setEnabled(True)
        self.crawl_btn.setStyleSheet('font: 10pt "Microsoft YaHei UI";background-color:#455ab3;color:#fff;')

    def update_talbe1(self):
        count = self.fileinfo_table.rowCount()
        for i in range(count):
            self.fileinfo_table.removeRow(count - i - 1)

        excel_data = self.excel_data
        row = len(excel_data)
        self.fileinfo_table.setRowCount(len(excel_data))
        for r in range(row):
            item = excel_data[r]
            self.fileinfo_table.setItem(r, 0, QTableWidgetItem(str(item['status'])))
            self.fileinfo_table.setItem(r, 1, QTableWidgetItem(str(item['telemetry_name'])))
            self.fileinfo_table.setItem(r, 2, QTableWidgetItem(str(item['telemetry_num'])))
            self.fileinfo_table.setItem(r, 3, QTableWidgetItem(str(item['normal_range'])))
            self.fileinfo_table.setItem(r, 4, QTableWidgetItem(str(item['telemetry_source'])))
            self.fileinfo_table.setItem(r, 5, QTableWidgetItem(str(item['img_num'])))
            self.fileinfo_table.setItem(r, 6, QTableWidgetItem(str(int(item['table_num']))))
            self.fileinfo_table.setItem(r, 7, QTableWidgetItem(str(item['params_one'])))
            self.fileinfo_table.setItem(r, 8, QTableWidgetItem(str(item['params_two'])))
            self.fileinfo_table.setItem(r, 9, QTableWidgetItem(str(item['params_three'])))
            self.fileinfo_table.setItem(r, 10, QTableWidgetItem(str(item['params_four'])))
        # 表格1禁止编辑
        self.fileinfo_table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

    def getSelectButton(self, id):
        # 手动剔野
        select_check_btn = QCheckBox()
        select_check_btn.setObjectName(str(id) + '_select')
        select_check_btn.setStyleSheet(''' text-align : center; margin : 40px; font : 13px  ''')
        select_check_btn.clicked.connect(lambda: self.select_row(id))
        return select_check_btn

    # 列表内添加按钮
    def buttonForRow(self, id):
        # 手动剔野
        updateBtn = QPushButton('手动剔野')
        updateBtn.setStyleSheet(''' text-align : center; background-color : Orange; margin : 5px;
                                    border-style: outmanual_choset; font: 10pt "Microsoft YaHei UI";  ''')
        updateBtn.clicked.connect(lambda: self.manual_choice(id))
        return updateBtn

        # # 列表内添加按钮
        # def buttonForRow(self, id):
        #     widget = QWidget()
        #     # 修改
        #     updateBtn = QPushButton('修改')
        #     updateBtn.setStyleSheet(''' text-align : center;
        #                                           background-color : NavajoWhite;
        #                                           height : 30px;
        #                                           border-style: outset;
        #                                           font : 13px  ''')
        #
        #     updateBtn.clicked.connect(lambda: self.updateTable(id))
        #
        #     # 查看
        #     viewBtn = QPushButton('查看')
        #     viewBtn.setStyleSheet(''' text-align : center;
        #                                   background-color : DarkSeaGreen;
        #                                   height : 30px;
        #                                   border-style: outset;
        #                                   font : 13px; ''')
        #
        #     viewBtn.clicked.connect(lambda: self.viewTable(id))
        #
        #     # 删除
        #     deleteBtn = QPushButton('删除')
        #     deleteBtn.setStyleSheet(''' text-align : center;
        #                                     background-color : LightCoral;
        #                                     height : 30px;
        #                                     border-style: outset;
        #                                     font : 13px; ''')
        #
        #     hLayout = QHBoxLayout()
        #     hLayout.addWidget(updateBtn)
        #     hLayout.addWidget(viewBtn)
        #     hLayout.addWidget(deleteBtn)
        #     hLayout.setContentsMargins(5, 2, 5, 2)
        #     widget.setLayout(hLayout)
        #     return widget

    def update_talbe2(self):
        count = self.fileinfo_table_2.rowCount()
        for i in range(count):
            self.fileinfo_table_2.removeRow(count - i - 1)

        excel_data = self.excel_data
        row = len(excel_data)
        self.fileinfo_table_2.setRowCount(len(excel_data))
        for r in range(row):
            item = excel_data[r]
            selectBtn = self.getSelectButton(r)
            self.fileinfo_table_2.setCellWidget(r, 0, selectBtn)
            tmp_text = "未剔野" if item['data'] else "数据读取失败"
            self.fileinfo_table_2.setItem(r, 1, QTableWidgetItem(tmp_text))
            if tmp_text == '数据读取失败':
                self.fileinfo_table_2.item(r, 1).setBackground(QColor(255, 185, 15))
            self.fileinfo_table_2.setItem(r, 2, QTableWidgetItem(str(item['telemetry_name'])))
            self.fileinfo_table_2.setItem(r, 3, QTableWidgetItem(str(item['telemetry_num'])))
            self.fileinfo_table_2.setItem(r, 4, QTableWidgetItem(str(item['normal_range'])))
            self.fileinfo_table_2.setItem(r, 5, QTableWidgetItem(str(item['telemetry_source'])))
            self.fileinfo_table_2.setItem(r, 6, QTableWidgetItem(str(item['img_num'])))
            self.fileinfo_table_2.setItem(r, 7, QTableWidgetItem(str(int(item['table_num']))))
            self.fileinfo_table_2.setItem(r, 8, QTableWidgetItem(str(item['params_one'])))
            self.fileinfo_table_2.setItem(r, 9, QTableWidgetItem(str(item['params_two'])))
            self.fileinfo_table_2.setItem(r, 10, QTableWidgetItem(str(item['params_three'])))
            self.fileinfo_table_2.setItem(r, 11, QTableWidgetItem(str(item['params_four'])))
            updateBtn = self.buttonForRow(r)
            self.fileinfo_table_2.setCellWidget(r, 12, updateBtn)

    # 已转换为使用多线程爬取
    # def crawl_thread(self, item, username, password, model, telemetry_name, create_time, end_time):
    #     index = self.excel_data.index(item)
    #     time.sleep(0.3)
    #     # 测试，使用相同数据
    #     # is_ok, data = crawl_test(model, "", create_time, end_time)
    #     is_ok, data = crawl(username, password, model, item['telemetry_name'], create_time, end_time)
    #     if is_ok:
    #         item["data"] = data
    #         self.fileinfo_table.setItem(index, 0, QTableWidgetItem("读取成功"))
    #         self.fileinfo_table.item(index, 0).setBackground(QColor(100, 255, 0))
    #     else:
    #         self.fileinfo_table.setItem(index, 0, QTableWidgetItem("读取失败"))
    #         self.fileinfo_table.item(index, 0).setBackground(QColor(255, 185, 15))
    #     QApplication.processEvents()

    def crawl_callback(self, msg):
        item, is_ok, data = msg
        index = self.excel_data.index(item)
        if is_ok:
            item["data"] = data
            self.fileinfo_table.setItem(index, 0, QTableWidgetItem("读取成功"))
            self.fileinfo_table.item(index, 0).setBackground(QColor(100, 255, 0))
            self.crawl_status_list[index] = True
        else:
            self.fileinfo_table.setItem(index, 0, QTableWidgetItem("读取失败"))
            self.fileinfo_table.item(index, 0).setBackground(QColor(255, 185, 15))
            self.crawl_status_list[index] = False

        if None not in self.crawl_status_list:
            self.crawl_status = False
            self.raw_data = copy.deepcopy(self.excel_data)
            # 切换到数据分析标签，并填充数据
            self.hidden_frame('data_analysis')
            self.update_talbe2()

    def crawl(self):
        if not self.excel_data:
            message_box = MyMessageBox()
            message_box.setContent("参数缺失", "未导入任何爬读取参数")
            message_box.exec_()
            return

        if self.crawl_status:
            message_box = MyMessageBox()
            message_box.setContent("请等待", "请等待数据读取完成")
            message_box.exec_()
            return

        # 检查各个控件参数
        username = self.username_edit.text()
        password = self.password_edit.text()
        model = self.model_edit.text()
        create_time = self.create_time_edit.text()
        end_time = self.end_time_edit.text()

        if username == '' or password == '' or model == '' or create_time == '' or end_time == '' or self.excel_data == []:
            message_box = MyMessageBox()
            message_box.setContent("参数缺失", "请完善参数信息")
            message_box.exec_()
            return
            # pass

        # 判断账号密码是否正确
        # todo: 发布前记得复原
        try:
            is_login = check_login(username, password)
        except:
            message_box = MyMessageBox()
            message_box.setContent("登录失败", "网络连接失败")
            message_box.exec_()
            return

        if not is_login:
            message_box = MyMessageBox()
            message_box.setContent("读取失败", "账号或密码错误")
            message_box.exec_()
            return
        else:
            # 保存账户和密码
            self.config.change_login(self.username_edit.text(), self.password_edit.text())

        self.crawl_status = True
        self.config.change_login(self.username_edit.text(), self.password_edit.text())
        # 多线程爬取
        # 创建线程
        self.crawl_btn.setEnabled(False)
        self.crawl_btn.setStyleSheet('font: 10pt "Microsoft YaHei UI";background-color:rgb(156,156,156);;color:#fff;')
        thread_list = []
        for item in self.excel_data:
            tmp_thread = CrawlThread(item, username, password, model, item['telemetry_num'], create_time, end_time)
            tmp_thread._signal.connect(self.crawl_callback)
            thread_list.append(tmp_thread)

        # 开始线程
        for thread in thread_list:
            thread.start()

        # while 1:
        #     time.sleep(1)
        #     if None not in self.crawl_status_list:
        #         break

        # # 创建新线程
        # for item in self.excel_data:
        #     threads.append(Thread(target=self.crawl_thread, args=(item, username, password, model, item['telemetry_name'], create_time, end_time)))
        # # 开启新线程
        # for thread in threads:
        #     thread.start()
        #
        # # 等待所有线程完成
        # for thread in threads:
        #     thread.join()

    def manual_choice(self, r):
        self.fileinfo_table_2.selectRow(r)
        self.update_choice_parms()
        self.manual_item = self.excel_data[r]
        if self.manual_item['data'] == [] or self.manual_item['data'] is None:
            message_box = MyMessageBox()
            message_box.setContent("获取失败", "请检查数据后重新读取")
            message_box.exec_()
            return
        self.choice_data = copy.deepcopy(self.manual_item["data"])
        self.undo_list = []
        # 传递到手动剔野页面,更新数据
        raw = copy.deepcopy(self.raw_data[r]["data"])
        l_x, l_y = self.get_choice_data_xy(raw)
        r_x, r_y = self.get_choice_data_xy()
        if self.l_plot_data == None:
            self.l_plot_data = self.l_pw.plot(x=l_x, y=l_y, pen=pg.mkPen('g', width=1))  # 在绘图控件中绘制图形
            self.r_plot_data = self.r_pw.plot(x=r_x, y=r_y, pen=pg.mkPen('r', width=1))
        else:
            self.l_plot_data.setData(x=l_x, y=l_y, pen=pg.mkPen('g', width=1))
            self.r_plot_data.setData(x=r_x, y=r_y, pen=pg.mkPen('r', width=1))

        # 手动剔野界面状态重置
        self.region.setSize([0, 0], [0, 0])
        self.hidden_frame('choice')
        self.r_pw.reset_rate_edit()
        self.r_pw.is_manual_edit = False
        self.r_pw.is_rate_edit = False

        self.manual_btn.setStyleSheet('background-color:#455ab3;color:#fff;font: 10pt "Microsoft YaHei UI";')
        self.rate_btn.setStyleSheet('background-color:#455ab3;color:#fff;font: 10pt "Microsoft YaHei UI";')

        self.undo_base_btn.setEnabled(False)
        self.undo_base_btn.setStyleSheet(
            'font: 10pt "Microsoft YaHei UI";background-color:rgb(156,156,156);;color:#fff;')
        self.delete_btn.setEnabled(False)
        self.delete_btn.setStyleSheet(
            'font: 10pt "Microsoft YaHei UI";background-color:rgb(156,156,156);;color:#fff;')
        self.undo_btn.setEnabled(False)
        self.undo_btn.setStyleSheet(
            'font: 10pt "Microsoft YaHei UI";background-color:rgb(156,156,156);;color:#fff;')
        self.save_change_btn.setEnabled(False)
        self.save_change_btn.setStyleSheet(
            'font: 10pt "Microsoft YaHei UI";background-color:rgb(156,156,156);;color:#fff;')



    def select_row(self, r):
        if self.raw_data[r]['data'] == [] or self.raw_data[r]['data'] is None:
            message_box = MyMessageBox()
            message_box.setContent("获取失败", "请检查数据后重新读取")
            message_box.exec_()
            object_name = str(r) + '_select'
            checkbox = self.findChild(QCheckBox, object_name)
            checkbox.setChecked(False)
            self.select_indexs = self.get_select_indexs()

    def get_select_indexs(self):
        # 获取当前勾选状态，0：未选中，2 已选中
        select_indexs = []
        number = len(self.raw_data)
        for i in range(number):
            object_name = str(i) + '_select'
            checkbox = self.findChild(QCheckBox, object_name)
            if checkbox.checkState() == 2:
                select_indexs.append(i)
        return select_indexs

    # 标签页切换
    def select_tab(self, tab_type):
        if self.crawl_status:
            message_box = MyMessageBox()
            message_box.setContent("请等待", "请等待数据读取完成")
            message_box.exec_()
            return
        self.hidden_frame(tab_type)

    def edit_model(self, key):
        if key == Qt.Key_M:
            self.rate_btn.setStyleSheet('background-color:#455ab3;color:#fff;font: 10pt "Microsoft YaHei UI";')
            self.undo_base_btn.setEnabled(False)
            self.undo_base_btn.setStyleSheet(
                'font: 10pt "Microsoft YaHei UI";background-color:rgb(156,156,156);;color:#fff;')
            self.undo_base_btn.setHidden(True)
            self.r_pw.is_rate_edit = False
            self.r_pw.reset_rate_edit()
            # 手动剔野修改按钮背景色,以及编辑状态
            if self.r_pw.is_manual_edit:
                self.r_pw.is_manual_edit = False
                self.manual_btn.setStyleSheet('background-color:#455ab3;color:#fff;font: 10pt "Microsoft YaHei UI";')
                self.r_pw.removeItem(self.region)
                self.delete_btn.setEnabled(False)
                self.delete_btn.setStyleSheet('font: 10pt "Microsoft YaHei UI";background-color:rgb(156,156,156);;color:#fff;')
                self.undo_btn.setEnabled(False)
                self.undo_btn.setStyleSheet('font: 10pt "Microsoft YaHei UI";background-color:rgb(156,156,156);;color:#fff;')
                self.save_change_btn.setEnabled(False)
                self.save_change_btn.setStyleSheet('font: 10pt "Microsoft YaHei UI";background-color:rgb(156,156,156);;color:#fff;')
            else:
                self.r_pw.is_manual_edit = True
                self.manual_btn.setStyleSheet(
                    'background-color : LightCoral;color:#fff;font: 10pt "Microsoft YaHei UI";')
                self.r_pw.addItem(self.region, ignoreBounds=True)
                self.delete_btn.setEnabled(True)
                self.delete_btn.setStyleSheet('background-color:#455ab3;color:#fff;font: 10pt "Microsoft YaHei UI";')
                self.delete_btn.setText("批量删除(D)")
                self.undo_btn.setEnabled(True)
                self.undo_btn.setStyleSheet('background-color:#455ab3;color:#fff;font: 10pt "Microsoft YaHei UI";')
                self.save_change_btn.setEnabled(True)
                self.save_change_btn.setStyleSheet('background-color:#455ab3;color:#fff;font: 10pt "Microsoft YaHei UI";')
        elif key == Qt.Key_R:
            self.manual_btn.setStyleSheet('background-color:#455ab3;color:#fff;font: 10pt "Microsoft YaHei UI";')
            self.r_pw.is_manual_edit = False
            self.r_pw.removeItem(self.region)
            if self.r_pw.is_rate_edit:
                self.r_pw.is_rate_edit = False
                self.rate_btn.setStyleSheet('background-color:#455ab3;color:#fff;font: 10pt "Microsoft YaHei UI";')
                self.undo_base_btn.setEnabled(False)
                self.undo_base_btn.setStyleSheet(
                    'font: 10pt "Microsoft YaHei UI";background-color:rgb(156,156,156);;color:#fff;')

                self.delete_btn.setEnabled(False)
                self.delete_btn.setStyleSheet(
                    'font: 10pt "Microsoft YaHei UI";background-color:rgb(156,156,156);;color:#fff;')
                self.undo_btn.setEnabled(False)
                self.undo_btn.setStyleSheet(
                    'font: 10pt "Microsoft YaHei UI";background-color:rgb(156,156,156);;color:#fff;')
                self.save_change_btn.setEnabled(False)
                self.save_change_btn.setStyleSheet(
                    'font: 10pt "Microsoft YaHei UI";background-color:rgb(156,156,156);;color:#fff;')
            else:
                self.r_pw.is_rate_edit = True
                self.rate_btn.setStyleSheet('background-color : LightCoral;color:#fff;font: 10pt "Microsoft YaHei UI";')
                self.undo_base_btn.setEnabled(True)
                self.undo_base_btn.setHidden(False)
                self.undo_base_btn.setStyleSheet('font: 10pt "Microsoft YaHei UI";background-color:#455ab3;color:#fff;')
                self.delete_btn.setEnabled(True)
                self.delete_btn.setText("变化率剔野(D)")
                self.delete_btn.setStyleSheet('background-color:#455ab3;color:#fff;font: 10pt "Microsoft YaHei UI";')
                self.undo_btn.setEnabled(True)
                self.undo_btn.setStyleSheet('background-color:#455ab3;color:#fff;font: 10pt "Microsoft YaHei UI";')
                self.save_change_btn.setEnabled(True)
                self.save_change_btn.setStyleSheet(
                    'background-color:#455ab3;color:#fff;font: 10pt "Microsoft YaHei UI";')


    def undo_base_point(self):
        self.r_pw.undo_base_line()

    def keyPressEvent(self, *args, **kwargs):
        key = args[0].key()
        if key == Qt.Key_M or key == Qt.Key_R:
            self.edit_model(key)
        elif key == Qt.Key_D:
            self.delete_data()

    def get_choice_data_xy(self, raw_data=None):
        if raw_data == None:
            data = self.choice_data
        else:
            data = raw_data
        x = []
        y = []
        for k, v in data.items():
            x.append(self.timestr2timestamp(k))
            y.append(float(v))
        return x, y

    # 删除数据
    def delete_data(self):
        if self.r_pw.is_manual_edit:  # 手动剔野
            # 选定区域
            select_range = self.r_pw.roi_range
            if select_range is None:
                return
            undo_data = copy.deepcopy(self.choice_data)
            self.undo_list.append(undo_data)
            # 修改数据
            for time_str, v in self.choice_data.items():
                # 时间判断
                f = self.timestr2timestamp(time_str)
                if f >= select_range[0] and f <= select_range[2]:
                    if v > select_range[1] and v < select_range[3]:
                        self.choice_data[time_str] = 0
            x, y = self.get_choice_data_xy()
            self.r_plot_data.setData(x=x, y=y, pen=pg.mkPen('r', width=1))
        elif self.r_pw.is_rate_edit:  # 变化率剔野
            undo_data = copy.deepcopy(self.choice_data)
            self.undo_list.append(undo_data)
            # 获取基准点
            base_point = self.r_pw.base_point_list
            normal_rate = self.manual_item['params_three']
            self.rate_choice(base_point, float(normal_rate))
            x, y = self.get_choice_data_xy()
            self.r_plot_data.setData(x=x, y=y, pen=pg.mkPen('r', width=1))

    def delete_undo(self):
        if self.undo_list:
            self.choice_data = self.undo_list.pop()
            x, y = self.get_choice_data_xy()
            self.r_plot_data.setData(x=x, y=y, pen=pg.mkPen('r', width=1))

    def rate_choice(self, base_point, normal_rate):
        if not base_point:
            message_box = MyMessageBox()
            message_box.setContent("提示", "前先选择基本点")
            message_box.exec_()
            return
        # 获取基准点对应的时间, 统一取右边值
        # 如果数据点太多的话，可以考虑用二叉搜索或者快速搜索
        tmp_chice_data = copy.deepcopy(self.choice_data)
        tmp_chice_data = list(tmp_chice_data.items())
        start_time = datetime.datetime.strptime(tmp_chice_data[0][0], "%Y-%m-%d %H:%M:%S.%f")
        end_time = datetime.datetime.strptime(tmp_chice_data[-1][0], "%Y-%m-%d %H:%M:%S.%f")

        base_point = [item for item in base_point if (item >= start_time and item < end_time)]
        base_point.reverse()
        correct_base_point = []
        tmp_point = base_point.pop()
        for index in range(len(tmp_chice_data)):
            time_str, v = tmp_chice_data[index]
            t = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")
            if t >= tmp_point:
                correct_base_point.append((index, t))
                if base_point:
                    tmp_point = base_point.pop()
                else:
                    break

        # 构建基准点结构数组
        base_point_struct_list = []
        for index, t in correct_base_point:
            base_point_struct_list.append({
                "left_status": 1,  # 1: 运行剔野， 0: 剔野停止
                "right_status": 1,
                "left": index - 1,  # 左边位置指针
                "right": index + 1,  # 右边位置指针
                "left_outlier": None,  # 左边野点的最后位置
                "right_outlier": None,  # 右边野点的最后位置
                "left_normal": index,  # 左边最后一个正常点
                "right_normal": index,  # 右边最后一个正常点
            })

        # 对解构数组进行扩增，避免循环中的越界判断
        base_point_struct_list.insert(0, {
            "left_status": 0,
            "right_status": 0,
            "left": 0,
            "right": 0,
            "left_outlier": None,
            "right_outlier": None,
            "left_normal": None,
            "right_normal": None
        })
        base_point_struct_list.append({
            "left_status": 0,
            "right_status": 0,
            "left": len(tmp_chice_data),
            "right": len(tmp_chice_data),
            "left_outlier": None,
            "right_outlier": None,
            "left_normal": None,
            "right_normal": None
        })

        # 开始剔野
        correct_index_list = []  # 需要剔除的野点
        number = math.ceil(len(tmp_chice_data) / (len(base_point_struct_list) - 2))  # 外部循环次数，每次对各个基准点处理一次
        for i in range(number):
            for n in range(1, len(base_point_struct_list) - 1):
                point_struct = base_point_struct_list[n]
                before_point_struct = base_point_struct_list[n - 1]
                after_point_struct = base_point_struct_list[n + 1]
                # 左右两边分别进行
                # 左边
                if point_struct["left_status"]:
                    if point_struct["left"] < 0:
                        point_struct["left_status"] = 0
                    else:
                        if point_struct["left"] >= before_point_struct['right']:
                            curr_point = tmp_chice_data[point_struct["left"]]
                            left_normal_point = tmp_chice_data[point_struct["left_normal"]]

                            # 判断时间是否超过十分钟, 超过则停止该方向剔野
                            curr_point_time = datetime.datetime.strptime(curr_point[0], "%Y-%m-%d %H:%M:%S.%f")
                            left_normal_point_time = datetime.datetime.strptime(left_normal_point[0],
                                                                                "%Y-%m-%d %H:%M:%S.%f")
                            if (left_normal_point_time - curr_point_time) > datetime.timedelta(seconds=600):
                                point_struct["left_status"] = 0
                            # 判断变化率
                            space = left_normal_point_time - curr_point_time
                            space_s = space.seconds * 1000000 + space.microseconds
                            if abs((left_normal_point[1] - curr_point[1]) / (space_s / 1000000)) > abs(normal_rate):
                                # 野点
                                correct_index_list.append(point_struct["left"])
                                # 判断野点数是否超过十分钟, 停止剔野
                                if point_struct["left_outlier"]:
                                    befor_outlier_point = tmp_chice_data[point_struct["left_outlier"]]
                                    befor_outlier_point_time = datetime.datetime.strptime(befor_outlier_point[0],
                                                                                          "%Y-%m-%d %H:%M:%S.%f")
                                    if (befor_outlier_point_time - curr_point_time) > datetime.timedelta(seconds=600):
                                        point_struct["left_status"] = 0
                                else:
                                    point_struct["left_outlier"] = point_struct["left"]
                            else:
                                # 正常点
                                point_struct["left_normal"] = point_struct["left"]
                                point_struct["left_outlier"] = None
                            point_struct["left"] = point_struct["left"] - 1
                        else:
                            point_struct["left_status"] = 0

                # 右边
                if point_struct["right_status"]:
                    if point_struct["right"] >= len(tmp_chice_data):
                        point_struct["right_status"] = 0
                    else:
                        if point_struct["right"] <= after_point_struct['left']:
                            curr_point = tmp_chice_data[point_struct["right"]]
                            right_normal_point = tmp_chice_data[point_struct["right_normal"]]

                            # 判断时间是否超过十分钟, 超过则停止该方向剔野
                            curr_point_time = datetime.datetime.strptime(curr_point[0], "%Y-%m-%d %H:%M:%S.%f")
                            right_normal_point_time = datetime.datetime.strptime(right_normal_point[0],
                                                                                 "%Y-%m-%d %H:%M:%S.%f")
                            if (curr_point_time - right_normal_point_time) > datetime.timedelta(seconds=600):
                                point_struct["right_status"] = 0
                            # 判断变化率
                            space = curr_point_time - right_normal_point_time
                            space_s = space.seconds * 1000000 + space.microseconds
                            if abs((curr_point[1] - right_normal_point[1]) / (space_s / 1000000)) > abs(normal_rate):
                                # 野点
                                correct_index_list.append(point_struct["right"])
                                # 判断野点数是否超过十分钟, 停止剔野
                                if point_struct["right_outlier"]:
                                    befor_outlier_point = tmp_chice_data[point_struct["right_outlier"]]
                                    befor_outlier_point_time = datetime.datetime.strptime(befor_outlier_point[0],
                                                                                          "%Y-%m-%d %H:%M:%S.%f")
                                    if (curr_point_time - befor_outlier_point_time) > datetime.timedelta(seconds=600):
                                        point_struct["right_status"] = 0
                                else:
                                    point_struct["right_outlier"] = point_struct["right"]
                            else:
                                # 正常点
                                point_struct["right_normal"] = point_struct["right"]
                                point_struct["right_outlier"] = None
                            point_struct["right"] = point_struct["right"] + 1
                        else:
                            point_struct["right_status"] = 0


        correct_index_list.sort()
        print(correct_index_list)
        # 剔除野点
        for index in correct_index_list:
            time_str = tmp_chice_data[index][0]
            self.choice_data[time_str] = 0

    def save_chaneg(self):
        message_box = MyMessageBox()
        message_box.setContent("提示", "确定修改数据")
        message_box.exec_()

        if message_box.reply == QMessageBox.Ok:
            self.manual_item["data"] = self.choice_data
            index = self.fileinfo_table_2.currentIndex().row()
            self.fileinfo_table_2.setItem(index, 1, QTableWidgetItem("手动剔野"))
            self.fileinfo_table_2.item(index, 1).setBackground(QColor(100, 255, 0))
            self.r_pw.is_edit = False
            self.hidden_frame('data_analysis')
            QApplication.processEvents()

    def select_all(self):
        number = len(self.raw_data)
        if self.select_all_btn.text() == '全选':
            for i in range(number):
                if self.raw_data[i]['data'] == [] or self.raw_data[i]['data'] is None:
                    continue
                object_name = str(i) + '_select'
                checkbox = self.findChild(QCheckBox, object_name)
                checkbox.setChecked(True)
            self.select_all_btn.setText('取消全选')
        elif self.select_all_btn.text() == '取消全选':
            for i in range(number):
                object_name = str(i) + '_select'
                checkbox = self.findChild(QCheckBox, object_name)
                checkbox.setChecked(False)
            self.select_all_btn.setText('全选')
        self.select_indexs = self.get_select_indexs()
        QApplication.processEvents()

    def update_choice_parms(self):
        # 通过界面剔野参数跟新源数据
        for item in self.excel_data:
            index = self.excel_data.index(item)
            item['normal_range'] = self.fileinfo_table_2.item(int(index), 4).text()
            item['telemetry_source'] = self.fileinfo_table_2.item(int(index), 5).text()
            item['img_num'] = self.fileinfo_table_2.item(int(index), 6).text()
            item['table_num'] = self.fileinfo_table_2.item(int(index), 7).text()
            item['params_one'] = self.fileinfo_table_2.item(int(index), 8).text()
            item['params_two'] = self.fileinfo_table_2.item(int(index), 9).text()
            item['params_three'] = self.fileinfo_table_2.item(int(index), 10).text()
            item['params_four'] = self.fileinfo_table_2.item(int(index), 11).text()

    def auto_choice(self):
        self.select_indexs = self.get_select_indexs()
        if not self.select_indexs:
            message_box = MyMessageBox()
            message_box.setContent("自动剔野", "请勾选自动剔野项")
            message_box.exec_()
            return

        self.update_choice_parms()

        tmp_data = collections.OrderedDict()
        for i in range(len(self.excel_data)):
            if i in self.select_indexs:
                tmp_data[str(i)] = copy.deepcopy(self.excel_data[i])

        # 源包剔野
        # source = {"source": {"index": "value"}}
        source_type = collections.OrderedDict()
        for index, value in tmp_data.items():
            if not self.check_choice("source", value["params_four"]):
                continue
            if value["telemetry_source"] not in source_type.keys():
                source_type[value["telemetry_source"]] = collections.OrderedDict()
            source_type[value["telemetry_source"]][index] = value
        for type, value in source_type.items():
            self.source_choice(value)

        # 阈值剔野
        for index, value in tmp_data.items():
            if self.check_choice('threshold', value['params_four']):
                self.threshold_choice(index, value)

        # 变化率剔野和手动剔野合并
        # # 变化率剔野
        # for index, value in tmp_data.items():
        #     if self.check_choice('rate', value['params_four']):
        #         self.rate_choice(index, value)

        # 修改剔野状态
        for index, value in tmp_data.items():
            self.fileinfo_table_2.setItem(int(index), 1, QTableWidgetItem("自动剔野"))
            self.fileinfo_table_2.item(int(index), 1).setBackground(QColor(100, 255, 0))
            QApplication.processEvents()

        message_box = MyMessageBox()
        message_box.setContent("自动剔野", "自动剔野已完成")
        message_box.exec_()

    # 选择自动剔野保存项
    def change_auto_choice_index(self):
        curr_index = self.auto_choices_cbbox.currentIndex()
        number = len(self.raw_data)
        # 清除原有选择
        for i in range(number):
            object_name = str(i) + '_select'
            checkbox = self.findChild(QCheckBox, object_name)
            checkbox.setChecked(False)
        self.select_indexs = []

        choice_lists = self.config.get_auto_choice_list()
        choice_lists.insert(0, [])
        for item in choice_lists[curr_index]:
            if item < number:
                if self.raw_data[item]['data'] == [] or self.raw_data[item]['data'] is None:
                    continue
                object_name = str(item) + '_select'
                checkbox = self.findChild(QCheckBox, object_name)
                checkbox.setChecked(True)
        self.select_indexs = self.get_select_indexs()

        QApplication.processEvents()

    # 保存自动剔野选项
    def save_auto_choice_config(self):
        self.select_indexs = self.get_select_indexs()
        if self.select_indexs == [] or self.select_indexs == None:
            message_box = MyMessageBox()
            message_box.setContent("配置保存", "当前选择为空")
            message_box.exec_()
        else:
            self.config.change_auto_choice(self.select_indexs)
            message_box = MyMessageBox()
            message_box.setContent("配置保存", "保存成功")
            message_box.exec_()

    def source_choice(self, source_data_dict):
        # {"index": "value"}
        # 长度小于5，直接返回
        if len(source_data_dict.values()) < 5:
            return

        # 获取所有时间键
        all_time = []
        for k, v in source_data_dict.items():
            all_time = all_time + [j for j in v['data'].keys()]
        all_time = list(set(all_time))

        for t in all_time:
            number = 0
            for item in source_data_dict.values():
                params_one = item['params_one']
                threshold = params_one.replace("[", '').replace("]", '').replace(' ', '').replace('，', ',')
                threshold = threshold.split(',')
                if t in item['data'].keys() and (
                        float(item['data'][t]) > float(threshold[1]) or float(item['data'][t]) < float(threshold[0])):
                    number = number + 1

            # 如果野点大于等于4，则用时间全部剔除
            if number >= 4:
                for item in source_data_dict.values():
                    item['data'][t] = 0

        for index, v in source_data_dict.items():
            self.excel_data[int(k)]['data'] = v['data']

    def threshold_choice(self, index, value):
        data = value['data']
        params_two = value['params_two']
        threshold = params_two.replace("[", '').replace("]", '').replace(' ', '').replace('，', ',')
        threshold = threshold.split(',')

        for t, v in value["data"].items():
            if float(v) > float(threshold[1]) or float(v) < float(threshold[0]):
                value['data'][t] = 0

        self.excel_data[int(index)]['data'] = value['data']

    def check_choice(self, module_name, params_four):
        params = params_four.replace("(", '').replace("（", '').replace(')', '').replace('）', ''). \
            replace(' ', '').replace('，', ',')
        params = params.split(',')
        if len(params) != 3:
            return False
        if module_name == "source" and params[0] in [1, '1']:
            return True
        elif module_name == 'threshold' and params[1] in [1, '1']:
            return True
        elif module_name == 'rate' and params[2] in [1, '1']:
            return True
        return False

    def report_excel(self):
        # 选择路径与文件名
        reportname = os.path.join(os.getcwd(), datetime.datetime.now().strftime('%Y%m%d%H%M') + '.docx')
        fileName_choose, filetype = QtWidgets.QFileDialog.getSaveFileName(self,
                                                                          "导出文件",
                                                                          reportname,  # 起始路径
                                                                          "Execl Files (*.docx;)")  # 设置文件扩展名过滤,用双分号间隔
        if fileName_choose == "":
            return
        self.update_choice_parms()
        # 准备数据
        create_time = self.create_time_edit.text()
        end_time = self.end_time_edit.text()
        start_y = create_time[0:4]
        start_m = create_time[5:7]
        start_d = create_time[8:10]
        end_y = end_time[0:4]
        end_m = end_time[5:7]
        end_d = end_time[8:10]
        error_number, records = self.create_table1_data()
        if error_number == 0:
            error_text = '无异常现象。'
        else:
            error_text = '异常' + str(error_number) + '次。'
        # 生成报告
        document = Document()
        # 标题一
        document.styles['Normal'].font.name = u'微软雅黑'
        document.styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'), u'微软雅黑')
        document.add_heading('1.XXXX卫星' + start_y + '年' + start_m + '月' + '至' + end_m + '月在轨维护报告', 0)
        # 标题一简介
        intr = ''.join(["        ", start_y, '年', start_m, '月', start_d, '日至', end_y, '年', end_m, '月', end_d, '日',
                        'XXXX卫星在轨运行状态正常，卫星运行在XXXX模式，所查询数据均在安全范围以内，', error_text,
                        '具体情况见表1 在轨遥测数据监视情况记录表，和表2在轨状态位变化情况记录表。'])
        document.add_paragraph(intr)

        # 添加表格一
        p2 = document.add_paragraph("表一 在轨遥测数据监视情况记录表")
        p2 = p2.paragraph_format
        p2.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        # p2.page_break_before = True
        table = document.add_table(rows=1, cols=6, style='Table Grid')
        table.autofit = True
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = '序号'
        hdr_cells[1].text = '监视内容'
        hdr_cells[2].text = '遥测代号'
        hdr_cells[3].text = '在轨范围'
        hdr_cells[4].text = '正常范围'
        hdr_cells[5].text = '判读结果'
        # records = self.create_table1_data()
        for order_number, test_content, telemetry_num, on_normal_range, normal_range, result in records:
            row_cells = table.add_row().cells
            row_cells[0].text = str(order_number)
            row_cells[1].text = test_content
            row_cells[2].text = telemetry_num
            row_cells[3].text = on_normal_range
            row_cells[4].text = normal_range
            row_cells[5].text = result

        # 表格二
        p3 = document.add_paragraph("表二 在轨状态位变化情况记录表")
        p3 = p3.paragraph_format
        p3.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        # p3.page_break_before = True
        table1 = document.add_table(rows=1, cols=5, style='Table Grid')
        table1.autofit = True
        h_cells = table1.rows[0].cells
        h_cells[0].text = '序号'
        h_cells[1].text = '遥测参数'
        h_cells[2].text = '遥测代号'
        h_cells[3].text = '状态位'
        h_cells[4].text = '状态变化'
        records1 = self.create_table2_data()
        for order_number, telemetry_params_num, params_num, status_bit, state_change in records1:
            h_cells = table1.add_row().cells
            h_cells[0].text = str(order_number)
            h_cells[1].text = telemetry_params_num
            h_cells[2].text = params_num
            h_cells[3].text = status_bit
            h_cells[4].text = state_change

        document.add_heading('1.1 XXXX卫星控制系统性能在轨状况', level=1)

        # 多组数据组合制图
        drafting_number = {}
        for item in self.excel_data:
            img_num = str(item['img_num'])
            if img_num == '' or img_num == 'None':
                continue
            if img_num not in drafting_number:
                drafting_number[img_num] = []
            drafting_number[img_num].append(item)

        # 制图名排血
        img_nums = [k for k in drafting_number.keys()]
        img_nums.sort()
        # 生成图片
        for img_num in img_nums:
            drafting_list = drafting_number[img_num]
            image_path = self.create_docx_image([item['data'] for item in drafting_list])
            document.add_picture(image_path)
            table1_title = document.add_paragraph("图" + img_num)
            table1_title = table1_title.paragraph_format
            table1_title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        document.add_heading('1.2 二浮陀螺在轨运行状况', level=1)

        document.add_heading('总结', level=1)

        document.save(fileName_choose)

        message_box = MyMessageBox()
        message_box.setContent("生成表格", "word文档生成成功")
        message_box.exec_()

    def table_update(self):
        # 在剔野中再统一修改剔野参数
        pass

    def create_table1_data(self):
        data = []
        error_number = 0
        for index in range(len(self.excel_data)):
            item = self.excel_data[index]
            if item['data'] == [] or item['data'] is None:
                continue
            if 'SPE故障判断允许位' in item['telemetry_name']:
                continue
            parms_range = self.get_data_range(item["data"])
            normal_split = item['normal_range'].replace('°', '').replace('[', '').replace(']', '').replace('~',
                                                                                                           ',').replace(
                ' ', '').split(',')
            normal_range = [float(normal_split[0]), float(normal_split[1])]

            if parms_range[0] >= normal_range[0] and parms_range[1] <= normal_range[1]:
                range_status = "正常"
            else:
                error_number = error_number + 1
                range_status = "异常"
            child = (
                index, item['telemetry_name'], item["telemetry_num"], str(parms_range), str(normal_range), range_status)
            data.append(child)
        return error_number, tuple(data)
        # data = (
        #     (1, '滚动角', 'RKSA1', '该变量的范围（min,max）', '', '正常/异常'),
        #     (2, '滚动角', 'RKSA1', '该变量的范围（min,max）', '', '正常/异常'),
        #     (3, '滚动角', 'RKSA1', '该变量的范围（min,max）', '', '正常/异常'),
        #     (4, '滚动角', 'RKSA1', '该变量的范围（min,max）', '', '正常/异常'),
        #     (5, '滚动角', 'RKSA1', '该变量的范围（min,max）', '', '正常/异常'),
        # )

    def create_table2_data(self):
        # todo 这里逻辑需要完善
        date = (
            (1, 'CIP故障判断允许', 'RKSC16', '允许/1', '不允许/0'),
        )
        return date

    def split_image(self, source_paths, save_path, flag='horizontal'):
        """
        :param source_paths: 原始图片数组
        :param save_path: 保存路径
        :param flag: horizontal or vertical
        :return:
        """
        # 计算图片长宽
        w_size = 0
        h_size = 0
        loc_list = []
        if flag == 'horizontal':
            for item in source_paths:
                loc_list.append((w_size, 0))
                img = Image.open(item)
                size = img.size
                w_size = w_size + size[0]
                h_size = size[1]
        elif flag == 'vertical':
            for item in source_paths:
                loc_list.append((0, h_size))
                img = Image.open(item)
                size = img.size
                w_size = size[0]
                h_size = h_size + size[1]

        # 拼接图片
        joint = Image.new('RGB', (w_size, h_size))
        for item in source_paths:
            img = Image.open(item)
            joint.paste(img, loc_list[source_paths.index(item)])

        joint.save(save_path)

    def create_docx_image(self, data_list):
        color_list = [(220, 20, 60), (0, 0, 255), (0, 255, 0), (255, 140, 0), (0, 255, 255), (255, 0, 255), (0, 0, 139)]
        index = 0
        split_name_list = []
        for data in data_list:
            color = color_list[index % len(color_list)]
            index = index + 1
            x = []
            y = []
            for k, v in data.items():
                x.append(self.timestr2timestamp(k))
                y.append(float(v))
            draw = DrawWindow(index, color, x, y, split_name_list)
            draw.showFullScreen()

        # 拼接图片
        file_name = 'tmp/' + str(uuid.uuid1()).replace('-', '') + '.png'
        self.split_image(split_name_list, file_name, flag='vertical')
        return file_name

    def get_data_range(self, data):
        value_list = list(data.values())
        minX = min(value_list)
        maxX = max(value_list)
        return [minX, maxX]

    def timestr2timestamp(self, timestr):
        datetime_obj = datetime.datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S.%f")
        ret_stamp = int(time.mktime(datetime_obj.timetuple()) * 1000.0 + datetime_obj.microsecond / 1000.0)
        return ret_stamp / 1000


class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        return [datetime.datetime.fromtimestamp(value) for value in values]


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    splash = QSplashScreen(QPixmap(r"source/wait.png"))  # 启动界面图片地址
    splash.show()
    app.processEvents()
    ui = UiTest()
    ui.show()
    splash.finish(ui)
    sys.exit(app.exec_())
