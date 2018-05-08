# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 01:01:59 2018
工程管理主入口文件
@author: lenovo
"""

import pandas as pd
from jntele_lte import OperateLteInfo
from jntele_spider import OperateHuanbao
from jntele_property import OperateLteProperty
from jntele_project import OperateLteProject
import datetime

if __name__ == '__main__':

    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    print('这是Troy的操作工具:%s'%(datetime.datetime.strftime(datetime.datetime.now(),"%d-%b-%Y")))
    ''' =================工程相关操作==========================='''
#    sap_file_in = 'LTE6-ALL-0502.xlsx'
#    zaijian_file_in = '在建工程明细总表(实时)导出(0504）.xlsx'
#    op = OperateLteProject()
#    op.getLteSapData(sap_file_in)
#    op.updateProjectBase(zaijian_file_in)       
    ''' =================转固相关操作==========================='''
#    op = OperateLteProperty() 
    ## 生成资源录入表
#    tmp = op.createLteResource('LTE6-0416.xlsx')   
    ## 生成资源录入表,并向资产基础管理文件追加资产条目
#    tmp = op.appendLteProperty('LTE六期资源录入0502.xlsx','LTE6-0504.xlsx')    
    wbs_ids = [
#            '17SD018303003',
#            '17SD018305001',
#            '17SD018305002',
#            '17SD018309001',
#            '17SD018310001',
#            '17SD018310002',
#            '17SD018311002',
#            '17SD018311003',
#            '17SD018314001',
#            '17SD018314002',
#            '17SD018314003',
#            '17SD018314004',
#            '17SD018315001',
#            '17SD018315002'
#            '17SD018303005',
#            '17SD018305003',

            ]
    ## 匹配资源ID
#    op.matchLteWebResource('LTE六期资源录入0502.xlsx',wbs_ids)
    ## 匹配SAP主材
#    op.matchLteSapZhucai('LTE六期资源录入0502.xlsx','gongcheng\\sap_ok\\LTE6-ALL-0502-ok.xlsx',wbs_ids)
    ## 生成资产明细
#    op.printLteProperty('LTE六期资源录入0502.xlsx',wbs_ids)
    
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
    

#    '''将JPG格式的验收报告扫描件命名格式化'''
#    op.matchYanshouImage()

#    '''将JPG格式无线网报账单添加签名'''    
#    wbs_ids = [
#            '17SD018315001',
#            '17SD018315002']
#    op.operateBaozhangImg(wbs_ids)
    
    '''网管数据相关操作'''
#    lteinfo_operate = OperateLteInfo()
#    huawei_in='lte_huawei_0507.xlsx'
##    nokia_in='lte_nokia_0424.xlsx'
#    huawei_out = lteinfo_operate.get_huawei_lte(huawei_in,base_design=True)
##    nokia_out = lteinfo_operate.get_nokia_lte(nokia_in,base_design=False)
##    lteinfo_operate.l_mix_dats(huawei_out,nokia_out)

    
    '''环保录入信息搜索操作'''
#    huanbao_operate = OperateHuanbao()
#    countys = ['平阴','历下','市中','槐荫','天桥','高新','历城','长清','平阴','济阳','商河','章丘']
#    huanbao_file = huanbao_operate.getJnteleWebInfo(countys=countys,date='2018-4-1',ifAll=True)
#    huanbao_operate.session.close()
#    huanbao_operate.matchJnteleInfo(key='济南电信LTE主设备项目',file_in='ALL20180409.xlsx',stations_in='stations2.xlsx')
    print('程序执行完成')
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
