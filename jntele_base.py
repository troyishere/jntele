# -*- coding: utf-8 -*-
"""
Created on Sun Apr  8 00:27:50 2018
LTE工程基础信息操作函数
@author: lenovo
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pandas import Series,DataFrame
from datetime import datetime
#import os
wbs_base = {
        'wbs_id':'工程编码',
        'wbs_name':'工程名称',
        'wbs_start':'工程开工日期',
        'wbs_end':'工程完工日期',
        'wbs_yanshou':'初验批复日期'    
        }
class LteBase(object):
    
    def __init__(self,wbs_in='wbs-ok.xlsx',dir_in='base\\'):
        self.dir_in = dir_in
        self.df_wbs = pd.read_excel(self.dir_in + wbs_in)
        self.df_danwei = pd.read_excel(self.dir_in + 'danwei.xlsx')
        self.base_col = [
                '工程编码',
                '工程名称',
                '工程开工日期',
                '工程完工日期',
                '初验批复日期',
                '终验批复日期',
                '工程状态',
                '设计批复金额'
                ]
#        print(os.path.abspath('.'))
    @staticmethod
    def getTimeStr():
        '''公共函数，获取当前时间字符串'''
        return datetime.now().strftime("%Y%m%d%H%M%S")
    @staticmethod
    def getDateStr():
        '''公共函数，获取当前日期字符串'''
        return datetime.now().strftime("%y%m%d")
    
    def getWBSName(self,wbs_id):
        '''获取工程编码对应的工程名称'''
        dfs = self.df_wbs[self.df_wbs[wbs_base['wbs_id']]==wbs_id]
        ls = dfs[wbs_base['wbs_name']].tolist()
        if len(ls)==0:
            print('---> %s未找到对应的工程信息，返回默认工程名称'%(wbs_id))
            wbs_name = '2018年济南电信LTE主设备工程'
        else:
            wbs_name = ls[0]
        return wbs_name
    
    
    def getWbsInvest(self,wbs_id):
        '''获取工程编码对应的工程投资'''
        dfs = self.df_wbs[self.df_wbs[wbs_base['wbs_id']]==wbs_id]
        ls = dfs['设计批复金额'].tolist()
        if len(ls)==0:
            print('---> %s未找到对应的工程投资，返回0'%(wbs_id))
            return 0
        return ls[0]
            

    
    def getWBSID(self,wbs_name):
        '''获取工程名称对应的工程编码'''
        dfs = self.df_wbs[self.df_wbs[wbs_base['wbs_name']]==wbs_name]
        ls = dfs[wbs_base['wbs_id']].tolist()
        if len(ls)==0:
            print('---> %s未找到对应的工程编码信息，返回默认工程编码'%(wbs_name))
            wbs_id = '18SDLTE001'
        else:
            wbs_id = ls[0]
        return wbs_id
        
    def getAllWBSId(self):
        '''获取在管控的所有工程编码'''
        return self.df_wbs[wbs_base['wbs_id']].tolist()
    
    def getWBSDates(self,wbs_id):
        '''获取工程编码对应的开工、完工、初验、终验时间'''
        dfs = self.df_wbs[self.df_wbs[wbs_base['wbs_id']]==wbs_id]
        dfs = dfs.fillna('')
        if dfs.shape[0] == 0:
            print('----> 未找到工程编码%s对应日期信息'%(wbs_id))
            return ['','','','']
        else:
            ls = dfs.loc[dfs.index[0]].values
            return [self.private_getDateStr(ls[2]),
                    self.private_getDateStr(ls[3]),
                    self.private_getDateStr(ls[4]),
                    self.private_getDateStr(ls[5])]
    
    def getChuyanDate(self,wbs_id):
        '''获取工程编码的初验时间'''
        dfs = self.df_wbs[self.df_wbs[wbs_base['wbs_id']]==wbs_id]
        dfs = dfs.fillna('')
        ls = dfs[wbs_base['wbs_yanshou']].tolist()
        if len(ls)==0:
            print('----> 未找到工程编码%s对应的初验日期,返回<空>'%(wbs_id))
            return ''
        return self.private_getDateStr(ls[0])
    
    def getDanwei(self,danwei):
        '''获取单位简称'''
        dfs= self.df_danwei.loc[:,danwei];
        tmp_df = np.array(dfs);
        name=tmp_df.tolist();
        return name[1];
        
    def getDanweiAll(self,danwei):
        '''获取单位全称'''
        dfs= self.df_danwei.loc[:,danwei];
        tmp_df = np.array(dfs);
        name=tmp_df.tolist();
        return name[0];
        
    def getDanweiFuze(self,danwei):
        '''获取单位负责人'''
        dfs= self.df_danwei.loc[:,danwei];
        tmp_df = np.array(dfs);
        name=tmp_df.tolist();
        return name[2];
    
    def private_getDateStr(self,date_info):

        if isinstance(date_info,int) or isinstance(date_info,np.int64):
            '''输入为数字'''
            dt = self.private_fromNum2Date(date_info)
        elif isinstance(date_info,float):
            '''输入为浮点数'''
            dt = self.private_fromNum2Date(int(date_info))
        elif isinstance(date_info,str):
            '''输入为字符串'''
            if date_info == '':
                return ''
            elif date_info.isdecimal():
                dt = self.private_fromNum2Date(int(date_info))
            elif '-' in date_info:
                dt = datetime.strptime(date_info, "%Y-%m-%d")
            elif '/' in date_info:
                dt = datetime.strptime(date_info, "%Y/%m/%d")
            elif '.' in date_info:
                dt = datetime.strptime(date_info, "%Y.%m.%d")
            else:
                print('----> [W]日期字符串为不识别格式%s'%(date_info))
                return ''
        elif isinstance(date_info,datetime):
            '''输入为datetime'''
            dt = date_info
        else:
            print('----> [W]日期数据为不识别格式%s'%type(date_info))
            return ''
        return dt.strftime("%Y-%m-%d")
    
    def private_fromNum2Date(self,date_int):
        day = date_int%100
        month = int(date_int/100)%100
        year = int(date_int/10000)
        if year < 100:
            year = year + 2000
        return datetime(year,month,day)
    
if __name__ == '__main__':
    op = LteBase()
#    print(LteBase.getTimeStr())
#    print(LteBase.getDateStr())
    wbs_id = '17SD018303003'
#    print(op.getWBSName(wbs_id))
#    wbs_name = '中国电信LTE六期工程济南800M无线网第六批基站主设备项目02批工程'
#    print(op.getWBSID(wbs_name))
#    print(op.getAllWBSId())
#    print(op.getWBSDates(wbs_id))
#    print(op.getChuyanDate(wbs_id))
    print(op.getWbsInvest(wbs_id))
