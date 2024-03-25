from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QImage, QPixmap

import numpy as np
import cv2,math
import sys
import logging
import copy

class ResultApp(QWidget):
    def __init__(self,parent=None):
        super().__init__()
        # raise ValueError("Assertion failed at libavcodec/pthread_frame.c:155")
        self.setWindowTitle("A Top-down View") 
        self.logger=parent.logger
        self.action_menu_aux=True
        self.action_menu_vtl=False
        self.rate=8
        self.display_width = 130*self.rate
        self.display_height = 60*self.rate
        self.annotation_on = False
        self.image_label = QLabel(self)
        self.image_label.setMinimumSize(self.display_width, self.display_height)
        #self.image_label.setStyleSheet("border :3px solid black;")
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # self.image_label.mousePressEvent = self.video_clicked

        vbox = QVBoxLayout()
        vbox.addWidget(self.image_label)#, alignment=Qt.AlignCenter)
        # vbox.addWidget(self.textLabel, alignment=Qt.AlignBottom)
        # set the vbox layout as the widgets layout
        self.setLayout(vbox)
        self.stack=[]
        
        # print(self.action_menu_aux)
    def adjust_window_size(self):
        display_width, display_height = self.display_width, self.display_height
        if self.action_menu_aux==False:
            display_height = display_height//2
        if self.action_menu_vtl==True:
            display_width, display_height = display_height, display_width
        
        self.image_label.setMinimumSize(display_width, display_height)
        self.resize(display_width, display_height)
        self.setPosition(self.position)


    def gen_image(self):
        if self.slbr=='Bridge':
            rate=self.rate
            x1,x2=self.mydict['x1'],self.mydict['x2']
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
            thickness=1
            csle=130
            color=(csle,csle,csle)     
            for i in range(2,30,2):
                a=int((original_i-i)*rate)
                start_point=(a,coord1[1])
                end_point=(a,coord2[1])
                img = cv2.line(img, start_point, end_point, color, thickness)    
            # colors=[(134,200,99),(165,181,117),(157,152,90),(146,191,125),(130,114,92)]

            colors=[(csle,csle,csle) for i in range(5)]
            cnt=0
            for i in range(-2,-50,-2):
                a=int((original_i-i)*rate)
                start_point=(a,0*rate)
                end_point=(a,30*rate)
                img = cv2.line(img, start_point, end_point, colors[cnt%5], thickness)
                cnt+=1
            colors.reverse()
            cnt=1
            for i in range(32,100,2):
                a=int((original_i-i)*rate)
                start_point=(a,0*rate)
                end_point=(a,30*rate)
                img = cv2.line(img, start_point, end_point, colors[cnt%5], thickness)
                cnt+=1

            img [0,:,:]=(255,255,255)
            self.original_i=original_i
            self.rate=rate
            self.radius=1*rate
            # self.radius2=*rate
        elif self.slbr=='Gaps':
            rate=self.rate
            # x1,x2=self.mydict['x1'],self.mydict['x2']
            # length=self.mydict['angle']*0.393701
            length=self.mydict['angle']*0.4
            # x1,x2=args.x1,args.x2

            
            original_i=100-30+length
            y=(140-30+length)*rate
            y=int(y)
            print(140-30+length)
            img = np.zeros((30*rate,y,3), np.uint8)+255

            y0=(original_i-length-70)*rate
            y1=(original_i-length)*rate
            y0,y1=int(y0),int(y1)
            cv2.rectangle(img,(y0,0),(y1,30*rate),(157,163,110),-1)
            y0=original_i*rate
            y1=(original_i+40)*rate
            y0,y1=int(y0),int(y1)
            cv2.rectangle(img,(y0,0),(y1,30*rate),(157,163,110),-1)

           
            thickness=1
            csle=130
            colors=[(csle,csle,csle) for i in range(5)]
            cnt=0
            i=-2
            while i>-50:
                a=int((original_i-i)*rate)
                start_point=(a,0*rate)
                end_point=(a,30*rate)
                img = cv2.line(img, start_point, end_point, colors[cnt%5], thickness)
                cnt+=1
                i-=2
            colors.reverse()

            cnt=1
            i=length
            while i<length+70:
                a=int((original_i-i)*rate)
                start_point=(a,0*rate)
                end_point=(a,30*rate)
                img = cv2.line(img, start_point, end_point, colors[cnt%5], thickness)
                cnt+=1
                i+=2
            
            # gap
            a=int((original_i)*rate)
            start_point=(a,0*rate)
            end_point=(a,30*rate)
            img = cv2.line(img, start_point, end_point, (0,0,0), thickness)

            a=int((original_i-length)*rate)
            start_point=(a,0*rate)
            end_point=(a,30*rate)
            img = cv2.line(img, start_point, end_point, (0,0,0), thickness)
            # gap end

            img [0,:,:]=(255,255,255)
            self.original_i=original_i
            self.rate=rate
            self.radius=1*rate
            # self.radius2=*rate
        else:
            rate=self.rate
            # if self.mydict['angle']!=-1:
            #     print('yes')
            angle=self.mydict['angle']
            
            self.logger.log(logging.DEBUG, 'slope angle: {}'.format(angle), extra={'qThreadName': 'ResultApp'})

            theta=angle/180*math.pi
            cos=math.cos(theta)
            L=38
            self.L=L
            self.adjac=L*cos
            self.cos=cos
            adjac=L#*cos

            a=int((60+adjac+32)*rate)
            img = np.zeros((30*rate,a,3), np.uint8)+255
            original_i=100
            cv2.rectangle(img,((original_i-100)*rate,0),((original_i-40)*rate,30*rate),(157,163,110),-1)

            a=original_i-40
            b=a+adjac
            a,b=int(a*rate),int(b*rate)
            cv2.rectangle(img,(a,0),(b,30*rate),(107,189,229),-1)
            cv2.rectangle(img,(b,0),(b+32*rate,30*rate),(157,163,110),-1)

            # colors=[(134,200,99),(165,181,117),(157,152,90),(146,191,125),(130,114,92)]
            csle=130
            colors=[(csle,csle,csle) for i in range(5)]
            a=original_i-40
            b=a+adjac
            step=adjac/19
            i=0
            cnt=4
            thickness=1
            while i<adjac:
                a1=int((a+i)*rate)
                start_point=(a1,0*rate)
                end_point=(a1,30*rate)
                img = cv2.line(img, start_point, end_point, colors[cnt%5], thickness)
                cnt+=1
                i+=step
            for i in range(0,36,2):
                a1=int((b+i)*rate)
                start_point=(a1,0*rate)
                end_point=(a1,30*rate)
                img = cv2.line(img, start_point, end_point, colors[cnt%5], thickness)
                cnt+=1
                i+=step
            colors.reverse()
            cnt=1
            for i in range(-2,-66,-2):
                a1=int((a+i)*rate)
                start_point=(a1,0*rate)
                end_point=(a1,30*rate)
                img = cv2.line(img, start_point, end_point, colors[cnt%5], thickness)
                cnt+=1
                i+=step

            img [0,:,:]=(255,255,255)
            self.original_i=original_i
            self.rate=rate
            self.radius=1*rate
        return img
    
    def del_stack(self):
        while len(self.stack)!=0:
            op,self.data,self.position,self.img,self.img1,self.img2=self.stack.pop()
            del self.data,self.position,self.img,self.img1,self.img2 
    def FindFrame(self,position_end,direction):
        # print(self.position+direction, position_end, direction)
        for position in range(self.position+direction, position_end, direction):
            if position in self.data:
                for key in ['L','R','L1','R1']:
                    if key in self.data[position]:
                        # print("# location 1")
                        # print(position)
                        return position
        return self.position
    
    def AddAction(self,key):
        stackdata=['A',copy.deepcopy(self.data),self.position,copy.deepcopy(self.img),copy.deepcopy(self.img1),copy.deepcopy(self.img2)]
        self.stack.append(stackdata)
        self.data[self.position][key]=self.data[self.position]['3dp'][key]
        self.setPosition1()
        img=cv2.vconcat([self.img1, self.img2])
        qt_img = self.convert_cv_qt(img)
        self.image_label.setPixmap(qt_img)

    def ClearAction(self):
        stackdata=['C',copy.deepcopy(self.data),self.position,self.img,self.img1,self.img2]
        self.stack.append(stackdata)
        for position in range(self.mydict['duration_on'],self.mydict['duration_off']):
            if position in self.data:
                for key in ['L','R','L1','R1']:
                    if key in self.data[position]:
                        self.data[position].pop(key)
        self.img=self.gen_image()
        self.img1=self.img.copy()
        img = cv2.vconcat([self.img1, self.img])
        qt_img = self.convert_cv_qt(img)
        self.image_label.setPixmap(qt_img)     
    
    def SaveAction(self):
        mydata={}
        mydata['data']=self.data
        np.save(self.mydict['path_data_sv'], mydata, allow_pickle=True)
        # self.del_stack()

    def RemoveAction(self):
        stackdata=['R',copy.deepcopy(self.data),self.position,self.img,self.img1,self.img2]
        self.stack.append(stackdata)
        if self.position in self.data:
            for key in ['L','R','L1','R1']:
                if key in self.data[self.position]:
                    self.data[self.position].pop(key)
        self.img1=self.gen_image()
        if self.position in self.myfoot:
            self.myfoot.remove(self.position)
        for position in self.myfoot:
            self.setPosition1(position)

        img = cv2.vconcat([self.img1, self.img])
        qt_img = self.convert_cv_qt(img)
        self.image_label.setPixmap(qt_img)  

    def UndoAction(self):
        # stackdata=self.stack.top()
        if len(self.stack)>0:
            del self.data,self.position,self.img,self.img1,self.img2 
            op,self.data,self.position,self.img,self.img1,self.img2=self.stack.pop()
            return self.position,self.data
        return -1,None



    def set_file(self,mydict):
        self.del_stack()
        self.data=mydict['data']

        self.mydict=mydict
        self.slbr=self.mydict['slbr']
        self.img=self.gen_image()
        self.img1=self.img.copy()
        self.myfoot=set()
        img = cv2.vconcat([self.img1, self.img])
        # print(img.shape)
        qt_img = self.convert_cv_qt(img)
        self.image_label.setPixmap(qt_img)
        
        self.setWindowTitle("A Top-down View | {}".format(self.mydict['angle'])) 


    def reset(self):
        self.myfoot=set()
        self.img=self.gen_image()
        self.img1=self.img.copy()
        img = cv2.vconcat([self.img1, self.img])
        qt_img = self.convert_cv_qt(img)
        self.image_label.setPixmap(qt_img)
    
    def preset(self):
        self.reset()
        timestamps=[]
        for t in self.data:
            for key in ['R','L']:
                if key in self.data[t]:
                    timestamps.append(t)
        tmin,tmax=min(timestamps),max(timestamps)
        for position in range(tmin,tmax):
            self.setPosition(position)


    def gen_y(self,y):
        if self.slbr[0]=='B' or self.slbr[0]=='G':return y
        else:
            y1=self.original_i-40
            y2=y1+self.adjac
            if y<=y1:
                return y
            elif y<=y2:
                return y1+(y-y1)/self.cos
            else:
                return y1+self.L+(y-y2)
        


    def setPosition1(self,position=-1):
        if position==-1:position=self.position
        thickness1=2
        for key in ['L','R','L1','R1']:
            if key in self.data[position]:
                self.myfoot.add(position)
                x,y,z=self.data[position][key]
                # print(x,y,z)
                y1,x1=self.gen_y(self.original_i+y)*self.rate,x*self.rate
                y1,x1=int(y1),int(x1)
                if key=='L':
                    cv2.circle(self.img1,(y1,x1), self.radius, (255,0,0), thickness1)
                    cv2.line(self.img1, (y1+self.radius,x1), (y1-self.radius,x1), (255,0,0), thickness1)
                elif key=='L1':
                    cv2.circle(self.img1,(y1,x1), self.radius, (255,0,0), thickness1)
                elif key=='R':
                    cv2.circle(self.img1,(y1,x1), self.radius, (0,0,255), thickness1)
                    cv2.line(self.img1, (y1+self.radius,x1), (y1-self.radius,x1), (0,0,255), thickness1)
                elif key=='R1':
                    cv2.circle(self.img1,(y1,x1), self.radius, (0,0,255), thickness1)
    
    # self.img: pure gray
    # self.img1: view with steps - top
    # self.img2: view for each frame, with overlay - bottom
    def setPosition(self, position):
        # print("# location 1")
        self.position=position
        thickness1=2
        overlay = self.img.copy()
        img1 = self.img.copy()
        cur_y=-1
        cur_key=''
        if position in self.data:
            self.setPosition1()
            for key in self.data[position]['3dp']:
            # print(k)

                data1=self.data[position]['3dp'][key]
                # print('#location 2',data1,key)
                x,y,z=data1
                # print(x,y,z)
                y1,x1=self.gen_y(self.original_i+y)*self.rate,x*self.rate
                y1,x1=int(y1),int(x1)
                
                cv2.circle(self.img,(y1,x1), self.radius, (0,0,0), thickness1)

                if key.find("L")==0:
                    cv2.circle(img1,(y1,x1), self.radius, (255,0,0), thickness1)
                else:
                    cv2.circle(img1,(y1,x1), self.radius, (0,0,255), thickness1)
                # else:
                #     cv2.circle(img1,(y1,x1), self.radius, (255,255,255), thickness1)
            for key in ['L','R','L1','R1']:
                if key in self.data[position]:
                    x,y,z=self.data[position][key]
                    y1=self.gen_y(self.original_i+y)*self.rate
                    cur_y=int(y1)
                    cur_key=key[0]
        alpha = 0.8  # Transparency factor.
        self.img = cv2.addWeighted(overlay, alpha, self.img, 1 - alpha, 0)
        
        self.img2 =img1
        img=cv2.vconcat([self.img1,img1])

        rline=2
        if cur_y!=-1:
            if cur_key=='L':
                img [:,cur_y-rline:cur_y+rline+1,:]=(255,0,0)
            else:
                img [:,cur_y-rline:cur_y+rline+1,:]=(0,0,255)

        qt_img = self.convert_cv_qt(img)
        self.image_label.setPixmap(qt_img)

    def select_view(self, img):
        h, w, _ = img.shape

        return_img=img
        if self.action_menu_aux==False:
            return_img=return_img[:h//2, :]
        if self.action_menu_vtl==True:
            return_img= cv2.rotate(return_img, cv2.ROTATE_90_CLOCKWISE)
        return return_img
        # return im


    def convert_cv_qt(self, cv_img):
        # print("A")
        """Convert from an opencv image to QPixmap"""
        # print("# location 1")
        # print(cv_img.shape)
        cv_img = self.select_view(cv_img)
        # print(cv_img.shape)
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)

        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        #p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)

        #convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio)

        return QPixmap.fromImage(p)