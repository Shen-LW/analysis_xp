import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from datetime import datetime
import time

tss1 = '2013-10-10 23:40:00'
# 转为时间数组
timestr = "2020-10-11 18:08:48.426"
import time
import datetime
# timestr = '2019-01-14 15:22:18.123'

def timestr2timestamp(timestr):
    datetime_obj = datetime.datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S.%f")
    ret_stamp = int(time.mktime(datetime_obj.timetuple()) * 1000.0 + datetime_obj.microsecond / 1000.0)
    return ret_stamp/1000





class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        return [datetime.datetime.fromtimestamp(value) for value in values]

# list_x = [datetime(2018, 3, 1, 9, 36, 50, 136415),
#         datetime(2018, 3, 1, 9, 36, 51, 330912),
#         datetime(2018, 3, 1, 9, 36, 51, 382815),
#         datetime(2018, 3, 1, 9, 36, 52, 928818)]
# list_y = [10, 9, 12, 11]
x_time = ['2020-10-11 18:08:48.426', '2020-10-11 18:08:49.426', '2020-10-11 18:08:50.427', '2020-10-11 18:08:51.426', '2020-10-11 18:08:52.427', '2020-10-11 18:08:53.428', '2020-10-11 18:08:54.428', '2020-10-11 18:08:55.428']
# aa = list_x[0].timestamp()

list_x = [timestr2timestamp(timestr) for timestr in x_time]
list_y = [10, 9, 12, 11, 3, 9, 13, 7]


app = QtGui.QApplication([])

date_axis = TimeAxisItem(orientation='bottom')
graph = pg.PlotWidget(axisItems={'bottom': date_axis})
x = [x for x in list_x]
graph.plot(x=x, y=list_y, pen=pg.mkPen('g', width=1))
graph.show()

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()