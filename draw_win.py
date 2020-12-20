import datetime

from PyQt5.QtGui import QColor
import pyqtgraph as pg
from pyqtgraph.exporters import ImageExporter

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        return [str(datetime.datetime.fromtimestamp(values[0])).replace(' ', '|') for value in values]



from PyQt5.QtWidgets import  QVBoxLayout, QMainWindow, QWidget
from PyQt5.QtGui import QFont
import pyqtgraph as pg

class DrawWindow(QMainWindow):
    def __init__(self, index, color, x, y, split_name_list):
        QMainWindow.__init__(self)
        # 设置窗体尺寸
        self.setGeometry(50, 50, 850, 650)
        date_axis = TimeAxisItem(orientation='bottom')
        self.plt = pg.PlotWidget(axisItems={'bottom': date_axis}, background="w")
        centralWidget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.plt)
        centralWidget.setLayout(main_layout)
        # 应用上述布局
        self.setCentralWidget(centralWidget)

        self.draw_image(index, color, x, y, split_name_list)

    def draw_image(self, index, color, x, y, split_name_list):
        self.plt.plot(x, y, pen=pg.mkPen(QColor(color[0], color[1], color[2])))

        pltItem = self.plt.getPlotItem()
        left_axis = pltItem.getAxis("left")
        left_axis.enableAutoSIPrefix(False)
        font = QFont()
        font.setPixelSize(16)
        left_axis.tickFont = font
        bottom_axis = pltItem.getAxis("bottom")
        bottom_axis.tickFont = font


        exporter = ImageExporter(self.plt.getPlotItem())
        exporter.parameters()['width'] = 800
        exporter.parameters()['height'] = 600

        split_name = 'tmp/' + 'split_' + str(index) + '.png'
        exporter.export(split_name)
        split_name_list.append(split_name)