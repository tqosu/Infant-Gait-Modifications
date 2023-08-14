from PyQt5.QtCore import QDir, Qt
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLineEdit, QButtonGroup,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget,QMessageBox)
from PyQt5.QtWidgets import QMainWindow,  QAction, QRadioButton, QSplitter, QFrame, QCheckBox, QComboBox
from PyQt5.QtGui import QIcon, QIntValidator

import sys,json
from DevEv1.Viewer3D.Viewer3DApp import View3D
from DevEv1.ViewerVideo.VideoWidgetApp import VideoApp
from DevEv1.ViewerVideo.ResultWidgetApp import ResultApp
import pandas as pd

import numpy as np

class VideoWindow(QMainWindow):

    def str2sec(self,string1):
        a1,b1,c1,d1=string1.split(':')
        a,b,c,d=float(a1),float(b1),float(c1),float(d1)
        abc=a*360+b*60+c+d/1000
        # print(a,b,c,abc)
        # abc1=(a1+b1).zfill(4)
        return abc
    # def init(self):
    # def str2sec(self,string1):
    #     a1,b1,c1=string1.split(':')
    #     a,b,c=float(a1),float(b1),float(c1)
    #     abc=a*60+b+c/1000
    #     #abc1=(a1+b1).zfill(4)
    #     return abc#,abc1


    def subject_combo_onActivated(self,text):
        self.subj=text
        int_subj=int(text[1:])
        self.dataframe1=self.dataframe.loc[self.dataframe['subj']==int_subj]
        
        set_a=set(self.dataframe['slope_or_bridge'].tolist())
        set_a=sorted(list(set_a))
        self.slbr_combo.clear()
        # self.slbr_combo.addItem('')
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
        
        set_a=set(self.dataframe2['total_trial_num'].tolist())
        self.trnu_combo.clear()
        for idx in set_a:
            self.trnu_combo.addItem(str(idx).zfill(2))
        # print(self.slope_or_bridge)




    def trnu_combo_onActivated(self,text):
        slbr=self.slbr_combo.currentText()
        print(self.subj,slbr,text)
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
        print(path1)
        with open(path1) as f:
            data1 = json.load(f)
        print(data1)
        offset=data1['start_time_seconds']

        path2='./Flex/box5_1/2021_Flex1_{}_{}_MCH-{}.npy'.format(info[0],info[2],text)
        data=np.load(path2, allow_pickle=True)
        data=data.item()['data']

        int_idx=int(text)
        for index, row in self.dataframe2.iterrows():
            if row['total_trial_num']==int_idx:
                on,off=row['trial_onset'],row['trial_offset']
                # print(row)
                break
        
        on=self.str2sec(on)-offset
        off=self.str2sec(off)-offset
        # print(info[3])
        # print(on,off)    
        mydict={'filename':fileName,'filename1':fileName1,
                 'on':on, 'off': off, 
                'data':data, 'path_json': path1, 'path_data' : path2,
                'slbr':slbr}
        self.setFile(mydict)
        if not self.mediaPlayer.isVisible():
            self.mediaPlayer.show()
       
        './Flex/box5_1/2021_Flex1_S17_Bridge_MCH-01.npy'
        './Flex/dataset2/2021_Flex1_{}_Bridge_MCH.mp4'
    # def ProtractorAction(self):
    #     if self.ProtractorAction.isChecked() == True:
    #         self.viewAction=[5]
    #     else:
    #         self.viewAction=[0]

    def prepare_trials(self):
        # self.dataframe=pd.read_csv('Flex.csv')
        self.dataframe=pd.read_csv('Flex_0721.csv')
        
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
        self.LeftButton.setShortcut(Qt.Key_Up)
        self.LeftButton.clicked.connect(self.LeftAction)

        self.RightButton = QPushButton("&Right", self)
        self.RightButton.setEnabled(True)
        self.RightButton.setIcon(QIcon('./icons/RightButton.png'))
        self.RightButton.setShortcut(Qt.Key_Down)
        self.RightButton.clicked.connect(self.RightAction)

        self.PrevButton = QPushButton("&Prev", self)
        self.PrevButton.setEnabled(True)
        self.PrevButton.setIcon(QIcon('./icons/PrevButton.png'))
        self.PrevButton.clicked.connect(self.PrevAction)

        self.NextButton = QPushButton("&Next", self)
        self.NextButton.setEnabled(True)
        self.NextButton.setIcon(QIcon('./icons/NextButton.png'))
        self.NextButton.clicked.connect(self.NextAction)


        self.RemoveButton = QPushButton("&Delete", self)
        self.RemoveButton.setEnabled(True)
        self.RemoveButton.setIcon(QIcon('./icons/RemoveButton.png'))
        self.RemoveButton.setShortcut(Qt.Key_Delete)
        self.RemoveButton.clicked.connect(self.RemoveAction)

        self.ClearButton = QPushButton("&Empty", self)
        self.ClearButton.setEnabled(True)
        self.ClearButton.setIcon(QIcon('./icons/ClearButton.png'))
        self.ClearButton.clicked.connect(self.ClearAction)

        self.SaveButton = QPushButton("&Save", self)
        self.SaveButton.setEnabled(True)
        self.SaveButton.setIcon(QIcon('./icons/SaveButton.png'))
        self.SaveButton.clicked.connect(self.SaveAction)

        self.SCButton = QPushButton("&Shortcuts", self)
        self.SCButton.setEnabled(True)
        self.SCButton.setIcon(QIcon('./icons/SCButton.png'))
        self.SCButton.clicked.connect(self.SCAction)

    def SCAction(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Shortcuts")
        mysc=[]
        # mysc.append('Key_Up')
        # mysc.append('Key_Down')
        key='001 Key_Left:'.ljust(20)
        func='PlayBack - 5 frames'.ljust(50)
        mysc.append(key+func)

        key='002 Key_Right:'.ljust(20)
        func='PlayForward + 5 frames'.ljust(50)
        mysc.append(key+func)

        key='003 Key_Up:'.ljust(20)
        func='Add A Left Step'.ljust(50)
        mysc.append(key+func)

        key='004 Key_Down:'.ljust(20)
        func='Add A Right Step'.ljust(50)
        mysc.append(key+func)

        key='005 Key_Delete:'.ljust(20)
        func='Delete Step'.ljust(50)
        mysc.append(key+func)

        mystr='\n'.join(mysc)
        dlg.setText(mystr)
        button = dlg.exec()

    def SaveAction(self):
        self.main3Dviewer.SaveAction()

    def reset3D(self):
        self.main3Dviewer.reset()
    
    def TrialAction(self):
        index = self.trnu_combo.currentIndex()
        total=self.trnu_combo.count()
        # print(index,total)
        self.trnu_combo.setCurrentIndex((index+1)%total)
        # print(self.trnu_combo.currentText())
        # pass
        # self.main3Dviewer.AddAction('L')

    def LeftAction(self):
        self.main3Dviewer.AddAction('L')

    def RightAction(self):
        self.main3Dviewer.AddAction('R')
    
    def PrevAction(self):
        self.sliderPause()
        # print(self.mediaPlayer.duration_on-1)
        position = self.main3Dviewer.FindFrame(self.mediaPlayer.duration_on-1,-1)
        self.setPosition(position)
        self.mediaPlayer.showImage()
        
    def NextAction(self):
        print('next')
        self.sliderPause()
        position = self.main3Dviewer.FindFrame(self.mediaPlayer.duration_off+1,1)
        self.setPosition(position)
        self.mediaPlayer.showImage()

    def RemoveAction(self):
        self.main3Dviewer.RemoveAction()

    def ClearAction(self):
        self.main3Dviewer.ClearAction()

    def setFile(self, mydict):
        print("# location 1")
        self.mediaPlayer.set_file(mydict)
        mydict['duration_on']=self.mediaPlayer.duration_on
        mydict['duration_off']=self.mediaPlayer.duration_off
        self.main3Dviewer.set_file(mydict)
        self.playButton.setEnabled(True)
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
        print(text)

    def __init__(self):
        super(VideoWindow, self).__init__()
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
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.playBackButton = QPushButton()
        self.playBackButton.setEnabled(False)
        self.playBackButton.setShortcut(Qt.Key_Left)
        self.playBackButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self.playBackButton.clicked.connect(self.playback)

        self.playBackButton1 = QPushButton()
        self.playBackButton1.setEnabled(False)
        # self.playBackButton1.setShortcut(Qt.Key_Left)
        self.playBackButton1.setIcon(QIcon('./icons/playBackButton1.png'))
        self.playBackButton1.clicked.connect(self.playback1)

        self.playFrontButton = QPushButton()
        self.playFrontButton.setEnabled(False)
        self.playFrontButton.setShortcut(Qt.Key_Right)
        self.playFrontButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))
        self.playFrontButton.clicked.connect(self.playfront)

        self.playFrontButton1 = QPushButton()
        self.playFrontButton1.setEnabled(False)
        # self.playFrontButton.setShortcut(Qt.Key_Right)
        self.playFrontButton1.setIcon(QIcon('./icons/playFrontButton1.png'))
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
        controlLayout.addWidget(self.playBackButton)
        controlLayout.addWidget(self.playBackButton1)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.playFrontButton1)
        controlLayout.addWidget(self.playFrontButton)
        controlLayout.addWidget(self.positionSlider)
        controlLayout.addLayout(sceneBLayout)

        control3DLayout = QHBoxLayout()
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
        control3DLayout.addWidget(self.SaveButton,1)
        control3DLayout.addWidget(self.SCButton,1)
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
        self.sliderPause()
        position = max(self.mediaPlayer.duration_on, self.positionSlider.value() - 1)
        self.setPosition(position)
        self.mediaPlayer.showImage()
        return

    def playfront(self):
        self.sliderPause()
        position = min(self.mediaPlayer.duration_off, self.positionSlider.value() + 5)
        self.setPosition(position)
        self.mediaPlayer.showImage()
        return
    
    def playfront1(self):
        self.sliderPause()
        position = min(self.mediaPlayer.duration_off, self.positionSlider.value() + 1)
        self.setPosition(position)
        self.mediaPlayer.showImage()
        return
    
    def play(self):
        if self.mediaPlayer.thread is None: return
        if self.mediaPlayer.thread._run_flag:
            self.mediaPlayer.stop_video()
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))
        else:
            self.mediaPlayer.start_video()
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))            

    def sliderPause(self):
        # When slider is clicked
        self.mediaPlayer.stop_video()
        self.playButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))
        
    def setImageSlider(self):
        # Update Image after slider release
        self.mediaPlayer.showImage()
        return

    def setPosition(self, position):
        # When slider is moved
        self.positionSlider.setValue(position)
        self.mediaPlayer.setPosition(position)
        self.main3Dviewer.setPosition(position)
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

