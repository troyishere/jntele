# -*- coding: utf-8 -*-
"""
Created on Sat May 12 14:34:41 2018

@author: lenovo
"""

import pandas as pd

from pandas import DataFrame
import warnings
import sys
sys.path.append('..\\')
from jntele_base import LteBase

def getformat(string,num=15):
    
    str_l = len(string)
    if str_l>=num:
        return str_l
    else:
        tmp = ''
        for i in range(num-str_l):
            tmp = tmp+' '
        return string+tmp
    
    

class LteNetwork(object):
    def __init__(self,dir_base,dir_log):
        self.dir_base = dir_base
        # 日志文件
        self.file_log = '%sLog网管%s.xlsx'%(dir_log, LteBase.getTimeStr())
        
        # 华为默认使用列状态
        self.col_hw_base_save = [
                'eNodeB标识',
                'LTE网元名称',
                '网元连接状态',
                '小区名称',
                '激活状态',
                '可用状态']
        self.col_hw_base = [
                '站点类型',
                '基站名',
                'RRU名称',
                '信源名',
                'eNodeB标识',
                'LTE网元名称',
                '小区名称',
                '网元连接状态',
                '可用状态',
                '激活状态']
        
        self.col_hw_base_ok = [
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
        # 诺基亚默认列状态
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
        # 保存列表状态
        self.log_col_names = ['站址类型',
                               '基站名', 
                               '设计名',
                               'RRU名称',
                               '信源名',
                               '站号',
                               'BBU名称',
                               '网管RRU数',
                               '在服RRU数',
                               '基站状态',
                               '告警等级',
                               '说明']
        # 比较输出表状态
        self.end_col_names = ['基站名',
                              '设计名',
                              '信源名',
                              'RRU名称',
                              'BBU名称',
                              '站号',
                              '网管RRU数',
                              '基站状态']
        self.dats_log = DataFrame(columns = self.log_col_names)
        self.index_log = 0
        self.dats_log.columns = self.log_col_names
        
        self.dats_log.loc[self.index_log] = self.log_col_names
        self.index_log += 1
        
        self.dats_log.to_excel(self.file_log,header=True,index=True)
        self.prosess_classes = {
                'h8':'华为800M',
                'hl':'华为LTE&CA',
                'n8':'诺基亚800M',
                'nl':'诺基亚LTE&CA'
                }
        
        
        
    '''华为网管信息处理函数''' 
    def get_huawei_lte(self,file_in,dir_in = 'cell_status\\',dir_out='data\\',base_design=True):
        file_name = self.dir_base + dir_in+file_in
        '''****************************************'''
        print('-> 开始处理华为数据,RRU状态判断依据为【可用状态】')
        dats = pd.read_excel(file_name)
        print('--> 已导入文件'+ file_name)
        '''****************************************'''
        print('--> 开始处理小区，过滤掉无用小区')
        dats = dats[self.col_hw_base_save]
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
                print('  > INFO:未能判别小区类型  '+ cell)
                print('  > 暂不处理该小区...')
        dats['站点类型'] = station_types
        dats= dats[selects]#过滤掉不需要小区
        print('  > 已过滤掉NB、室分、共享联通小区...')
        '''****************************************'''
        print('--> 开始处理合并小区...')
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
        print('  > C2类型的合并小区数为：'+str(datsC2.shape[0]))
        print('  > C3类型的合并小区数为：'+str(datsC3.shape[0]))
        dats = dats.append(datsC2)
        dats = dats.append(datsC3)
        dats = dats.append(datsC3)
        print('  > 目前网管有数据室外小区数为：'+str(dats.shape[0]))
        print('--> 已处理完合并小区...')
#        dats = dats.drop(['分区','小区标识','管理状态','操作状态','本地小区标识'],axis=1)
        '''****************************************'''
        print('--> 开始获取站点名、信源名、RRU名')
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
        print('  > 已获取站点名、信源名、RRU名....')
        '''****************************************'''
        print('--> 开始处理BBU、RRU状态')
        dats = dats[self.col_hw_base]
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
        print('  > BBU、RRU状态已获取')
        '''****************************************'''
        dats.columns = self.col_hw_base_ok  
        print('--> 基础数据处理完成。。。')
        file_out = self.dir_base+ dir_out + file_in[0:(len(file_in)-5)]+'-ok.xlsx'
        writer = pd.ExcelWriter(file_out)
        dats = dats.sort_values(by=['站号','小区名称'])
        dats.to_excel(writer,'ok',header=True,index=False)
        
        dats = dats.drop(['RRU激活'],axis = 1)#留待处理激活状态
        print('--> 基础数据已保存到：'+ file_out )
        '''****************************************'''
        dats = dats.drop(['小区名称'],axis = 1)
        print('--> 开始处理LTE800M数据')
        dats_800 = dats[dats['站点类型'] == '800M']
        dats_800 = dats_800.drop(['站点类型'],axis=1)
        dats_800 = self._get_station_status(dats_800,'h8',base_design)
        dats_800.to_excel(writer,'800M',header=True,index=False)
        print(' > LTE800M数据处理完成，已保存')
        '''****************************************'''
        print('-->开始处理LTE1800M&CA数据')
        dats_lte = dats[dats['站点类型'] != '800M']
        dats_lte = dats_lte.drop(['站点类型'],axis=1)
        dats_lte = self._get_station_status(dats_lte,'hl',base_design)
        dats_lte.to_excel(writer,'LTE&CA',header=True,index=False)
        print('--> LTE1800M&CA数据处理完成，已保存')
        '''****************************************'''
#        print('|设备类型|网管RRU数|在服RRU数|RRU在服率|网管站点数|正常站点数|部分扇区故障|RRU脱管|BBU脱管|')
        writer.save()
        return file_out
        
    
    '''Nokia网管信息处理函数''' 
    def get_nokia_lte(self,file_in,dir_in = 'cell_status\\',dir_out='data\\',base_design=True):
        
        file_name = self.dir_base + dir_in+file_in
        '''****************************************'''
        print('--> 开始处理诺基亚数据')
        dats = pd.read_excel(file_name)
        print('--> 已导入文件'+ file_name)
        '''****************************************'''
        print('--> 开始处理小区，过滤掉无用小区')
        dats = dats[dats['站型']=='宏站']
        dats = dats[['RRH类型',	'ENBID','站名','小区名',	'RMODNO','MODULE_STATE','BBU_STATE']]
        dats.columns = ['站点类型','站号','BBU名称','小区名称',	'RMODNO','MODULE_STATE','BBU_STATE']
        print('--> 已保留800M/1.8G/2.1G室外小区')
        '''****************************************'''
        print('--> 开始获取站点名、信源名、RRU名')
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
        print('--> 已获取站点名、信源名、RRU名....')
        '''****************************************'''
        print('--> 开始获取RRU序号')
        cell_nums = dats['RMODNO']
        cell_nums_ok = []
        for cell_num in cell_nums:
            cell_nums_ok.append(cell_num.split('-')[-1])
        dats['RRU序号'] = cell_nums_ok
        print('--> 已获取RRU序号....')
        dats = dats.drop(['RMODNO'],axis=1)
        '''****************************************'''
        print('--> 开始处理BBU、RRU状态')
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
        print('--> 处理BBU、RRU状态完成')
        print('--> 基础数据处理完成。。。')
        dats = dats[self.nokia_col_names]
        file_out = self.dir_base+ dir_out + file_in[0:(len(file_in)-5)]+'-ok.xlsx'
        writer = pd.ExcelWriter(file_out)
        dats = dats.sort_values(by=['站号','小区名称'])
        dats.to_excel(writer,'ok',header=True,index=False)
    #    writer.save()
        print('--> 基础数据已保存到：'+ file_out )
        '''****************************************'''
        dats = dats.drop(['小区名称','RRU序号'],axis = 1)
        print('--> 开始处理LTE800M数据')
        dats_800 = dats[dats['站点类型'] == '800M']
        dats_800 = dats_800.drop(['站点类型'],axis=1)
        dats_800 = self._get_station_status(dats_800,'n8',base_design)
        dats_800.to_excel(writer,'800M',header=True,index=False)
        print('--> LTE800M数据处理完成，已保存')
        '''****************************************'''
        print('--> 开始处理LTE1800M&CA数据')
        dats_lte = dats[dats['站点类型'] != '800M']
        dats_lte = dats_lte.drop(['站点类型'],axis=1)
        dats_lte = self._get_station_status(dats_lte,'nl',base_design)
        dats_lte.to_excel(writer,'LTE&CA',header=True,index=False)
        
        print('--> LTE1800M&CA数据处理完成，已保存')
        writer.save()
        '''****************************************'''
        return file_out
    
    
    
    
    
    def matchLTECAdats(self,file_base,huawei_in,nokia_in,dir_out='data\\'):
        '''对LTE&CA基础表和网管数据进行比对'''
        return self._match_net_dats(file_base,huawei_in,nokia_in,dir_out,'LTE&CA')

    
    def matchL800Mdats(self,file_base,huawei_in,nokia_in,dir_out='data\\'):
        '''对800M基础表和网管数据进行比对'''
        return self._match_net_dats(file_base,huawei_in,nokia_in,dir_out,'800M')

    def _match_net_dats(self,file_base,huawei_in,nokia_in,dir_out='data\\',operate='800M'):
        '''匹配基础表与网管的基本函数'''
        print('---> 开始获取%s华为、Nokia网管信息'%(operate))
        print('---> 开始获取站点基础表信息：%s'%(file_base))
        dats_base = pd.read_excel(self.dir_base+file_base,sheetname='明细')
        dats_base = dats_base[['设计名称','信源站','RRU名称','网管名称','enode ID','扇区数','情况']]
        dats_base = dats_base.fillna('')
        dats_tmp = dats_base[dats_base['设计名称']!='']
        if len(dats_tmp['设计名称'].unique()) != len(dats_tmp['设计名称']):
            
            print('   > 基础表存在重复设计名，请先核实！')
            list_name = dats_tmp['设计名称'].tolist()
            for name in dats_tmp['设计名称'].unique():
                if list_name.count(name) > 1:
                    print('   -> %s，重复%d次'%(name,list_name.count(name)))
            return ''
        print('   > 已获取站点基础表信息')
        
        huawei_dats = pd.read_excel(huawei_in,sheetname=operate)
        huawei_changjias = ['华为'] * len(huawei_dats.index)
        huawei_dats['站点类型'] = huawei_changjias
        nokia_dats = pd.read_excel(nokia_in,sheetname=operate)
        nokia_changjias = ['诺基亚'] * len(nokia_dats.index)
        nokia_dats['站点类型'] = nokia_changjias
        dats_ok = huawei_dats.append(nokia_dats)
        dats_ok = dats_ok[self.end_col_names]
        print('   > 已获取%s华为、Nokia网管信息'%(operate))
        
        print('---> 开始获取站点基础表信息：%s'%(file_base))
        dats_base = pd.read_excel(self.dir_base+file_base,sheetname='明细')
        dats_base = dats_base[['设计名称','信源站','RRU名称','网管名称','enode ID','扇区数','情况']]
        dats_base = dats_base.fillna('')
        dats_tmp = dats_base[dats_base['设计名称']!='']
        
        
        
        dats_qu = DataFrame(columns = self.end_col_names)#差异信息
        index_qu = 0
        status = []
        print('---> 开始对基础表中逐个站点比对')
        for inx in dats_base.index:
            list_base = dats_base.loc[inx].tolist()#设计名
            if list_base[0] == '':#设计名为空，表示未建设站点
                status.append('')
                continue
            dats_tmp = dats_ok[dats_ok['设计名'] == list_base[0]]#在网管数据中查找站点
            if dats_tmp.shape[0] == 0:# 网管中未查询到
                if list_base[6] == '开通':# 判断是否开通
                    print('    > 【%s】已开通，但网管无数据，请核实！'%(list_base[0]))
                    status.append('【无】') 
                else:
                    status.append('')
                continue
            else:
                if dats_tmp.shape[0] > 1:# 网管中未查询到大于一条
                    print('    > 【%s】有大于1条网管，默认使用第一条，请核实'%(list_base[0]))
                list_tmp = dats_tmp.loc[dats_tmp.index[0]].tolist()
                state = self._match_station_data(list_base[:-1],list_tmp)
                if state:
                    dats_qu.loc[index_qu] = list_tmp
                    index_qu += 1
                status.append(list_tmp[7])
        dats_base['基站状态'] = status        
        
        
        dats_qu = dats_qu.drop(['基站名'],axis=1)
        if index_qu != 0:
            print('   > 基础表与网管站点信息存在差异，请核实！')
#            print(dats_qu.shape)
            dats_base = pd.merge(dats_base, dats_qu,how='left',
                                 left_on = '设计名称',right_on = '设计名')
        else:
            print('   > 基础表与网管站点信息完全相同')
        print('---> 基础表逐个站点比对完成')
        file_out = self.dir_base + dir_out+'Match' + operate + LteBase.getTimeStr() +'.xlsx'
        writer = pd.ExcelWriter(file_out)
        dats_base.to_excel(writer,'基础表',header=True,index=True)
        writer.save()
        print('---> 数据已保存至%s'%(file_out))
        return file_out    
        
        
    def _match_station_data(self,list_base,list_net):
        list_ok = []
        state = False
        
        col_dir = {
                1:'信源名',
                2:'RRU名称',
                3:'网管名称',
                4:'enode ID',
                5:'扇区数'
                }
        list_ok.append(list_base[0]) # 设计名
        if list_base[2] == '':
            print('    > 【%s】基础表网管信息为空'%(list_base[0]))
            state = True
            return state
        for i in range(len(list_base)-1):
            if list_base[i+1] != list_net[i+2]:
                
                if i==4:#扇区数为数字
                    if isinstance(list_base[i+1],str):
                        dat_base = int(list_base[i+1][0])
                    else:
                        dat_base = list_base[i+1]
                    if dat_base != list_net[i+2] :
                        print('    > 【%s】基础表【%s】为【%d】，网管为【%d】，请核实'%(list_base[0],col_dir[i+1],list_base[i+1],list_net[i+2]))
                        state = True
                else:
                    print('    > 【%s】基础表【%s】为【%s】，网管为【%s】，请核实'%(list_base[0],col_dir[i+1],list_base[i+1],list_net[i+2]))
                    state = True
        return state
    
        
        
        
        
        
    def get_cell_dat(self,cell_name):
        '''对小区名进行处理，提取小区站点名，信源名，RRU名'''
        cell_dats = cell_name.split('-')
        if len(cell_dats) < 4:
            print(cell_name)
        cell_xinyuan = cell_dats[2]
        cell_zhanname = cell_dats[3]
        cell_name_ok = cell_dats[0]+'-'+cell_dats[1]+'-'+cell_dats[2]+'-'+cell_dats[3]
        return cell_zhanname,cell_xinyuan,cell_name_ok
    
    def _append_log(self,process_shuoming,list_dats,dengji,info):
        '''向log日志中追加数据'''
        list_dats.insert(0,process_shuoming)
        list_dats.append(dengji)
        list_dats.append(info)
        
        self.dats_log.loc[self.index_log] = list_dats
        self.index_log += 1
        
        
        
    def _judge_name_repeat(self,dats,process_shuoming):
        '''判断设计名对应不同的小区名'''
        print('-----> 开始判断设计名是否对应不同的网管名')
        dats_repeat = dats[['设计名','基站名','RRU名称','站号']]
        
        for design_name in dats_repeat['设计名'].unique():
            dats_tmp = dats_repeat[dats_repeat['设计名']==design_name]
            if dats_tmp.shape[0]>1:
                print('     > 【%s】发现【%d】个不同网管名:'%(design_name,dats_tmp.shape[0]))
            if dats_tmp.shape[0] == 2:
                list_tmp0 = dats.loc[dats_tmp.index[0]].tolist()
                list_tmp1 = dats.loc[dats_tmp.index[1]].tolist()
                id0 = dats_tmp.loc[dats_tmp.index[0],'站号'] 
                id1 = dats_tmp.loc[dats_tmp.index[1],'站号']
                if id0==id1:
                    print('     -> 站号相同,默认使用第一个')
                    self._append_log(process_shuoming,list_tmp0,'W','重复：站号相同')
                    self._append_log(process_shuoming,list_tmp1,'W','重复：站号相同')
                else:
                    print('     -> 站号不同,进行合并')
                    dats.loc[dats_tmp.index[0],'站号'] = str(list_tmp0[4]) + '\n' + str(list_tmp1[4])
                    dats.loc[dats_tmp.index[0],'BBU名称'] = str(list_tmp0[5]) + '\n' + str(list_tmp1[5])
                    if list_tmp0[2] != list_tmp0[2]:# RRU名不同时，合并RRU名
                        dats.loc[dats_tmp.index[0],'RRU名称'] = list_tmp0[2] + '\n' + list_tmp1[2]
                    if list_tmp0[3] != list_tmp0[3]:
                        print('     -> 信源名不同，请核实！')
                        self._append_log(process_shuoming,list_tmp0,'E','重复：信源名，站号均不同')
                        self._append_log(process_shuoming,list_tmp1,'E','重复：信源名，站号均不同')
                    else:
                        self._append_log(process_shuoming,list_tmp0,'W','重复：站号不同')
                        self._append_log(process_shuoming,list_tmp1,'W','重复：站号不同')
                dats = dats.drop(dats_tmp.index[1])
            if dats_tmp.shape[0] > 2:
                for i,(station_name,rru_name,station_id) in enumerate(zip(dats_tmp['基站名'],dats_tmp['RRU名称'],dats_tmp['站号'])):
                    print('     -> %1d: %s||%d||站号%s'%(i+1,getformat(station_name),station_id,rru_name)) 
                for inx in dats_tmp.index:
                    list_tmp = dats.loc[inx].tolist()
                    self._append_log(process_shuoming,list_tmp,'E','重复：多于2个')
          
        return dats
        
    def _get_station_status(self,dats,c = 'h8',base_design = True):
        '''提取基站状态信息'''
        process_shuoming = self.prosess_classes[c]
        print('---> 进入%s在服信息处理函数'%(process_shuoming))
#        dats = dats.sort_index(by='站号')
        print('----> 开始获取设计名信息')
        dats_design = pd.read_excel(self.dir_base+'lte_base.xlsx',sheetname = c)
        design_names = []
        for station_name in dats['基站名']:
            nname = dats_design[dats_design['网管基站名']==station_name]
            if nname.shape[0] == 0:
                print('    > %s网管名%s未找到对应设计名，以【】做标记'%(process_shuoming,station_name))
                design_names.append('【%s】'%(station_name))
            elif nname.shape[0] >= 1:
                if nname.shape[0] > 1:
                    print('---> %s网管名【%s】找到多于一个设计名，默认使用第一个'%(process_shuoming,station_name))
                design_names.append(nname.loc[nname.index[0]][2])
        
        dats['设计名'] = design_names
        print('----> 设计名信息获取完成。。。')
        print('----> 开始获取基站RRU数目、RRU在服数目')
        base_name = '设计名' if base_design else 'RRU名称'
        print('    > 以[%s]为依据统计在服信息'%(base_name))
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
        print('    > 已获取基站RRU数目、RRU在服数目。。。')
        print('----> 开始获取基站网管状态')
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
        print('    > 获取网管状态完成。。。')
        print('----> 开始获取信源设计名信息')
        xinyuan_names = []
        xinyuan_design = pd.read_excel(self.dir_base+'lte_base.xlsx',sheetname = 'xinyuan')
        for xinyuan in dats['信源名']:
            dats_xinyuan = xinyuan_design[xinyuan_design['网管信源']==xinyuan]
            if dats_xinyuan.shape[0] == 0:
                print('---> %s信源名【%s】未找到对应设计信源站，用【】标记'%(process_shuoming,xinyuan))
                xinyuan_names.append('【%s】'%(xinyuan))
            elif dats_xinyuan.shape[0] >= 1:
                if dats_xinyuan.shape[0] > 1:
                    print('---> %s网管名【%s】找到多于一个设计名，默认使用第一个'%(process_shuoming,xinyuan))
                xinyuan_names.append(dats_xinyuan.loc[dats_xinyuan.index[0]][2])
        dats['信源名'] = xinyuan_names
        print('----> 获取信源设计名信息完成。。。')
        
        dats = dats[['基站名','设计名','RRU名称','信源名',
                     '站号','BBU名称','网管RRU数','在服RRU数','基站状态']]
        dats = dats.drop_duplicates()#删除重复项
        self.dats_log = pd.read_excel(self.file_log)
        for inx in dats.index:#将设计名问题加入日志文件
            if '【' in dats.loc[inx,'设计名']:
                self._append_log(process_shuoming,dats.loc[inx].tolist(),'E','设计名：未找到')
            if '【' in dats.loc[inx,'信源名']:
                self._append_log(process_shuoming,dats.loc[inx].tolist(),'E','设计信源名：未找到')
        print('----> 开始判断重复站点')
        dats = self._judge_name_repeat(dats,process_shuoming)
        if self.index_log >= 1:
            print('    > 请查看日志：%s'%(self.file_log))
            self.dats_log.to_excel(self.file_log,header=True,index=True) 
        print('----> 重复站点判断完成')
        print('---> 退出%s基站在服信息处理函数'%(process_shuoming))
        return dats