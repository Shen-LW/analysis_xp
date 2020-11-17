# -*- coding: utf-8 -*-
import pyqtgraph as pg
from pyqtgraph import Point
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore


class MyPlotWidget(pg.PlotWidget):
    is_edit = False
    select_status = False
    x = 0
    y = 0
    region = None
    roi_range = None


    def mousePressEvent(self, ev):
        if self.is_edit:
            self.select_status = True
            point = self.plotItem.vb.mapSceneToView(ev.pos())
            self.x = point.x()
            self.y = point.y()
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
        if self.is_edit:
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
        if self.is_edit and self.select_status:
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


