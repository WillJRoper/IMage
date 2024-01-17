from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QSlider,
    QGraphicsRectItem,
)
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt


class ZoomWidget(QWidget):
    def __init__(self, main_view, parent=None):
        super(ZoomWidget, self).__init__(parent)

        self.main_view = main_view

        # Create an overview QGraphicsView
        self.overview_view = QGraphicsView(self)
        self.overview_view.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.overview_view.setRenderHint(
            QtGui.QPainter.SmoothPixmapTransform, True
        )
        self.overview_scene = QGraphicsScene(self)
        self.overview_view.setScene(self.overview_scene)
        self.overview_item = QGraphicsPixmapItem()
        self.overview_scene.addItem(self.overview_item)

        # Create an overlay box for the currently visible area
        self.overlay_box = QGraphicsRectItem()
        self.overlay_box.setPen(
            QtGui.QPen(QtGui.QColor(255, 0, 0), 2, Qt.SolidLine)
        )
        self.overview_scene.addItem(self.overlay_box)

        # Vertical slider for zooming the main view
        self.zoom_slider = QSlider(Qt.Vertical)
        self.zoom_slider.setMinimum(0)
        self.zoom_slider.setMaximum(200)  # Adjust the maximum as needed
        self.zoom_slider.setValue(100)  # Initial zoom level
        self.zoom_slider.valueChanged.connect(self.update_main_view_zoom)

        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.overview_view)
        layout.addWidget(self.zoom_slider)

        self.setLayout(layout)

        self.set_image()

        # Connect signals
        self.main_view.sceneRectChanged.connect(self.update_overlay_box)
        self.main_view.transformChanged.connect(self.update_main_view_zoom)
        self.update_main_view_zoom()

        # Connect the wheel_event_signal from ImageView to the update_slider slot
        main_view.zoomChanged.connect(self.update_slider)

    def set_image(self):
        # Set up the overview image (low resolution)
        pil_img = self.main_view.pil_img
        overview_img = pil_img.copy()
        overview_img.thumbnail((100, 100))  # Adjust the size as needed
        overview_pixmap = QPixmap.fromImage(self._pil_to_qimage(overview_img))
        self.overview_item.setPixmap(overview_pixmap)

    def _pil_to_qimage(self, pil_image):
        image_byte_array = pil_image.tobytes()
        q_image = QImage(
            image_byte_array,
            pil_image.width,
            pil_image.height,
            QImage.Format_Grayscale8,
        )
        return q_image

    def update_main_view_zoom(self):
        # Update the zoom level in the main view based on the slider value
        zoom_factor = self.zoom_slider.value() / 100.0
        self.main_view.scale(zoom_factor, zoom_factor)

    def update_overlay_box(self):
        # Update the position and size of the overlay box based on the visible area in the main view
        visible_rect = self.main_view.mapToScene(
            self.main_view.viewport().rect()
        ).boundingRect()
        self.overlay_box.setRect(visible_rect)

    def update_slider(self, event):
        # Update the zoom level slider based on the wheel event
        delta = event.angleDelta().y()
        current_value = self.zoom_slider.value()
        new_value = current_value + delta / 120  # Adjust as needed
        self.zoom_slider.setValue(int(new_value))
