#!/usr/bin/env python
from pyqtgraph.Qt import QtGui, QtCore
import copy as cp
import pyqtgraph as pg
import itertools
import subprocess
import os
import signal
import threading
import shlex, time
import sys
import realtime_back

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class dateAxis(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        strns = []
        rng = max(values)-min(values)
        string = '%M:%S'
        label1 = '%b %d -'
        label2 = ' %b %d, %Y'
        for x in values:
            try:
                strns.append(time.strftime(string, time.localtime(x)))
            except ValueError:  ## Windows can't handle dates before 1970
                strns.append('')
        try:
            label = time.strftime(label1, time.localtime(min(values)))+time.strftime(label2, time.localtime(max(values)))
        except ValueError:
            label = ''
        return strns

class uiMainWindow(object):
    def __init__(self):
        self.WIN_HEIGHT = 1024
        self.WIN_WIDTH = 768
        self.MAX_SIZE = 16777215

    def select_jobfile(self):
        if (QtCore.QT_VERSION_STR >= "5"):
            jobfile = QtGui.QFileDialog.getOpenFileName()[0]
        else:
            jobfile = QtGui.QFileDialog.getOpenFileName()
        self.fio_jobfile_path.setText(jobfile)
        if not jobfile:
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.fio_jobfile_contents.clear()
        try:
            text = open('' + jobfile).read()
            self.fio_jobfile_contents.setPlainText(text)
            self.start_button.setEnabled(True)
        except IOError:
            pass
        self.browse_button.setChecked(False)

    def reset_window(self, MainWindow):
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(0, 0))
        MainWindow.setMaximumSize(QtCore.QSize(self.MAX_SIZE, self.MAX_SIZE))

    def create_splitter(self, orientation, widget, name):
        widget.setAccessibleName(_fromUtf8(""))
        widget.setLineWidth(0)
        widget.setOrientation(orientation)
        widget.setHandleWidth(0)
        widget.setObjectName(_fromUtf8(name))

    def setup_ui(self, MainWindow):
        y_axis_read_iops=pg.AxisItem(orientation='left', showValues=True)
        self.set_y_ax(y_axis_read_iops,'Read IOPs (IOP/s)<br><br>')
        y_axis_write_iops=pg.AxisItem(orientation='left')
        self.set_y_ax(y_axis_write_iops, '<br>Write IOPs (IOP/s)<br><br>')
        y_axis_read_bw=pg.AxisItem(orientation='left')
        self.set_y_ax(y_axis_read_bw, 'Read BW (autoscale)<br><br>')
        y_axis_write_bw=pg.AxisItem(orientation='left')
        self.set_y_ax(y_axis_write_bw, '<br>Write BW (autoscale)<br><br>')
        y_axis_read_lat=pg.AxisItem(orientation='left')
        self.set_y_ax(y_axis_read_lat, 'Read latency (ms)<br><br>')
        y_axis_write_lat=pg.AxisItem(orientation='left')
        self.set_y_ax(y_axis_write_lat, '<br>Write latency (ms)<br><br>')
        x_ax_r_iops, x_ax_w_iops, x_ax_r_bw, x_ax_w_bw, x_ax_r_lat, x_ax_w_lat = dateAxis(orientation='bottom'), dateAxis(orientation='bottom'), dateAxis(orientation='bottom'), dateAxis(orientation='bottom'), dateAxis(orientation='bottom'), dateAxis(orientation='bottom')
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(self.WIN_HEIGHT, self.WIN_WIDTH)
        self.reset_window(MainWindow)
        palette = QtGui.QPalette()
        self.set_brush(0, 0, 0, QtGui.QPalette.WindowText, palette, QtGui.QPalette.Active)
        self.set_brush(227, 227, 227,QtGui.QPalette.Button, palette, QtGui.QPalette.Active)
        self.set_brush(255, 255, 255,QtGui.QPalette.Light, palette, QtGui.QPalette.Active)
        self.set_brush(241, 241, 241,QtGui.QPalette.Midlight, palette, QtGui.QPalette.Active)
        self.set_brush(113, 113, 113,QtGui.QPalette.Dark, palette, QtGui.QPalette.Active)
        self.set_brush(151, 151, 151,QtGui.QPalette.Mid, palette, QtGui.QPalette.Active)
        self.set_brush(0, 0, 0,QtGui.QPalette.Text, palette, QtGui.QPalette.Active)
        self.set_brush(255, 255, 255,QtGui.QPalette.BrightText, palette, QtGui.QPalette.Active)
        self.set_brush(0, 0, 0,QtGui.QPalette.ButtonText, palette, QtGui.QPalette.Active)
        self.set_brush(255, 255, 255,QtGui.QPalette.Base, palette, QtGui.QPalette.Active)
        self.set_brush(227, 227, 227,QtGui.QPalette.Window, palette, QtGui.QPalette.Active)
        self.set_brush(0, 0, 0,QtGui.QPalette.Shadow, palette, QtGui.QPalette.Active)
        self.set_brush(241, 241, 241,QtGui.QPalette.AlternateBase, palette, QtGui.QPalette.Active)
        self.set_brush(255, 255, 220,QtGui.QPalette.ToolTipBase, palette, QtGui.QPalette.Active)
        self.set_brush(0, 0, 0,QtGui.QPalette.ToolTipText, palette, QtGui.QPalette.Active)
        self.set_brush(0, 0, 0,QtGui.QPalette.WindowText, palette, QtGui.QPalette.Inactive)
        self.set_brush(227, 227, 227,QtGui.QPalette.Button, palette, QtGui.QPalette.Inactive)
        self.set_brush(255, 255, 255,QtGui.QPalette.Light, palette, QtGui.QPalette.Inactive)
        self.set_brush(241, 241, 241,QtGui.QPalette.Midlight, palette, QtGui.QPalette.Inactive)
        self.set_brush(113, 113, 113,QtGui.QPalette.Dark, palette, QtGui.QPalette.Inactive)
        self.set_brush(151, 151, 151,QtGui.QPalette.Mid, palette, QtGui.QPalette.Inactive)
        self.set_brush(0, 0, 0,QtGui.QPalette.Text, palette, QtGui.QPalette.Inactive)
        self.set_brush(255, 255, 255,QtGui.QPalette.BrightText, palette, QtGui.QPalette.Inactive)
        self.set_brush(0, 0, 0,QtGui.QPalette.ButtonText, palette, QtGui.QPalette.Inactive)
        self.set_brush(255, 255, 255,QtGui.QPalette.Base, palette, QtGui.QPalette.Inactive)
        self.set_brush(227, 227, 227,QtGui.QPalette.Window, palette, QtGui.QPalette.Inactive)
        self.set_brush(0, 0, 0,QtGui.QPalette.Shadow, palette, QtGui.QPalette.Inactive)
        self.set_brush(241, 241, 241,QtGui.QPalette.AlternateBase, palette, QtGui.QPalette.Inactive)
        self.set_brush(255, 255, 220,QtGui.QPalette.ToolTipBase, palette, QtGui.QPalette.Inactive)
        self.set_brush(0, 0, 0,QtGui.QPalette.ToolTipText, palette, QtGui.QPalette.Inactive)
        self.set_brush(113, 113, 113,QtGui.QPalette.WindowText, palette, QtGui.QPalette.Disabled)
        self.set_brush(227, 227, 227,QtGui.QPalette.Button, palette, QtGui.QPalette.Disabled)
        self.set_brush(255, 255, 255,QtGui.QPalette.Light, palette, QtGui.QPalette.Disabled)
        self.set_brush(241, 241, 241,QtGui.QPalette.Midlight, palette, QtGui.QPalette.Disabled)
        self.set_brush(113, 113, 113,QtGui.QPalette.Dark, palette, QtGui.QPalette.Disabled)
        self.set_brush(151, 151, 151,QtGui.QPalette.Mid, palette, QtGui.QPalette.Disabled)
        self.set_brush(113, 113, 113,QtGui.QPalette.Text, palette, QtGui.QPalette.Disabled)
        self.set_brush(255, 255, 255,QtGui.QPalette.BrightText, palette, QtGui.QPalette.Disabled)
        self.set_brush(113, 113, 113,QtGui.QPalette.ButtonText, palette, QtGui.QPalette.Disabled)
        self.set_brush(227, 227, 227,QtGui.QPalette.Base, palette, QtGui.QPalette.Disabled)
        self.set_brush(227, 227, 227,QtGui.QPalette.Window, palette, QtGui.QPalette.Disabled)
        self.set_brush(0, 0, 0,QtGui.QPalette.Shadow, palette, QtGui.QPalette.Disabled)
        self.set_brush(227, 227, 227,QtGui.QPalette.AlternateBase, palette, QtGui.QPalette.Disabled)
        self.set_brush(255, 255, 220,QtGui.QPalette.ToolTipBase, palette, QtGui.QPalette.Disabled)
        self.set_brush(0, 0, 0,QtGui.QPalette.ToolTipText, palette, QtGui.QPalette.Disabled)
        MainWindow.setPalette(palette)
        MainWindow.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.centralWidget = QtGui.QWidget(MainWindow)
        self.reset_window(MainWindow)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.gridLayout_8 = QtGui.QGridLayout(self.centralWidget)
        self.gridLayout_8.setMargin(3)
        self.gridLayout_8.setSpacing(0)
        self.gridLayout_8.setObjectName(_fromUtf8("gridLayout_8"))
        self.splitter_3 = QtGui.QSplitter(self.centralWidget)
        self.create_splitter(QtCore.Qt.Horizontal, self.splitter_3, "splitter_3")
        self.splitter = QtGui.QSplitter(self.splitter_3)
        self.create_splitter(QtCore.Qt.Vertical, self.splitter, "splitter")
        self.read_iops_plot = pg.PlotWidget(self.splitter, axisItems={'left': y_axis_read_iops, 'bottom':x_ax_r_iops})
        self.setup_plot(self.read_iops_plot, "read_iops_plot")
        self.read_bw_plot = pg.PlotWidget(self.splitter, axisItems={'left': y_axis_read_bw, 'bottom':x_ax_r_bw})
        self.setup_plot(self.read_bw_plot, "read_bw_plot")
        self.read_lat_plot = pg.PlotWidget(self.splitter, axisItems={'left': y_axis_read_lat, 'bottom':x_ax_r_lat})
        self.setup_plot(self.read_lat_plot, "read_lat_plot")
        self.splitter_2 = QtGui.QSplitter(self.splitter_3)
        self.splitter_2.setAccessibleName(_fromUtf8(""))
        self.splitter_2.setLineWidth(0)
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setHandleWidth(4)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.write_iops_plot = pg.PlotWidget(self.splitter_2, axisItems={'left': y_axis_write_iops, 'bottom':x_ax_w_iops})
        self.setup_plot(self.write_iops_plot, "write_iops_plot")
        self.write_bw_plot = pg.PlotWidget(self.splitter_2, axisItems={'left': y_axis_write_bw, 'bottom':x_ax_w_bw})
        self.setup_plot(self.write_bw_plot, "write_bw_plot")
        self.write_lat_plot = pg.PlotWidget(self.splitter_2, axisItems={'left': y_axis_write_lat, 'bottom':x_ax_w_lat})
        self.setup_plot(self.write_lat_plot, "write_lat_plot")
        self.gridLayout_8.addWidget(self.splitter_3, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralWidget)
        self.dockWidget = QtGui.QDockWidget(MainWindow)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dockWidget.sizePolicy().hasHeightForWidth())
        self.dockWidget.setSizePolicy(sizePolicy)
        self.dockWidget.setMinimumSize(QtCore.QSize(180, 723))
        self.dockWidget.setMaximumSize(QtCore.QSize(180, 524287))
        self.dockWidget.setAccessibleName(_fromUtf8(""))
        self.dockWidget.setFloating(False)
        self.dockWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea)
        self.dockWidget.setWindowTitle(_fromUtf8("Settings"))
        self.dockWidget.setObjectName(_fromUtf8("dockWidget"))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout_6 = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout_6.setMargin(0)
        self.gridLayout_6.setSpacing(0)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.frame_10 = QtGui.QFrame(self.dockWidgetContents)
        self.set_size(self.frame_10)

        self.frame_10.setAccessibleName(_fromUtf8(""))
        self.frame_10.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame_10.setFrameShadow(QtGui.QFrame.Plain)
        self.frame_10.setObjectName(_fromUtf8("frame_10"))
        self.gridLayout_5 = QtGui.QGridLayout(self.frame_10)
        self.gridLayout_5.setMargin(2)
        self.gridLayout_5.setHorizontalSpacing(0)
        self.gridLayout_5.setVerticalSpacing(2)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.frame_11 = QtGui.QFrame(self.frame_10)
        self.set_size(self.frame_11)

        self.frame_11.setAccessibleName(_fromUtf8(""))
        self.frame_11.setFrameShape(QtGui.QFrame.WinPanel)
        self.frame_11.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_11.setObjectName(_fromUtf8("frame_11"))
        self.gridLayout_2 = QtGui.QGridLayout(self.frame_11)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.start_button = QtGui.QPushButton(self.frame_11)
        self.set_size(self.start_button)

        font = QtGui.QFont()
        font.setPointSize(9)
        self.start_button.setFont(font)
        self.start_button.setAccessibleName(_fromUtf8(""))
        self.start_button.setStyleSheet(_fromUtf8(""))
        self.start_button.setObjectName(_fromUtf8("start_button"))
        self.gridLayout_2.addWidget(self.start_button, 0, 0, 1, 1)
        self.stop_button = QtGui.QPushButton(self.frame_11)
        self.set_size(self.stop_button)
        self.start_button.setEnabled(False)

        font = QtGui.QFont()
        font.setPointSize(9)
        self.stop_button.setFont(font)
        self.stop_button.setAccessibleName(_fromUtf8(""))
        self.stop_button.setStyleSheet(_fromUtf8(""))
        self.stop_button.setObjectName(_fromUtf8("stop_button"))
        self.gridLayout_2.addWidget(self.stop_button, 1, 0, 1, 1)
        self.stop_button.setEnabled(False)
        self.frame = QtGui.QFrame(self.frame_10)
        self.set_size(self.frame)

        self.gridLayout_5.addWidget(self.frame_11, 2, 0, 1, 2)
        self.frame.setAccessibleName(_fromUtf8(""))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.gridLayout_7 = QtGui.QGridLayout(self.frame)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.label_8 = QtGui.QLabel(self.frame)
        self.set_size(self.label_8)

        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_8.setFont(font)
        self.label_8.setAccessibleName(_fromUtf8(""))
        self.label_8.setStyleSheet(_fromUtf8(""))
        self.label_8.setFrameShape(QtGui.QFrame.NoFrame)
        self.label_8.setFrameShadow(QtGui.QFrame.Plain)
        self.label_8.setLineWidth(-5)
        self.label_8.setScaledContents(False)
        self.label_8.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_8.setMargin(0)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout_7.addWidget(self.label_8, 0, 0, 1, 1)
        self.fio_jobfile_path = QtGui.QLineEdit(self.frame)
        self.set_size(self.fio_jobfile_path)

        self.fio_jobfile_path.setAccessibleName(_fromUtf8(""))
        self.fio_jobfile_path.setReadOnly(True)
        self.fio_jobfile_path.setObjectName(_fromUtf8("fio_jobfile_path"))
        self.gridLayout_7.addWidget(self.fio_jobfile_path, 1, 0, 1, 1)
        self.fio_jobfile_contents = QtGui.QPlainTextEdit(self.frame)
        self.set_size(self.fio_jobfile_contents)

        self.fio_jobfile_contents.setAccessibleName(_fromUtf8(""))
        self.fio_jobfile_contents.setUndoRedoEnabled(False)
        self.fio_jobfile_contents.setReadOnly(True)
        self.fio_jobfile_contents.setObjectName(_fromUtf8("fio_jobfile_contents"))
        self.gridLayout_7.addWidget(self.fio_jobfile_contents, 2, 0, 1, 2)

        self.browse_button = QtGui.QPushButton(self.frame)
        self.set_size(self.browse_button)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.browse_button.setFont(font)
        self.browse_button.setAccessibleName(_fromUtf8(""))
        self.browse_button.setStyleSheet(_fromUtf8(""))
        self.browse_button.setCheckable(True)
        self.browse_button.setChecked(False)
        self.browse_button.setAutoExclusive(False)
        self.browse_button.setObjectName(_fromUtf8("browse_button"))
        self.gridLayout_7.addWidget(self.browse_button, 1, 1, 1, 1)
        self.gridLayout_5.addWidget(self.frame, 0, 0, 1, 2)

        self.tabWidget = QtGui.QTabWidget(self.frame_10)
        self.set_size(self.tabWidget)
        self.tabWidget.setAccessibleName(_fromUtf8(""))
        self.tabWidget.setUsesScrollButtons(True)
        self.tabWidget.setDocumentMode(False)
        self.tabWidget.setTabsClosable(False)
        self.tabWidget.setMovable(False)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.gridLayout_11 = QtGui.QGridLayout(self.tab)
        self.gridLayout_11.setObjectName(_fromUtf8("gridLayout_11"))

        self.frame_4 = QtGui.QFrame(self.tab)
        self.set_size(self.frame_4)
        self.frame_4.setFrameShape(QtGui.QFrame.Box)
        self.frame_4.setFrameShadow(QtGui.QFrame.Plain)
        self.frame_4.setObjectName(_fromUtf8("frame_4"))
        self.gridLayout_12 = QtGui.QGridLayout(self.frame_4)
        self.gridLayout_12.setObjectName(_fromUtf8("gridLayout_12"))
        self.read_iops_checkbox = QtGui.QCheckBox(self.frame_4)
        self.set_size(self.read_iops_checkbox)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.read_iops_checkbox.setFont(font)
        self.read_iops_checkbox.setStyleSheet(_fromUtf8(""))
        self.read_iops_checkbox.setChecked(True)
        self.read_iops_checkbox.setAutoExclusive(False)
        self.read_iops_checkbox.setTristate(False)
        self.read_iops_checkbox.setObjectName(_fromUtf8("read_iops_checkbox"))
        self.gridLayout_12.addWidget(self.read_iops_checkbox, 0, 0, 2, 1)
        self.read_iops_total_checkbox = QtGui.QCheckBox(self.frame_4)
        self.set_size_pol(self.read_iops_total_checkbox, "read_iops_total_checkbox", True, (0, 1, 1, 1), self.gridLayout_12, self.frame_4)
        self.read_iops_threads_checkbox = QtGui.QCheckBox(self.frame_4)
        self.set_size_pol(self.read_iops_threads_checkbox, "read_iops_threads_checkbox", False, (1, 1, 1, 1), self.gridLayout_12, self.frame_4)
        self.gridLayout_11.addWidget(self.frame_4, 0, 0, 1, 1)
        self.frame_5 = QtGui.QFrame(self.tab)
        self.set_size(self.frame_5)
        self.frame_5.setFrameShape(QtGui.QFrame.Box)
        self.frame_5.setFrameShadow(QtGui.QFrame.Plain)
        self.frame_5.setObjectName(_fromUtf8("frame_5"))
        self.gridLayout_13 = QtGui.QGridLayout(self.frame_5)
        self.gridLayout_13.setObjectName(_fromUtf8("gridLayout_13"))
        self.read_bw_checkbox = QtGui.QCheckBox(self.frame_5)
        self.set_size_pol(self.read_bw_checkbox, "read_bw_checkbox", True, (0,0,2,1), self.gridLayout_13, self.frame_5)
        self.read_bw_total_checkbox = QtGui.QCheckBox(self.frame_5)
        self.set_size_pol(self.read_bw_total_checkbox, "read_bw_total_checkbox", True, (0,1,1,1), self.gridLayout_13, self.frame_5)
        self.read_bw_threads_checkbox = QtGui.QCheckBox(self.frame_5)
        self.set_size(self.read_bw_threads_checkbox)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.read_bw_threads_checkbox.setFont(font)
        self.read_bw_threads_checkbox.setStyleSheet(_fromUtf8(""))
        self.read_bw_threads_checkbox.setObjectName(_fromUtf8("read_bw_threads_checkbox"))
        self.gridLayout_13.addWidget(self.read_bw_threads_checkbox, 1, 1, 1, 1)
        self.gridLayout_11.addWidget(self.frame_5, 1, 0, 1, 1)
        self.frame_9 = QtGui.QFrame(self.tab)
        self.set_size(self.frame_9)
        self.frame_9.setFrameShape(QtGui.QFrame.Box)
        self.frame_9.setFrameShadow(QtGui.QFrame.Plain)
        self.frame_9.setObjectName(_fromUtf8("frame_9"))
        self.gridLayout_14 = QtGui.QGridLayout(self.frame_9)
        self.gridLayout_14.setObjectName(_fromUtf8("gridLayout_14"))
        self.read_lat_checkbox = QtGui.QCheckBox(self.frame_9)
        self.set_size_pol(self.read_lat_checkbox, "read_lat_checkbox", True, (0,0,2,1), self.gridLayout_14, self.frame_9)
        self.read_lat_max_checkbox = QtGui.QCheckBox(self.frame_9)
        self.set_size_pol(self.read_lat_max_checkbox, "read_lat_max_checkbox", True, (0,1,1,1), self.gridLayout_14, self.frame_9)
        self.read_lat_threads_checkbox = QtGui.QCheckBox(self.frame_9)
        self.set_size_pol(self.read_lat_threads_checkbox, "read_lat_threads_checkbox", False, (1,1,1,1), self.gridLayout_14, self.frame_9)
        self.gridLayout_11.addWidget(self.frame_9, 2, 0, 1, 1)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.gridLayout = QtGui.QGridLayout(self.tab_2)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.frame_6 = QtGui.QFrame(self.tab_2)

        self.set_size(self.frame_6)
        self.frame_6.setAccessibleName(_fromUtf8(""))
        self.frame_6.setFrameShape(QtGui.QFrame.Box)
        self.frame_6.setFrameShadow(QtGui.QFrame.Plain)
        self.frame_6.setObjectName(_fromUtf8("frame_6"))
        self.gridLayout_10 = QtGui.QGridLayout(self.frame_6)
        self.gridLayout_10.setObjectName(_fromUtf8("gridLayout_10"))
        self.write_iops_checkbox = QtGui.QCheckBox(self.frame_6)
        self.set_size_pol(self.write_iops_checkbox, "write_iops_checkbox", True, (0,0,2,1), self.gridLayout_10, self.frame_6)
        self.write_iops_total_checkbox = QtGui.QCheckBox(self.frame_6)
        self.set_size_pol(self.write_iops_total_checkbox, "write_iops_total_checkbox", True, (0,1,1,1), self.gridLayout_10, self.frame_6)
        self.write_iops_threads_checkbox = QtGui.QCheckBox(self.frame_6)
        self.set_size_pol(self.write_iops_threads_checkbox, "write_iops_threads_checkbox", False, (1,1,1,1), self.gridLayout_10, self.frame_6)
        self.gridLayout.addWidget(self.frame_6, 0, 0, 1, 1)
        self.frame_7 = QtGui.QFrame(self.tab_2)

        self.set_size(self.frame_7)
        self.frame_7.setAccessibleName(_fromUtf8(""))
        self.frame_7.setFrameShape(QtGui.QFrame.Box)
        self.frame_7.setFrameShadow(QtGui.QFrame.Plain)
        self.frame_7.setObjectName(_fromUtf8("frame_7"))
        self.gridLayout_9 = QtGui.QGridLayout(self.frame_7)
        self.gridLayout_9.setObjectName(_fromUtf8("gridLayout_9"))
        self.write_bw_checkbox = QtGui.QCheckBox(self.frame_7)
        self.set_size_pol(self.write_bw_checkbox, "write_bw_checkbox", True, (0,0,2,1), self.gridLayout_9, self.frame_7)
        self.write_bw_total_checkbox = QtGui.QCheckBox(self.frame_7)
        self.set_size_pol(self.write_bw_total_checkbox, "write_bw_total_checkbox", True, (0,1,1,1), self.gridLayout_9, self.frame_7)
        self.write_bw_threads_checkbox = QtGui.QCheckBox(self.frame_7)
        self.set_size_pol(self.write_bw_threads_checkbox, "write_bw_threads_checkbox", False, (1,1,1,1), self.gridLayout_9, self.frame_7)
        self.gridLayout.addWidget(self.frame_7, 1, 0, 1, 1)
        self.frame_8 = QtGui.QFrame(self.tab_2)

        self.set_size(self.frame_8)
        self.frame_8.setAccessibleName(_fromUtf8(""))
        self.frame_8.setFrameShape(QtGui.QFrame.Box)
        self.frame_8.setFrameShadow(QtGui.QFrame.Plain)
        self.frame_8.setObjectName(_fromUtf8("frame_8"))
        self.gridLayout_4 = QtGui.QGridLayout(self.frame_8)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.write_lat_checkbox = QtGui.QCheckBox(self.frame_8)
        self.set_size_pol(self.write_lat_checkbox, "write_lat_checkbox", True, (0,0,2,1), self.gridLayout_4, self.frame_8)
        self.write_lat_max_checkbox = QtGui.QCheckBox(self.frame_8)
        self.set_size_pol(self.write_lat_max_checkbox, "write_lat_max_checkbox", True, (0, 1, 1, 1), self.gridLayout_4, self.frame_8)
        self.write_lat_threads_checkbox = QtGui.QCheckBox(self.frame_8)
        self.set_size_pol(self.write_lat_threads_checkbox, "write_lat_threads_checkbox", False, (1,1,1,1), self.gridLayout_4, self.frame_8)
        self.gridLayout.addWidget(self.frame_8, 2, 0, 1, 1)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.gridLayout_5.addWidget(self.tabWidget, 1, 0, 1, 2)
        self.gridLayout_6.addWidget(self.frame_10, 0, 0, 1, 1)
        self.dockWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockWidget)
        self.actionSettings = QtGui.QAction(MainWindow)
        self.actionSettings.setObjectName(_fromUtf8("actionSettings"))
        self.actionPlot_Area = QtGui.QAction(MainWindow)
        self.actionPlot_Area.setObjectName(_fromUtf8("actionPlot_Area"))
        self.browse_button.clicked.connect(self.select_jobfile)
        plots = [self.read_iops_plot, self.write_iops_plot, self.read_bw_plot, self.write_bw_plot, self.read_lat_plot, self.write_lat_plot]
        for plot in plots:
            plot.setLimits(yMin=0, xMin=0)
            plot.showGrid(x=True, y=True, alpha=0.2)
        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def set_size(self, widget):
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(widget.sizePolicy().hasHeightForWidth())
        widget.setSizePolicy(sizePolicy)
        widget.setMinimumSize(QtCore.QSize(0, 0))

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "FIO visualizing tool", None))
        self.start_button.setText(_translate("MainWindow", "START", None))
        self.stop_button.setText(_translate("MainWindow", "STOP", None))
        self.label_8.setText(_translate("MainWindow", "Jobfile:", None))
        self.browse_button.setText(_translate("MainWindow", "Browse", None))
        self.set_check_text(self.read_iops_checkbox, self.read_iops_total_checkbox, self.read_iops_threads_checkbox, self.read_bw_checkbox, self.read_bw_total_checkbox, self.read_bw_threads_checkbox, self.read_lat_checkbox, self.read_lat_max_checkbox, self.read_lat_threads_checkbox)
        self.set_check_text(self.write_iops_checkbox, self.write_iops_total_checkbox, self.write_iops_threads_checkbox, self.write_bw_checkbox, self.write_bw_total_checkbox, self.write_bw_threads_checkbox, self.write_lat_checkbox, self.write_lat_max_checkbox, self.write_lat_threads_checkbox)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Read", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Write", None))
        self.actionSettings.setText(_translate("MainWindow", "Settings", None))
        self.actionPlot_Area.setText(_translate("MainWindow", "Plot Area", None))

    def set_size_pol(self, checkbox, name, checked, coord, grid, frame):
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(checkbox.sizePolicy().hasHeightForWidth())
        checkbox.setSizePolicy(sizePolicy)
        checkbox.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(9)
        checkbox.setFont(font)
        checkbox.setAccessibleName(_fromUtf8(""))
        checkbox.setStyleSheet(_fromUtf8(""))
        checkbox.setChecked(checked)
        checkbox.setObjectName(_fromUtf8(name))
        grid.addWidget(checkbox, coord[0], coord[1], coord[2], coord[3])

    def checkbox_handler(self, plot, total_checkbox, thread_checkbox, unit_checkbox):
        checked = unit_checkbox.isChecked()
        thread_checkbox.setEnabled(checked)
        total_checkbox.setEnabled(checked)
        if checked:
            plot.show()
        else:
            plot.hide()

    def set_brush(self, r,g,b,widget,palette,status):
        brush = QtGui.QBrush(QtGui.QColor(r, g, b))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(status, widget, brush)

    def setup_plot(self, plot, name):
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(plot.sizePolicy().hasHeightForWidth())
        plot.setSizePolicy(sizePolicy)
        plot.setMinimumSize(QtCore.QSize(0, 0))
        plot.setMaximumSize(QtCore.QSize(16777215, 16777215))
        plot.setBaseSize(QtCore.QSize(0, 0))
        plot.setAccessibleName(_fromUtf8(""))
        plot.setInteractive(True)
        plot.setObjectName(_fromUtf8(name))

    def set_y_ax(self, y_ax, label):
        y_ax.setLabel(label)
        y_ax.setStyle(autoExpandTextSpace=False)


    def set_check_text(self, iops, iops_tot, iops_threads, bw, bw_tot, bw_threads, lat, lat_max, lat_threads):
        iops.setText(_translate("MainWindow", "IOPS", None))
        iops_tot.setText(_translate("MainWindow", "Total", None))
        iops_threads.setText(_translate("MainWindow", "Threads", None))
        bw.setText(_translate("MainWindow", "BW", None))
        bw_tot.setText(_translate("MainWindow", "Total", None))
        bw_threads.setText(_translate("MainWindow", "Threads", None))
        lat.setText(_translate("MainWindow", "LAT", None))
        lat_max.setText(_translate("MainWindow", "Peak\n(max of\nclat_max)", None))
        lat_threads.setText(_translate("MainWindow", "Threads clat_avg", None))

def init_fio():
    global parsing_thread, fio_process, timer
    numjobs = realtime_back.get_jobs(str(ui.fio_jobfile_path.text()))
    read_iops_data = {
            'type':'r_iops',
            'all':[],
            'job_vals':[[] for i in itertools.repeat(None, numjobs)],
            'plot':ui.read_iops_plot,
            'checkb':ui.read_iops_checkbox,
            'thread_check':ui.read_iops_threads_checkbox,
            'total_check':ui.read_iops_total_checkbox,
            'colors':['#00aeef']
            }
    read_bw_data = {
            'type': 'r_bw',
            'all':[],
            'job_vals':[[] for i in itertools.repeat(None, numjobs)],
            'plot':ui.read_bw_plot,
            'checkb':ui.read_bw_checkbox,
            'thread_check':ui.read_bw_threads_checkbox,
            'total_check':ui.read_bw_total_checkbox,
            'colors':['#fd9613']
            }
    read_lat_data = {
            'type': 'r_lat',
            'all':[],
            'job_vals':[[] for i in itertools.repeat(None, numjobs)],
            'plot':ui.read_lat_plot,
            'checkb':ui.read_lat_checkbox,
            'thread_check':ui.read_lat_threads_checkbox,
            'total_check':ui.read_lat_max_checkbox,
            'colors':['#004280']
            }
    write_iops_data = {
            'type':'w_iops',
            'all':[],
            'job_vals':[[] for i in itertools.repeat(None, numjobs)],
            'plot':ui.write_iops_plot,
            'checkb':ui.write_iops_checkbox,
            'thread_check':ui.write_iops_threads_checkbox,
            'total_check':ui.write_iops_total_checkbox,
            'colors':['#00aeef']
            }
    write_bw_data = {
            'type': 'w_bw',
            'all':[],
            'job_vals':[[] for i in itertools.repeat(None, numjobs)],
            'plot':ui.write_bw_plot,
            'checkb':ui.write_bw_checkbox,
            'thread_check':ui.write_bw_threads_checkbox,
            'total_check':ui.write_bw_total_checkbox,
            'colors':['#fd9613']
            }
    write_lat_data = {
            'type': 'w_lat',
            'all':[],
            'job_vals':[[] for i in itertools.repeat(None, numjobs)],
            'plot':ui.write_lat_plot,
            'checkb':ui.write_lat_checkbox,
            'thread_check':ui.write_lat_threads_checkbox,
            'total_check':ui.write_lat_max_checkbox,
            'colors':['#004280']
            }

    fio_all_data = [read_iops_data, read_bw_data, read_lat_data, write_iops_data, write_bw_data, write_lat_data]
    for entry in fio_all_data:
        entry['colors'] = gen_colors(entry['colors'][0], numjobs)
    exit_code = [None]
    parsing_thread, fio_process = realtime_back.start_fio(str(ui.fio_jobfile_path.text()), fio_all_data, exit_code)
    parsing_thread.start()
    timer = QtCore.QTimer()
    timer.timeout.connect(lambda: update(fio_all_data, parsing_thread, exit_code[0], timer))
    timer.start(1000)
    ui.stop_button.setEnabled(True)
    ui.start_button.setEnabled(False)

def gen_colors(base_color, numjobs):
    colors = []
    grad_weight = int(64000/numjobs)
    for i in range(0, numjobs):
        colors.append(format(int(base_color[1:], 16) + (i * grad_weight), '06X'))
    return colors

def kill_fio():
    os.killpg(fio_process.pid, signal.SIGTERM)
    fio_process_output, fio_process_error = fio_process.communicate()
    ui.start_button.setEnabled(True)
    ui.stop_button.setEnabled(False)

def is_lat(entry):
    dtype = entry['type']
    return (dtype == 'w_lat' or dtype == 'r_lat')

def update(fio_data, parsing_thread, exit_code, timer):
    if parsing_thread.isAlive():
        for entry in fio_data:
            if entry['checkb'].isChecked():
                entry['plot'].clear()
                if entry['thread_check'].isChecked():
                    for i in range(0, len(entry['job_vals'])):
                        entry['plot'].plot(pen=entry['colors'][i]).setData(entry['job_vals'][i])

                if entry['total_check'].isChecked():
                    entry['plot'].plot(pen=entry['colors'][0]).setData(entry['all'])

    else:
        timer.stop()
        msg = QtGui.QMessageBox()
        if exit_code==0:
            msg.about(msg, 'Informational', 'FIO succefully finished with exit code: '+str(exit_code))
        elif exit_code==128:
            msg.about(msg, 'Informational', 'FIO was terminated by user, exit code: '+str(exit_code))
        else:
            fio_process_output, fio_process_error = fio_process.communicate()
            msg.about(msg, 'Informational', 'FIO was terminated with exit code: '+str(exit_code)+'\n\nSTDERR :'+str(fio_process_error))

application = QtGui.QApplication([])
pg.setConfigOptions(antialias=True)
pg.setConfigOptions(foreground='k')
pg.setConfigOptions(background=(227, 227, 227))
window = QtGui.QMainWindow()
ui = uiMainWindow()
ui.setup_ui(window)
window.show()
ui.read_iops_checkbox.stateChanged.connect(lambda: ui.checkbox_handler(ui.read_iops_plot, ui.read_iops_total_checkbox, ui.read_iops_threads_checkbox, ui.read_iops_checkbox))
ui.write_iops_checkbox.stateChanged.connect(lambda: ui.checkbox_handler(ui.write_iops_plot, ui.write_iops_total_checkbox, ui.write_iops_threads_checkbox, ui.write_iops_checkbox))
ui.read_bw_checkbox.stateChanged.connect(lambda: ui.checkbox_handler(ui.read_bw_plot, ui.read_bw_total_checkbox, ui.read_bw_threads_checkbox, ui.read_bw_checkbox))
ui.write_bw_checkbox.stateChanged.connect(lambda: ui.checkbox_handler(ui.write_bw_plot, ui.write_bw_total_checkbox, ui.write_bw_threads_checkbox, ui.write_bw_checkbox))
ui.read_lat_checkbox.stateChanged.connect(lambda: ui.checkbox_handler(ui.read_lat_plot, ui.read_lat_max_checkbox, ui.read_lat_threads_checkbox, ui.read_lat_checkbox))
ui.write_lat_checkbox.stateChanged.connect(lambda: ui.checkbox_handler(ui.write_lat_plot, ui.write_lat_max_checkbox, ui.write_lat_threads_checkbox, ui.write_lat_checkbox))
ui.start_button.clicked.connect(init_fio)
ui.stop_button.clicked.connect(kill_fio)
QtGui.QApplication.instance().exec_()

def main(argv=None):
    if argv is None:
        argv = sys.argv
if __name__ == "__main__":
    sys.exit(main())

