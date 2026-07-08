from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QAction, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from . import ops


class ImageCanvas(QLabel):
    def __init__(self):
        super().__init__("打开一张图片开始")
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(720, 520)
        self.setObjectName("canvas")
        self.image: np.ndarray | None = None
        self._pixmap = QPixmap()
        self._drag_start: QPoint | None = None
        self.selection = QRect()

    def set_image(self, img: np.ndarray):
        self.image = img
        h, w = img.shape[:2]
        fmt = QImage.Format_Grayscale8 if img.ndim == 2 else QImage.Format_RGB888
        qimg = QImage(img.data, w, h, img.strides[0], fmt).copy()
        self._pixmap = QPixmap.fromImage(qimg)
        self.selection = QRect()
        self._refresh()

    def selected_rect_on_image(self) -> tuple[int, int, int, int] | None:
        if self.image is None or self.selection.isNull() or self._pixmap.isNull():
            return None
        target = self._scaled_rect()
        sel = self.selection.normalized().intersected(target)
        if sel.isEmpty():
            return None
        sx = self.image.shape[1] / target.width()
        sy = self.image.shape[0] / target.height()
        return (
            int((sel.x() - target.x()) * sx),
            int((sel.y() - target.y()) * sy),
            max(1, int(sel.width() * sx)),
            max(1, int(sel.height() * sy)),
        )

    def _scaled_rect(self) -> QRect:
        scaled = self._pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        x = (self.width() - scaled.width()) // 2
        y = (self.height() - scaled.height()) // 2
        return QRect(x, y, scaled.width(), scaled.height())

    def _refresh(self):
        if self._pixmap.isNull():
            return
        scaled = self._pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        canvas = QPixmap(self.size())
        canvas.fill(Qt.transparent)
        painter = QPainter(canvas)
        painter.drawPixmap((self.width() - scaled.width()) // 2, (self.height() - scaled.height()) // 2, scaled)
        if not self.selection.isNull():
            painter.setPen(QPen(Qt.cyan, 2, Qt.DashLine))
            painter.drawRect(self.selection.normalized())
        painter.end()
        self.setPixmap(canvas)

    def resizeEvent(self, event):
        self._refresh()
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.image is not None:
            self._drag_start = event.position().toPoint()
            self.selection = QRect(self._drag_start, self._drag_start)
            self._refresh()

    def mouseMoveEvent(self, event):
        if self._drag_start is not None:
            self.selection = QRect(self._drag_start, event.position().toPoint())
            self._refresh()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start = None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vision Beautifier")
        self.resize(1180, 760)
        self.current: np.ndarray | None = None
        self.original: np.ndarray | None = None
        self.mask: np.ndarray | None = None

        self.canvas = ImageCanvas()
        self.status = QLabel("支持 BMP / JPG / PNG")
        self.status.setObjectName("status")

        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)
        layout.addWidget(self._tools(), 0)
        layout.addWidget(self.canvas, 1)
        self.setCentralWidget(root)
        self._menu()
        self._style()

    def _menu(self):
        file_menu = self.menuBar().addMenu("文件")
        for text, fn in [("打开", self.open_image), ("保存结果", self.save_image), ("恢复原图", self.restore)]:
            action = QAction(text, self)
            action.triggered.connect(fn)
            file_menu.addAction(action)

    def _tools(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("panel")
        box = QVBoxLayout(panel)
        box.setSpacing(10)
        box.addWidget(QLabel("图像美化系统", objectName="title"))
        box.addWidget(self.status)
        box.addLayout(self._row("打开图片", self.open_image, "保存结果", self.save_image))
        box.addLayout(self._row("恢复原图", self.restore, "灰度读取", self.open_gray))

        self.brightness = self._slider(-120, 120, 0)
        self.contrast = self._slider(20, 220, 100)
        self.hue = self._slider(-90, 90, 0)
        self.saturation = self._slider(0, 220, 100)
        box.addWidget(self._control("亮度", self.brightness))
        box.addWidget(self._control("对比度", self.contrast))
        box.addWidget(self._control("色相", self.hue))
        box.addWidget(self._control("饱和度", self.saturation))
        box.addWidget(self._button("应用增强", self.enhance))

        grid = QGridLayout()
        actions = [
            ("高斯噪声", lambda: self.apply(lambda x: ops.add_noise(x, "gaussian"))),
            ("椒盐噪声", lambda: self.apply(lambda x: ops.add_noise(x, "salt_pepper"))),
            ("均匀噪声", lambda: self.apply(lambda x: ops.add_noise(x, "uniform"))),
            ("均值滤波", lambda: self.apply(lambda x: ops.denoise(x, "mean"))),
            ("中值滤波", lambda: self.apply(lambda x: ops.denoise(x, "median"))),
            ("高斯滤波", lambda: self.apply(lambda x: ops.denoise(x, "gaussian"))),
            ("左旋 15°", lambda: self.apply(lambda x: ops.rotate(x, 15))),
            ("右旋 15°", lambda: self.apply(lambda x: ops.rotate(x, -15))),
            ("水平镜像", lambda: self.apply(lambda x: ops.flip(x, "horizontal"))),
            ("垂直镜像", lambda: self.apply(lambda x: ops.flip(x, "vertical"))),
            ("平移", lambda: self.apply(lambda x: ops.translate(x, 35, 25))),
            ("裁剪选区", self.crop_selection),
            ("锐化", lambda: self.apply(ops.sharpen)),
            ("描边", lambda: self.apply(ops.outline)),
            ("阈值分割", self.threshold_segment),
            ("框选分割", self.grabcut_segment),
            ("加边框", lambda: self.apply(ops.add_border)),
            ("雾化", lambda: self.apply(ops.fog)),
            ("浮雕", lambda: self.apply(ops.emboss)),
            ("艺术文字", lambda: self.apply(ops.add_text)),
            ("测量选区", self.measure_selection),
        ]
        for i, (text, fn) in enumerate(actions):
            grid.addWidget(self._button(text, fn), i // 2, i % 2)
        box.addLayout(grid)
        box.addStretch()
        return panel

    def _row(self, a: str, fa, b: str, fb) -> QHBoxLayout:
        row = QHBoxLayout()
        row.addWidget(self._button(a, fa))
        row.addWidget(self._button(b, fb))
        return row

    def _button(self, text: str, fn) -> QPushButton:
        btn = QPushButton(text)
        btn.clicked.connect(fn)
        return btn

    def _slider(self, lo: int, hi: int, value: int) -> QSlider:
        slider = QSlider(Qt.Horizontal)
        slider.setRange(lo, hi)
        slider.setValue(value)
        return slider

    def _control(self, text: str, slider: QSlider) -> QWidget:
        w = QWidget()
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 0, 0, 0)
        label = QLabel(text)
        value = QLabel()
        slider.valueChanged.connect(lambda v: value.setText(str(v)))
        value.setText(str(slider.value()))
        row.addWidget(label)
        row.addWidget(slider)
        row.addWidget(value)
        return w

    def _style(self):
        self.setStyleSheet(
            """
            QMainWindow, QWidget { background: #101419; color: #edf2f4; font-family: "Microsoft YaHei"; font-size: 14px; }
            QMenuBar, QMenu { background: #151b22; color: #edf2f4; }
            #panel { background: #171f28; border: 1px solid #263443; border-radius: 8px; padding: 14px; }
            #canvas { background: #0b0f14; border: 1px solid #2a3847; border-radius: 8px; color: #8fa3b5; font-size: 20px; }
            #title { font-size: 24px; font-weight: 700; color: #ffffff; padding-bottom: 2px; }
            #status { color: #8fa3b5; padding-bottom: 8px; }
            QPushButton { background: #233142; border: 1px solid #31465c; border-radius: 6px; padding: 9px 10px; color: #f6fbff; }
            QPushButton:hover { background: #2d4258; border-color: #57c7ff; }
            QPushButton:pressed { background: #1b2836; }
            QSlider::groove:horizontal { height: 5px; background: #263443; border-radius: 2px; }
            QSlider::handle:horizontal { background: #57c7ff; width: 16px; margin: -6px 0; border-radius: 8px; }
            """
        )

    def require_image(self) -> bool:
        if self.current is None:
            QMessageBox.warning(self, "提示", "请先打开图片")
            return False
        return True

    def open_image(self):
        self._open(False)

    def open_gray(self):
        self._open(True)

    def _open(self, gray: bool):
        path, _ = QFileDialog.getOpenFileName(self, "打开图片", "", "Images (*.bmp *.jpg *.jpeg *.png)")
        if not path:
            return
        try:
            self.current = ops.read_image(path, gray)
            self.original = self.current.copy()
            self.mask = None
            self.canvas.set_image(self.current)
            self.status.setText(Path(path).name)
        except Exception as exc:
            QMessageBox.critical(self, "读取失败", str(exc))

    def save_image(self):
        if not self.require_image():
            return
        path, _ = QFileDialog.getSaveFileName(self, "保存结果", "result.png", "Images (*.bmp *.jpg *.png)")
        if path:
            ops.save_image(path, self.current)
            self.status.setText(f"已保存：{Path(path).name}")

    def restore(self):
        if self.original is not None:
            self.current = self.original.copy()
            self.mask = None
            self.canvas.set_image(self.current)
            self.status.setText("已恢复原图")

    def apply(self, fn):
        if not self.require_image():
            return
        try:
            self.current = fn(self.current)
            self.canvas.set_image(self.current)
        except Exception as exc:
            QMessageBox.critical(self, "处理失败", str(exc))

    def enhance(self):
        def run(img):
            out = ops.adjust_brightness_contrast(img, self.brightness.value(), self.contrast.value() / 100)
            return ops.adjust_hsv(out, self.hue.value(), self.saturation.value() / 100) if out.ndim == 3 else out
        self.apply(run)

    def crop_selection(self):
        rect = self.canvas.selected_rect_on_image()
        if rect:
            self.apply(lambda img: ops.crop_region(img, *rect))
        else:
            self.status.setText("请先拖拽选择裁剪区域")

    def threshold_segment(self):
        if not self.require_image():
            return
        self.mask = ops.threshold_mask(self.current)
        self.current = ops.apply_mask(self.current if self.current.ndim == 3 else np.dstack([self.current] * 3), self.mask)
        self.canvas.set_image(self.current)
        self.status.setText("已完成阈值分割")

    def grabcut_segment(self):
        rect = self.canvas.selected_rect_on_image()
        if not rect:
            self.status.setText("请先拖拽框选目标")
            return
        self.mask = ops.grabcut_mask(self.current, rect)
        self.current = ops.apply_mask(self.current, self.mask)
        self.canvas.set_image(self.current)
        self.status.setText("已完成框选分割")

    def measure_selection(self):
        if self.mask is None:
            rect = self.canvas.selected_rect_on_image()
            if not rect:
                self.status.setText("请先分割或拖拽选择区域")
                return
            x, y, w, h = rect
            self.mask = np.zeros(self.current.shape[:2], dtype=np.uint8)
            self.mask[y:y + h, x:x + w] = 255
        r = ops.measure_mask(self.mask)
        self.status.setText(
            f"面积 {r['area']} | 重心 {r['centroid']} | 周长 {r['perimeter']} | 矩形度 {r['rectangularity']} | 圆形度 {r['circularity']}"
        )


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
