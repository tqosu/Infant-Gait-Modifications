from PyQt5.QtCore import QThread, pyqtSignal

import numpy as np
import cv2
import time

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    protractor_signal = pyqtSignal(np.ndarray)
    frame_id = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        # whether is currently being played
        self._run_flag = False
        self.cap = None
        self.curr_frame = 0
        self.fps = 1

    # read video by filename
    def set_file(self, mydict):
        if self.cap is not None:
            self.cap.release() 
        self.filename = mydict['filename']
        self.cap = cv2.VideoCapture(self.filename)
        self.slbr=mydict['slbr']
        if self.slbr=='Slope':
            self.filename1 = mydict['filename1']
            self.cap1 = cv2.VideoCapture(self.filename1)
        self.last_image = None
        self._run_flag = False
        self.position_flag = None
        width_video = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height_video = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.h,self.w=int(height_video/2),int(width_video/2)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.duration_on= int(self.fps*mydict['on']) 
        self.duration_off= int(self.fps*mydict['off']) 
        self.curr_frame = self.duration_on
        self.cap.set(1,self.curr_frame)
        self.data=mydict['data']
        self.view = [0]
        # self.duration = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        return self.duration_on,self.duration_off, height_video, width_video
    
    # play video and replay it after reaching the end
    def run(self):
        # capture from web cam
        while 1:
            if self.cap is None: break

            if self._run_flag:
                ret, cv_img = self.cap.read()
                if ret:   
                    # print("# location 125")
                    cv_img=self.box_img(cv_img)
                    self.last_image = cv_img        
                    self.change_pixmap_signal.emit(cv_img)
                    if self.slbr=='Slope':
                        self.cap1.set(1,self.curr_frame*2) 
                        ret, cv_img1 = self.cap1.read()
                        self.protractor_signal.emit(cv_img1)
                    time.sleep(1/self.fps)
                    self.curr_frame += 1
                    if self.curr_frame>self.duration_off:
                        self.curr_frame = self.duration_on
                        self.cap.set(1,self.curr_frame) 
                else:
                    print('Error1-7ea5f38b078ac28e434f25c9468509148a7527ba')
                    break
                self.frame_id.emit(self.curr_frame)
            else: break
        return
    
    # get the last frame and id
    def get_last_image(self, emit_frame=True):
        if self.cap is None or self.last_image is None: return
        self.change_pixmap_signal.emit(self.last_image)
        self.protractor_signal.emit(self.last_image1)
        if emit_frame: self.frame_id.emit(self.curr_frame)
    
    def box_img(self,cv_img):
        h,w=self.h,self.w
        t=self.curr_frame
        color = (0, 255, 0)
        thickness = 2
        # print(t)
        if t in self.data:
            for key in self.data[t]['box']:
                # print(key,self.data[t][key])
                # if key !=2:continue
                if key==0:
                    h,w=0,0
                elif key==1:
                    h,w=0,self.w
                elif key==2:
                    h,w=self.h,0
                elif key==3:
                    h,w=self.h,self.w
    
                for bt in self.data[t]['box'][key]:
                    bt=bt.astype('int')
                    start_point = (bt[0]+w,bt[1]+h)
                    end_point = (bt[2]+w,bt[3]+h)

                    cv_img=cv2.rectangle(cv_img, start_point, end_point, color, thickness)
        return cv_img
       
    def get_image(self, position, emit_frame=True):
        if self.cap is None: return
        if self.duration_on <= position < self.duration_off:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, position)
            self.curr_frame = position
            ret, cv_img = self.cap.read()
            # print(' # location 124')
            cv_img =self.box_img(cv_img)
            if self.slbr=='Slope':
                self.cap1.set(1,self.curr_frame*2) 
                ret, cv_img1 = self.cap1.read()
                print(ret,cv_img1.shape)
                self.protractor_signal.emit(cv_img1)
            self.last_image = cv_img
            self.last_image1 = cv_img1
            if not ret: return
            self.change_pixmap_signal.emit(cv_img)
            if emit_frame: self.frame_id.emit(self.curr_frame)

    # release the video
    def close(self):
        self._run_flag = False
        if self.cap is not None:
            self.cap.release() 
