# -*- coding: utf-8 -*-
"""
Created on Mon Apr 30 15:05:50 2018

@author: lenovo
"""
import pandas as pd
from pandas import Series,DataFrame

class OperateZaijian(object):
    
    def __init__(self,dir_base,dir_log):
        self.dir_base = dir_base
        self.dir_log = dir_log
        
    def updateProjectData(self,file_in,dir_in):
        pass
        
    def getZaijianData(self,file_in,dir_in='zaijian_in\\',dir_out='zaijian_ok\\',save=False):
        
        col_stays = [
            '序号',
            '工程编码',
            '工程名称',
            '立项年份',
            '一级专业',
            '二级专业',
            '投资渠道',
            '项目类型',
            '客户类型',
            '建设性质',
            '工程状态',
            '主项管理员',
            '工程管理员',
            '设计单位',
            '监理单位',
            '施工单位',
            '立项批复日期',
            '单项拆分日期',
            '设计批复日期(第一次)',
            '工程开工日期',
            '工程完工日期',
            '初验批复日期',
            '结算送审日期',
            '结算审计审定日期',
            '终验批复日期',
            '决算发起日期',
            '决算转固提交财务共享时间',
            '决算转固日期',
            '决算转固工程会计 ',
            '工程关闭日期',
            '设计批复金额',
            '累计资本性支出',
            '本年累计资本性支出',
            '预转固金额',
            '正式转固金额',
            '本年交付资产',
            '以前年度交付资产',
            '在建工程期末余额',
            '在建工程账面余额'
            ]
        
        
        print('--->开始处理在建工程表...')
        dats = pd.read_excel(self.dir_base + dir_in+file_in)
        print(' --->已导入建工程表'+file_in)
        col_alls = Series(dats.columns)
        col_drops = col_alls[-col_alls.isin(col_stays)]
        dats = dats.drop(col_drops,axis=1)
        if save:
            file_out = file_in.split('.')[0]+'-ok.xlsx'
            dats.to_excel(self.dir_out+file_out,header=True,index=False)
            print(' --->处理好的在建工程表已保存到:'+file_out)
        return dats