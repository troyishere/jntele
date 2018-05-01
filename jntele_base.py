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
    
    def __init__(self, wbs_in='wbs0316-ok.xlsx',dir_in='base\\'):
        self.dir_in = dir_in
#        print(os.getcwd())
#        print(os.path.abspath('.'))
        self.df_wbs = pd.read_excel(self.dir_in + wbs_in)
        self.df_danwei = pd.read_excel(self.dir_in + 'danwei.xlsx')
        
    @staticmethod
    def getTimeStr():
        return datetime.now().strftime("%Y%m%d%H%M%S")
    @staticmethod
    def getDateStr():
        return datetime.now().strftime("%Y%m%d")[2:]
    
    def getWBSName(self,wbs_id):
        '''获取工程编码对应的工程名'''
        dfs = self.df_wbs[self.df_wbs[wbs_base['wbs_id']]==wbs_id]
        ls = dfs[wbs_base['wbs_name']].tolist()
        if len(ls)==0:
            wbs_name = '2018年济南电信LTE主设备工程'
        else:
            wbs_name = ls[0]
        return wbs_name
    def getWBSId(self,wbs_name):
        pass
    
    def getWBSDates(self,wbs_id):
        '''获取工程编码对应的开工、完工、初验、终验时间'''
        dfs = self.df_wbs[self.df_wbs[wbs_base['wbs_id']]==wbs_id]
        dfs = dfs.fillna('')
        if dfs.shape[0] == 0:
            print('----> 未找到工程编码%s对应信息'%(wbs_id))
            return ['','','','']
        else:
            ls = dfs.loc[dfs.index[0]].values
            return [self.private_getDateStr(ls[2]),
                    self.private_getDateStr(ls[3]),
                    self.private_getDateStr(ls[4]),
                    '']
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
            dt = self.private_fromNum2Datetime(date_info)
        elif isinstance(date_info,float):
            '''输入为浮点数'''
            dt = self.private_fromNum2Datetime(int(date_info))
        elif isinstance(date_info,str):
            '''输入为字符串'''
            if date_info == '':
                print('----> 有未确定日期')
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
    base_operate = OperateBase()
#    wbs_name = base_operate.getWBSName('17SD002341003')
#    name = base_operate.getDanweiName('郭佳文')
#    nameAll = base_operate.getDanweiNameAll('郭佳文')
#    fuze = base_operate.getDanweiFuze('郭佳文')
    print(base_operate.getWBSDates('17SD018315001'))  
