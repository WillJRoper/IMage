"""Definition of the HistogramWidget class.

This class is used to display and manipulate the histogram of an image.
"""
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
)

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QFrame
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal, QRect, Qt

from imagemage import styles_dir
from imagemage.widgets.range_slider import RangeSlider


class LabeledLineEdit(QWidget):
    # Custom signal
    textChanged = pyqtSignal(str)

    def __init__(self, label_text, parent=None):
        super().__init__(parent)

        self.label = QLabel(label_text)
        self.line_edit = QLineEdit()

        layout = QHBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)

        # Optional: Adjust layout spacing or margins as needed
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Connect the internal QLineEdit's textChanged signal to the custom signal
        self.line_edit.textChanged.connect(self.textChanged.emit)

    def text(self):
        return self.line_edit.text()

    def setText(self, text):
        self.line_edit.setText(text)

    def setLabelText(self, text):
        self.label.setText(text)


class HistogramWidget(QFrame):
    histChanged = pyqtSignal(float, float)

    def __init__(self, parent=None, preview=False):
        super().__init__(parent)

        # Set the geometry
        self.setMinimumSize(350, 200)

        # Set up histogram
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)

        # Set the facecolor to 'none' for a transparent background
        self.fig.patch.set_facecolor("none")
        self.fig.patch.set_alpha(0)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setEnabled(True)

        if not preview:
            # Store data specific to this images tab
            self.nbins = 50

            self.img_data = None

            self.img_min = self.img_data.min()
            self.img_max = self.img_data.max()
            self.img_range = self.img_data.max() - self.img_min

        else:
            # Here we set up the preview
            self.nbins = 50

            self.img_min = 0
            self.img_max = 100
            self.img_range = 100

            self.img_data = np.random.rand(100) * self.img_max

        self.setupUi()
        self.horizontalLayout.addWidget(self.canvas)
        self.update_hist()

    def _scale_relative_to_size(
        self,
        x_pcent,
        y_pcent,
        width_pcent,
        height_pcent,
    ):
        return QRect(
            int(x_pcent * self.width()),
            int(y_pcent * self.height()),
            int(width_pcent * self.width()),
            int(height_pcent * self.height()),
        )

    def setupUi(self):
        # Set up the main properties of HistogramWidget
        self.setObjectName("HistogramWidget")

        # Set size policy
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)

        # Horizontal layout for sliders and entries
        self.horizontalLayoutWidget = QtWidgets.QWidget(self)
        self.horizontalLayoutWidget.setGeometry(
            self._scale_relative_to_size(0.05, 0.01, 0.9, 0.55)
        )
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")

        # Horizontal layout setup
        self.horizontalLayout = QtWidgets.QHBoxLayout(
            self.horizontalLayoutWidget
        )
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # Slider for vmin
        self.slider = RangeSlider(self)
        self.slider.setGeometry(
            self._scale_relative_to_size(0.05, 0.58, 0.9, 0.2)
        )
        self.slider.setObjectName("slider")
        self.slider.setMinimum(self.img_min)
        self.slider.setLow(self.img_min)
        self.slider.setMaximum(self.img_max)
        self.slider.setHigh(self.img_max)
        self.slider.sliderMoved.connect(self.update_lims)

        # Radio buttons for log scale
        self.log_x = QtWidgets.QCheckBox(self)
        self.log_x.setGeometry(
            self._scale_relative_to_size(0.05, 0.8, 0.25, 0.18)
        )
        self.log_x.setObjectName("log_x")
        self.log_x.stateChanged.connect(self.update_hist)

        self.log_y = QtWidgets.QCheckBox(self)
        self.log_y.setGeometry(
            self._scale_relative_to_size(0.30, 0.8, 0.25, 0.18)
        )
        self.log_y.setObjectName("log_y")
        self.log_y.stateChanged.connect(self.update_hist)

        # Entry for the number of bins
        self.nbin_entry = LabeledLineEdit(label_text="bins:", parent=self)
        self.nbin_entry.setGeometry(
            self._scale_relative_to_size(0.6, 0.8, 0.35, 0.18)
        )
        self.nbin_entry.setText(str(self.nbins))
        self.nbin_entry.setObjectName("nbin_entry")
        self.nbin_entry.textChanged.connect(self.update_nbins)

        # Connect signals and slots
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        # Load the button style sheet
        with open(f"{styles_dir}hist.qss", "r") as file:
            style_sheet = file.read()

        self.setStyleSheet(style_sheet)

    def set_img_data(self, img_arr):
        # Store the image array
        self.img_data = img_arr
        self.img_min = self.img_data.min()
        self.img_max = self.img_data.max()
        self.img_range = self.img_data.max() - self.img_min

        tolerence = int(self.img_range / self.nbins)

        # Update the slider data
        self.slider.setMinimum(self.img_min - tolerence)
        self.slider.setLow(self.img_min)
        self.slider.setMaximum(self.img_max + tolerence)
        self.slider.setHigh(self.img_max)

        # And update the histogram to show it
        self.update_hist()

    def update_hist(self):
        # Clear the axes
        self.ax.clear()

        if self.log_x.isChecked():
            self.ax.set_xscale("log")
            bins = np.logspace(
                np.log10(self.slider.low()),
                np.log10(self.slider.high() + self.img_range / self.nbins),
                self.nbins + 1,
            )
        else:
            self.ax.set_xscale("linear")
            bins = np.linspace(
                self.slider.low(),
                self.slider.high() + self.img_range / self.nbins,
                self.nbins + 1,
            )

        if self.log_y.isChecked():
            self.ax.set_yscale("log")
        else:
            self.ax.set_yscale("linear")

        # Plot the histogram
        self.ax.hist(self.img_data.flatten(), bins=bins, alpha=0.7)

        # Set the facecolor of the axis to 'none' for a transparent background
        self.ax.patch.set_facecolor("none")
        self.ax.patch.set_alpha(0)

        self.ax.axis("off")

        self.ax.set_xlim(self.img_min, self.img_max)

        # Draw the canvas
        self.canvas.draw()

        # Signal that something happened
        self.histChanged.emit(self.slider.low(), self.slider.high())

    def update_nbins(self, text):
        try:
            self.nbins = int(text)
            self.update_hist()
        except ValueError:
            pass  # Handle the case where the input is not a valid integer

    def update_lims(self, low, high):
        self.slider.setLow(low)
        self.slider.setHigh(high)
        self.update_hist()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("HistogramWidget", "Form"))
        self.log_x.setText(_translate("HistogramWidget", "log(x)"))
        self.log_y.setText(_translate("HistogramWidget", "log(y)"))
