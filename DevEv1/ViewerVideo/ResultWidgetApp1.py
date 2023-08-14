from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QImage, QPixmap

import numpy as np
import cv2,math
import sys

class ResultApp(QWidget):
    def __init__(self):
        super().__init__()
        rate=8
        self.disply_width = 140*rate
        self.display_height = 60*rate
        self.annotation_on = False
        #self.disply_width = 670
        #self.display_height = 540
        # create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.setMinimumSize(self.disply_width, self.display_height)
        #self.image_label.setStyleSheet("border :3px solid black;")
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # self.image_label.mousePressEvent = self.video_clicked

        vbox = QVBoxLayout()
        vbox.addWidget(self.image_label)#, alignment=Qt.AlignCenter)
        # vbox.addWidget(self.textLabel, alignment=Qt.AlignBottom)
        # set the vbox layout as the widgets layout
        self.setLayout(vbox)
        self.slbr='Bridge'
        self.img=self.gen_image()
        self.img1=self.img.copy()
        img = cv2.vconcat([self.img, self.img1])
        # print(img.shape)
        qt_img = self.convert_cv_qt(img)
        self.image_label.setPixmap(qt_img)
    
    def gen_image(self):
        if self.slbr=='Bridge':
            rate=15
            x1,x2=3.95, 20
            # x1,x2=args.x1,args.x2

            img = np.zeros((30*rate,140*rate,3), np.uint8)+255
            original_i=100
            cv2.rectangle(img,((original_i-100)*rate,0),((original_i-30)*rate,30*rate),(157,163,110),-1)
            cv2.rectangle(img,(original_i*rate,0),((original_i+40)*rate,30*rate),(157,163,110),-1)

            # delta_x,x=x2-x1,x1
            a,b=(original_i-30)*rate,x1*rate
            a,b=int(a),int(b)
            coord1=(a,b)

            a,b=original_i*rate,x2*rate
            a,b=int(a),int(b)
            coord2=(a,b)

            cv2.rectangle(img,coord1,coord2,(107,189,229),-1)
            # print(img.shape)
            # print(coord1,coord2)
            color=(0,0,0)
            thickness=1
            for i in range(2,30,2):
                a=int((original_i-i)*rate)
                start_point=(a,coord1[1])
                end_point=(a,coord2[1])
                img = cv2.line(img, start_point, end_point, color, thickness)
            img [0,:,:]=(255,255,255)
            self.original_i=original_i
            self.rate=rate
            self.radius=1*rate
        else:
            rate=15
            angle=0
            # x1,x2=3.95, 20
            # x1,x2=args.x1,args.x2

            theta=angle/180*math.pi
            cos=math.cos(theta)
            L=38
            adjac=L*cos


            a=int((60+adjac+32)*rate)
            img = np.zeros((30*rate,a,3), np.uint8)+255
            original_i=100
            cv2.rectangle(img,((original_i-100)*rate,0),((original_i-40)*rate,30*rate),(157,163,110),-1)

            a=original_i-40
            b=a+adjac
            a,b=int(a*rate),int(b*rate)
            cv2.rectangle(img,(a,0),(b,30*rate),(107,189,229),-1)
            cv2.rectangle(img,(b,0),(b+32*rate,30*rate),(157,163,110),-1)
            img [0,:,:]=(255,255,255)
            self.original_i=original_i
            self.rate=rate
            self.radius=1*rate
        return img
        
    def FindFrame(self,position_end,direction):
        for position in range(self.position+direction, position_end, direction):
            # print('# location 1 : ',end='')
            # print(self.position, position, position_end, direction)
            if position in self.data:
                if 'L' in self.data[position] or 'R' in self.data[position]:
                    # print(self.position,position)
                    return position
        return self.position



    
    def AddAction(self,key):
        length=len(self.data[self.position]['3dp'])
        if length==2:
            if key =='L':
                self.data[self.position][key]=self.data[self.position]['3dp'][0]
            elif key=='R':
                self.data[self.position][key]=self.data[self.position]['3dp'][1]
        else:
            self.data[self.position][key]=self.data[self.position]['3dp'][0]
        self.setPosition1()
        # print(self.position)
        img=cv2.vconcat([self.img2, self.img1])
        # print(img.shape)
        qt_img = self.convert_cv_qt(img)
        self.image_label.setPixmap(qt_img)

    def ClearAction(self):
        for position in range(self.mydict['duration_on'],self.mydict['duration_off']):
            if position in self.data:
                for key in ['L','R']:
                    if key in self.data[position]:
                        self.data[position].pop(key)
        self.img=self.gen_image()
        self.img1=self.img.copy()
        img = cv2.vconcat([self.img, self.img1])
        qt_img = self.convert_cv_qt(img)
        self.image_label.setPixmap(qt_img)     
    
    def SaveAction(self):
        mydata={}
        mydata['data']=self.data
        print('save_action')
        np.save(self.mydict['path_data'], mydata, allow_pickle=True)

    def RemoveAction(self):
        if self.position in self.data:
            for key in ['L','R']:
                if key in self.data[self.position]:
                    self.data[self.position].pop(key)
        self.img1=self.gen_image()
        self.myfoot.remove(self.position)
        for position in self.myfoot:
            self.setPosition1(position)

        # thickness1=2
        # for position in range(self.mydict['duration_on'],self.position):
        #     if position in self.data:
        #         for key in ['L','R']:
        #             if key in self.data[position]:
        #                 x,y,z=self.data[self.position][key]
        #                 # print(x,y,z)
        #                 y1,x1=(self.original_i+y)*self.rate,x*self.rate
        #                 y1,x1=int(y1),int(x1)
        #                 if key=='L':
        #                     cv2.circle(self.img1,(y1,x1), self.radius, (255,0,0), thickness1)
        #                 elif key=='R':
        #                     cv2.circle(self.img1,(y1,x1), self.radius, (0,0,255), thickness1)
        img = cv2.vconcat([self.img, self.img1])
        qt_img = self.convert_cv_qt(img)
        self.image_label.setPixmap(qt_img)  

    def set_file(self,mydict):
        self.data=mydict['data']
        self.mydict=mydict
        self.slbr=self.mydict['slbr']
        self.img=self.gen_image()
        self.img1=self.img.copy()
        self.myfoot=set()
        

    def reset(self):
        self.img=self.gen_image()
        self.img1=self.img.copy()
        img = cv2.vconcat([self.img, self.img1])
        qt_img = self.convert_cv_qt(img)
        self.image_label.setPixmap(qt_img)
    
    def setPosition1(self,position=-1):
        if position==-1:position=self.position
        thickness1=2
        for key in ['L','R']:
            if key in self.data[position]:
                self.myfoot.add(position)
                x,y,z=self.data[position][key]
                # print(x,y,z)
                y1,x1=(self.original_i+y)*self.rate,x*self.rate
                y1,x1=int(y1),int(x1)
                if key=='L':
                    cv2.circle(self.img1,(y1,x1), self.radius, (255,0,0), thickness1)
                elif key=='R':
                    cv2.circle(self.img1,(y1,x1), self.radius, (0,0,255), thickness1)
        

    def setPosition(self, position):
        self.position=position
        thickness1=2
        overlay = self.img.copy()
        img1 = self.img.copy()
        if position in self.data:
            self.setPosition1()
            self.data[position]['3dp'].sort()
            # print(self.data[position]['3dp'])
            length=len(self.data[position]['3dp'])
            for i,data1 in enumerate(self.data[position]['3dp']):
            # print(k)
                x,y,z=data1
                # print(x,y,z)
                y1,x1=(self.original_i+y)*self.rate,x*self.rate
                y1,x1=int(y1),int(x1)
                
                cv2.circle(self.img,(y1,x1), self.radius, (0,0,0), thickness1)
                if length==2:
                    if i==0:
                        cv2.circle(img1,(y1,x1), self.radius, (255,0,0), thickness1)
                    else:
                        cv2.circle(img1,(y1,x1), self.radius, (0,0,255), thickness1)
                else:
                    cv2.circle(img1,(y1,x1), self.radius, (255,255,255), thickness1)
        alpha = 0.8  # Transparency factor.
        
        self.img = cv2.addWeighted(overlay, alpha, self.img, 1 - alpha, 0)
        self.img2 =img1
        img=cv2.vconcat([img1, self.img1])
        # print(img.shape)
        qt_img = self.convert_cv_qt(img)
        self.image_label.setPixmap(qt_img)
        if position+1>=self.mydict['duration_off']:
            self.SaveAction()
        
            # def draw_frame(self,f):


    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        # cv_img = self.select_view(cv_img)
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)

        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        #p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)

        #convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio)

        return QPixmap.fromImage(p)