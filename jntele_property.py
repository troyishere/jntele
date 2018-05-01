# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 10:27:45 2017
无线网转固资源相关操作
@author: lenovo
"""
'''=============================================================='''    
from property.jntele_import_property import LteImport
from property.jntele_web_resource import LteWebResource
from property.jntele_print_property import LtePrint
from property.jntele_create_property import LteCreateProperty
from property.jntele_sap_property import LteSapProperty

class OperateLteProperty(object):
    '''无线网转固处理整合类'''
    def __init__(self):
        self.dir_base = 'zhuangu\\'
        self.dir_log = 'zhuangu\\log\\'
        
    '''生成LTE资源录入表'''    
    def createLteResource(self,file_in,
                          dir_in='',dir_out='create_ok\\',saveProp = True):
        op = LteCreateProperty(self.dir_base,self.dir_log)
        return op.createLteResource(file_in,dir_in,dir_out,saveProp)
    
    '''向资产基础管理文件追加资产条目'''
    def appendLteProperty(self,file_base,file_in,
                          dir_in='',dir_out='create_ok\\'):
        op = LteCreateProperty(self.dir_base,self.dir_log)
        return op.appendLteProperty(file_base,file_in,dir_in,dir_out)
    
    '''匹配资产管理文件资产对应物料信息'''
    def matchLteSapZhucai(self,file_base,file_sap,wbs_ids):
        op = LteSapProperty(self.dir_base,self.dir_log)
        return op.matchLteSapZhucai(file_base,file_sap,wbs_ids)
    
    '''将资产匹配资源ID'''
    def matchLteWebResource(self,file_base,wbs_ids):
        op = LteWebResource(self.dir_base,self.dir_log)
        return op.matchLteWebResource(file_base,wbs_ids)
    
    '''生成打印版的资产明细表'''
    def printLteProperty(self,file_base,wbs_ids,
                            dir_out = 'print_ok\\',saveOne=True):
        op = LtePrint(self.dir_base,self.dir_log)
        return op.printLteProperty(file_base,wbs_ids,dir_out,saveOne)
    
    '''生成转固导入表'''
    def operateLteImport(self,file_base,wbs_ids,
                         dir_in='import_old\\',dir_out='import_ok\\'):
        op = LteImport(self.dir_base,self.dir_log)
        return op.operateLteImport(file_base,wbs_ids,dir_in,dir_out)
    
    '''生成单站验收报告'''
    def getLteSingleReport(self,file_in,
                           dir_in='report_in\\',dir_out='report_ok\\'):
        op = LtePrint(self.dir_base,self.dir_log)
        return op.getLteSingleReport(file_in,dir_in,dir_out)
    
    '''生成总验收报告'''
    def getLteMultipleReport(self,file_in,
                          dir_in='report_in\\',dir_out='report_ok\\'):
        op = LtePrint(self.dir_base,self.dir_log)
        return op.getLteMultipleReport(file_in,dir_in,dir_out)
    
    '''生成通用验收报告'''
    def getCommonReport(self,wbs_id,fuze,wbs_info,dir_out='report_ok\\'):
        op = LtePrint(self.dir_base,self.dir_log)
        return op.getCommonReport(wbs_id,fuze,wbs_info,dir_out)
    
'''=============================================================='''             
if __name__ == '__main__':
    op = OperateLteProperty()
    
    # 生成资源录入表
#    tmp = op.createLteResource('LTE6-0416.xlsx')   
    #向资产基础管理文件追加资产条目
#    op.appendLteProperty('LTE六期资源录入0403.xlsx','LTE6-0416.xlsx')    
    wbs_ids = [
            '17SD018303003',
            '17SD018305001',
            '17SD018305002',
            '17SD018309001',
            '17SD018310001',
            '17SD018310002',
            '17SD018311002',
            '17SD018311003',
            '17SD018314001',
            '17SD018314002',
            '17SD018314003',
            '17SD018314004',
            '17SD018315001',
            '17SD018315002']
    # 匹配资源ID
    op.matchLteWebResource('LTE六期资源录入0403.xlsx',wbs_ids)
    op.matchLteSapZhucai('LTE六期资源录入0403.xlsx','gongcheng\\sap_ok\\SAP-LTE6-041902-ok.xlsx',wbs_ids)
    
    # 生成PDF版资产明细
#    wbs_ids = [
#        '17SD002342005'
#        ]
#    tmp = op.printLteProperty('LTE五期.xlsx',wbs_ids)
    
    # 生成导入表
#    wbs_ids = [
#        '17SD002342005'
#        ]
#    tmp = op.operateLteImport('LTE五期.xlsx',wbs_ids)
    
    #生成单站验收报告
#    single_name = 'single0408.xlsx'
#    op.getLteSingleReport(single_name)
    
    #生成总验收报告
#    multiple_name = 'multiple0416.xlsx'
#    op.getLteMultipleReport(multiple_name)
    
    #生成通用验收报告
#    op.getCommonReport('17SD018316001','谷中杰','LTE六期枢纽楼华为网管')
