import sys
import os
import datetime
import time
import copy
import uuid

import xlrd
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QColor
# from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QCheckBox, QPushButton, QApplication
import pyqtgraph as pg
from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml.ns import qn

from interface import Ui_MainWindow
from crawl import crawl, crawl_test
from myMessage import MyMessageBox, MessageReply

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')


class UiTest(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(UiTest, self).__init__(parent)
        self.raw_data = []  # 爬取的原始数据
        self.excel_data = []  # 所有excel爬取的数据, 修改记录在这里
        self.manual_item = {}  # 当前操作的数据
        self.choice_data = []  # 剔野暂存数据
        self.select_indexs = []  # 自动剔野选择行数组
        self.l_plot_data = None  # 左侧绘图数据
        self.r_plot_data = None  # 右侧绘图数据
        self.undo_list = []  # undo列表
        self.crawl_status = False
        self.setupUi(self)
        self.bing_signal()
        self.extar_control()
        self.init_style()
        self.create_dir(['tmp', 'source'])
        self.message_box = MyMessageBox()


    def bing_signal(self):
        self.upload_excel_btn.clicked.connect(self.choose_excel)
        self.crawl_btn.clicked.connect(self.crawl)
        self.report_docx_btn.clicked.connect(self.report_excel)
        self.edit_btn.clicked.connect(self.edit_model)
        self.delete_btn.clicked.connect(self.delete_data)
        self.undo_btn.clicked.connect(self.delete_undo)
        self.save_change_btn.clicked.connect(self.save_chaneg)
        self.select_all_btn.clicked.connect(self.select_all)
        self.auto_choice_btn.clicked.connect(self.auto_choice)
        self.data_get_btn.clicked.connect(lambda: self.select_tab('data_get'))
        self.data_analysis_btn.clicked.connect(lambda: self.select_tab('data_analysis'))
        self.choice_btn.clicked.connect(lambda: self.select_tab('choice'))

    def init_style(self):
        # self.setWindowFlags(Qt.FramelessWindowHint)
        logo = QtGui.QPixmap('source/logo.png')
        self.label_3.setPixmap(logo)
        self.label_3.setScaledContents(True)
        self.hidden_frame('data_get')


    def hidden_frame(self, tab):
        style_1 = 'font: 75 12pt "微软雅黑";background-color: rgb(255, 255, 255);color:#455ab3;border-top-left-radius:15px;border-top-right-radius:15px;'
        style_2 = 'background-color: rgb(80, 103, 203);font: 75 12pt "微软雅黑";color: rgb(255, 255, 255);border-top-left-radius:15px;border-top-right-radius:15px;'
        if tab == "data_get":
            self.frame.setHidden(False)
            self.fileinfo_table.setHidden(False)

            self.frame_2.setHidden(True)
            self.fileinfo_table_2.setHidden(True)

            self.frame_3.setHidden(True)
            self.l_widget.setHidden(True)
            self.r_widget.setHidden(True)
            self.frame_4.setHidden(True)

            self.data_get_btn.setStyleSheet(style_1)
            self.data_analysis_btn.setStyleSheet(style_2)
            self.choice_btn.setStyleSheet(style_2)
        elif tab == 'data_analysis':
            self.frame.setHidden(True)
            self.fileinfo_table.setHidden(True)

            self.frame_2.setHidden(False)
            self.fileinfo_table_2.setHidden(False)

            self.frame_3.setHidden(True)
            self.l_widget.setHidden(True)
            self.r_widget.setHidden(True)
            self.frame_4.setHidden(True)

            self.data_get_btn.setStyleSheet(style_2)
            self.data_analysis_btn.setStyleSheet(style_1)
            self.choice_btn.setStyleSheet(style_2)

        elif tab == 'choice':
            self.frame.setHidden(True)
            self.fileinfo_table.setHidden(True)

            self.frame_2.setHidden(True)
            self.fileinfo_table_2.setHidden(True)

            self.frame_3.setHidden(False)
            self.l_widget.setHidden(False)
            self.r_widget.setHidden(False)
            self.frame_4.setHidden(False)

            self.data_get_btn.setStyleSheet(style_2)
            self.data_analysis_btn.setStyleSheet(style_2)
            self.choice_btn.setStyleSheet(style_1)

    def create_dir(slef, path_list):
        for path in path_list:
            if not os.path.exists(path):
                os.makedirs(path)


    def extar_control(self):
        # 左边框
        l_plot_layout = QtWidgets.QGridLayout()  # 实例化一个网格布局层
        self.l_widget.setLayout(l_plot_layout)  # 设置K线图部件的布局层
        self.l_pw = pg.PlotWidget(self)  # 创建一个绘图控件
        self.l_pw.showGrid(x=True, y=True)
        # 要将pyqtgraph的图形添加到pyqt5的部件中，我们首先要做的就是将pyqtgraph的绘图方式由window改为widget。PlotWidget方法就是通过widget方法进行绘图的
        self.l_widget.layout().addWidget(self.l_pw)

        # 右边框
        r_plot_layout = QtWidgets.QGridLayout()  # 实例化一个网格布局层
        self.r_widget.setLayout(r_plot_layout)  # 设置K线图部件的布局层
        self.r_pw = pg.PlotWidget(self)  # 创建一个绘图控件
        self.r_pw.showGrid(x=True, y=True)
        self.region = pg.LinearRegionItem()
        self.region.setRegion([0, 0])
        self.r_pw.addItem(self.region, ignoreBounds=True)
        # 要将pyqtgraph的图形添加到pyqt5的部件中，我们首先要做的就是将pyqtgraph的绘图方式由window改为widget。PlotWidget方法就是通过widget方法进行绘图的
        self.r_widget.layout().addWidget(self.r_pw)

    def choose_excel(self):
        if self.crawl_status:
            QMessageBox.warning(self, "请等待", "请等待数据爬取完成", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return
        fileName_choose, filetype = QtWidgets.QFileDialog.getOpenFileName(self,
                                                                          "选取文件",
                                                                          os.getcwd(),  # 起始路径
                                                                          "Execl Files (*.xlsx;*.xls)")  # 设置文件扩展名过滤,用双分号间隔

        if fileName_choose == "":
            return
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
                "status": '未爬取',
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
        self.update_talbe1()

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
                                    border-style: outset; font: 10pt "Microsoft YaHei UI";  ''')
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
            self.fileinfo_table_2.setItem(r, 1, QTableWidgetItem("未剔野"))
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
            # self.fileinfo_table_2.setItem(r, 9, QTableWidgetItem(str(item['params_four'])))

    def crawl(self):
        if not self.excel_data:
            self.message_box.setContent("参数缺失", "未导入任何爬取参数")
            self.message_box.show()
            # time.sleep(100)
            # QMessageBox.warning(self, "参数缺失", "未导入任何爬取参数", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return

        if self.crawl_status:
            QMessageBox.warning(self, "请等待", "请等待数据爬取完成", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            return

        self.crawl_status = True
        # 检查各个控件参数
        username = self.username_edit.text()
        password = self.password_edit.text()
        model = self.model_edit.text()
        create_time = self.create_time_edit.text()
        end_time = self.end_time_edit.text()

        if username == '' or password == '' or model == '' or create_time == '' or end_time == '' or self.excel_data == []:
            # QMessageBox.warning(self, "参数缺失", "请完善参数信息", QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)
            pass

        # 循环爬取
        for item in self.excel_data:
            index = self.excel_data.index(item)
            is_ok, data = crawl_test(model, item['telemetry_name'], create_time, end_time)
            if is_ok:
                item["data"] = data
                self.fileinfo_table.setItem(index, 0, QTableWidgetItem("爬取成功"))
                self.fileinfo_table.item(index, 0).setBackground(QColor(100, 255, 0))
            else:
                self.fileinfo_table.setItem(index, 0, QTableWidgetItem("失败"))
                self.fileinfo_table.item(index, 0).setBackground(QColor(255, 185, 15))
            QApplication.processEvents()

        self.crawl_status = False
        self.raw_data = copy.deepcopy(self.excel_data)
        # 切换到数据分析标签，并填充数据
        self.hidden_frame('data_analysis')
        self.update_talbe2()

    def manual_choice(self, r):
        self.manual_item = self.excel_data[r]
        self.choice_data = copy.deepcopy(self.manual_item["data"])
        self.undo_list = []
        # 传递到手动剔野页面,更新数据
        # todo 数据处理还需要完善
        raw = copy.deepcopy(self.raw_data[r]["data"])
        l_x, l_y = self.get_choice_data_xy(raw)
        r_x, r_y = self.get_choice_data_xy()
        if self.l_plot_data == None:
            self.l_plot_data = self.l_pw.plot(l_y, pen=pg.mkPen('g', width=1))  # 在绘图控件中绘制图形
            self.r_plot_data = self.r_pw.plot(r_y, pen=pg.mkPen('r', width=1))
        else:
            self.l_plot_data.setData(l_y, pen=pg.mkPen('g', width=1))
            self.r_plot_data.setData(r_y, pen=pg.mkPen('r', width=1))

        self.region.setRegion([0,0])
        self.hidden_frame('choice')


    def select_row(self, r):
        if r in self.select_indexs:
            self.select_indexs.remove(r)
        else:
            self.select_indexs.append(r)


    # 标签页切换
    def select_tab(self, tab_type):
        if self.crawl_status:
            QMessageBox.warning(self, "请等待", "请等待数据爬取完成", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            self.tabWidget.setCurrentIndex(0)
            return
        self.hidden_frame(tab_type)



    def edit_model(self):
        data_len = len(self.manual_item["data"])
        middle = int(data_len / 2)
        w = 1 if int(data_len / 10) == 0 else int(data_len / 10)
        self.region.setRegion([middle - w, middle + w])

    def get_choice_data_xy(self, raw_data=None):
        x = []
        y = []
        if raw_data == None:
            data = self.choice_data
        else:
            data = raw_data

        for item in data:
            for k, v in item.items():
                if k == "T0":
                    x.append(v)
                else:
                    y.append(float(v))
        return x, y

    # 删除数据
    def delete_data(self):
        # 选定区域
        minX, maxX = self.region.getRegion()

        minX = 0 if minX < 0 else int(minX)
        c_len = len(self.choice_data)
        maxX = c_len if maxX > c_len else int(maxX)

        undo_data = copy.deepcopy(self.choice_data)
        self.undo_list.append(undo_data)

        # 修改数据
        for i in range(minX, maxX):
            item = self.choice_data[i]
            for k, v in item.items():
                if k != "T0":
                    item[k] = 0
        x, y = self.get_choice_data_xy()
        self.r_plot_data.setData(y, pen=pg.mkPen('r', width=1))


    def delete_undo(self):
        if self.undo_list:
            self.choice_data = self.undo_list.pop()
            x, y = self.get_choice_data_xy()
            self.r_plot_data.setData(y, pen=pg.mkPen('r', width=1))

    def save_chaneg(self):
        message_result = QMessageBox.warning(self, "请等待", "确定修改数据", QMessageBox.Yes | QMessageBox.No,
                                             QMessageBox.Yes)
        if message_result == QMessageBox.Yes:
            self.manual_item["data"] = self.choice_data
            index = self.fileinfo_table_2.currentIndex().row()
            self.fileinfo_table_2.setItem(index-1, 1, QTableWidgetItem("手动剔野"))
            self.fileinfo_table_2.item(index-1, 1).setBackground(QColor(100, 255, 0))
            QApplication.processEvents()
            self.region.setZValue(0)
            self.hidden_frame('data_analysis')


    def select_all(self):
        number = len(self.raw_data)
        if self.select_all_btn.text() == '全选':
            for i in range(number):
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
        QApplication.processEvents()



    def auto_choice(self):
        if not self.select_indexs:
            message_result = QMessageBox.warning(self, "自动剔野", "请勾选自动剔野项", QMessageBox.Yes | QMessageBox.No,
                                                 QMessageBox.Yes)
            return

        tmp_data = {}
        for i in range(len(self.excel_data)):
            if i in self.select_indexs:
                tmp_data[str(i)] = copy.deepcopy(self.excel_data[i])

        # 修改data组合方式，按键值对重新组合数据，键为时间
        for index, value in tmp_data.items():
            data = value["data"]
            new_dict = {}
            for item in data:
                for k, v in item.items():
                    if k != "T0":
                        new_dict[item["T0"]] = v
                        break
            value["data"] = new_dict

        # 源包剔野
        # source = {"source": {"index": "value"}}
        source_type = {}
        for index, value in tmp_data.items():
            if not self.check_choice("source", value["params_four"]):
                continue
            if value["telemetry_source"] not in source_type.keys():
                source_type[value["telemetry_source"]] = {}
            source_type[value["telemetry_source"]][index] = value
        for type, value in source_type.items():
            self.source_choice(value)

        # 阈值剔野
        for index, value in tmp_data.items():
            if self.check_choice('threshold', value['params_four']):
                self.threshold_choice(index, value)

        # 变化率剔野
        for index, value in tmp_data.items():
            if self.check_choice('rate', value['params_four']):
                self.rate_choice(index, value)

        # 修改剔野状态
        for index, value in tmp_data.items():
            self.fileinfo_table_2.setItem(int(index), 1, QTableWidgetItem("自动剔野"))
            self.fileinfo_table_2.item(int(index), 1).setBackground(QColor(100, 255, 0))
            QApplication.processEvents()

        QMessageBox.information(self, "自动剔野", "自动剔野已完成", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

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

            # 如果野点大于等于5，则用时间全部剔除
            if number >= 5:
                for item in source_data_dict.values():
                    item['data'][t] = 0

        for index, v in source_data_dict.items():
            new_data = [{"T0": k, "V02317575": v} for k, v in v['data'].items()]
            self.excel_data[int(k)]['data'] = new_data

    def threshold_choice(self, index, value):
        data = value['data']
        params_two = value['params_two']
        threshold = params_two.replace("[", '').replace("]", '').replace(' ', '').replace('，', ',')
        threshold = threshold.split(',')

        for t, v in value["data"].items():
            if float(v) > float(threshold[1]) or float(v) < float(threshold[0]):
                value['data'][t] = 0

        new_data_list = [{"T0": k, "V02317575": v} for k, v in value['data'].items()]

        self.excel_data[int(index)]['data'] = new_data_list

    def rate_choice(self, index, data):
        pass
        # 异常值处理还有疑问

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
        intr =''.join(["        ", start_y, '年', start_m, '月',start_d, '日至', end_y,'年', end_m,'月',  end_d, '日',
                       'XXXX卫星在轨运行状态正常，卫星运行在XXXX模式，所查询数据均在安全范围以内，', error_text, '具体情况见表1 在轨遥测数据监视情况记录表，和表2在轨状态位变化情况记录表。'])
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
        # 生成图片
        for item in self.excel_data:
            img_num = str(item['img_num'])
            if img_num == '' or img_num[0] != '1':
                continue
            table1_title = document.add_paragraph("图" + img_num)
            table1_title = table1_title.paragraph_format
            table1_title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            image_path = self.create_docx_image(item['data'])
            document.add_picture(image_path)

        document.add_heading('1.2 二浮陀螺在轨运行状况', level=1)

        document.add_heading('总结', level=1)


        reportname = datetime.datetime.now().strftime('%Y%m%d%H%M') + '.docx'
        report = reportname
        document.save(report)
        QMessageBox.information(self, "生成表格", "word文档生成成功", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)


    def create_table1_data(self):
        data = []
        error_number = 0
        for index in range(len(self.excel_data)):
            item = self.excel_data[index]
            if 'SPE故障判断允许位' in item['telemetry_name']:
                continue
            parms_range = self.get_data_range(item["data"])
            normal_split = item['normal_range'].replace('°', '').replace('~', ',').replace(' ', '').split(',')
            normal_range = [float(normal_split[0]), float(normal_split[1])]

            if parms_range[0] >= normal_range[0] and parms_range[1] <= normal_range[1]:
                range_status = "正常"
            else:
                error_number = error_number + 1
                range_status = "异常"
            child = (index, item['telemetry_name'], item["telemetry_num"], str(parms_range), str(normal_range), range_status)
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



    def create_docx_image(self, data):
        y_list = []
        for item in data:
            for k, v in item.items():
                if k != "T0":
                    y_list.append(v)
        # pw = pg.PlotWidget(self)  # 创建一个绘图控件
        # pw.showGrid(x=True, y=True)
        # pw.plot(y_list)
        plt = pg.plot(y_list, pen=pg.mkPen('r', width=1))
        exporter = pg.exporters.ImageExporter(plt.plotItem)
        exporter.parameters()['width'] = 800
        exporter.parameters()['height'] = 400

        file_name = 'tmp/' + str(uuid.uuid1()).replace('-', '') + '.png'
        exporter.export(file_name)
        return file_name




    def get_data_range(self, data):
        value_list = []
        for item in data:
            for k, v in item.items():
                if k != "T0":
                    value_list.append(v)
        minX = min(value_list)
        maxX = max(value_list)
        return [minX, maxX]



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = UiTest()
    ui.show()
    sys.exit(app.exec_())
