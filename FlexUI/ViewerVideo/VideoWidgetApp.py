# create user interface

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget
from PyQt5.QtWidgets import QWidget,QAction,QMenu
# from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon,QImage, QPixmap

import numpy as np
import cv2
import sys

from .VideoThreadApp import VideoThread

class VideoApp(QWidget):
    frame_id = pyqtSignal(int)
    # annotations_id = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Player") 
        self.setWindowIcon(QIcon('./icons/bridge.png'))
        self.disply_width = 1000
        self.display_height = 600
        self.annotation_on = False
        #self.disply_width = 670
        #self.display_height = 540
        # create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.setMinimumSize(self.disply_width, self.display_height)
        #self.image_label.setStyleSheet("border :3px solid black;")
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.image_label.mousePressEvent = self.video_clicked

        # create a text label
        self.textLabel = QLabel('Video')
        self.textLabel.setStyleSheet("border :1px solid black;")

        vbox = QVBoxLayout()
        vbox.addWidget(self.image_label)#, alignment=Qt.AlignCenter)
        vbox.addWidget(self.textLabel, alignment=Qt.AlignBottom)
        # set the vbox layout as the widgets layout
        self.setLayout(vbox)


       
        self.duration_on, self.duration_off= 0, 0
        self.width_video, self.height_video = 0, 0
        self.last_position = 0
        self.p2d = {}
        self.clicked_att = {}

        # start the thread     
        self.view = [0]
        self.setThread()

    def setThread(self):
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        # self.thread.protractor_signal.connect(self.update_image)
        self.thread.frame_id.connect(self.update_text)
        return

    def select_view(self, img):
        h, w, _ = img.shape
        if self.view[0] in [0,5]: return img
        im = []
        for view in self.view:
            if view == 1: im.append(img[:h//2, :w//2])
            elif view == 2: im.append(img[:h//2, w//2:])
            elif view == 3: im.append(img[h//2:, :w//2])
            elif view == 4: im.append(img[h//2:, w//2:])
        im = np.concatenate(im, axis=0)
        return im
    
    def set_file(self, mydict):
        self.thread._run_flag = False
        self.duration_on, self.duration_off, self.height_video, self.width_video = self.thread.set_file(mydict)    
        self.last_position=self.duration_on
        # self.resize(self.height_video, self.width_video)
    
    def setPosition(self, position):
        self.thread.position_flag = position
        second = position//self.thread.fps
        self.textLabel.setText("Time: {:.0f}:{:.0f} \t-\t Frame: {}".format(second//60, second % 60, position))
        self.last_position = position
        # self.showImage()
        return

    def update_last_image(self):
        self.thread.get_last_image()
    
    def showImage(self):
        self.thread.get_image(self.last_position)
    
    def stop_video(self):
        self.thread._run_flag = False
    
    def start_video(self,S,D,one2one=False):
        print("S {:.1f}, D {}".format(S,D))
        self.thread._run_flag = True
        self.thread.S = S
        self.thread.D = D
        self.thread.one2one=one2one
        self.thread.start()
    
    def closeEvent(self, event):
        self.stop_video()
        event.accept()
    
    def close_thread(self):
        self.thread._run_flag = False
        self.thread.exit()
        self.thread.wait()
        return

    def video_clicked(self, event):
        if not self.annotation_on: return
        return
    
    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        
        qt_img = self.convert_cv_qt(cv_img)
        # print(qt_img.shape)
        self.image_label.setPixmap(qt_img)
    
    # @pyqtSlot(np.ndarray)
    # def update_image1(self, cv_img):
    #     self.cv_img1=cv_img

    @pyqtSlot(int)
    def update_text(self, frame):
        second = frame//self.thread.fps
        self.textLabel.setText("Frame: {} \t Time: {} mn {} s".format(frame, second//60, second % 60))
        self.frame_id.emit(frame)
    
    @pyqtSlot(bool)
    def set_annotation(self, state):
        self.annotation_on = state
    
    @pyqtSlot(bool)
    def send_annotation(self, state):
        self.annotations_id.emit(self.clicked_att)
    
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        cv_img = self.select_view(cv_img)
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)

        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        #p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)

        #convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio)

        return QPixmap.fromImage(p)