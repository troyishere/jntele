# -*- coding: utf-8 -*-
"""
Created on Mon May  7 13:21:08 2018

@author: lenovo
"""

from network.jntele_lte_network import LteNetwork


if __name__ == '__main__': 
    
    op = LteNetwork(dir_base = 'wangguan\\',dir_log = 'wangguan\\log')
#    file_huawei = op.get_huawei_lte(file_in = 'lte_huawei_0507.xlsx')
#    file_nokia = op.get_nokia_lte(file_in = 'lte_nokia_0507.xlsx')
    file_base = 'LTE800M建设总表20180506.xlsx'
    dats = op.matchL800Mdats(file_base,file_huawei,file_nokia)