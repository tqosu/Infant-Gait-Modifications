import pkg_resources
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np
import os
import cv2

from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QVector3D, QQuaternion, QMatrix4x4

from matplotlib import cm
from scipy.spatial import ConvexHull
from scipy import stats
import trimesh
# from .TexturedMesh import OBJ, GLMeshTexturedItem, MTL

SKELETON = [
    [1,3],[1,0],[2,4],[2,0],[0,5],[0,6],[5,7],[7,9],[6,8],[8,10],[5,11],[6,12],[11,12],[11,13],[13,15],[12,14],[14,16]
]

CocoColors = [[255, 0, 0], [255, 85, 0], [255, 170, 0], [255, 255, 0], [170, 255, 0], [85, 255, 0], [0, 255, 0],
              [0, 255, 85], [0, 255, 170], [0, 255, 255], [0, 170, 255], [0, 85, 255], [0, 0, 255], [85, 0, 255],
              [170, 0, 255], [255, 0, 255], [255, 0, 170]]

class View3D(gl.GLViewWidget):
    position_sig = pyqtSignal(np.ndarray)
    direction_sig = pyqtSignal(np.ndarray)
    attention_sig = pyqtSignal(np.ndarray)

    def __init__(self):
        super(View3D, self).__init__()    
        self.base_color = (1.0,0.0,0.0,1.0)
        self.base_color2 = (0.2,0.0,0.0,1.0)
        self.base_color_t = (0.8,0.8,0.8,1.0)   
        ## create three grids, add each to the view   
        xgrid = gl.GLGridItem()
        xgrid.setSize(x=50, y=40)
        self.addItem(xgrid)