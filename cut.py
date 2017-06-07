#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 16:33:04 2017

@author: ean2
根据hor.txt对数据进行层位分割
"""
import numpy as np
import pandas as pd
import os

class ReadHor(object):
    '读取层位文件hor.txt的有用信息'
    def __init__(self,fileadress):
        self.fileadress = fileadress
        self.filename = fileadress.split('/')[-1]
        print('Reading the file: ' + self.filename)
    def read(self):
        #该文件为txt格式，分隔符为‘\t’
        self.filedata = pd.read_csv(self.fileadress,sep='\t',header=0)
        print('The %s columns is: %s' %(self.filename,self.filedata.columns))
        self.LineName = list(set(self.filedata.LineName)) #得到LineName

class ReadSeisWave(object):
    '读取地震波形数据文件'
    '波形数据：行代表采集时间点，列代表道数'
    def __init__(self,fileadress):
        self.fileadress = fileadress #文件的位置
        self.filename = fileadress.split('/') #文件的名字
        print('Will read the file: %s' % self.filename)
    def getHead(self):
        '文件头存储着CDP与道数信息'
        f = open(self.fileadress,'rb')
        line0 = f.readline().strip().split('\t') #采样点数信息
        line1 = f.readline().strip().split('\t') #道数信息
        f.close()
        self.head = [eval(line0[-1]),eval(line1[-1])]
        return self.head
    def getNum(self):
        '读取数组信息（忽略前两行）'
        data = np.loadtxt(open(self.fileadress,'rb'),
                          delimiter='\t', skiprows=2)
        self.data = data.transpose() #转置后，行代表道数，列代表采集时间点，每行代表一道数据
        return self.data
        

class cutSeis(object):
    def __init__(self,horadress,foldadress,Top,Bot,HorName):
        self.horadress = horadress #hor.txt存放位置
        self.foldadress = foldadress #SeisWave存放位置
        self.Top = Top
        self.Bot = Bot #确定层位的顶和底
        self.HorName = HorName
        print('Cut the SeisWave as Top=%s, Bot=%s' % (self.Top,self.Bot))
    def action1(self,List1,List2):
        '从List1中删除属于List1但是不属于List2的元素'
        '判定hor.txt中LineName是否全部有SeisWave，缺失的LineName删除'
        return [element for element in List1 if element+'.txt' in List2]
    def action2(self,data,head,CDP_TB):
        'CDP_TB是含有CDP TOP BOT 三列数据的DataFrame'
        if CDP_TB['CDP'].max() > head[1]:
            CDP_TB = CDP_TB.loc[CDP_TB['CDP'] < head[1]+1,:]
        if CDP_TB.loc[:,-1].max() > head[0]:
            CDP_TB = CDP_TB.loc[CDP_TB.loc[:,-1] < head[0]+1,:]
        newData = []
        #循环截取data的对应层位数据
        for i in range(np.shape(CDP_TB)):
            newData.append(data[CDP_TB['CDP'][i]-1,
                                int(CDP_TB.loc[i,1]):int(CDP_TB.loc[i,2])])
            
        return newData
    def fit(self):
        '进行层位分割'
        hor = ReadHor(self.horadress)
        hor.read() # 读取层位信息
        horData = hor.filedata
        LineNameIn = self.action1(hor.LineName,os.list(self.foldadress))#得到共有的文件名
        for linename in LineNameIn:
            fileadress = self.foldadress + '/' + linename + '.txt' #循环设定需要读取扥文件名
            Wave = ReadSeisWave(fileadress)
            WaveHead = Wave.getHead()
            WaveData = Wave.getNum()
            CDP_TB = horData.loc[horData['LineName' == linename],['CDP',self.Top,self.Bot]]
            WaveHor = pd.DataFrame(self.action2(WaveData,WaveHead,CDP_TB),
                                   columns=self.HorName)
            WaveHor.to_excel('/'+'/'.join(self.foldadress.strip().split('/')[:-1])+
                             self.HorName + '/'+linename+'.xlsx')
            
            
            
            
            
        
if __name__ == '__main__':
    hor = ReadHor('/Users/ean2/Documents/Project/YZW/hor.txt')
    hor.read()
    Data = hor.filedata