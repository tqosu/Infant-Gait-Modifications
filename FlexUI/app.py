from email.policy import default
from PyQt5.QtCore import QDir, Qt
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLineEdit, QButtonGroup,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget,QMessageBox)
from PyQt5.QtWidgets import QMainWindow,  QAction, QRadioButton, QSplitter, QFrame, QCheckBox, QComboBox
from PyQt5.QtGui import QIcon, QIntValidator

import sys,json,os
# from DevEv1.Viewer3D.Viewer3DApp import View3D
from FlexUI.ViewerVideo.VideoWidgetApp import VideoApp
from FlexUI.ViewerVideo.ResultWidgetApp import ResultApp
import pandas as pd
from collections import defaultdict
import numpy as np
from functools import partial
from pathlib import Path

class VideoWindow(QMainWindow):

    def str2sec(self,string1):
        a1,b1,c1,d1=string1.split(':')
        a,b,c,d=float(a1),float(b1),float(c1),float(d1)
        abc=a*360+b*60+c+d/1000
        return abc
  
    def user_combo_onActivated(self,text):
        self.user=text
        self.slope_or_bridge=self.slbr_combo.currentText()
        self.slbr_combo_onActivated(self.slope_or_bridge)

    def subject_combo_onActivated(self,text):
        self.subj=text
        int_subj=int(text[1:])
        self.dataframe1=self.dataframe.loc[self.dataframe['subj']==int_subj]
        
        set_a=set(self.dataframe['slope_or_bridge'].tolist())
        set_a=sorted(list(set_a))
        self.slbr_combo.clear()
        for sb in set_a:
            if sb =='s':
                self.slbr_combo.addItem('Slope')
            else:
                self.slbr_combo.addItem('Bridge')
        self.slope_or_bridge=self.slbr_combo.currentText()
        self.slbr_combo_onActivated(self.slope_or_bridge)

    def slbr_combo_onActivated(self,text):
        self.slope_or_bridge=text[0].lower()
        self.dataframe2=self.dataframe1.loc[self.dataframe1['slope_or_bridge']==self.slope_or_bridge]
        
        set_a=list(set(self.dataframe2['total_trial_num'].tolist()))
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
               'angle':float, 'bridge_l':float, 'bridge_r':float,'partial':bool}
            self.dataframe3=pd.DataFrame(columns=columns_with_dtypes)
            self.dataframe3.rename_axis('total_trial_num', inplace=True)

        print(path3)
        for idx in set_a:
            int_idx=int(idx)
            # print(self.dataframe3.index)
            if int_idx in self.dataframe3.index:
                # print(self.dataframe3.loc[int_idx]['partial'])
                if self.dataframe3.loc[int_idx]['partial']==True:
                    padding='P'
                else:
                    padding='C'
                # self.mydict['angle']=self.dataframe3.loc[int_idx]['angle']
            else: 
                padding=' '
                # self.mydict['angle']=-1
            self.trnu_combo.addItem(padding+str(idx).zfill(2))

    # path3 is always user's
    # path2 change to user's when saving 
    # path1 is the offset doesn't matter
    def trnu_combo_onActivated(self,text):
        user_path='User/'+self.user_combo.currentText()+'/'

        text=text[1:]
        slbr=self.slbr_combo.currentText()
        # self.slbr_combo_onActivated(slbr)
        # print(self.subj,slbr,text)
        info=[self.subj,'',slbr]
        if slbr=='Slope':
            self.Protractor.setEnabled(True)
            self.PLine.setEnabled(True)
        else:
            self.Protractor.setEnabled(False)
            self.PLine.setEnabled(False)
        fileName = './Flex/dataset2/2021_Flex1_{}_{}_MCH.mp4'.format(info[0],info[2])
        fileName1 = './Flex/dataset/2021_Flex1_{}_SlopeProtractor.mp4'.format(info[0])

        # mixed view offset
        path1='./Flex/sync/2021_Flex1_{}_{}_MCH.json'.format(info[0],info[2])
        # print(path1)
        with open(path1) as f:
            data1 = json.load(f)
        # print(data1)
        offset=data1['start_time_seconds']

        pathdata='2021_Flex1_{}_{}_MCH-{}.npy'.format(info[0],info[2],text)
        path2='./Flex/box5_2/'+pathdata
        path2sv=user_path+pathdata
        
        os.makedirs(user_path, exist_ok=True)
        path3=user_path+'2021_Flex1_{}_{}_MCH.csv'.format(info[0],info[2])

        data=np.load(path2, allow_pickle=True)
        data=data.item()['data']

        int_idx=int(text)
        if int_idx in self.dataframe3.index:
            path2=path2sv
            self.mydict['angle']=self.dataframe3.loc[int_idx]['angle']
            if self.mydict['angle']!=-1:
                angle_str=str(self.mydict['angle'])
                self.PLine.setText(angle_str)
        else:
            self.mydict['angle']=-1
        for index, row in self.dataframe2.iterrows():
            if row['total_trial_num']==int_idx:
                on,off=row['trial_onset'],row['trial_offset']
                # print(row)
                break
        
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

        self.setFile()
        if not self.mediaPlayer.isVisible():
            self.mediaPlayer.show()
        # self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))


    def prepare_trials(self):
        # self.dataframe=pd.read_csv('Flex.csv')
        self.dataframe=pd.read_csv('Flex_0721.csv')
        
        self.user_combo = QComboBox(self)
        self.user_combo.addItem('Tieqiao')
        self.user_combo.addItem('Alice')
        self.user_combo.addItem('Bob')
        self.user_combo.addItem('Christina')
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
        # set_a=set(self.dataframe['subj'].tolist())
        # for index, row in self.dataframe.iterrows():
        #     a=row['Trial'].split('Ordinal ')[1]
        #     mystr='S'+str(row['Subject'])+', '+a.zfill(2)+', '+row['Apparatus'].rjust(6)+', '+str(row['Onset time']).zfill(9)+'-'+str(row['Offset time']).zfill(9)
        #     self.subject_combo.addItem(mystr)
        
        # self.subject_combo.textActivated[str].connect(self.onActivated)
        # self.subject_combo.setIcon(QIcon('./icons/dataset.png'))

        # self.ProtractorBox =QCheckBox("",self)
        # self.ProtractorBox.setEnabled(True)
        # self.ProtractorBox.setIcon(QIcon('./icons/Protractor.png'))
        # self.ProtractorBox.stateChanged.connect(self.ProtractorAction)

        self.TrialButton = QPushButton("", self)
        self.TrialButton.setEnabled(True)
        self.TrialButton.setIcon(QIcon('./icons/TrialButton.png'))
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
        self.ClearButton.clicked.connect(self.ClearAction)

        self.SaveButton = QPushButton("&CSave", self)
        self.SaveButton.setEnabled(True)
        self.SaveButton.setIcon(QIcon('./icons/SaveButton.png'))
        self.SaveButton.clicked.connect(partial(self.SaveAction,0))

        self.PSaveButton = QPushButton("&PSave", self)
        self.PSaveButton.setEnabled(True)
        self.PSaveButton.setIcon(QIcon('./icons/PSaveButton.png'))
        self.PSaveButton.clicked.connect(partial(self.SaveAction,1))

        # self.SCButton = QPushButton("&Shortcuts", self)
        # self.SCButton.setEnabled(True)
        # self.SCButton.setIcon(QIcon('./icons/SCButton.png'))
        # self.SCButton.clicked.connect(self.SCAction)

    # def SCAction(self):
    #     dlg = QMessageBox(self)
    #     dlg.setWindowTitle("Shortcuts")
    #     mysc=[]
    #     # mysc.append('Key_Up')
    #     # mysc.append('Key_Down')
    #     key='001 Key_Left:'.ljust(20)
    #     func='PlayBack - 5 frames'.ljust(50)
    #     mysc.append(key+func)

    #     key='002 Key_Right:'.ljust(20)
    #     func='PlayForward + 5 frames'.ljust(50)
    #     mysc.append(key+func)

    #     key='003 Key_Up:'.ljust(20)
    #     func='Add A Left Step'.ljust(50)
    #     mysc.append(key+func)

    #     key='004 Key_Down:'.ljust(20)
    #     func='Add A Right Step'.ljust(50)
    #     mysc.append(key+func)

    #     key='005 Key_Delete:'.ljust(20)
    #     func='Delete Step'.ljust(50)
    #     mysc.append(key+func)

    #     mystr='\n'.join(mysc)
    #     dlg.setText(mystr)
    #     button = dlg.exec()

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


    def SaveAction(self,part=0):
        self.sliderPause()
        mydict=self.mydict
        self.dataframe3.loc[int(self.mydict['trnu'])] =\
            [mydict['subj'],mydict['slbr'],mydict['usr'], mydict['angle'],-1,-1,part]
        print(self.mydict['path_csv'],part)
        self.dataframe3.to_csv(self.mydict['path_csv'], index=True)
        self.update_trnu_combo(part)
        self.main3Dviewer.SaveAction()

    def reset3D(self):
        self.main3Dviewer.reset()
    
    def TrialAction(self):
        self.sliderPause()
        index = self.trnu_combo.currentIndex()
        total=self.trnu_combo.count()
        self.trnu_combo.setCurrentIndex((index+1)%total)
        self.trnu_combo_onActivated(self.trnu_combo.currentText())
        # pass
        # self.main3Dviewer.AddAction('L')

    def LeftAction(self):
        self.main3Dviewer.AddAction('L')
        pass

    def RightAction(self):
        self.main3Dviewer.AddAction('R')
    
    def PrevAction(self):
        self.sliderPause()
        position = self.main3Dviewer.FindFrame(self.mediaPlayer.duration_on-1,-1)
        self.setPosition(position)
        self.mediaPlayer.showImage()
        
    def NextAction(self):
        self.sliderPause()
        position = self.main3Dviewer.FindFrame(self.mediaPlayer.duration_off+1,1)
        self.setPosition(position)
        self.mediaPlayer.showImage()

    def RemoveAction(self):
        self.sliderPause()
        self.main3Dviewer.RemoveAction()

    def ClearAction(self):
        self.sliderPause()
        self.main3Dviewer.ClearAction()
        if self.mydict['trnu'] in self.dataframe3:
            self.dataframe3.drop(self.mydict['trnu'], inplace=True)
        self.update_trnu_combo(-1)

    def setFile(self):

        self.mediaPlayer.set_file(self.mydict)
        self.mydict['duration_on']=self.mediaPlayer.duration_on
        self.mydict['duration_off']=self.mediaPlayer.duration_off
        self.main3Dviewer.set_file(self.mydict)
        self.playButton.setEnabled(True)
        self.playButtonS.setEnabled(True)
        self.playButtonSR.setEnabled(True)
        self.pauseButton.setEnabled(True)
        self.playBackButton.setEnabled(True)
        self.playBackButton1.setEnabled(True)
        self.playFrontButton.setEnabled(True)
        self.playFrontButton1.setEnabled(True)
        self.positionSlider.setRange(self.mediaPlayer.duration_on, self.mediaPlayer.duration_off)
        for i,action in enumerate(self.viewAction):            
            if i == 0: action.setChecked(True)
            else: action.setChecked(False)
        self.curr_views=[0]
        self.mediaPlayer.view = sorted(self.curr_views)
        self.mediaPlayer.thread.view = sorted(self.curr_views)
        self.mediaPlayer.showImage() 

    def PLineChanged(self, text):
        if text!='':
            self.mydict['angle']=float(text)
            print('angle: '+text)
            self.main3Dviewer.set_file(self.mydict)

    def show_message(self, message):
        self.statusBar().showMessage(message)

    def clear_message(self, event):
        self.statusBar().clearMessage()

    def __init__(self):
        super(VideoWindow, self).__init__()
        self.mydict=defaultdict()
        # self.init()
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
    
        self.Protractor = QAction('&Protractor', self, checkable=True)       
        self.Protractor.setStatusTip('Select Protractor')
        self.Protractor.setData(5)
        self.Protractor.triggered.connect(self.viewSelect)
        self.viewAction.append(self.Protractor)

        self.PLine=QLineEdit(self)
        self.PLine.setEnabled(False)
        self.PLine.textChanged[str].connect(self.PLineChanged)

        self.prepare_trials()
        self.setWindowTitle("Flex") 
        self.setWindowIcon(QIcon('./icons/baby-boy.png'))
        self.move(200, 100)

        self.mediaPlayer = VideoApp()
        self.mediaPlayer.frame_id.connect(self.setPosition)

        self.main3Dviewer = ResultApp()
        # self.main3Dviewer.frame_id.connect(self.setPosition)

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
        self.resetButton.setIcon(QIcon('./icons/resetButton.png'))
        self.resetButton.clicked.connect(self.reset3D)

        self.clearRoomButton = QCheckBox("&Hide scene", self)
        self.clearRoomButton.setEnabled(True)
        self.clearRoomButton.setChecked(False)
        # self.clearRoomButton.clicked.connect(self.main3Dviewer.clearRoom)


        menuBar = self.menuBar()
        # fileMenu = menuBar.addMenu('&File')
        # #fileMenu.addAction(newAction)
        # fileMenu.addAction(openAction)
        # fileMenu.addAction(exitAction)

        viewMenu = menuBar.addMenu('&View')
        for i in range(6):
            viewMenu.addAction(self.viewAction[i])
            if i == 0:
                viewMenu.addSeparator()

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
        # control3DLayout.addWidget(self.SCButton,1)
        control3DLayout.addWidget(self.PLine,0.5)
        # control3DLayout.addWidget(self.fillUpBox)
        
        view3DLayout = QVBoxLayout()
        view3DLayout.addWidget(self.main3Dviewer)
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
        self.sliderPause()
        position = max(self.mediaPlayer.duration_on, self.positionSlider.value() - 5)
        self.setPosition(position)
        self.mediaPlayer.showImage()
        return
    
    def playback1(self):
        if self.mediaPlayer.thread is None: return
        if self.mediaPlayer.thread._run_flag:
            self.mediaPlayer.stop_video()
        self.mediaPlayer.thread.run_one(-1)
        return

    def playfront(self):
        self.sliderPause()
        position = min(self.mediaPlayer.duration_off, self.positionSlider.value() + 5)
        self.setPosition(position)
        self.mediaPlayer.showImage()
        return
    
    def playfront1(self):
        if self.mediaPlayer.thread is None: return
        if self.mediaPlayer.thread._run_flag:
            self.mediaPlayer.stop_video()
        self.mediaPlayer.thread.run_one(1)

        # self.sliderPause()
        # position = min(self.mediaPlayer.duration_off, self.positionSlider.value() + 1)
        # self.setPosition(position)
        # self.mediaPlayer.showImage()
        return
    
    def play(self,speed=1,direction=1):
        if self.mediaPlayer.thread is None: return
        if self.mediaPlayer.thread._run_flag:
            self.mediaPlayer.stop_video()
        self.mediaPlayer.start_video(speed,direction)

    def pause(self):
        if self.mediaPlayer.thread is None: return
        if self.mediaPlayer.thread._run_flag:
           self.mediaPlayer.stop_video()
        # if self.mediaPlayer.thread._run_flag:
        #     self.mediaPlayer.stop_video()
        #     self.playButton.setIcon(
        #             self.style().standardIcon(QStyle.SP_MediaPlay))
        # else:
        #     self.mediaPlayer.start_video()
        #     self.playButton.setIcon(
        #             self.style().standardIcon(QStyle.SP_MediaPause))            

    def sliderPause(self):
        # When slider is clicked
        self.mediaPlayer.stop_video()
        # self.playButton.setIcon(
        #         self.style().standardIcon(QStyle.SP_MediaPlay))
        
    def setImageSlider(self):
        # Update Image after slider release
        self.mediaPlayer.showImage()
        return

    def setPosition(self, position):
        # When slider is moved
        self.positionSlider.setValue(position)
        self.mediaPlayer.setPosition(position)
        self.main3Dviewer.setPosition(position)
        if position+1==self.main3Dviewer.mydict['duration_off']:
            self.SaveAction(part=1)
        # self.main3Dviewer.draw_frame(position, plot_vec = True)

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
def run():
    """
    run(video_file=None, att_file=None) function run the GUI for visualizaing video

    :video_file (Optionnal): video file to visualize, if nothing is provided the video wiget will be empty
    :att_file (Optionnal): attention file containing 3D data, if nothing is provided the 3D wigdet will just display the room
    :return: Nothing, the application ends when the GUI is closed
    """ 
    app = QApplication(sys.argv)
    player = VideoWindow()
    rate=10
    player.resize(120*rate , (30)*rate)
    player.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()

