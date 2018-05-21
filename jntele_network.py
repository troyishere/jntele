# -*- coding: utf-8 -*-
"""
Created on Mon May  7 13:21:08 2018
无线网网管相关操作
@author: lenovo
"""

from network.jntele_lte_network import LteNetwork
import os

class OperateLteNetwork(object):
    def __init__(self):
        self.dir_base = 'wangguan\\'
        self.dir_log = 'log\\'
        self.op = LteNetwork(dir_base = self.dir_base,dir_log = self.dir_log)
    def getHuaweiLte(self,file_in,dir_in = 'cell_status\\',dir_out='data\\',base_design=True):
        return self.op.get_huawei_lte(file_in,dir_in,dir_out,base_design)
    
    def getNokiaLte(self,file_in,dir_in = 'cell_status\\',dir_out='data\\',base_design=True):
        return self.op.get_nokia_lte(file_in,dir_in,dir_out,base_design)
    
    def matchL800MBase(self,file_base,huawei_in,nokia_in,dir_out='data\\'):
        file = self.op.matchL800Mdats(file_base,huawei_in,nokia_in,dir_out)
        if file != '':
            os.popen(file)

    def matchLTECABase(self,file_base,huawei_in,nokia_in,dir_out='data\\'):
        file = self.op.matchLTECAdats(file_base,huawei_in,nokia_in,dir_out)
        if file != '':
            os.popen(file)

if __name__ == '__main__':
    op = OperateLteNetwork()
    huawei_in = 'lte_huawei_0507.xlsx'
    nokia_in = 'lte_nokia_0507.xlsx'
#    file_huawei = op.getHuaweiLte(huawei_in)
#    file_nokia = op.getNokiaLte(nokia_in)
    file_800_base = 'LTE800M建设总表20180508.xlsx'
    tmp = op.matchL800MBase(file_800_base,file_huawei,file_nokia)
#    file_lte_base = 'LTE1800M建设总表201805.xlsx'
#    tmp = op.matchLTECABase(file_lte_base,file_huawei,file_nokia)