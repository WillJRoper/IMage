"""
"""
import numpy as np
from PIL import Image

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QGraphicsView, QGraphicsPixmapItem, QGraphicsScene
from PyQt5.QtGui import QPixmap, QImage, QWheelEvent
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal


class ImageView(QGraphicsView):
    """
    A custom QGraphicsView widget for displaying images.

    Attributes:
    """

    sceneRectChanged = pyqtSignal()
    transformChanged = pyqtSignal()
    zoomChanged = pyqtSignal(QWheelEvent)
    imgOpened = pyqtSignal(np.ndarray)

    def __init__(self, parent):
        """
        Initializes the ImageView widget.

        Args:
            parent (QWidget): The parent widget.
        """

        super().__init__(parent)

        self.resize(300, 300)
        self.setMinimumSize(300, 300)

        # Set up the image
        self.pil_img = None
        self.img_arr = None

        # Image dimensions
        self._width = None
        self._height = None
        self._depth = None

        self.vmin = None
        self.vmax = None

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.image_item = None

        self.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

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
                    self._open_pil(filepath)
                case "jpg":
                    self._open_pil(filepath)
                case "jpeg":
                    self._open_pil(filepath)
                case "bmp":
                    self._open_pil(filepath)
                case "tiff":
                    self._open_pil(filepath)
                case "hdf5":
                    pass
                case "h5":
                    pass
                case "fits":
                    pass
                case _:
                    pass

        self._width = self.img_arr.shape[0]
        self._height = self.img_arr.shape[1]
        self._depth = (
            self.img_arr.shape[2] if len(self.img_arr.shape) > 2 else 1
        )

        self.update_vlims(self.img_arr.min(), self.img_arr.max())

        self.update_img()

        # Emit a signal to say the image has been opened!
        self.imgOpened.emit(self.img_arr)

    def _open_pil(self, filepath):
        """
        Opens the image file using PIL.

        Args:
            filepath (str): The path to the image file.

        Returns:
            PIL.Image: The PIL image object.
        """
        # Set up the image
        self.pil_img = Image.open(filepath).convert("L")
        self.img_arr = np.array(self.pil_img, dtype=np.uint8)

    def update_vlims(self, vmin, vmax):
        self.vmin = vmin
        self.vmax = vmax
        self.update_img()

    def get_image_dimensions(self):
        """
        Gets the dimensions of the currently displayed image.

        Returns:
            Tuple[int, int]: A tuple containing the width and height of the image.
        """
        return self.width, self.height

    def update_img(self):
        # Normalize the image data for display
        normalized_image = self.normalize_image(self.img_arr)

        # Convert the normalized NumPy array to a QImage
        height, width = normalized_image.shape
        bytes_per_channel = normalized_image.itemsize
        bytes_per_line = bytes_per_channel * width
        q_image = QImage(
            normalized_image.data,
            height,
            width,
            bytes_per_line,
            QImage.Format_Grayscale16
            if bytes_per_channel == 2
            else QImage.Format_Grayscale8,
        )

        # Find the non-white region
        bounding_rect = q_image.rect()

        # Crop the image to the non-white region
        q_image = q_image.copy(bounding_rect)

        # Create a QPixmap from the QImage and set it to the QLabel
        pixmap = QPixmap.fromImage(q_image)

        # Set the desired size for the pixmap relative to the container
        width = self.width()
        height = self.height()
        new_size = QtCore.QSize(int(width * 0.95), int(height * 0.95))
        pixmap = pixmap.scaled(new_size, QtCore.Qt.KeepAspectRatio)

        if self.image_item:
            self.scene.removeItem(self.image_item)

        self.image_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.image_item)

    def normalize_image(self, image_array):
        # Clip values to vmin and vmax
        image_array = np.clip(image_array, self.vmin, self.vmax)

        # Normalize image data to 8-bit range for display
        min_val = self.vmin
        max_val = self.vmax
        normalized_image = (
            (image_array - min_val) / (max_val - min_val) * 255
        ).astype(np.uint8)
        return normalized_image

    def wheelEvent(self, event):
        if self.image_item is None:
            return
        # Zoom in or out based on the wheel delta
        factor = 1.2
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor

        self.scale(factor, factor)

        self.transformChanged.emit()
        self.zoomChanged.emit(event)

    def mouseMoveEvent(self, event):
        if self.image_item is None:
            return
        # Panning with the mouse drag
        if event.buttons() == Qt.LeftButton:
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()

            delta /= self.transform().m11()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )

        super().mouseMoveEvent(event)

        self.sceneRectChanged.emit()

    def mousePressEvent(self, event):
        if self.image_item is None:
            return
        # Start tracking the position for panning
        if event.button() == Qt.LeftButton:
            self._pan_start = event.pos()

        super().mousePressEvent(event)

        self.sceneRectChanged.emit()

    def resizeEvent(self, event):
        if self.image_item is None:
            return
        # Update the view when the widget is resized
        super().resizeEvent(event)
        self.update_img()
