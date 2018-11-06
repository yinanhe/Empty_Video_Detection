#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import os
import numpy as np
import argparse
import subprocess
from itertools import izip
from PIL import Image
#from Tkinter import *
import tkMessageBox
#from tkinter.filedialog import askdirectory
import wx

my_path = '/home/'
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--videos_path",type = str ,default = my_path ,help="full path to the input videos")
args = vars(ap.parse_args())

# method 1 :
threshod = 35  # 有无目标的灵敏度参数，越小越灵敏
def pic_sub(s1_path,s2_path):
    s1 =  cv2.imread(s1_path,0)
    s2 =  cv2.imread(s2_path,0)
    if s1.shape == s2.shape:
        result = np.zeros(s1.shape,np.uint8)
        for i in range(s1.shape[0]):
            for j in range(s1.shape[1]):
                if (s2[i,j] > s1[i,j]):
                    result[i,j] = s2[i,j] - s1[i,j]
                else:
                    result[i,j] = s1[i,j] - s2[i,j]
                if(result[i,j] < threshod):
                    result[i,j] = 0
                else:
                    result[i,j] = 1
        return result
    else :
        return '错误：两张图片的格式不同！'


## method 2

def Difference(i1_path,i2_path):
    i1 =  Image.open(i1_path)
    i2 =  Image.open(i2_path)
    pairs = izip(i1.getdata(), i2.getdata())
    if len(i1.getbands()) == 1:
        # for gray-scale jpegs
        dif = sum(abs(p1-p2) for p1,p2 in pairs)
    else:
        dif = sum(abs(c1-c2) for p1,p2 in pairs for c1,c2 in zip(p1,p2))

    ncomponents = i1.size[0] * i1.size[1] * 3
    difference = np.round((dif / 255.0 * 100) / ncomponents,0)
    # print "Difference (percentage):{}".format(difference)
    return difference


def get_video_file_name(my_path):
    #print 222
    videos_list = [os.path.join(my_path,f) for f in os.listdir(my_path) if f.endswith('.AVI')]
    return videos_list

def video_key_frames_extract_and_empty_detection(video_file_name,my_path): 
    #print 333
    #path = args['videos_path']
    temp = video_file_name.split('/')[-1]
    temp = temp.split('.')[0]
    key_frame_file = os.path.join(my_path, 'key_frames')
    # create a folder
    if not os.path.exists(key_frame_file):
       print('Creating key frames output path {}'.format(key_frame_file))
       os.mkdir(key_frame_file)
    ffmpeg_command = "ffmpeg -i " + video_file_name + " -r 0.5 -s 300*300 " + os.path.join(key_frame_file,temp) + "-%03d.jpeg"
    child_out = subprocess.call(ffmpeg_command,shell = True)###此处可以以变量自动获取视频名称。
    imlist = [os.path.join(key_frame_file, f) for f in os.listdir(key_frame_file) if f.startswith(temp) and f.endswith('.jpeg')]
    print '获得突变帧图片数量为:{}张'.format(str(len(imlist)))

    # method 1 :
    ls = []
    for i in range(len(imlist) - 1):
        result = np.sum(pic_sub(imlist[i], imlist[i + 1]))
        ls.append(result)

    threshod_2 = 1000
    threshod_3 = 800
    if np.max(ls)< threshod_2 and np.average(ls)< threshod_3:
        print "视频里无目标"
        name_after_change = my_path+temp+'_NONE.AVI'
        os.rename(video_file_name, name_after_change)
    else:
        print "视频里有目标"

    # ## method 2 :
    # ls = []
    # for i in range(len(imlist) - 1):
    #     result = Difference(imlist[i], imlist[i + 1])
    #     ls.append(result)
    # threshod_2 = 0.75
    # if np.float(np.average(ls)) / np.max(ls) < threshod_2:
    #     print "视频里有目标"
    # else:
    #     print "视频里无目标"
    #     name_after_change = path+temp+'_NONE.AVI'
    #     os.rename(video_file_name, name_after_change)
    #
    print "max:{}".format(np.max(ls))
    # print "min:{}".format(np.min(ls))
    print "average:{}".format(np.average(ls))
    print "max - average:{}".format(np.max(ls)-np.average(ls))
    # print "ave/max:{}".format(np.float(np.average(ls)) / np.max(ls))
    print "ls:{}".format(ls)

class MyFrame(wx.Frame):
	def __init__(self):  
		wx.Frame.__init__(self, None, -1, '静态视频快速甄别软件', size=(794, 350))  
		panel = wx.Panel(self, -1)				
		pic = wx.Image("title.png",wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		#self.button =wx.BitmapButton(panel,-1,pic,pos=(0,0))
		#self.button.SetDefault()
		PicShow = wx.StaticBitmap(panel,-1,pic,pos=(0,0),size=(794,350))
		#self.Picshow.SetBitmap(wx.BitmaoFromImage(pic))
		#wx.StaticText(panel, -1, '静态视频快速筛选软件', pos=(380, 100))  
		wx.StaticText(panel, -1, '请输入或选择视频路径:', pos=(340, 100))  
		self.textctrl1 = wx.TextCtrl(panel, -1, '', pos=(340, 130),size=(150,-1))
		#self.write = wx.TextCtrl(panel, -1, style=wx.TE_MULTILINE)
		button_open = wx.Button(panel, -1, '打开路径',pos=(500,125))
		panel.Bind(wx.EVT_BUTTON, self.Inputpath,button_open) 
		button_start = wx.Button(panel, -1, '开始筛选',pos=(500,210))
		panel.Bind(wx.EVT_BUTTON, self.confirm,button_start)
		button_exit = wx.Button(panel, -1, '退出软件',pos=(500,250))
		panel.Bind(wx.EVT_BUTTON, self.exit,button_exit)
	def Inputpath(self,event):
		global my_path
		dlg=wx.DirDialog(self,'选择视频路径',style=wx.DD_DEFAULT_STYLE)
		if dlg.ShowModal() == wx.ID_OK:
			path_ = dlg.GetPath()
  	  		my_path = path_+'/'
		self.textctrl1.SetValue('%s' % my_path)
		dlg.Destroy()
	def exit(self,event):
		exit()
	def confirm(self,event):
		print my_path
		ap = argparse.ArgumentParser()
		ap.add_argument("-p", "--videos_path",type = str ,default = my_path ,help="full path to the input videos")
		args = vars(ap.parse_args())
		videos_list = get_video_file_name(my_path)
		print videos_list
		dlg = wx.SingleChoiceDialog(self,'请确认您路径下文件列表','视频列表',videos_list)
		#self.listbox = wx.ListBox(self,-1,pos=(10,10),size=(300,150),choices=videos_list,style = wx.LB_SINGLE)
		if dlg.ShowModal() == wx.ID_OK:
			self.detect(videos_list)
        	#self.list=wx.ListCtrl(self,-1,style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		#self.list.show(True)
		#self.list.InsertColumn(0,"视频列表")
		#vd_num =1
		#for index,vd in enumerate(videos_list):
		#	self.list.InsertStringItem(index,vd)		
	def detect(self,videos_list):
		print '程序开始甄别'	
		for vd in videos_list:
			video_key_frames_extract_and_empty_detection(vd, my_path)
		dlg = wx.MessageDialog(self,u'甄别完毕，甄别后空视频已标注至%s' % my_path,'Message box',wx.OK)
		if dlg.ShowModal() == wx.ID_OK:
			dlg.Destroy()

if __name__ == '__main__':
	app=wx.App()
	frame=MyFrame()
	frame.Show(True)
	app.MainLoop()
## 减小风和镜头移动的影响：调大threshod1（降低灵敏度），同时会导致夜晚的小目标找不到

## HC-6-25: 3 4 5 6 8 11 15 80 83 105 121 127  131 135 136 137 138 139 140   precision = 9/12  recall = 9/19

## HC-7-09: Ture: 5 6 7 8 11 14 16 24 25 26 28 33 34 35 36 37 38 40 41 42 63 67 69 70 71 87 88 94  96 102 103 110 121 124 128 131 132     recall = 31/37
        #           6 7 8 11 14 16 24 25 26 28 33   35 36 37 38    41 42 63 67 69 70 71 87 88 94      102 103    121     128 131 132     precision =  31/37   (34、96和124视频中有物体出现但没有捕捉到。5、110光影变化影响）
        #                    13               30                          62  64                                  115 117 118


## Y1= 30,Y2 = 2000， 19个真值检测出9个。16个    fps = 0.5
##     35，Y2 = 800， 19            8    11
#      35   Y3  2000  19            14
#      35  Y2 = 2000,Y3 = 1500      11    18
##     40      2000  1500           13    20
#      30      1000   800  7         5      8
#       35      1000    800          10     13    (效果最好）


#      20   Y2 = 2000,Y3 = 1500     6   8         fps = 0.2
#      25      2000  1500           8    11
#      30     2000  1500            9    13
#      35     2000  1500           11    18
#      40     2000  1500            11    18

#      20   Y2 = 2000,Y3 = 1500             fps = 1
#      25       2000    1500
#      30       2000    1500
#      35       2000    1500
#      40       1500     1000      11     16
