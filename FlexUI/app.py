from email.policy import default
from PyQt5 import QtCore
from PyQt5.QtCore import QDir, Qt
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLineEdit, QButtonGroup,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget,QMessageBox)
from PyQt5.QtWidgets import QMainWindow, QShortcut, QAction, QRadioButton, QSplitter, QFrame, QCheckBox, QComboBox, qApp
from PyQt5.QtGui import QIcon, QIntValidator,  QKeySequence

import sys,json,os
# from DevEv1.Viewer3D.Viewer3DApp import View3D
from FlexUI.ViewerVideo.VideoWidgetApp import VideoApp
from FlexUI.ViewerVideo.ResultWidgetApp import ResultApp
import pandas as pd
from collections import defaultdict
import numpy as np
import random
from functools import partial
from pathlib import Path
import cv2,math
from .app_helper import to_labelme, spoint, camera

import logging
from datetime import datetime

import colorama
from colorama import Fore, Style
from io import StringIO
colorama.init()
def ctname():
    return QtCore.QThread.currentThread().objectName()
LEVELS = (logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR,
          logging.CRITICAL)

class CustomFormatter(logging.Formatter):
    def format(self, record):
        level_colors = {
            logging.DEBUG: Fore.BLUE,
            logging.INFO: Fore.GREEN,
            logging.WARNING: Fore.YELLOW,
            logging.ERROR: Fore.RED,
            logging.CRITICAL: Fore.MAGENTA,
        }

        level_color = level_colors.get(record.levelno, Fore.WHITE)
        message = super().format(record)
        return f"{Style.BRIGHT}{level_color}{message}{Style.RESET_ALL}"

def setup_logging():
    os.makedirs('LOG_', exist_ok=True)
    current_datetime = datetime.now()

    # Create a formatted string for the log file name
    log_file_name = 'LOG_/' + current_datetime.strftime("%Y-%m-%d_%H-%M-%S") + "_app_log.txt"
    
    # Configure a file handler
    file_handler = logging.FileHandler(log_file_name)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(name)s %(message)s\n%(pathname)s:%(lineno)d %(funcName)s'))
    
    # Configure a console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(CustomFormatter('%(asctime)s %(levelname)-8s %(name)s %(message)s'))

    # Get the root logger and add the handlers
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    root_logger.log(logging.DEBUG, log_file_name)


setup_logging()
logger=logging.getLogger(__name__)


class VideoWindow(QMainWindow):


    def str2sec(self,string1):
        a1,b1,c1,d1=string1.split(':')
        a,b,c,d=float(a1),float(b1),float(c1),float(d1)
        abc=a*3600+b*60+c+d/1000
        return abc
  
    def user_combo_onActivated(self,text):
        self.user=text
        self.slope_or_bridge=self.slbr_combo.currentText()
        self.slbr_combo_onActivated(self.slope_or_bridge)

    def subject_combo_onActivated(self,text):
        self.subj=text
        int_subj=int(text[1:])
        self.dataframe1=self.dataframe.loc[self.dataframe['subj']==int_subj]
        
        set_a=set(self.dataframe1['slope_or_bridge'].tolist())
        set_a=sorted(list(set_a))
        self.slbr_combo.clear()
        for sb in set_a:
            if sb =='s':
                self.slbr_combo.addItem('Slope')
            elif sb =='g':
                self.slbr_combo.addItem('Gaps')
            else:
                self.slbr_combo.addItem('Bridge')
        self.slope_or_bridge=self.slbr_combo.currentText()
        self.slbr_combo_onActivated(self.slope_or_bridge)

    def slbr_combo_onActivated(self,text):
        self.slope_or_bridge=text[0].lower()
        self.dataframe2=self.dataframe1.loc[self.dataframe1['slope_or_bridge']==self.slope_or_bridge]
        
        # set_a=list(set(self.dataframe2['total_trial_num'].tolist()))
        self.trnu_combo.clear()
        slbr=self.slbr_combo.currentText()

        info=[self.subj,'',slbr]

        user_path='User/'+self.user_combo.currentText()+'/'
        os.makedirs(user_path, exist_ok=True)
        path3=user_path+'2021_Flex1_{}_{}_MCH.csv'.format(info[0],info[2])
        if os.path.isfile(path3):
            self.dataframe3=pd.read_csv(path3)
            self.dataframe3.set_index('total_trial_num', inplace=True)
        else:
            columns_with_dtypes={'subj': int, 'slope_or_bridge': str, 'user':str,
               'bridge_l':float, 'bridge_r':float,'partial':bool}
            self.dataframe3=pd.DataFrame(columns=columns_with_dtypes)
            self.dataframe3.rename_axis('total_trial_num', inplace=True)
            
        self.logger.log(logging.DEBUG, path3, extra={'qThreadName': ctname()})
        for _, row in self.dataframe2.iterrows():
            idx=row['total_trial_num']
            trial_increment=row['trial_increment']
        # for idx in set_a:
            int_idx=int(idx)
            if int_idx in self.dataframe3.index:
                if self.dataframe3.loc[int_idx]['partial']==True:
                    padding='P'
                else:
                    padding='C'
                # self.mydict['angle']=self.dataframe3.loc[int_idx]['angle']
            else: 
                padding=' '
                # self.mydict['angle']=-1
            if not isinstance(row['trial_type'], str):
                row['trial_type']=''
            self.trnu_combo.addItem(padding+str(idx).zfill(2)+' | '+str(trial_increment).zfill(2)+' | '+row['trial_type'])

    # path3 is always user's
    # path2 change to user's when saving 
    # path1 is the offset doesn't matter
    def trnu_combo_onActivated(self,text):
        self.viewMenu1.setEnabled(True)
        self.viewMenu2.setEnabled(True)
        self.viewMenu3.setEnabled(True)
        self.remove_menu.setEnabled(True)
        self.swap_menu.setEnabled(True)
        
        
        user_path='User/'+self.user_combo.currentText()+'/'

        text=text[1:].split(' | ')[0]
        slbr=self.slbr_combo.currentText()
        # self.slbr_combo_onActivated(slbr)
        info=[self.subj,'',slbr]

        fileName = './Flex/dataset3/2021_Flex1_{}_{}_MCH.mp4'.format(info[0],info[2])
        fileName1 = './Flex/dataset/2021_Flex1_{}_SlopeProtractor.mp4'.format(info[0])

        # mixed view offset
        path1='./Flex/sync/2021_Flex1_{}_{}_MCH.json'.format(info[0],info[2])
        # level = random.choice(LEVELS)
    
        
        with open(path1) as f:
            data1 = json.load(f)
        offset=data1['start_time_seconds']

        pathdata='2021_Flex1_{}_{}_MCH-{}.npy'.format(info[0],info[2],text)
        path2='./Flex/box6_5/'+pathdata
        path2sv=user_path+pathdata
        self.logger.log(logging.DEBUG, path2, extra={'qThreadName': ctname()})
        
        os.makedirs(user_path, exist_ok=True)

        path3=user_path+'2021_Flex1_{}_{}_MCH.csv'.format(info[0],info[2])
    # try:
        data=np.load(path2, allow_pickle=True)
        # except:
            

        data=data.item()['data']

        int_idx=int(text)
        if int_idx in self.dataframe3.index:
            path2=path2sv
            data=np.load(path2, allow_pickle=True)
            data=data.item()['data']

        for index, row in self.dataframe2.iterrows():
            if row['total_trial_num']==int_idx:
                on,off=row['trial_onset'],row['trial_offset']
                self.mydict['angle']=row['trial_increment']
                break
        
        if info[2]=='Bridge':
            bridge_json='./Flex/bridge_boundary/2021_Flex1_{}_{}_MCH-{}.json'.format(info[0],info[2],int(text))
            with open(bridge_json) as f:
                data1 = json.load(f)
                self.mydict['x1']=data1['x1']
                self.mydict['x2']=data1['x2']
                # self.logger.log(logging.DEBUG, bridge_json, extra={'qThreadName': ctname()})
        
        on=self.str2sec(on)-offset
        off=self.str2sec(off)-offset

        self.mydict['filename']=fileName
        self.mydict['filename1']=fileName1
        self.mydict['on']=on
        self.mydict['off']=off
        self.mydict['data']=data
        self.mydict['path_json']=path1
        self.mydict['path_data']=path2
        self.mydict['path_data_sv']=path2sv
        self.mydict['subj']=int(self.subject_combo.currentText()[1:])
        self.mydict['usr']=self.user_combo.currentText()
        self.mydict['slbr']=slbr
        self.mydict['trnu']=text
        self.mydict['path_csv']=path3
        self.mydict['user_path']=user_path
        
        if self.slope_or_bridge=='b':
            if int(self.subj[1:])<30:
                self.mydict['camera']='./camera/Flex1_S20-Bridge1.npy'
            else:
                self.mydict['camera']='./camera/Bridge_0723.npy'
        elif self.slope_or_bridge=='g':
            self.mydict['camera']='./camera/Bridge_0723.npy'
        elif self.slope_or_bridge=='s':
            self.mydict['camera']='./camera/Slope_0723.npy'

        self.setFile()
        if not self.mediaPlayer.isVisible():
            self.mediaPlayer.show()
        if not self.main3Dviewer.isVisible():
            self.main3Dviewer.show()
        self.cams=camera(self.mydict)
        # self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))


    def prepare_trials(self,args):
        # self.dataframe=pd.read_csv('Flex.csv')
        self.logger.log(logging.DEBUG, args.csv_name, extra={'qThreadName': ctname()})
        
        self.dataframe=pd.read_csv(args.csv_name)
        # self.dataframe=pd.read_csv('Flex_0919.csv')
        # self.dataframe=pd.read_csv('Flex_1023.csv')
        
        self.user_combo = QComboBox(self)
        self.user_combo.addItem('Christina')
        self.user_combo.addItem('Eva')
        self.user_combo.addItem('Lily')
        self.user_combo.addItem('Tieqiao')
        self.user_combo.addItem('Yasmine')
        # self.user_combo.addItem('Bob')
        self.user_combo.textActivated[str].connect(self.user_combo_onActivated)

        self.subject_combo = QComboBox(self)
        self.slbr_combo = QComboBox(self)
        self.trnu_combo = QComboBox(self)
        # for i in range(10):
        set_a=set(self.dataframe['subj'].tolist())
        lst_a=sorted(set_a)
        for subj in lst_a:
            self.subject_combo.addItem('S'+str(subj))
        self.subject_combo.textActivated[str].connect(self.subject_combo_onActivated)
        self.slbr_combo.textActivated[str].connect(self.slbr_combo_onActivated)
        self.trnu_combo.textActivated[str].connect(self.trnu_combo_onActivated)
        self.subject_combo_onActivated(self.subject_combo.currentText())

        self.TrialButton = QPushButton("", self)
        self.TrialButton.setEnabled(True)
        self.TrialButton.setIcon(QIcon('./icons/TrialButton.png'))
        self.TrialButton.enterEvent=lambda event: self.show_message("Go To The Next Trial | Key_9")
        self.TrialButton.leaveEvent = self.clear_message
        self.TrialButton.setShortcut(Qt.Key_9)
        self.TrialButton.clicked.connect(self.TrialAction)


        self.LeftButton = QPushButton("&Left", self)
        self.LeftButton.setEnabled(True)
        self.LeftButton.resize(10,3)
        self.LeftButton.setIcon(QIcon('./icons/LeftButton.png'))
        self.LeftButton.enterEvent=lambda event: self.show_message("New Left Foot | Key_0")
        self.LeftButton.leaveEvent = self.clear_message
        self.LeftButton.setShortcut(Qt.Key_0)
        
        self.LeftButton.clicked.connect(self.LeftAction)

        self.RightButton = QPushButton("&Right", self)
        self.RightButton.setEnabled(True)
        self.RightButton.setIcon(QIcon('./icons/RightButton.png'))
        self.RightButton.setShortcut(Qt.Key_Enter)
        self.RightButton.enterEvent=lambda event: self.show_message("New Right Foot | Key_Enter")
        self.RightButton.leaveEvent = self.clear_message
        self.RightButton.clicked.connect(self.RightAction)

        self.PrevButton = QPushButton("&Prev", self)
        self.PrevButton.setEnabled(True)
        self.PrevButton.setIcon(QIcon('./icons/PrevButton.png'))
        self.PrevButton.setShortcut(Qt.Key_Left)
        self.PrevButton.enterEvent=lambda event: self.show_message("Previous Step | Key_Left")
        self.PrevButton.leaveEvent = self.clear_message
        self.PrevButton.clicked.connect(self.PrevAction)


        self.NextButton = QPushButton("&Next", self)
        self.NextButton.setEnabled(True)
        self.NextButton.setIcon(QIcon('./icons/NextButton.png'))
        self.NextButton.setShortcut(Qt.Key_Right)
        self.NextButton.enterEvent=lambda event: self.show_message("Next Step | Key_Right")
        self.NextButton.leaveEvent = self.clear_message
        self.NextButton.clicked.connect(self.NextAction)


        self.RemoveButton = QPushButton("&Delete", self)
        self.RemoveButton.setEnabled(True)
        self.RemoveButton.setIcon(QIcon('./icons/RemoveButton.png'))
        self.RemoveButton.setShortcut(Qt.Key_Delete)
        self.RemoveButton.enterEvent=lambda event: self.show_message("Delete Step | Key_Delete")
        self.RemoveButton.leaveEvent = self.clear_message
        self.RemoveButton.clicked.connect(self.RemoveAction)

        self.ClearButton = QPushButton("&Clear", self)
        self.ClearButton.setEnabled(True)
        self.ClearButton.setIcon(QIcon('./icons/ClearButton.png'))
        self.ClearButton.enterEvent=lambda event: self.show_message("Clear All Estimates")
        self.ClearButton.leaveEvent = self.clear_message
        self.ClearButton.clicked.connect(self.ClearAction)

        self.SaveButton = QPushButton("&CSave", self)
        self.SaveButton.setEnabled(True)
        self.SaveButton.setIcon(QIcon('./icons/SaveButton.png'))
        self.SaveButton.enterEvent=lambda event: self.show_message("Complete Save | *")
        self.SaveButton.leaveEvent = self.clear_message
        self.SaveButton.setShortcut('*')
        self.SaveButton.clicked.connect(partial(self.SaveAction,0))

        self.PSaveButton = QPushButton("&PSave", self)
        self.PSaveButton.setEnabled(True)
        self.PSaveButton.setIcon(QIcon('./icons/PSaveButton.png'))
        self.PSaveButton.enterEvent=lambda event: self.show_message("Partial Auto Save")
        self.PSaveButton.leaveEvent = self.clear_message
        self.PSaveButton.clicked.connect(partial(self.SaveAction,1))

        self.UndoButton = QPushButton("&Undo", self)
        self.UndoButton.setEnabled(True)
        self.UndoButton.setShortcut(QKeySequence.Undo)
        self.UndoButton.setIcon(QIcon('./icons/UndoButton.png'))
        self.UndoButton.enterEvent=lambda event: self.show_message("Undo | Command + Z")
        self.UndoButton.leaveEvent = self.clear_message
        self.UndoButton.clicked.connect(self.UndoAction)

    def update_trnu_combo(self,part):
        text=self.trnu_combo.currentText()
        index_to_replace=self.trnu_combo.currentIndex()
        if part==0:
            text='C'+text[1:]
        elif part==1:
            text='P'+text[1:]
        else:
            text=' '+text[1:]

        if index_to_replace != -1:
            self.trnu_combo.setItemText(index_to_replace, text)  # Replace the item text

    # 0 complete
    # 1 part
    def SaveAction(self,part=0):
        ltxt='SaveAction {}'.format(self.mediaPlayer.thread.curr_frame)
        self.logger.log(logging.DEBUG, ltxt, extra={'qThreadName': ctname()})
        try:
            self.sliderPause()
            mydict=self.mydict
            self.dataframe3.loc[int(self.mydict['trnu'])] =\
                [mydict['subj'],mydict['slbr'],mydict['usr'], -1,-1,part]
            ltxt='{} {}'.format(self.mydict['path_csv'],part)
            self.logger.log(logging.DEBUG, ltxt, extra={'qThreadName': ctname()})
            self.dataframe3.to_csv(self.mydict['path_csv'], index=True)
            self.update_trnu_combo(part)
            self.main3Dviewer.SaveAction()
        except Exception as e:
            self.logger.log(logging.ERROR, e, extra={'qThreadName': ctname()})

    def UndoAction(self):
        ltxt='UndoAction {}'.format(self.mediaPlayer.thread.curr_frame)
        self.logger.log(logging.DEBUG, ltxt, extra={'qThreadName': ctname()})
        try:
            self.sliderPause()
            position=self.main3Dviewer.UndoAction()
            if position!=-1:
                self.setPosition(position)
                self.mediaPlayer.showImage()    
        except Exception as e:
            self.logger.log(logging.ERROR, e, extra={'qThreadName': ctname()})

    def reset3D(self):
        ltxt='reset3D {}'.format(self.mediaPlayer.thread.curr_frame)
        self.logger.log(logging.DEBUG, ltxt, extra={'qThreadName': ctname()})
        try:
            ltxt='reset3D {}'.format(self.mediaPlayer.thread.curr_frame)
            self.logger.log(logging.DEBUG, ltxt, extra={'qThreadName': ctname()})
            self.main3Dviewer.reset()
        except Exception as e:
            self.logger.log(logging.ERROR, e, extra={'qThreadName': ctname()})
    
    def TrialAction(self):
        self.logger.log(logging.DEBUG, 'TrialAction', extra={'qThreadName': ctname()})
        try:
            self.sliderPause()
            index = self.trnu_combo.currentIndex()
            total=self.trnu_combo.count()
            self.trnu_combo.setCurrentIndex((index+1)%total)
            # print("# location 8")
            self.trnu_combo_onActivated(self.trnu_combo.currentText())
        except Exception as e:
            self.logger.log(logging.ERROR, e, extra={'qThreadName': ctname()})

    def LeftAction(self):
        ltxt='LeftAction {}'.format(self.mediaPlayer.thread.curr_frame)
        self.logger.log(logging.DEBUG, ltxt, extra={'qThreadName': ctname()})
        try:
            self.main3Dviewer.AddAction('L')
        except Exception as e:
            self.logger.log(logging.ERROR, e, extra={'qThreadName': ctname()})
        # pass

    def RightAction(self):
        ltxt='RightAction {}'.format(self.mediaPlayer.thread.curr_frame)
        self.logger.log(logging.DEBUG, ltxt, extra={'qThreadName': ctname()})
        try:
            self.main3Dviewer.AddAction('R')
        except Exception as e:
            self.logger.log(logging.ERROR, e, extra={'qThreadName': ctname()})

    def PrevAction(self):
        ltxt='PrevAction {}'.format(self.mediaPlayer.thread.curr_frame)
        self.logger.log(logging.DEBUG, ltxt, extra={'qThreadName': ctname()})
        try:
            self.sliderPause()
            position = self.main3Dviewer.FindFrame(self.mediaPlayer.duration_on-1,-1)
            self.setPosition(position)
            self.mediaPlayer.showImage()
        except Exception as e:
            self.logger.log(logging.ERROR, e, extra={'qThreadName': ctname()})
    def NextAction(self):
        ltxt='NextAction {}'.format(self.mediaPlayer.thread.curr_frame)
        self.logger.log(logging.DEBUG, ltxt, extra={'qThreadName': ctname()})
        try:
            self.sliderPause()
            position = self.main3Dviewer.FindFrame(self.mediaPlayer.duration_off+1,1)
            self.setPosition(position)
            self.mediaPlayer.showImage()
        except Exception as e:
            self.logger.log(logging.ERROR, e, extra={'qThreadName': ctname()})
    
    def ToStartActionF(self):
        ltxt='ToStartActionF'
        self.logger.log(logging.DEBUG, ltxt, extra={'qThreadName': ctname()})
        try:
            print("immediately takes you to the start of the trial")
            self.sliderPause()
            # position = self.mediaPlayer.duration_on
            self.setPosition(self.mediaPlayer.duration_on)
            self.mediaPlayer.showImage()
        except Exception as e:
            self.logger.log(logging.ERROR, e, extra={'qThreadName': ctname()})

   
    
    def SwapLR(self):
        ltxt='SwapLR {}'.format(self.mediaPlayer.thread.curr_frame)
        self.logger.log(logging.DEBUG, ltxt, extra={'qThreadName': ctname()})
        try:
            t=self.mediaPlayer.thread.curr_frame
            data=self.mediaPlayer.thread.data
            box=data[t]['box']
            midpoint=data[t]['midpoint']
            if 'box_s' in data[t]:
                box_s=data[t]['box_s']
            else:
                box_s=set()
            for view_id in box:
                myres={'midpoint':defaultdict(dict),'box':defaultdict(dict)}
                # box swap
                if view_id in box_s:
                    box_s.remove(view_id)
                else:
                    box_s.add(view_id)
                for key in box[view_id]:
                    myres['midpoint'][view_id][1-key]=midpoint[view_id][key]
                    myres['box'][view_id][1-key]=box[view_id][key]
                box[view_id]=myres['box'][view_id]
                midpoint[view_id]=myres['midpoint'][view_id]
            data[t]['box_s']=box_s
            print("Swap all views")
            self.mediaPlayer.Box_Frame_Update()
        except Exception as e:
            self.logger.log(logging.ERROR, e, extra={'qThreadName': ctname()})
        

    def Boxes_On(self):
        ltxt='Boxes_On {}'.format(self.mediaPlayer.thread.curr_frame)
        self.logger.log(logging.DEBUG, ltxt, extra={'qThreadName': ctname()})
        try:
            self.mediaPlayer.thread.boxes_on= not self.mediaPlayer.thread.boxes_on
        except Exception as e:
            self.logger.log(logging.ERROR, e, extra={'qThreadName': ctname()})

    def RemoveAction(self):
        ltxt='RemoveAction {}'.format(self.mediaPlayer.thread.curr_frame)
        self.logger.log(logging.DEBUG, ltxt, extra={'qThreadName': ctname()})
        try:
            self.sliderPause()
            self.main3Dviewer.RemoveAction()
        except Exception as e:
            self.logger.log(logging.ERROR, e, extra={'qThreadName': ctname()})

    def ClearAction(self):
        ltxt='ClearAction {}'.format(self.mediaPlayer.thread.curr_frame)
        self.logger.log(logging.DEBUG, ltxt, extra={'qThreadName': ctname()})
        try:
            self.sliderPause()
            self.main3Dviewer.ClearAction()
            if self.mydict['trnu'] in self.dataframe3:
                self.dataframe3.drop(self.mydict['trnu'], inplace=True)
            self.update_trnu_combo(-1)
        except Exception as e:
            self.logger.log(logging.ERROR, e, extra={'qThreadName': ctname()})

    def setFile(self):

        self.mediaPlayer.set_file(self.mydict)
        self.mydict['duration_on']=self.mediaPlayer.duration_on
        self.mydict['duration_off']=self.mediaPlayer.duration_off
        self.main3Dviewer.set_file(self.mydict)
        self.UndoButton.setEnabled(True)
        self.playButton.setEnabled(True)
        self.playButtonS.setEnabled(True)
        self.playButtonSR.setEnabled(True)
        self.pauseButton.setEnabled(True)
        self.playBackButton.setEnabled(True)
        self.playBackButton1.setEnabled(True)
        self.playFrontButton.setEnabled(True)
        self.playFrontButton1.setEnabled(True)
        self.positionSlider.setRange(self.mediaPlayer.duration_on, self.mediaPlayer.duration_off)
        # for i,action in enumerate(self.viewAction):            
        #     if i == 0: action.setChecked(True)
        #     else: action.setChecked(False)
        # self.curr_views=[0]
        self.mediaPlayer.view = sorted(self.curr_views)
        self.mediaPlayer.thread.view = sorted(self.curr_views)
        self.mediaPlayer.showImage() 


    def show_message(self, message):
        self.statusBar().showMessage(message)

    def clear_message(self, event):
        self.statusBar().clearMessage()
    

    def menu_init(self):
        menuBar = self.menuBar()


        self.viewAction, self.curr_views = [], [0]
        for i in range(5):
            # Create exit action
            action = QAction('&Select View '+str(i), self, checkable=True)        
            # action.setShortcut(str(i))
            if i == 0: action.setChecked(True)
            else: action.setChecked(False)
            action.setStatusTip('Select view '+str(i))
            action.setData(i)
            action.triggered.connect(self.viewSelect)
            self.viewAction.append(action)

        self.viewMenu1 = menuBar.addMenu('&Player')
        for i in range(5):
            self.viewMenu1.addAction(self.viewAction[i])
            if i == 0:
                self.viewMenu1.addSeparator()

        self.viewMenu2 = menuBar.addMenu('&Top-down')
        self.action_menu_aux = QAction('&Auxiliary', self, checkable=True)        
        self.action_menu_aux.setChecked(True)
        # self.action_menu_aux.setData(1)
        self.action_menu_aux.triggered.connect(self.viewSelect2)
        self.action_menu_aux.setStatusTip('Show foot location for each frame')
        self.viewMenu2.addAction(self.action_menu_aux)

        self.action_menu_vtl = QAction('&Vertical', self, checkable=True)        
        self.action_menu_vtl.setChecked(False)
        # self.action_menu_vtl.setData(1)
        self.action_menu_vtl.triggered.connect(self.viewSelect2)
        self.action_menu_vtl.setStatusTip('Choose vertical or horizontal')
        self.viewMenu2.addAction(self.action_menu_vtl)
        # action.triggered.connect(self.viewSelect)
        # self.viewAction.append(action)

        self.viewMenu3 = menuBar.addMenu('&Action')
        # self.ToStartAction = QAction("ToStartAction", self)
        self.viewAction3=[]
        action = QAction('&ToStart')        
        action.setShortcut(Qt.Key_Plus)
        action.triggered.connect(self.ToStartActionF)
        action.setStatusTip('To the start of the trial | Key_Plus')
        self.viewAction3.append(action)
        

        action = QAction('&Reverse Play, 1.0X Speed')        
        action.setShortcut(Qt.Key_7)
        action.setStatusTip("Reverse Play, 1.0X Speed | Key_7")
        action.triggered.connect(lambda: self.play(1,-1))
        self.viewAction3.append(action)

        action = QAction('&Boxes on and off | Key_B', self, checkable=True)      
        action.setChecked(True)
        action.setShortcut(Qt.Key_B)
        action.setStatusTip("Boxes on and off")
        action.triggered.connect(self.Boxes_On)
        self.viewAction3.append(action)

        action = QAction('&L <-> R')        
        action.setShortcut(Qt.Key_S)
        action.setStatusTip("Swap Left and Right | Key_S")
        action.triggered.connect(self.SwapLR)
        self.viewAction3.append(action)

        action = QAction('&Exit')        
        action.setShortcut(Qt.Key_Escape)
        action.setStatusTip("Exit | Qt.Key_Escape")
        action.triggered.connect(qApp.quit) 
        self.viewAction3.append(action)
        for i in range(len(self.viewAction3)):
            self.viewMenu3.addAction(self.viewAction3[i])

        self.remove_menu = menuBar.addMenu('Remove')
        mystr='QWER'
        for i in range(4):
            # Create exit action
            action = QAction('&Remove '+str(i+1), self, checkable=True)
            action.setChecked(False)
            action.setStatusTip('Remove '+str(i+1))
            action.setData(i)
            action.setShortcut(QKeySequence(Qt.ShiftModifier + getattr(Qt, f"Key_{mystr[i]}")))
            
            # action.setShortcut(Qt.Key_Plus)
            action.triggered.connect(self.mediaPlayer.removeSelect)
            self.remove_menu.addAction(action)

        self.swap_menu = menuBar.addMenu('Swap')

        for i in range(4):
            # Create exit action
            action = QAction('&Swap View '+str(i+1), self, checkable=True)
            action.setChecked(False)
            action.setShortcut(QKeySequence(getattr(Qt, f"Key_{mystr[i]}")))
            # action.setStatusTip('Swap view '+str(i+1))
            action.setData(i)
            action.triggered.connect(self.mediaPlayer.swapSelect)
            self.swap_menu.addAction(action)


        self.viewMenu1.setEnabled(False)
        self.viewMenu2.setEnabled(False)
        self.viewMenu3.setEnabled(False)
        self.remove_menu.setEnabled(False)
        self.swap_menu.setEnabled(False)

    def viewSelect2(self):
        self.mediaPlayer.stop_video()
        self.main3Dviewer.action_menu_aux=self.action_menu_aux.isChecked()
        self.main3Dviewer.action_menu_vtl=self.action_menu_vtl.isChecked()
        self.main3Dviewer.adjust_window_size()

    def viewSelect(self):
        self.mediaPlayer.stop_video()
        view_id = self.sender().data()
        if view_id == 0:
            self.curr_views = [view_id]
        elif view_id == 5:
            self.curr_views = [view_id]
        else:
            if len(self.curr_views) == 1:
                if self.curr_views[0] == 0:
                    self.curr_views = [view_id]
                elif view_id not in self.curr_views: self.curr_views.append(view_id)
            else:
                if view_id not in self.curr_views: 
                    self.curr_views.pop(0)
                    self.curr_views.append(view_id)
                else: self.curr_views.remove(view_id)

        for i in range(5): 
            if i in self.curr_views: self.viewAction[i].setChecked(True)
            else: self.viewAction[i].setChecked(False)
        self.mediaPlayer.view = sorted(self.curr_views)
        self.mediaPlayer.thread.view = sorted(self.curr_views)
        self.mediaPlayer.update_last_image()

    def __init__(self, args):
        super(VideoWindow, self).__init__()

        
        self.logger= logger

        self.mydict=defaultdict()
        
        # print(args)
        # self.init()

        self.prepare_trials(args)
        self.setWindowTitle("3D Foot Position Correction") 
        self.setWindowIcon(QIcon('./icons/baby-boy.png'))
        self.move(200, 100)

        self.mediaPlayer = VideoApp(self)
        self.mediaPlayer.frame_id.connect(self.setPosition)
        self.main3Dviewer = ResultApp(self)
        self.menu_init()
        # Button
        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(QIcon('./icons/playButton.png'))
        self.playButton.setShortcut(Qt.Key_8)
        self.playButton.enterEvent=lambda event: self.show_message("Play | Key_8")
        self.playButton.leaveEvent = self.clear_message
        self.playButton.clicked.connect(lambda: self.play(1,1))

        self.playButtonS = QPushButton()
        self.playButtonS.setEnabled(False)
        self.playButtonS.setIcon(QIcon('./icons/playButtonS.png'))
        self.playButtonS.setShortcut(Qt.Key_6)
        self.playButtonS.enterEvent=lambda event: self.show_message("Play, 0.5X Speed | Key_6")
        self.playButtonS.leaveEvent = self.clear_message
        self.playButtonS.clicked.connect(lambda: self.play(0.5,1))

        self.playButtonSR = QPushButton()
        self.playButtonSR.setEnabled(False)
        self.playButtonSR.setIcon(QIcon('./icons/playButtonSR.png'))
        self.playButtonSR.setShortcut(Qt.Key_4)
        self.playButtonSR.enterEvent=lambda event: self.show_message("Reverse Play, 0.5X Speed | Key_4")
        self.playButtonSR.leaveEvent = self.clear_message
        self.playButtonSR.clicked.connect(lambda: self.play(0.5,-1))
        
        self.pauseButton = QPushButton()
        self.pauseButton.setEnabled(False)
        self.pauseButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.pauseButton.setShortcut(Qt.Key_5)
        self.pauseButton.enterEvent=lambda event: self.show_message("Pause | Key_5")
        self.pauseButton.leaveEvent = self.clear_message
        self.pauseButton.clicked.connect(self.pause)

        self.playBackButton = QPushButton()
        self.playBackButton.setEnabled(False)
        # self.playBackButton.setShortcut(Qt.Key_Left)
        self.playBackButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self.playBackButton.enterEvent=lambda event: self.show_message("5 Frame Backward")
        self.playBackButton.leaveEvent = self.clear_message
        self.playBackButton.clicked.connect(self.playback)

        self.playBackButton1 = QPushButton()
        self.playBackButton1.setEnabled(False)
        self.playBackButton1.setShortcut(Qt.Key_1)
        self.playBackButton1.setIcon(QIcon('./icons/playBackButton1.png'))
        self.playBackButton1.enterEvent=lambda event: self.show_message("1 Frame Backward | Key_1")
        self.playBackButton1.leaveEvent = self.clear_message
        self.playBackButton1.clicked.connect(self.playback1)

        self.playFrontButton = QPushButton()
        self.playFrontButton.setEnabled(False)
        # self.playFrontButton.setShortcut(Qt.Key_Right)
        self.playFrontButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))
        self.playFrontButton.enterEvent=lambda event: self.show_message("5 Frame Forward")
        self.playFrontButton.leaveEvent = self.clear_message
        self.playFrontButton.clicked.connect(self.playfront)

        self.playFrontButton1 = QPushButton()
        self.playFrontButton1.setEnabled(False)
        self.playFrontButton1.setShortcut(Qt.Key_3)
        self.playFrontButton1.setIcon(QIcon('./icons/playFrontButton1.png'))
        self.playFrontButton1.enterEvent=lambda event: self.show_message("1 Frame Forward | Key_3")
        self.playFrontButton1.leaveEvent = self.clear_message
        self.playFrontButton1.clicked.connect(self.playfront1)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderPressed.connect(self.sliderPause)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        self.positionSlider.sliderReleased.connect(self.setImageSlider)

        self.resetButton = QPushButton("&Reset View", self)
        self.resetButton.setEnabled(True)
        self.resetButton.setShortcut(Qt.Key_Space)
        self.resetButton.enterEvent=lambda event: self.show_message("Top-down View Reset | Key_Space")
        self.resetButton.leaveEvent = self.clear_message
        self.resetButton.setIcon(QIcon('./icons/resetButton.png'))
        self.resetButton.clicked.connect(self.reset3D)

        sceneBLayout = QVBoxLayout()
        sceneBLayout.addWidget(self.resetButton)
        # sceneBLayout.addWidget(self.clearRoomButton)

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        # controlLayout.addWidget(self.playBackButton)
        controlLayout.addWidget(self.playBackButton1)
        controlLayout.addWidget(self.playButtonSR)
        controlLayout.addWidget(self.pauseButton)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.playButtonS)
        controlLayout.addWidget(self.playFrontButton1)
        # controlLayout.addWidget(self.playFrontButton)
        controlLayout.addWidget(self.positionSlider)
        
        controlLayout.addLayout(sceneBLayout)

        control3DLayout = QHBoxLayout()
        control3DLayout.addWidget(self.user_combo,0.5)
        control3DLayout.addWidget(self.subject_combo,0.5)
        control3DLayout.addWidget(self.slbr_combo,0.5)
        control3DLayout.addWidget(self.trnu_combo,0.5)
        control3DLayout.addWidget(self.TrialButton,0.5)
        
        # control3DLayout.addWidget(self.ProtractorBox,0.5)
        control3DLayout.addWidget(self.LeftButton,1)
        control3DLayout.addWidget(self.RightButton,1)
        control3DLayout.addWidget(self.RemoveButton,1)
        control3DLayout.addWidget(self.PrevButton,1)
        control3DLayout.addWidget(self.NextButton,1)
        control3DLayout.addWidget(self.ClearButton,1)
        control3DLayout.addWidget(self.PSaveButton,1)
        control3DLayout.addWidget(self.SaveButton,1)
        control3DLayout.addWidget(self.UndoButton,1)
        
        view3DLayout = QVBoxLayout()
        # view3DLayout.addWidget(self.main3Dviewer)
        view3DLayout.addLayout(control3DLayout)


        view3Dwid = QWidget()
        view3Dwid.setLayout(view3DLayout)

        mainlayout = QVBoxLayout()
        mainlayout.addWidget(view3Dwid)
        mainlayout.addLayout(controlLayout)

        wid = QWidget(self)
        self.setCentralWidget(wid)
        wid.setLayout(mainlayout)

    def playback(self):
        ltxt='playback {}'.format(self.mediaPlayer.thread.curr_frame)
        self.logger.log(logging.DEBUG, ltxt, extra={'qThreadName': ctname()})
        try:
            self.sliderPause()
            position = max(self.mediaPlayer.duration_on, self.positionSlider.value() - 5)
            self.setPosition(position)
            self.mediaPlayer.showImage()
        except Exception as e:
            self.logger.error("An error occurred", exc_info=True)
    def playback1(self):
        ltxt='playback1 {}'.format(self.mediaPlayer.thread.curr_frame)
        self.logger.log(logging.DEBUG, ltxt, extra={'qThreadName': ctname()})
        try:
            if self.mediaPlayer.thread is None: return
            if self.mediaPlayer.thread._run_flag:
                self.mediaPlayer.stop_video()
            self.mediaPlayer.thread.run_one(-1)
        except Exception as e:
            self.logger.error("An error occurred", exc_info=True)

    def playfront(self):
        ltxt='playfront {}'.format(self.mediaPlayer.thread.curr_frame)
        self.logger.log(logging.DEBUG, ltxt, extra={'qThreadName': ctname()})
        try:
            self.sliderPause()
            position = min(self.mediaPlayer.duration_off, self.positionSlider.value() + 5)
            self.setPosition(position)
            self.mediaPlayer.showImage()
        except Exception as e:
            self.logger.error("An error occurred", exc_info=True)
    
    def playfront1(self):
        ltxt='playfront1 {}'.format(self.mediaPlayer.thread.curr_frame)
        self.logger.log(logging.DEBUG, ltxt, extra={'qThreadName': ctname()})
        try:
            if self.mediaPlayer.thread is None: return
            if self.mediaPlayer.thread._run_flag:
                self.mediaPlayer.stop_video()
            self.mediaPlayer.thread.run_one(1)
        except Exception as e:
            self.logger.error("An error occurred", exc_info=True)
    
    def play(self,speed=1,direction=1):
        ltxt='play {}'.format(self.mediaPlayer.thread.curr_frame)
        self.logger.log(logging.DEBUG, ltxt, extra={'qThreadName': ctname()})
        try:
            if self.mediaPlayer.thread is None: return
            if self.mediaPlayer.thread._run_flag:
                self.mediaPlayer.stop_video()
            self.mediaPlayer.start_video(speed,direction)
        except Exception as e:
            self.logger.error("An error occurred", exc_info=True)

    def pause(self):
        ltxt='pause {}'.format(self.mediaPlayer.thread.curr_frame)
        self.logger.log(logging.DEBUG, ltxt, extra={'qThreadName': ctname()})
        try:
            if self.mediaPlayer.thread is None: return
            if self.mediaPlayer.thread._run_flag:
                self.mediaPlayer.stop_video()  
        except Exception as e:
            self.logger.error("An error occurred", exc_info=True)
        # print("# location 7", self.mediaPlayer.thread.curr_frame)

    def sliderPause(self):
        # When slider is clicked
        self.mediaPlayer.stop_video()
        # self.playButton.setIcon(
        #         self.style().standardIcon(QStyle.SP_MediaPlay))
        
    def setImageSlider(self):
        # Update Image after slider release
        self.mediaPlayer.showImage()

    def setPosition(self, position):
        # When slider is moved
        self.positionSlider.setValue(position)
        self.mediaPlayer.setPosition(position)
        self.main3Dviewer.setPosition(position)
        if position+1==self.main3Dviewer.mydict['duration_off']:
            if int(self.mydict['trnu']) in self.dataframe3.index and len(self.main3Dviewer.stack)==0:
                pass
            else:
                self.SaveAction(part=1)
        # self.main3Dviewer.draw_frame(position, plot_vec = True)



def run(args):
    """
    run(video_file=None, att_file=None) function run the GUI for visualizaing video

    :video_file (Optionnal): video file to visualize, if nothing is provided the video wiget will be empty
    :att_file (Optionnal): attention file containing 3D data, if nothing is provided the 3D wigdet will just display the room
    :return: Nothing, the application ends when the GUI is closed
    """ 
    try:
        
        # os.makedirs(user_path, exist_ok=True)
        QtCore.QThread.currentThread().setObjectName('MainThread')
        # logging.getLogger().setLevel(logging.DEBUG)
        app = QApplication(sys.argv)
        # args='test_string'
        player = VideoWindow(args)
        rate=10
        player.resize(120*rate , (10)*rate)
        player.show()

        sys.exit(app.exec_())
    except Exception as e:
        logger.log(logging.ERROR, e, extra={'qThreadName': 'run'})
