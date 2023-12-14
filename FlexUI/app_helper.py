import numpy as np

import base64,json
import labelme

from scipy.optimize import least_squares
import cv2
import logging
def fun_rosenbrock(x,imgpoints,cams):
    residuals=[]
    for viewid in cams:
        if viewid not in imgpoints:
            continue

        imgpoints2, _ = cv2.projectPoints(x, cams[viewid]['r'], cams[viewid]['t'], cams[viewid]['mtx'], cams[viewid]['dist'])
        imgpoints2=np.array(imgpoints2).squeeze()

        residuals.extend(list(imgpoints2-imgpoints[viewid]))
    residuals=np.array(residuals)
    return residuals    

def spoint(cams,midpoints,key):
    imgpoints={}
    for viewid in midpoints:
        if key in midpoints[viewid]:
            imgpoints[viewid]=midpoints[viewid][key]
    if len(imgpoints.keys())<2:
        return None
    init_ans=np.array([0,0,0]).astype('float32')

    res_1 = least_squares(fun_rosenbrock,init_ans,args=(imgpoints,cams))
    # print(imgpoints)
    # print(cams)
    # print(res_1.x)
    return res_1.x
def get_depth(lst):
    if not isinstance(lst, list):
        return 0
    if not lst:  # an empty list has depth 1
        return 1
    return 1 + max(get_depth(item) for item in lst)

def to_labelme(mydict,logger):
    img_path=mydict['img_path']
    im=mydict['im']
    data = labelme.LabelFile.load_image_file(img_path)
    image_data = base64.b64encode(data).decode('utf-8')
    one_img_json = {}
    one_img_json['imageData'] = image_data
    one_img_json['imagePath'] = img_path
    one_img_json['flags']     = {}
    one_img_json['version']   = "5.3.1"
    one_img_json['imageWidth']  = im.shape[1]   # im.shape = (480, 640, 3)
    one_img_json['imageHeight'] = im.shape[0]
    RLdict={0:'R',1:'L'}
    shapes = []
    for key in mydict['polys']:
        polygon2=mydict['polys'][key]
        # polygon3=np.array(polygon2)
        if get_depth(polygon2)==2:
            polygon2=[polygon2]
            # polygon2 = convert_polygon(pmask.polygons)               
        # print(polygon2.shape)
        for one_polygon_points in polygon2:
            one_instance = {}
            one_instance['shape_type'] = 'polygon'
            one_instance['flags'] = {}
            one_instance['group_id'] = 1
            one_instance['label'] = RLdict[key]
            one_instance['points'] = one_polygon_points
            shapes.append(one_instance)
    one_img_json['shapes'] = shapes            
    json_output_filepath = img_path[:-4]+'.json'

    # json_output_filepath
    ltxt=json_output_filepath
    logger.log(logging.DEBUG, ltxt)
    with open(json_output_filepath, "w") as fp:
        json.dump(one_img_json, fp)

def camera(mydict):
    # print(args.camera)
    # print(mydict['camera'])
    filename1=mydict['camera']
    cams = {}
    data=np.load(filename1, allow_pickle=True).item()
    # print("# lcasd")
    # print(data)
    # h,w,_=im.shape
    h,w=mydict['h'],mydict['w']
    # 1. bridge 
    # front flip, center, corner, clock

    # mixed view
    # front   | clock
    # center  | corner
    # print()
    # print(mydict['slbr'])
    if mydict['slbr']=='Bridge' or mydict['slbr']=='Gaps':
        if len(data.keys())==3:
            key=0
            cams[key]=data[0]
            cams[key]['h'],cams[key]['w']=0,0

            key=2
            cams[key]=data[1]
            cams[key]['h'],cams[key]['w']=h,0

            key=3
            cams[key]=data[2]
            cams[key]['h'],cams[key]['w']=h,w
        elif len(data.keys())==4:            
            key=0
            cams[key]=data[0]
            cams[key]['h'],cams[key]['w']=0,0

            key=1
            cams[key]=data[3]
            cams[key]['h'],cams[key]['w']=0,w

            key=2
            cams[key]=data[1]
            cams[key]['h'],cams[key]['w']=h,0

            key=3
            cams[key]=data[2]
            cams[key]['h'],cams[key]['w']=h,w
    # front flip, angle, left, right

    # mixed view
    # left   | front 
    # angled | right
    
    elif mydict['slbr']=='Slope':
        key=0
        cams[key]=data[2]
        cams[key]['h'],cams[key]['w']=0,0

        key=1
        cams[key]=data[0]
        cams[key]['h'],cams[key]['w']=0,w

        key=2
        cams[key]=data[1]
        cams[key]['h'],cams[key]['w']=h,0

        key=3
        cams[key]=data[3]
        cams[key]['h'],cams[key]['w']=h,w

    return cams
