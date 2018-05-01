# -*- coding: utf-8 -*-
"""
Created on Sun Jan 14 01:01:59 2018
工程管理主入口文件
@author: lenovo
"""

import pandas as pd
from jntele_wbs import OperateSAP,OperateZaijian
from jntele_lte import OperateLteInfo
from jntele_spider import OperateHuanbao
from jntele_property import OperateLteProperty
#import csv 

if __name__ == '__main__':

    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    print('这是Troy的操作工具')
    
    '''SAP相关操作'''    
    sap_file_in = 'SAP-ZG-06P-0425.xlsx'
    sap_operate = OperateSAP()
    sap_operate.get_sap_data(sap_file_in)#处理格式
    sap_operate.get_sap_sum(sap_file_in)#SAP入账值
    sap_operate.get_sap_zhucai(sap_file_in)#主材列账
      
    '''在建工程相关操作'''
#    # 在建工程表相关操作
#    bianma_file_in = '在建工程明细总表(实时)导出0316.xlsx'
#    zaijian_operate = OperateZaijian()
#    zaijian_operate.get_zaijian_data(bianma_file_in)

    '''资源资产相关操作'''
#    ziyuan_operate = OperateZiyuan()
#    生成资源、资产录入信息
#    ziyuan_operate.get_ziyuan_data('LTE6-0416.xlsx')
#    ziyuan_operate.get_tianxian_data('0415-TX.xlsx')
#    wbs_ids = [
#                '17SD018305002',
#                '17SD018309001',
#                '17SD018310001',
#                '17SD018311002',
#                '17SD018311003',
#                '17SD018314001',
#                '17SD018314002',
#                '17SD018314003',
#                '17SD018314004',
#                '17SD018315001',
#                '17SD018315002',
##                '17SD018303003'
#            ]
#    ziyuan_operate.operate_web_data(wbs_ids)
#    
    '''网管数据相关操作'''
#    lteinfo_operate = OperateLteInfo()
#    huawei_in='lte_huawei_0424.xlsx'
#    nokia_in='lte_nokia_0424.xlsx'
#    huawei_out = lteinfo_operate.get_huawei_lte(huawei_in,base_design=True)
#    nokia_out = lteinfo_operate.get_nokia_lte(nokia_in,base_design=False)
#    lteinfo_operate.l_mix_dats(huawei_out,nokia_out)
    

    '''验收报告与资产明细相关操作'''
#    yanshou_operate = OperateYanshou()
#    single_name = 'single0408.xlsx'
#    multiple_name = 'multiple0416.xlsx'
#    zichan_name = 'zichan0416.xlsx'
#    yanshou_operate.getSingleYanshou(single_name)
#    yanshou_operate.getMultipleYanshou(multiple_name)
#    yanshou_operate.getZichanmingxi(zichan_name)
#    yanshou_operate.getCommonYanshou('17SD018311001','谷中杰','LTE六期无线网枢纽楼诺基亚网管')
    
    '''环保录入信息搜索操作'''
#    huanbao_operate = OperateHuanbao()
#    countys = ['平阴','历下','市中','槐荫','天桥','高新','历城','长清','平阴','济阳','商河','章丘']
#    huanbao_file = huanbao_operate.getJnteleWebInfo(countys=countys,date='2018-4-1',ifAll=True)
#    huanbao_operate.session.close()
#    huanbao_operate.matchJnteleInfo(key='济南电信LTE主设备项目',file_in='ALL20180409.xlsx',stations_in='stations2.xlsx')
    print('程序执行完成')
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
