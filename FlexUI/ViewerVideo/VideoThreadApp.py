from PyQt5.QtCore import QThread, pyqtSignal

import numpy as np
import cv2
import time
# from ..app_helper import camera

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    frame_id = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        # whether is currently being played
        self._run_flag = False
        self.cap = None
        self.curr_frame = 0
        self.fps = 1
        self.one2one=False

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
        mydict['h'],mydict['w']=self.h,self.w
        # self.camera=camera(mydict)
        # print(self.h,self.w)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)

        # print('fps: {}'.format(self.fps))
        self.S=1
        self.D=1
        self.duration_on= int(self.fps*mydict['on'])
        self.duration_off= int(self.fps*mydict['off']) 
        # print(self.duration_on,self.duration_off)
        self.curr_frame = self.duration_on
        # print(self.curr_frame)
        self.cap.set(1,self.curr_frame)
        self.cap_curr_frame=self.curr_frame
        self.data=mydict['data']
        self.cv_img_mb={}
        self.boxes_on=True
        # print(self.duration_on,self.duration_off)
        # self.duration = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        return self.duration_on,self.duration_off, height_video, width_video

    def run_one(self,D):
        # print('# location 3')
        self.curr_frame+=D
        if D>0:
            if self.curr_frame>=self.duration_off:
                self.curr_frame = self.duration_off-1
        else:
            if self.curr_frame<self.duration_on:
                self.curr_frame = self.duration_on
        if self.cap is None: return     
        if self.curr_frame in self.cv_img_mb:
            ret,cv_img=True,self.cv_img_mb[self.curr_frame]
        else:
            if self.curr_frame!=self.cap_curr_frame:
                self.cap.set(1,self.curr_frame)     
            self.cap_curr_frame=self.curr_frame+1
            ret, cv_img = self.cap.read()
            self.cv_img_mb[self.curr_frame]=cv_img
            
        cv_img=self.box_img(np.copy(cv_img))
            
        self.last_image = cv_img        
        self.change_pixmap_signal.emit(cv_img)
        self.frame_id.emit(self.curr_frame)
 
    # play video and replay it after reaching the end
    def run(self):
        # print('# location 2')
        while self._run_flag:
            self.curr_frame+=self.D
            if self.D>0:
                if self.curr_frame>=self.duration_off:
                    self.curr_frame=self.duration_off-1
                    break
            else:
                if self.curr_frame<self.duration_on:
                    self.curr_frame=self.duration_on
                    break
            
            if self.cap is None: break
            if self._run_flag:
                if self.curr_frame in self.cv_img_mb:
                    ret,cv_img=True,self.cv_img_mb[self.curr_frame]
                    time.sleep(1/self.fps/self.S)
                else:
                    # print('else',self.D,self.curr_frame, self.cap_curr_frame)
                    if self.curr_frame!=self.cap_curr_frame:
                        self.cap.set(1,self.curr_frame)     
                    self.cap_curr_frame=self.curr_frame+1
                    ret, cv_img = self.cap.read()
                    self.cv_img_mb[self.curr_frame]=cv_img
                    time.sleep(1/self.fps/self.S*0.7)

                cv_img=self.box_img(np.copy(cv_img))
                self.last_image = cv_img        
                self.change_pixmap_signal.emit(cv_img)
                
                self.frame_id.emit(self.curr_frame)
            else:
                if self.D>0:
                    self.run_one(1)
                elif self.D<0:
                    self.run_one(-1)
                break

    # get the last frame and id
    def get_last_image(self, emit_frame=True):
        if self.cap is None or self.last_image is None: return
        self.change_pixmap_signal.emit(self.last_image)
        if emit_frame: self.frame_id.emit(self.curr_frame)
    
    def box_img(self,cv_img):
        if not self.boxes_on:return cv_img
        h,w=self.h,self.w
        t=self.curr_frame
        # color = (0, 255, 0)
        color = [(0, 0, 255),(255, 0, 0)]
        thickness = 2
        # print(t)
        if t in self.data:
            if 'box_r' in self.data[t]:
                box_r=self.data[t]['box_r']
            else:
                box_r=set()
            for viewid in self.data[t]['box']:
                if viewid in box_r:continue

                if viewid==0:
                    h,w=0,0
                elif viewid==1:
                    h,w=0,self.w
                elif viewid==2:
                    h,w=self.h,0
                elif viewid==3:
                    h,w=self.h,self.w

                for key in self.data[t]['box'][viewid]:
                    bt=self.data[t]['box'][viewid][key]
                    # print(t,self.data[t]['box'])
                    # print(bt)
                    bt=bt.astype('int')
                    start_point = (bt[0]+w,bt[1]+h)
                    end_point = (bt[2]+w,bt[3]+h)

                    cv_img=cv2.rectangle(cv_img, start_point, end_point, color[key], thickness)
        return cv_img
       
    def get_image(self, position, emit_frame=True):
        # print("#location 1")
        # print(position)
        if self.cap is None: return
        if self.duration_on <= position < self.duration_off:
            self.curr_frame = position
            if self.cap is None: return     
            if self.curr_frame in self.cv_img_mb:
                ret,cv_img=True,self.cv_img_mb[self.curr_frame]
            else:
                if self.curr_frame!=self.cap_curr_frame:
                    self.cap.set(1,self.curr_frame)     
                ret, cv_img = self.cap.read()
                self.cv_img_mb[self.curr_frame]=np.copy(cv_img)
                self.cap_curr_frame=self.curr_frame+1
                
            cv_img=self.box_img(cv_img)
            # self.curr_frame+=self.D
            self.last_image = cv_img        
            
            if not ret: return
            self.change_pixmap_signal.emit(cv_img)
            if emit_frame: self.frame_id.emit(self.curr_frame)

    # release the video
    def close(self):
        self._run_flag = False
        if self.cap is not None:
            self.cap.release() 
