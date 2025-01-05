import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QMessageBox, QScrollArea
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer

class ImageProcessorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Main window settings
        self.setWindowTitle('Image Processor')
        self.setGeometry(100, 100, 800, 600)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333333;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QScrollArea {
                border: 1px solid #dddddd;
                background-color: white;
            }
            QMenuBar {
                background-color: #ffffff;
                color: #333333;
            }
            QMenuBar::item {
                padding: 4px 8px;
            }
            QMenuBar::item:selected {
                background-color: #e0e0e0;
            }
            QMessageBox {
                background-color: #ffffff;
            }
        """)
        
        # Create menu bar
        menubar = self.menuBar()
        
        # Add help menu
        help_menu = menubar.addMenu('Help')
        help_action = help_menu.addAction('Usage Guide')
        help_action.triggered.connect(self.show_help)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Create horizontal container for image displays
        image_container = QWidget()
        image_layout = QHBoxLayout(image_container)
        
        # Image display area
        self.image_label = QLabel('Upload an image to begin processing')
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet('''
            border: 1px solid #dddddd;
            padding: 20px;
            background-color: white;
        ''')
        
        # Scroll area for large images
        scroll1 = QScrollArea()
        scroll1.setWidget(self.image_label)
        scroll1.setWidgetResizable(True)
        image_layout.addWidget(scroll1)
        
        # Button container
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        
        # Upload button
        self.upload_btn = QPushButton('Upload Image')
        self.upload_btn.clicked.connect(self.upload_image)
        button_layout.addWidget(self.upload_btn)
        
        # Process button
        self.process_btn = QPushButton('Process Image')
        self.process_btn.clicked.connect(self.process_image)
        self.process_btn.setEnabled(False)
        button_layout.addWidget(self.process_btn)
        
        # Save button
        self.save_btn = QPushButton('Save Result')
        self.save_btn.clicked.connect(self.save_result)
        self.save_btn.setEnabled(False)
        button_layout.addWidget(self.save_btn)
        
        main_layout.addWidget(button_container)
        
        # Result display area
        self.result_label = QLabel('Processing results will appear here')
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet('''
            border: 1px solid #dddddd;
            padding: 20px;
            background-color: white;
        ''')
        
        # Scroll area for result
        scroll2 = QScrollArea()
        scroll2.setWidget(self.result_label)
        scroll2.setWidgetResizable(True)
        image_layout.addWidget(scroll2)
        
        # Add horizontal container to main layout
        main_layout.addWidget(image_container)
        
    def upload_image(self):
        # File dialog to select image
        file_name, _ = QFileDialog.getOpenFileName(
            self, 'Open Image', '', 
            'Images (*.png *.jpg *.jpeg *.bmp *.gif)'
        )
        
        if file_name:
            # Load and display image
            self.current_image = QPixmap(file_name)
            self.image_label.setPixmap(
                self.current_image.scaled(
                    self.image_label.width(),
                    self.image_label.height(),
                    Qt.KeepAspectRatio
                )
            )
            self.process_btn.setEnabled(True)
            
    def process_image(self):
        if not hasattr(self, 'current_image'):
            QMessageBox.warning(self, 'No Image', 'Please upload an image first')
            return
            
        # Show processing indicator
        self.result_label.setText('Processing...')
        QApplication.processEvents()
        
        try:
            # Convert QPixmap to OpenCV format
            qimg = self.current_image.toImage()
            ptr = qimg.bits()
            ptr.setsize(qimg.byteCount())
            img = np.array(ptr).reshape(qimg.height(), qimg.width(), 4)
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
            
            # Basic image processing - edge detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            
            # Convert result back to QPixmap
            edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
            height, width, channel = edges_rgb.shape
            bytes_per_line = 3 * width
            qimg = QImage(edges_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            
            # Display result
            # Use same dimensions as image display area
            self.result_label.setPixmap(
                pixmap.scaled(
                    self.image_label.width(),
                    self.image_label.height(),
                    Qt.KeepAspectRatio
                )
            )
            self.save_btn.setEnabled(True)
            self.processed_pixmap = pixmap
            
        except Exception as e:
            QMessageBox.critical(self, 'Processing Error', 
                f'An error occurred during processing:\n{str(e)}')
            self.save_btn.setEnabled(False)
            
    def save_result(self):
        if not hasattr(self, 'processed_pixmap'):
            return
            
        file_name, _ = QFileDialog.getSaveFileName(
            self, 'Save Image', '', 
            'PNG Image (*.png);;JPEG Image (*.jpg);;BMP Image (*.bmp)'
        )
        
        if file_name:
            try:
                self.processed_pixmap.save(file_name)
                QMessageBox.information(self, 'Save Successful', 
                    'Image saved successfully!')
            except Exception as e:
                QMessageBox.critical(self, 'Save Error', 
                    f'Failed to save image:\n{str(e)}')
                
    def show_help(self):
        help_text = """Image Processing Application Usage Guide

1. Upload Image:
   - Click 'Upload Image' to select an image file
   - Supported formats: PNG, JPEG, BMP, GIF

2. Process Image:
   - Click 'Process Image' to analyze the image
   - The application will detect edges in the image

3. Save Result:
   - After processing, click 'Save Result' to save the output
   - Choose from PNG, JPEG, or BMP format

4. Help:
   - Click Help > Usage Guide for this information
"""
        QMessageBox.information(self, 'Help', help_text)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageProcessorApp()
    window.show()
    sys.exit(app.exec_())
