# -*- coding: utf-8 -*-
"""
Created on Sun Apr 29 23:15:55 2018
无线网工程相关的操作
@author: lenovo
"""
from project.jntele_sap import OperateLteSAP
from project.jntele_zaijian import OperateZaijian
import os

class OperateLteProject(object):
    '''无线网工程操作处理整合类'''
    def __init__(self,wbs_in='wbs0316-ok.xlsx',dir_in='base\\'):
        self.dir_base = 'gongcheng\\'
        self.dir_log = 'gongcheng\\log\\'
    
    # 获取SAP相关数据    
    def getLteSapData(self,file_in,zhucai_file='lte_zhucai.xlsx',dir_in='sap_old\\',dir_out='sap_ok\\'):
        op = OperateLteSAP(self.dir_base,self.dir_log)
        file_out = op.getLteSapData(file_in,zhucai_file,dir_in,dir_out)
        os.popen(file_out)
    
    # 从在建工程表更新基础表
    def updateProjectBase(self,file_in,dir_in='zaijian_in\\',file_base = 'base\\wbs-ok.xlsx'):
        op = OperateZaijian(self.dir_base,self.dir_log)
        return op.updateProjectBase(file_in,dir_in,file_base)
    
if __name__ == '__main__':

    sap_file_in = 'LTE6-ALL-0502.xlsx'
    zaijian_file_in = '在建工程明细总表(实时)导出(0504）.xlsx'
    op = OperateLteProject()
    op.getLteSapData(sap_file_in)
#    op.updateProjectBase(zaijian_file_in)