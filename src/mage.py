"""The defintion for the IMage application window.

This module contains the defintion of the Application window using PyQt5.
"""
from PyQt5.QtWidgets import (
    QMainWindow,
    QSizeGrip,
    QLabel,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
)
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPoint, QSize, QMimeData, pyqtSignal
from PyQt5.QtGui import QDrag, QPixmap

from image import ImageView
from hist import HistogramWidget
from zoom import ZoomWidget


class DragButton(QPushButton):
    def __init__(self, attached_widget, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Attach an uninstantiated widget to this button
        self.attached_widget = attached_widget

        self.widget_kwargs = None

        # Attach the parent widget
        self.parent = parent

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)

            # Instantiate the attached widget if it isn't yet
            if isinstance(self.attached_widget, type):
                self.attached_widget = self.attached_widget(
                    **self.widget_kwargs
                )

            pixmap = QPixmap(
                QSize(
                    self.attached_widget.width(), self.attached_widget.height()
                )
            )
            self.attached_widget.render(pixmap)
            drag.setPixmap(pixmap)

            drag.exec_(Qt.MoveAction)


class DragWidget(QFrame):
    """
    Generic list sorting handler.

    Credit: https://www.pythonguis.com/faq/pyqt-drag-drop-widgets/
    """

    orderChanged = pyqtSignal(list)
    histChanged = pyqtSignal(float, float)

    def __init__(self, *args, orientation=Qt.Orientation.Vertical, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)

        # Store the orientation for drag checks later.
        self.orientation = orientation

        if self.orientation == Qt.Orientation.Vertical:
            self.blayout = QVBoxLayout()
        else:
            self.blayout = QHBoxLayout()

        # Load the window style sheet
        with open("src/styles/window.qss", "r") as file:
            style_sheet = file.read()

        self.setStyleSheet(style_sheet)

        self.setLayout(self.blayout)

        # Set font
        font = QtGui.QFont()
        font.setFamily("Hack Nerd Font Mono")
        font.setPointSize(8)
        self.setFont(font)

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        pos = e.pos()
        widget = e.source().attached_widget

        widget.setWidth = self.width()

        # If the layout is empty just add the widget
        if self.blayout.count() == 0:
            self.blayout.insertWidget(0, widget)

        else:
            for n in range(self.blayout.count()):
                # Get the widget at each index in turn.
                w = self.blayout.itemAt(n).widget()
                if self.orientation == Qt.Orientation.Vertical:
                    # Drag drop vertically.
                    drop_here = pos.y() < w.y() + w.size().height() // 2
                else:
                    # Drag drop horizontally.
                    drop_here = pos.x() < w.x() + w.size().width() // 2

                if drop_here:
                    # We didn't drag past this widget.
                    # insert to the left of it.
                    self.blayout.insertWidget(n - 1, widget)
                    # self.orderChanged.emit(self.get_item_data())
                    break

        # Connect any signals we need
        if isinstance(widget, HistogramWidget):
            widget.histChanged.connect(self.handleHistogramChange)

        e.accept()

    def add_item(self, item):
        self.blayout.addWidget(item)

    def get_item_data(self):
        data = []
        for n in range(self.blayout.count()):
            # Get the widget at each index in turn.
            w = self.blayout.itemAt(n).widget()
            data.append(w.data)
        return data

    def handleHistogramChange(self, low, high):
        # Emit a new signal with the captured values
        self.histChanged.emit(low, high)


class ImageMageMainWindow(QMainWindow):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 700)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setupMainWindowStyles(MainWindow)
        self.setupCentralWidget(MainWindow)
        self.setupImageDisplay(MainWindow)
        self.setupKnobs(MainWindow)
        self.setupButtonBar(MainWindow)
        self.setupTabs(MainWindow)
        self.setupMenuBar(MainWindow)

        self.setMouseTracking(True)

        self.retranslateUi(MainWindow)
        self.Tabs.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Create a QSizeGrip to the bottom-right corner for resizing
        self.size_grip = QSizeGrip(self.centralwidget)
        self.size_grip.setGeometry(
            self.centralwidget.width() - 16,
            self.centralwidget.height() - 16,
            16,
            16,
        )

        # Variables for moving and resizing
        self.mouse_pressed = False
        self.resizing = False
        self.old_pos = QPoint()

    def _size_relative_to_main_window(self, x, y, width, height):
        wheight = self.centralwidget.height()
        wwidth = self.centralwidget.width()

        return (
            int(x * wwidth),
            int(y * wheight),
            int(width * wwidth),
            int(height * wheight),
        )

    def _size_relative_to_main_window_squ(self, x, y, width):
        wheight = self.centralwidget.height()
        wwidth = self.centralwidget.width()

        return (
            int(x * wwidth),
            int(y * wheight),
            int(width * wwidth),
            int(width * wwidth),
        )

    def setupMainWindowStyles(self, MainWindow):
        MainWindow.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Load the window style sheet
        with open("src/styles/window.qss", "r") as file:
            style_sheet = file.read()

        MainWindow.setStyleSheet(style_sheet)

        font = QtGui.QFont()
        font.setFamily("Hack Nerd Font Mono")
        font.setPointSize(15)
        MainWindow.setFont(font)

    def setupCentralWidget(self, MainWindow):
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(
            self.centralwidget.sizePolicy().hasHeightForWidth()
        )
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.resize(MainWindow.size())
        font = QtGui.QFont()
        font.setFamily("Hack Nerd Font Mono")
        font.setPointSize(15)
        font.setBold(False)
        font.setWeight(50)
        self.centralwidget.setFont(font)

        self.centralwidget.setFocusPolicy(QtCore.Qt.NoFocus)
        self.centralwidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.centralwidget.setAutoFillBackground(False)

        # Load the button style sheet
        with open("src/styles/window.qss", "r") as file:
            style_sheet = file.read()

        self.centralwidget.setStyleSheet(style_sheet)

        self.centralwidget.setObjectName("centralwidget")

    def setupImageDisplay(self, MainWindow):
        self.ImageDisplay = ImageView(self.centralwidget)
        self.ImageDisplay.setGeometry(
            QtCore.QRect(
                *self._size_relative_to_main_window_squ(0.03, 0.1, 0.55)
            )
        )
        self.ImageDisplay.setObjectName("ImageDisplay")

        # Set alignment to center
        self.ImageDisplay.setAlignment(QtCore.Qt.AlignCenter)

    def setupKnobs(self, MainWindow):
        self.Knobs = DragWidget(self.centralwidget)
        self.Knobs.setGeometry(
            QtCore.QRect(
                *self._size_relative_to_main_window(0.61, 0.1, 0.36, 0.84)
            )
        )
        self.Knobs.setObjectName("Knobs")

        # Connect any signals
        self.Knobs.histChanged.connect(self.ImageDisplay.update_vlims)

    def setupButtonBar(self, MainWindow):
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget_2.setGeometry(
            QtCore.QRect(
                *self._size_relative_to_main_window(0.03, 0.01, 0.96, 0.06)
            )
        )
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.ButtonBar = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.ButtonBar.setContentsMargins(0, 0, 0, 0)
        self.ButtonBar.setObjectName("ButtonBar")

        font = QtGui.QFont()
        font.setFamily("Hack Nerd Font Mono")
        font.setPointSize(15)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        font.setKerning(True)

        # Load the button style sheet
        with open("src/styles/button.qss", "r") as file:
            style_sheet = file.read()

        self.ZoomView = DragButton(
            ZoomWidget,
            self,
            self.horizontalLayoutWidget_2,
        )
        self.ZoomView.setFont(font)
        self.ZoomView.setObjectName("Zoom View")
        self.ZoomView.setStyleSheet(style_sheet)
        self.ZoomView.widget_kwargs = {
            "main_view": self.ImageDisplay,
            "parent": None,
        }
        self.ButtonBar.addWidget(self.ZoomView)

        self.Histogram = DragButton(
            HistogramWidget,
            self,
            self.horizontalLayoutWidget_2,
        )
        self.Histogram.setFont(font)
        self.Histogram.setObjectName("Histogram")
        self.Histogram.setStyleSheet(style_sheet)
        self.ButtonBar.addWidget(self.Histogram)

        self.Scaling = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Hack Nerd Font Mono")
        font.setPointSize(15)
        self.Scaling.setFont(font)
        self.Scaling.setObjectName("Scaling")
        self.Scaling.setStyleSheet(style_sheet)
        self.ButtonBar.addWidget(self.Scaling)

        self.Code = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Hack Nerd Font Mono")
        font.setPointSize(15)
        self.Code.setFont(font)
        self.Code.setObjectName("Code")
        self.Code.setStyleSheet(style_sheet)
        self.ButtonBar.addWidget(self.Code)

    def setupTabs(self, MainWindow):
        self.Tabs = QtWidgets.QTabWidget(self.centralwidget)
        self.Tabs.setGeometry(
            QtCore.QRect(
                *self._size_relative_to_main_window(0.03, 0.94, 0.96, 0.06)
            )
        )
        font = QtGui.QFont()
        font.setFamily("Hack Nerd Font Mono")
        self.Tabs.setFont(font)
        self.Tabs.setStyleSheet("")
        self.Tabs.setObjectName("Tabs")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.Tabs.addTab(self.tab, "")

    def setupMenuBar(self, MainWindow):
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 900, 37))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(
            self.menubar.sizePolicy().hasHeightForWidth()
        )
        self.menubar.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Hack Nerd Font Mono")
        self.menubar.setFont(font)
        self.menubar.setAcceptDrops(True)
        self.menubar.setAutoFillBackground(True)
        self.menubar.setStyleSheet("")
        self.menubar.setDefaultUp(False)
        self.menubar.setNativeMenuBar(True)
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setGeometry(QtCore.QRect(388, 333, 134, 42))
        font = QtGui.QFont()
        font.setFamily("Hack Nerd Font Mono")
        self.menuFile.setFont(font)
        self.menuFile.setAutoFillBackground(False)
        self.menuFile.setStyleSheet("")
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.Tabs.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Enable opening of image files
        open_action = QtWidgets.QAction("Open", self)
        open_action.triggered.connect(self.open_image)
        open_action.setShortcut(QtGui.QKeySequence("Ctrl+O"))
        self.menuFile.addAction(open_action)

        # Add a separator
        self.menuFile.addSeparator()

        # Add a "Close" action to the menu
        close_action = QtWidgets.QAction("Close", self)
        close_action.triggered.connect(self.close)
        self.menuFile.addAction(close_action)

    def dragEnterEvent(self, e):
        e.accept()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "IMage"))
        self.ZoomView.setText(_translate("MainWindow", "Zoom View"))
        self.Histogram.setText(_translate("MainWindow", "Histogram"))
        self.Scaling.setText(_translate("MainWindow", "Scaling"))
        self.Code.setText(_translate("MainWindow", "Code"))
        self.Tabs.setTabText(
            self.Tabs.indexOf(self.tab), _translate("MainWindow", "Tab 1")
        )
        self.menuFile.setTitle(_translate("MainWindow", "File"))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

            # Check if the cursor is near the edges for resizing
            rect = self.rect()
            if (
                event.x() < rect.left() + 5
                or event.x() > rect.right() - 5
                or event.y() < rect.top() + 5
                or event.y() > rect.bottom() - 5
            ):
                self.resizing = True
            else:
                self.mouse_pressed = True

    def mouseMoveEvent(self, event):
        if self.mouse_pressed or self.resizing:
            delta = event.globalPos() - self.old_pos

            # Check if it's a move or resize
            if self.mouse_pressed:
                self.move(self.pos() + delta)
            elif self.resizing:
                new_size = self.size() + QSize(delta.x(), delta.y())
                self.resize(new_size)

            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = False
            self.resizing = False

    def event(self, event):
        if event.type() == QtCore.QEvent.HoverMove:
            rect = self.rect()
            if (
                event.pos().x() < rect.left() + 5
                or event.pos().x() > rect.right() - 5
                or event.pos().y() < rect.top() + 5
                or event.pos().y() > rect.bottom() - 5
            ):
                self.setCursor(Qt.SizeAllCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
        return super().event(event)


class ImageMage(ImageMageMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.img = None

    def open_image(self):
        options = QtWidgets.QFileDialog.Options()
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff);;HDF5 Files "
            "(*.hdf5 *.h5);;Fits Files (*.fits);;All Files (*)",
            options=options,
        )

        # Handle the different possible formats
        if filepath:
            match filepath.split(".")[-1]:
                case "png":
                    self.ImageDisplay.open_image(filepath)
                case "jpg":
                    self.ImageDisplay.open_image(filepath)
                case "jpeg":
                    self.ImageDisplay.open_image(filepath)
                case "bmp":
                    self.ImageDisplay.open_image(filepath)
                case "tiff":
                    self.ImageDisplay.open_image(filepath)
                case "hdf5":
                    pass
                case "h5":
                    pass
                case "fits":
                    pass
                case _:
                    pass

        # Attach the image to the widgets that need it
        self.Histogram.widget_kwargs = {"img_data": self.ImageDisplay.img_arr}
