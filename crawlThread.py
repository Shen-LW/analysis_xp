import sys
import time

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import *

from crawl import crawl, check_login, crawl_test


# 继承QThread
class CrawlThread(QtCore.QThread):
    # 通过类成员对象定义信号对象
    _signal = pyqtSignal(tuple)

    def __init__(self, satellite_data, username, password, model, create_time, end_time):
        super(CrawlThread, self).__init__()
        self.satellite_data = satellite_data
        self.username = username
        self.password = password
        self.model = model
        self.telemetry_num = satellite_data.dataHead['telemetry_num']
        self.create_time = create_time
        self.end_time = end_time

    def __del__(self):
        self.wait()

    def run(self):
        # time.sleep(0.3)
        # 测试，使用相同数据
        is_ok, content, satellite_data = crawl_test(self.satellite_data, self.model, "", self.create_time, self.end_time)
        # is_ok, content, satellite_data = crawl(self.satellite_data, self.username, self.password, self.model, self.telemetry_num, self.create_time, self.end_time)
        self._signal.emit((is_ok, content, satellite_data))
