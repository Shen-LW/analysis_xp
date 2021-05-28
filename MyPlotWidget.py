# -*- coding: utf-8 -*-
import datetime
import pyqtgraph as pg
from pyqtgraph import Point
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore, QT_LIB


class MyPlotWidget(pg.PlotWidget):
    is_manual_edit = False
    is_rate_edit = False
    select_status = False
    x = 0
    y = 0
    region = None
    roi_range = None
    base_point_list = []
    position_lable = None
    vLine = None
    hLine = None
    undo_base_point_list = None

    def mousePressEvent(self, ev):
        if self.is_manual_edit:
            self.select_status = True
            point = self.plotItem.vb.mapSceneToView(ev.pos())
            self.x = point.x()
            self.y = point.y()
        if self.is_rate_edit:
            point = self.plotItem.vb.mapSceneToView(ev.pos())
            # 添加竖线
            base_line = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('g', width=1))
            self.addItem(base_line, ignoreBounds=True)
            base_line.setPos(point.x())
            if self.undo_base_point_list is not None:
                self.base_point_list.append(datetime.datetime.fromtimestamp(point.x()))
                self.base_point_list.sort()
                self.undo_base_point_list.append(base_line)

        else:
            QtGui.QGraphicsView.mousePressEvent(self, ev)

            if not self.mouseEnabled:
                return
            self.lastMousePos = Point(ev.pos())
            self.mousePressPos = ev.pos()
            self.clickAccepted = ev.isAccepted()
            if not self.clickAccepted:
                self.scene().clearSelection()
            return  ## Everything below disabled for now..

    def mouseReleaseEvent(self, ev):
        if self.is_manual_edit:
            self.select_status = False
            pos = self.region.pos()
            size = self.region.size()
            l = pos.x()
            t = pos.y()
            w = size.x()
            h = size.y()
            r = l + w
            b = t + h
            if r < l:
                tmp = r
                r = l
                l = tmp
            if b < t:
                tmp = t
                t = b
                b = tmp
            self.roi_range = (l, t, r, b)
        else:
            QtGui.QGraphicsView.mouseReleaseEvent(self, ev)
            if not self.mouseEnabled:
                return
            self.sigMouseReleased.emit(ev)
            self.lastButtonReleased = ev.button()
            return  ## Everything below disabled for now..

    def mouseMoveEvent(self, ev):
        if self.position_lable:
            point = self.plotItem.vb.mapSceneToView(ev.pos())
            self.updata_position(point.x(), point.y())
        if self.is_manual_edit and self.select_status:
            point = self.plotItem.vb.mapSceneToView(ev.pos())
            # 注意反向的问题
            w = point.x() - self.x
            h = point.y() - self.y
            if self.region:
                self.region.setPos([self.x, self.y])
                self.region.setSize([w, h])
        else:
            if self.lastMousePos is None:
                self.lastMousePos = Point(ev.pos())
            delta = Point(ev.pos() - QtCore.QPoint(*self.lastMousePos))
            self.lastMousePos = Point(ev.pos())

            QtGui.QGraphicsView.mouseMoveEvent(self, ev)
            if not self.mouseEnabled:
                return
            self.sigSceneMouseMoved.emit(self.mapToScene(ev.pos()))

            if self.clickAccepted:  ## Ignore event if an item in the scene has already claimed it.
                return

            if ev.buttons() == QtCore.Qt.RightButton:
                delta = Point(np.clip(delta[0], -50, 50), np.clip(-delta[1], -50, 50))
                scale = 1.01 ** delta
                self.scale(scale[0], scale[1], center=self.mapToScene(self.mousePressPos))
                self.sigDeviceRangeChanged.emit(self, self.range)

            elif ev.buttons() in [QtCore.Qt.MidButton, QtCore.Qt.LeftButton]:  ## Allow panning by left or mid button.
                px = self.pixelSize()
                tr = -delta * px

                self.translate(tr[0], tr[1])
                self.sigDeviceRangeChanged.emit(self, self.range)

    def updata_position(self, x, y):
        self.vLine.setPos(x)
        self.hLine.setPos(y)
        x = str(datetime.datetime.fromtimestamp(x))
        y = str(round(y, 3))
        position = "<span style='font-size: 12pt'> x(时间)=" + x + "， <span style='color: red'>y= " + y + "</span>"
        self.position_lable.setText(position)

    def undo_base_line(self):
        if self.undo_base_point_list:
            self.removeItem(self.undo_base_point_list.pop())
            self.base_point_list.pop()

    def reset_rate_edit(self):
        if self.undo_base_point_list:
            for i in range(len(self.undo_base_point_list)):
                if self.undo_base_point_list:
                    self.removeItem(self.undo_base_point_list.pop())
                    self.base_point_list.pop()
        self.is_rate_edit = False

