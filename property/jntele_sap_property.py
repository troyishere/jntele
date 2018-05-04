# -*- coding: utf-8 -*-
"""
Created on Sun Apr 29 13:54:55 2018
将SAP物料信息匹配到基础表
@author: lenovo
"""
import sys
sys.path.append('..\\')
from jntele_base import LteBase
import pandas as pd
from pandas import Series,DataFrame

class LteSapProperty(object):
    
    def __init__(self,dir_base,dir_log):
        self.dir_base = dir_base
        self.dir_log = dir_log
    
    
    def matchLteSapZhucai(self,file_base,file_sap,wbs_ids):
        '''file_base为资产信息存储文件'''
        '''file_sap为sap文件'''
        '''wbs_ids为工程编码列表'''
        print('-> 开始将资产基础文件中的资产条目同SAP中的主材条目数进行比对')
        dats_base = pd.read_excel(self.dir_base+file_base,
                                  dtype = {'资源ID':str,'固定资产目录':str})
        dats_sap = pd.read_excel(file_sap,sheetname = 'zhucai_num')
        dats_detail = pd.read_excel(file_sap,sheetname = 'zhucai')
        dats_log = DataFrame(columns=['等级','工程编码','主材类型','说明'])
        log_index = 0
        for wbs_id in wbs_ids:
            print('---> 开始比对%s'%(wbs_id))
            dats_tmp = dats_sap[dats_sap['工程编码'] == wbs_id]
            if dats_tmp.shape[0] == 0:
                print('---> 工程编码【%s】对应未找到对应的RRU数和天线数信息，默认均返回0'%(wbs_id))
                dats_log.loc[log_index] = ['E',wbs_id,'天线和RRU','SAP中未查到工程编码对应信息']
                log_index += 1
                rru_num = 0
                tianxian_num = 0
            else:
                rru_num = Series(dats_tmp.loc[dats_tmp.index[0]]).tolist()[1]
                tianxian_num = Series(dats_tmp.loc[dats_tmp.index[0]]).tolist()[2]
            dats_tmp = dats_base[dats_base['工程编码'] == wbs_id]
            base_rru = dats_tmp[dats_tmp['资产名称']=='分布式基站设备'].shape[0]
            base_tianxian = dats_tmp[dats_tmp['资产名称']=='定向天线'].shape[0]
            if rru_num == base_rru:
                print('    > RRU总数目ok：%d'%(rru_num))
            else:
                print('    > RRU总数目不同：资产表中为%d，SAP中为%d'%(base_rru,rru_num))
                dats_log.loc[log_index] = ['E',wbs_id,'RRU','基础表中为%d,SAP中为%d'%(base_rru,rru_num)]
                log_index += 1
            if tianxian_num == base_tianxian:
                print('    > 天线总数目ok：%d'%(tianxian_num))
            else:
                print('    > 天线总数目不同：资产表中为%d，SAP中为%d'%(base_tianxian,tianxian_num))
                dats_log.loc[log_index] = ['E',wbs_id,'天线','基础表中为%d,SAP中为%d'%(base_tianxian,tianxian_num)]
                log_index += 1
            print('    > 开始核算主材数目：')
            
            dats_tmp = dats_base[dats_base['工程编码'] == wbs_id]
            list_zhucai = Series(dats_tmp['物料编码']).unique().tolist()
            if 'none' in list_zhucai:
                print('     > 存在未定物料编码的资产，请核实！')
                dats_log.loc[log_index] = ['E',wbs_id,'物料编码','存在none，请确定资源所对应物料编码']
                log_index += 1
                list_zhucai.remove('none')
            dats_tmp2 = dats_detail[dats_detail['工程编码']==wbs_id]
            for zhucai in list_zhucai:
                num_base = dats_tmp[dats_tmp['物料编码']==zhucai].shape[0]
                dats_tmp3 = dats_tmp2[dats_tmp2['物料编码'] == zhucai]
                if dats_tmp3.shape[0] != 0:
                    num_sap =  Series(dats_tmp3.loc[dats_tmp3.index[0]]).tolist()[3]
                else:
                    print('      > %s: 在SAP中没有')
                    num_sap = 0
                if num_base == num_sap:
                    print('      > %s: SAP %d;基础表 %d,ok'%(zhucai,num_sap,num_base))
                else:
                    print('      > %s: SAP %d;基础表 %d,请核实！'%(zhucai,num_sap,num_base))
                    dats_log.loc[log_index] = ['E',wbs_id,zhucai,'SAP %d;基础表 %d,需核实'%(num_sap,num_base)]
                    log_index += 1
        
        if dats_log.shape[0] == 0:
            print('-> 比对完全成功，无相关日志输出')
        else:
            log_out = self.dir_log + 'SAP主材匹配日志' + LteBase.getTimeStr() + '.csv'
            dats_log.to_csv(log_out,header=True,index=False)
            print('-> 比对存在问题，请查看相关日志:%s'%(log_out)) 
        print('-> 资产基础文件中的资产条目同SAP中的主材条目数比对完成')
    
if __name__ == '__main__':
    dir_base = '..\\zhuangu\\'
    dir_log = '..\\zhuangu\\log\\'
    op = LteSapProperty(dir_base,dir_log)
    wbs_ids = [
        '17SD018315001'
        ]
    tmp = op.matchLteSapZhucai('LTE六期资源录入0403.xlsx','..\\gongcheng\\sap_ok\\SAP-LTE6-041902-ok.xlsx',wbs_ids)