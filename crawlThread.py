import sys
import time

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import *

from crawl import crawl, check_login, crawl_test


# 继承QThread
class CrawlThread(QtCore.QThread):
    # 通过类成员对象定义信号对象
    _signal = pyqtSignal(tuple)

    def __init__(self, item, username, password, model, telemetry_num, create_time, end_time, filename, data_len):
        super(CrawlThread, self).__init__()
        self.item = item
        self.username = username
        self.password = password
        self.model = model
        self.telemetry_num = telemetry_num
        self.create_time = create_time
        self.end_time = end_time
        self.filename = filename
        self.data_len = data_len

    def __del__(self):
        self.wait()

    def run(self):
        # time.sleep(0.3)
        # 测试，使用相同数据
        is_ok, data = crawl_test(self.model, "", self.create_time, self.end_time, self.filename)
        # is_ok, data = crawl(self.username, self.password, self.model, self.telemetry_num, self.create_time, self.end_time)
        self._signal.emit((self.item, is_ok, data, self.data_len))
