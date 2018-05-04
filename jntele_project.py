# -*- coding: utf-8 -*-
"""
Created on Sun Apr 29 23:15:55 2018
无线网工程相关的操作
@author: lenovo
"""
from project.jntele_sap import OperateLteSAP
import pandas as pd
import numpy as np
from datetime import datetime
from pandas import Series,DataFrame


wbs_base = {
        'wbs_id':'工程编码',
        'wbs_name':'工程名称',
        'wbs_start':'工程开工日期',
        'wbs_end':'工程完工日期',
        'wbs_yanshou':'初验批复日期'    
        }

class OperateLteProject(object):
    '''无线网工程操作处理整合类'''
    def __init__(self,wbs_in='wbs0316-ok.xlsx',dir_in='base\\'):
        self.dir_base = 'gongcheng\\'
        self.dir_log = 'gongcheng\\log\\'
        self.df_wbs = pd.read_excel(dir_in + wbs_in)
        self.df_danwei = pd.read_excel(dir_in + 'danwei.xlsx')
    
    # 获取SAP相关数据    
    def getLteSapData(self,file_in,zhucai_file='lte_zhucai.xlsx',dir_in='sap_old\\',dir_out='sap_ok\\'):
        op = OperateLteSAP(self.dir_base,self.dir_log)
        return op.getLteSapData(file_in,zhucai_file,dir_in,dir_out)
    
    def updateProjectData(self):
        pass
    
    
if __name__ == '__main__':

    sap_file_in = 'LTE6-ALL-0502.xlsx'
    op = OperateLteProject()
    op.getLteSapData(sap_file_in)