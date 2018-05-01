# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 13:45:00 2018

@author: lenovo
"""

import pandas as pd
import numpy as np
from pandas import Series,DataFrame
import warnings

def getformat(string,num=15):
    
    str_l = len(string)
    if str_l>=num:
        return str_l
    else:
        tmp = ''
        for i in range(num-str_l):
            tmp = tmp+' '
        return string+tmp
    
    

class OperateLteInfo(object):
    def __init__(self, dir_in='wangguan_old\\',dir_out='wangguan_ok\\'):
        self.dir_in = dir_in
        self.dir_out = dir_out
        
        self.huawei_col_names = [
                '站点类型',
                '基站名',
                'RRU名称',
                '信源名',
                '站号',
                'BBU名称',
                '小区名称',
                'BBU状态',
                'RRU状态',
                'RRU激活']
        self.nokia_col_names = [
                '站点类型',
                '基站名',
                'RRU名称',
                '信源名',
                '站号',
                'BBU名称',
                '小区名称',
                'BBU状态',
                'RRU状态',
                'RRU序号']
#        self.h800_names = pd.read_excel(dir_in+'lte_base.xlsx',sheetname = 'huawei_800m') 
#        self.n800_names = pd.read_excel(dir_in+'lte_base.xlsx',sheetname = 'nokia_800m')
        self.prosess_classes = {
                'h8':'华为800M',
                'hl':'华为LTE&CA',
                'n8':'诺基亚800M',
                'nl':'诺基亚LTE&CA'
                }
        
    def get_huawei_lte(self,file_in,base_design=True):
        file_name = self.dir_in+file_in
        print('****************************************')
        print('--> 开始处理华为数据,RRU状态判断依据为【可用状态】')
        dats = pd.read_excel(file_name)
        print('--> 已导入文件'+ file_name)
        print('****************************************')
        print('--> 开始处理小区，过滤掉无用小区')
        cell_names = dats['小区名称']
        selects = []#是否为要求小区
        station_types = []#小区分类（含CA，800M，高铁，普通，其他）
        for cell in cell_names:
            if '-H-O-' in cell:
                # 判断是否为NB小区或共享联通小区
                if '-NB' in cell or 'LO' in cell:
                    selects.append(False)
                    station_types.append('其他') 
                # 判断800M小区，即小区命名尾为-800M
                elif '800M' in cell:
                    selects.append(True)
                    station_types.append('800M')
                else:#普通小区
                    selects.append(True)
                    station_types.append('普通')
            elif '-H-G-' in cell:#高铁小区
                selects.append(True)
                station_types.append('高铁')
            elif '-H-OC1-' in cell:#含CA小区 
                selects.append(True)
                station_types.append('含CA')
            elif '-H-I' in cell:#室分小区
                selects.append(False)
                station_types.append('室分')
            else:
                print('--> INFO:未能判别小区类型  '+ cell)
                print('----暂不处理该小区...')
        dats['站点类型'] = station_types
        dats= dats[selects]#过滤掉不需要小区
        print('-->已过滤掉NB、室分、共享联通小区...')
        print('****************************************')
        print('-->开始处理合并小区...')
        cell_names = dats['小区名称']
        selectsC2 = []
        selectsC3 = []
        for cell in cell_names:
            if '-C2' in cell:#C2表示2小区合并
                selectsC2.append(True)
            else:
                selectsC2.append(False)
            if '-C3' in cell:#C3表示3小区合并
                selectsC3.append(True)
            else:
                selectsC3.append(False)
        datsC2 = dats[selectsC2]
        datsC3 = dats[selectsC3]
        print('-->C2类型的合并小区数为：'+str(datsC2.shape[0]))
        print('-->C3类型的合并小区数为：'+str(datsC3.shape[0]))
        dats = dats.append(datsC2)
        dats = dats.append(datsC3)
        dats = dats.append(datsC3)
        print('-->目前网管有数据室外小区数为：'+str(dats.shape[0]))
        print('-->已处理完合并小区...')
        dats = dats.drop(['分区','小区标识','管理状态','操作状态','本地小区标识'],axis=1)
        print('****************************************')
        print('-->开始获取站点名、信源名、RRU名')
        cell_names = dats['小区名称']
        xinyuan_names = []
        zhan_names = []
        rru_names = []
        for cell_name in cell_names:
            cell_zhanname,cell_xinyuan,cell_name_ok = self.get_cell_dat(cell_name)
            xinyuan_names.append(cell_xinyuan)
            zhan_names.append(cell_zhanname)
            rru_names.append(cell_name_ok)
        dats['RRU名称'] = rru_names
        dats['信源名'] = xinyuan_names
        dats['基站名'] = zhan_names
        print('-->已获取站点名、信源名、RRU名....')
        print('****************************************')
        print('-->开始处理BBU、RRU状态')
        dats = dats[['站点类型','基站名','RRU名称','信源名','eNodeB标识','LTE网元名称','小区名称','网元连接状态','可用状态','激活状态']]
        rru_status = dats['可用状态']
        rru_status_ok = []
        for rru_statu in rru_status:
            if rru_statu == '正常':
                rru_status_ok.append('ok')
            else:
                rru_status_ok.append('loss')
        bbu_status = dats['网元连接状态']
        bbu_status_ok = []
        for bbu_statu in bbu_status:
            if bbu_statu == '在线':
                bbu_status_ok.append('ok')
            else:
                bbu_status_ok.append('loss')
        rru_actives = dats['激活状态']
        rru_actives_ok = []
        for rru_active in rru_actives:
            if rru_active == '激活':
                rru_actives_ok.append('ok')
            else:
                rru_actives_ok.append('un')
        dats['可用状态'] = rru_status_ok
        dats['网元连接状态'] = bbu_status_ok
        dats['激活状态'] = rru_actives_ok
        print('-->处理BBU、RRU状态完成')
        print('****************************************')
        dats.columns = self.huawei_col_names   
        print('-->基础数据处理完成。。。')
        file_out = file_in[0:(len(file_in)-5)]+'-ok.xlsx'
        writer = pd.ExcelWriter(self.dir_out+file_out)
        dats.to_excel(writer,'ok',header=True,index=False)
        
#        writer.save()
        dats = dats.drop(['RRU激活'],axis = 1)#留待处理激活状态
        print('-->基础数据已保存到：'+ file_out )
        print('****************************************')
        
        dats = dats.drop(['小区名称'],axis = 1)
        print('-->开始处理LTE800M数据')
        dats_800 = dats[dats['站点类型'] == '800M']
        dats_800 = dats_800.drop(['站点类型'],axis=1)
        dats_800 = self.private_online_status(dats_800,'h8',base_design)
        dats_800.to_excel(writer,'800m',header=True,index=False)
        print('-->LTE800M数据处理完成，已保存')
        print('****************************************')
        print('-->开始处理LTE1800M&CA数据')
        dats_lte = dats[dats['站点类型'] != '800M']
        dats_lte = dats_lte.drop(['站点类型'],axis=1)
        dats_lte = self.private_online_status(dats_lte,'hl',base_design)
        dats_lte.to_excel(writer,'1800m&ca',header=True,index=False)
        print('-->LTE1800M&CA数据处理完成，已保存')
        print('****************************************')
        print('|设备类型|网管RRU数|在服RRU数|RRU在服率|网管站点数|正常站点数|部分扇区故障|RRU脱管|BBU脱管|')
        writer.save()
        return file_out
        
    
    
    def get_nokia_lte(self,file_in,base_design=True):
        
        file_name = self.dir_in+file_in
        print('****************************************')
        print('--> 开始处理诺基亚数据')
        dats = pd.read_excel(file_name)
        print('--> 已导入文件'+ file_name)
        print('****************************************')
        print('--> 开始处理小区，过滤掉无用小区')
        dats = dats[dats['站型']=='宏站']
        dats = dats[['RRH类型',	'ENBID','站名','小区名',	'RMODNO','MODULE_STATE','BBU_STATE']]
        dats.columns = ['站点类型','站号','BBU名称','小区名称',	'RMODNO','MODULE_STATE','BBU_STATE']
        print('--> 已保留800M/1.8G/2.1G室外小区')
        print('****************************************')
        print('-->开始获取站点名、信源名、RRU名')
        cell_names = dats['小区名称']
        xinyuan_names = []
        zhan_names = []
        rru_names = []
        for cell_name in cell_names:
            cell_zhanname,cell_xinyuan,cell_name_ok = self.get_cell_dat(cell_name)
            xinyuan_names.append(cell_xinyuan)
            zhan_names.append(cell_zhanname)
            rru_names.append(cell_name_ok)
        dats['基站名'] = zhan_names
        dats['RRU名称'] = rru_names
        dats['信源名'] = xinyuan_names
        print('-->已获取站点名、信源名、RRU名....')
        print('****************************************')
        print('-->开始获取RRU序号')
        cell_nums = dats['RMODNO']
        cell_nums_ok = []
        for cell_num in cell_nums:
            cell_nums_ok.append(cell_num.split('-')[-1])
        dats['RRU序号'] = cell_nums_ok
        print('-->已获取RRU序号....')
        dats = dats.drop(['RMODNO'],axis=1)
        print('****************************************')
        print('-->开始处理BBU、RRU状态')
        rru_status = dats['MODULE_STATE']
        rru_status_ok = []
        for rru_statu in rru_status:
            if rru_statu == '在服':
                rru_status_ok.append('ok')
            else:
                rru_status_ok.append('loss')
                
        dats = dats.drop(['MODULE_STATE'],axis = 1)
        dats['RRU状态'] = rru_status_ok
        
        bbu_status = dats['BBU_STATE']
        bbu_status_ok = []
        for bbu_statu in bbu_status:
            if bbu_statu == '在服':
                bbu_status_ok.append('ok')
            else:
                bbu_status_ok.append('loss')
        dats = dats.drop(['BBU_STATE'],axis = 1)
        dats['BBU状态'] = bbu_status_ok
        print('-->处理BBU、RRU状态完成')
        print('-->基础数据处理完成。。。')
        dats = dats[self.nokia_col_names]
        file_out = file_in[0:(len(file_in)-5)]+'-ok.xlsx'
        writer = pd.ExcelWriter(self.dir_out+file_out)
        dats.to_excel(writer,'ok',header=True,index=False)
    #    writer.save()
        print('-->基础数据已保存到：'+ file_out )
        print('****************************************')
        dats = dats.drop(['小区名称','RRU序号'],axis = 1)
        print('-->开始处理LTE800M数据')
        dats_800 = dats[dats['站点类型'] == '800M']
        dats_800 = dats_800.drop(['站点类型'],axis=1)
        dats_800 = self.private_online_status(dats_800,'n8',base_design)
        dats_800.to_excel(writer,'800m',header=True,index=False)
        print('-->LTE800M数据处理完成，已保存')
        print('****************************************')
        print('-->开始处理LTE1800M&CA数据')
        dats_lte = dats[dats['站点类型'] != '800M']
        dats_lte = dats_lte.drop(['站点类型'],axis=1)
        dats_lte = self.private_online_status(dats_lte,'nl',base_design)
        dats_lte.to_excel(writer,'1800m&ca',header=True,index=False)
        
        print('-->LTE1800M&CA数据处理完成，已保存')
        writer.save()
        print('****************************************')
        return dats_lte
    
    def l_mix_dats(self,huawei_in,nokia_in):
        '''非完整函数'''
        huawei_dats = pd.read_excel(self.dir_out+huawei_in,sheetname='800m')
        huawei_changjias = ['华为800M' for info in huawei_dats['站点类型']]
        huawei_dats['站点类型'] = huawei_changjias
        print(huawei_dats.shape)
        nokia_dats = pd.read_excel(self.dir_out+nokia_in,sheetname='800m')
        nokia_changjias = ['诺基亚800M' for info in nokia_dats['站点类型']]
        nokia_dats['站点类型'] = nokia_changjias
        dats_ok = huawei_dats.append(nokia_dats)
        dats_ok.to_excel(self.dir_out+'041902.xlsx',header=True,index=False)
        return dats_ok
        
        
        
    def get_cell_dat(self,cell_name):
        
        cell_dats = cell_name.split('-')
        cell_xinyuan = cell_dats[2]
        cell_zhanname = cell_dats[3]
        cell_name_ok = cell_dats[0]+'-'+cell_dats[1]+'-'+cell_dats[2]+'-'+cell_dats[3]
        
        return cell_zhanname,cell_xinyuan,cell_name_ok
    
    def private_judge_name_repeat(self,dats):
        '''判断设计名对应不同的小区名'''
        print('---> 开始判断设计名是否对应不同的网管名')
        dats_repeat = dats[['设计名','基站名','RRU名称',]]
        for design_name in dats_repeat['设计名'].unique():
            dats_tmp = dats_repeat[dats_repeat['设计名']==design_name]
            if dats_tmp.shape[0]>1:
                print('==> %s发现不同网管名:'%(design_name))
#                for i in range(dats_tmp.shape[0]):
                for i,(station_name,rru_name) in enumerate(zip(dats_tmp['基站名'],dats_tmp['RRU名称'])):
                    print('===> %1d: %s||%s'%(i+1,getformat(station_name),rru_name))
        
        
    
    def private_online_status(self,dats,c = 'h8',base_design = True):
        '''提取RRU状态信息'''
        process_shuoming = self.prosess_classes[c]
        print('======= 进入%s在服信息处理函数  ========'%(process_shuoming))
        
        print('--->开始获取设计名信息')
        dats_design = pd.read_excel(self.dir_in+'lte_base.xlsx',sheetname = c)
        design_names = []
        for station_name in dats['基站名']:
            nname = dats_design[dats_design['网管基站名']==station_name]
            if nname.shape[0] == 0:
                print('---> %s网管名%s未找到对应设计名，以【】做标记'%(process_shuoming,station_name))
                design_names.append('【%s】'%(station_name))
            elif nname.shape[0] >= 1:
                if nname.shape[0] > 1:
                    print('---> %s网管名<%s>找到多于一个设计名，默认使用第一个'%(process_shuoming,station_name))
                design_names.append(nname.loc[nname.index[0]][2])
        xinyuan_design = pd.read_excel(self.dir_in+'lte_base.xlsx',sheetname = 'xinyuan')
        dats['设计名'] = design_names
        print('--->获取设计名信息完成。。。')
        print('--->开始获取基站RRU数目、RRU在服数目')
        
        base_name = '设计名' if base_design else 'RRU名称'
        print('----> 以[%s]为依据统计在服信息'%(base_name))
        rru_infos = dats[[base_name,'RRU状态']]
        rru_names = dats[base_name]
        rru_nums = []#RRU总数
        rru_nums_ok = []#正常的RRU数目
        for rru_name in rru_names:
            dats_tmp = rru_infos.loc[rru_infos[base_name] == rru_name]
            rru_nums.append(dats_tmp.shape[0])#网管RRU数
            rru_nums_ok.append((dats_tmp.loc[dats_tmp['RRU状态'] == 'ok']).shape[0])#网管正常的RRU数
        warnings.filterwarnings('ignore')
        dats['网管RRU数'] = rru_nums
        dats['在服RRU数'] = rru_nums_ok
        warnings.filterwarnings('default')
        dats = dats.drop(['RRU状态'],axis = 1)
        dats = dats.drop_duplicates()#删除重复项
        print('--->已获取基站RRU数目、RRU在服数目。。。')
        print('--->开始获取基站网管状态')
        station_status = []
        rru_nums_ok = []
        for bbu_statu,rru_num,rru_num_ok in zip(dats['BBU状态'],dats['网管RRU数'],dats['在服RRU数']):
            if bbu_statu == 'loss':
                station_status.append('BBU脱管')
                rru_nums_ok.append(0)
            else:
                rru_nums_ok.append(rru_num_ok)
                if rru_num_ok == 0:
                    station_status.append('RRU脱管')
                elif rru_num == rru_num_ok:
                    station_status.append('正常')
                else:
                    station_status.append('部分扇区故障')
        dats['在服RRU数'] = rru_nums_ok
        dats['基站状态'] = station_status
        dats = dats.drop(['BBU状态'],axis = 1)                                
        print('--->获取网管状态完成。。。')
        print('======= 退出%s基站在服信息处理函数 ========='%(process_shuoming))
        
        
        if c=='h8' or c=='n8':
            print('--->开始获取信源设计名信息')
            xinyuan_names = []
            for xinyuan in dats['信源名']:
                dats_xinyuan = xinyuan_design[xinyuan_design['网管信源']==xinyuan]
                if dats_xinyuan.shape[0] == 0:
                    print('---> %s信源名<%s>未找到对应设计信源站，返回<空>'%(process_shuoming,xinyuan))
                    xinyuan_names.append('<空>')
                elif dats_xinyuan.shape[0] >= 1:
                    if dats_xinyuan.shape[0] > 1:
                        print('---> %s网管名<%s>找到多于一个设计名，默认使用第一个'%(process_shuoming,xinyuan))
                    xinyuan_names.append(dats_xinyuan.loc[dats_xinyuan.index[0]][2])
            dats['信源名'] = xinyuan_names
            print('--->获取信源设计名信息完成。。。')
        
        dats = dats[['基站名','设计名','RRU名称','信源名',
                     '站号','BBU名称','网管RRU数','在服RRU数','基站状态']]
        dats = dats.drop_duplicates()#删除重复项
        self.private_judge_name_repeat(dats)
        return dats

if __name__ == '__main__':
    
    lteinfo_operate = OperateLteInfo()
    huawei_in='lte_huawei_0328.xlsx'
    nokia_in='lte_nokia_0403.xlsx'
#    lteinfo_operate.get_huawei_lte(huawei_in)
#    lteinfo_operate.get_nokia_lte(nokia_in)
    
