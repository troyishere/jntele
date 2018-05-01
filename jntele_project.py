# -*- coding: utf-8 -*-
"""
Created on Sun Apr 29 23:15:55 2018
无线网工程相关的操作
@author: lenovo
"""
from project.jntele_sap import OperateLteSAP

class OperateLteProject(object):
    '''无线网工程操作处理整合类'''
    def __init__(self):
        self.dir_base = 'gongcheng\\'
        self.dir_log = 'gongcheng\\log\\'
        
    # 获取SAP相关数据    
    def getLteSapData(self,file_in,zhucai_file='lte_zhucai.xlsx',dir_in='sap_old\\',dir_out='sap_ok\\'):
        op = OperateLteSAP(self.dir_base,self.dir_log)
        return op.getLteSapData(file_in,zhucai_file,dir_in,dir_out)
    
    def updateProjectData(self):
        pass
    
    
if __name__ == '__main__':

    sap_file_in = 'SAP-LTE6-041902.xlsx'
    op = OperateLteProject()
    op.getLteSapData(sap_file_in)