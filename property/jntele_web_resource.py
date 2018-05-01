# -*- coding: utf-8 -*-
"""
Created on Sat Apr 28 18:10:57 2018
将无线网三码导出资源匹配到资源基础管理文件中
@author: lenovo
"""

import sys
sys.path.append('..\\')
from jntele_base import LteBase
from pandas import DataFrame
import pandas as pd


class LteWebResource(object):

    def __init__(self,dir_base,dir_log):
        self.dir_base = dir_base
        self.dir_log = dir_log
        self.web_col = ['资源ID','资源名称','资源编码',
                        '规格','工程名','工程编码','地市']
    '''====================================================================='''
    '''资源录入核实模块'''
    # 无线网CMD调用函数
    def matchLteWebResource(self,file_base,wbs_ids):
        '''将无线网三码导出资源匹配到资源基础管理文件中'''
        print('==============================================================')
        print('-> 开始将三码系统导出的无线网资源匹配到资产基础管理文件中')
        file_name = self.dir_base + file_base
        dats_base = pd.read_excel(file_name,dtype = {
                '固定资产目录':str,
                '资源ID':str})
        dats_web = self.operateLteWebResource(wbs_ids,ifSave=False)
        
        dats_log = DataFrame(columns=['等级','基础表工程编码','资源名称','资源ID','三码工程编码','三码资源名称','说明'])
        log_index = 0
        
        for wbs_id in wbs_ids:
            print('---> 开始匹配%s:'%(wbs_id))
            
            dats_web_wbs = dats_web[dats_web['工程编码'] == wbs_id]
            print('-----> 该工程共有%d条资源需匹配'%(dats_web_wbs.shape[0]))
            for index in dats_web_wbs.index:
                web_res_id = dats_web_wbs.loc[dats_web_wbs.index[index],'资源ID']
                web_res_name = dats_web_wbs.loc[dats_web_wbs.index[index],'资源名称']
                web_res_wbs = dats_web_wbs.loc[dats_web_wbs.index[index],'工程编码']
                dats_res = dats_base[dats_base['资源名称']==web_res_name]
                if dats_res.shape[0] == 0:
                    print('-----> ID【%s】'%(web_res_id))
                    print('       资源【%s】未匹配到'%(web_res_name))
                    dats_log.loc[log_index] = ['E','NONE','NONE',web_res_id,web_res_wbs,web_res_name,'未在基础表中匹配到']
                    log_index += 1
                elif dats_res.shape[0] == 1:
                    base_res_wbs = dats_res.loc[dats_res.index[0],'工程编码']
                    base_id = dats_res.loc[dats_res.index[0],'资源ID']
                    if base_id != 'none' and base_id != web_res_id:
                        print('-----> ID【%s】'%(web_res_id))
                        print('       资源【%s】匹配到不同的资源ID【%s】'%(web_res_name,base_id))
                        dats_log.loc[log_index] = ['E',base_res_wbs,web_res_name,web_res_id,web_res_wbs,web_res_name,
                                    '在基础表中匹配到不同的资源ID【%s】'%(base_id)]
                        log_index += 1
                    else:
                        dats_base.loc[dats_base['资源名称']==web_res_name,'资源ID'] = web_res_id
                    if base_res_wbs == web_res_wbs+'N':
                        print('-----> ID【%s】'%(web_res_id))
                        print('       资源【%s】计划将不进行转固'%(web_res_name))
                        dats_log.loc[log_index] = ['W',base_res_wbs,web_res_name,web_res_id,web_res_wbs,web_res_name,'该资源拟不转固']
                        log_index += 1
                    elif  base_res_wbs != web_res_wbs:
                        print('-----> ID【%s】'%(web_res_id))
                        print('       资源【%s】匹配工程编码错误:'%(web_res_name))
                        print('       应录入【%s】,实际录入【%s】'%(base_res_wbs,web_res_wbs))
                        dats_log.loc[log_index] = ['E',base_res_wbs,web_res_name,web_res_id,web_res_wbs,web_res_name,'录入工程编码不一致']
                        log_index += 1
                else:
                    print('-----> ID【%s】'%(web_res_id))
                    print('       资源【%s】搜索到多于1个资源名称'%(web_res_name))
                    dats_log.loc[log_index] = ['E','NONE','NONE',web_res_id,web_res_wbs,web_res_name,
                                '在基础表中匹配到多于一个资源名称']
                    log_index += 1
                    
            dats_base_wbs = dats_base[dats_base['工程编码']==wbs_id]
            dats_base_wbs = dats_base_wbs[dats_base_wbs['资源ID']=='none']
            if dats_base_wbs.shape[0] != 0:
                print('---> 本工程有%d条资产未匹配到资源ID'%(dats_base_wbs.shape[0]))
                for index in dats_base_wbs.index:
                    dats_log.loc[log_index]=['E',wbs_id,dats_base_wbs.loc[index,'资源名称'],
                                 'NONE','NONE','NONE','未找到匹配的资源ID']
                    log_index += 1
            print('---> %s匹配完成'%(wbs_id))
        dats_base.to_excel(file_name,header=True,index=False)           
        print('-> 全部工程编码匹配完成，已存入资产基础管理文件%s'%(file_name))  
        if dats_log.shape[0] == 0:
            print('-> 匹配完全成功，无相关日志输出')
        else:
            log_out = self.dir_log + '三码导出资源整合日志' + LteBase.getTimeStr() + '.csv'
            dats_log.to_csv(log_out,header=True,index=False)
            print('-> 请查看相关日志:%s'%(log_out)) 
        print('==============================================================')
        return dats_base
    
    # 无线网CMD调用函数
    def operateLteWebResource(self,wbs_ids,dir_in='web_resource\\',dir_out='tmp\\',ifSave=True):
        '''无线网三码导出资源处理函数'''
        '''三码导出资源的命名格式为：工程资源导出_<工程编码>.xls'''
        '''会生成时间码命名的记录文件方便存储于tmp文件夹'''
        files_in = ['%s%s工程资源导出_%s.xls'%(self.dir_base,dir_in,wbs_id) for wbs_id in wbs_ids]
        file_out = self.dir_base + dir_out + '三码导出资源整合记录' + LteBase.getTimeStr() + '.xlsx'
        return self._getWebResource(wbs_ids,files_in,file_out,ifSave)        
    
    #这是基础函数
    def _getWebResource(self,wbs_ids,files_in,file_out,ifSave=True):
        '''处理三码导出资源的基础函数'''
        print('---> 开始讲三码系统中下载的资源文件整合到DataFrame中')
        
        df_all = pd.DataFrame()
       
        for file_in in files_in:
            
            df_all = df_all.append(pd.read_excel(file_in,dtype = {'编码':str}))
        df_all = df_all[['实物ID','名称','编码','规格名称','工程名称','工程编码','所属行政管理区']]
        df_all['名称'] = [name.strip() for name in df_all['名称']]
        df_all['编码'] = [bianma.strip() for bianma in df_all['编码']]
        df_all.columns = self.web_col
        print('---> 三码系统资源文件已整合完成')
        if file_out != '' and ifSave:
            df_all.to_excel(file_out,header=True,index=False)
            print('---> 整合的数据已存入%s'%(file_out))
        return df_all
    '''====================================================================='''
    
if __name__ == '__main__':
    
    dir_base = '..\\zhuangu\\'
    dir_log = '..\\zhuangu\\log\\'
    op = LteWebResource(dir_base,dir_log)
    wbs_ids = [
            '17SD018315001'
            ]
    tmp = op.matchLteWebResource('LTE六期资源录入0403.xlsx',wbs_ids)
