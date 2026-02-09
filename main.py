import sys
import argparse

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QSystemTrayIcon
from PyQt6.QtCore import Qt, QRect, QTimer, pyqtSignal, QPoint
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QCursor

import capture

class SelectionOverlay(QWidget):
    areaSelected = pyqtSignal(int, int, int, int)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.start_point = None
        self.end_point = None
        self.is_selecting = False

        # Get the geometry of the virtual desktop (all screens)
        screen_geometry = QApplication.primaryScreen().virtualGeometry()
        self.setGeometry(screen_geometry)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw a semi-transparent background to indicate selection mode
        painter.setBrush(QColor(0, 0, 0, 100))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

        if self.start_point and self.end_point:
            # Clear the selected area (make it fully transparent) or draw the rect
            # Here we just draw a red border rectangle
            rect = QRect(self.start_point, self.end_point).normalized()
            
            # Use CompositionMode to "cut out" the selection or just draw on top
            # Let's just draw a red box for simplicity
            pen = QPen(QColor(255, 0, 0), 2)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.pos()
            self.end_point = event.pos()
            self.is_selecting = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_selecting:
            self.end_point = event.pos()
            self.is_selecting = False
            
            rect = QRect(self.start_point, self.end_point).normalized()
            if rect.width() > 10 and rect.height() > 10:
                self.areaSelected.emit(rect.x(), rect.y(), rect.width(), rect.height())
                self.close()
            else:
                self.start_point = None
                self.end_point = None
                self.update()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

class ControlWindow(QWidget):
    def __init__(self, save_dir="captures", interval_ms=500):
        super().__init__()
        self.setWindowTitle(f"Auto Capture - {save_dir} ({interval_ms}ms)")
        self.resize(300, 200)
        
        self.engine = capture.CaptureEngine(save_dir=save_dir, interval_ms=interval_ms)

        
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Status: Idle")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.info_label = QLabel("Region: Not Set")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)
        
        self.select_btn = QPushButton("Select Area")
        self.select_btn.clicked.connect(self.start_selection)
        layout.addWidget(self.select_btn)
        
        self.start_btn = QPushButton("Start Capture")
        self.start_btn.clicked.connect(self.start_capture)
        self.start_btn.setEnabled(False)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop Capture")
        self.stop_btn.clicked.connect(self.stop_capture)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        self.setLayout(layout)

    def start_selection(self):
        self.overlay = SelectionOverlay()
        self.overlay.areaSelected.connect(self.on_area_selected)
        self.overlay.show()
        # On macOS, sometimes need to raise specifically
        self.overlay.raise_()
        self.overlay.activateWindow()

    def on_area_selected(self, x, y, w, h):
        self.engine.set_region(x, y, w, h)
        self.info_label.setText(f"Region: {x},{y} {w}x{h}")
        self.start_btn.setEnabled(True)

    def start_capture(self):
        self.engine.start()
        self.status_label.setText("Status: Capturing...")
        self.status_label.setStyleSheet("color: green")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.select_btn.setEnabled(False)

    def stop_capture(self):
        self.engine.stop()
        self.status_label.setText("Status: Stopped")
        self.status_label.setStyleSheet("color: red")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.select_btn.setEnabled(True)

    def closeEvent(self, event):
        self.engine.stop()
        event.accept()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ScreenLog - Auto Screen Capture Tool")
    parser.add_argument("--save-dir", type=str, default="captures", help="Directory to save screenshots")
    parser.add_argument("--interval", type=int, default=500, help="Capture interval in milliseconds")
    
    args = parser.parse_args()

    app = QApplication(sys.argv)
    window = ControlWindow(save_dir=args.save_dir, interval_ms=args.interval)
    window.show()
    sys.exit(app.exec())

