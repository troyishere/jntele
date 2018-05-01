# -*- coding: utf-8 -*-
"""
Created on Sat Apr 28 18:26:51 2018
无线网自动生成导入表
@author: lenovo
"""
import sys
sys.path.append('..\\')
from jntele_base import LteBase

import pandas as pd
from pandas import DataFrame

class LteImport():
    def __init__(self,dir_base,dir_log):
        self.dir_base = dir_base
        self.dir_log = dir_log
    
    '''====================================================================='''
    '''转固三码系统导入表输入文件模块'''
    # 无线网CMD调用函数
    def operateLteImport(self,file_base,wbs_ids,
                         dir_in='import_old\\',dir_out='import_ok\\'):
        '''file_base为资产信息存储文件'''
        '''wbs_ids为工程编码列表'''
        '''默认存储的导出表名称为:交资【明细】导出_<工程编码>.xls'''
        dats_base = pd.read_excel(self.dir_base+file_base,
                                  dtype = {'资源ID':str,'固定资产目录':str})
        print('===================================================')
        print('-> 开始自动处理无线网工程转固导入表')
        for wbs_id in wbs_ids:
            print('---> 开始处理%s的导入表'%(wbs_id))
            file_wbs = '%s%s交资【明细】导出_%s.xls'%(self.dir_base,dir_in,wbs_id)
            file_out = '%s%s%s导入表ok.xls'%(self.dir_base,dir_out,wbs_id)
            self.getLteImportFile(dats_base,wbs_id,file_wbs,file_out)
        print('-> 无线网工程转固导入表已处理完成')
        print('===================================================')
    
    # 无线网基础函数,为可视化留接口
    def getLteImportFile(self,dats_base,wbs,file_wbs,file_out):
        '''基于getImportFile函数的LTE导入表处理函数'''
        info_dict = {
                '成本中心': '股份济南网络运行维护部（成本）(A370100009)',
                '资产管理部门': '股份济南网络运行维护部(A370100009)',
                '资产管理员': '周帅(W0069237@SD)',
                '使用单位': '山东-济南分公司(2937019901)',
                '使用部门': '股份济南网络运行维护部(A370100009)',
                '保管员': '李臻(37011865@SD)',
                '使用人': '李臻(37011865@SD)'
                }
        
        print('-----> 无线网转固导入表处理函数，默认保管员和使用人为李臻')
        return self._getImportFile(info_dict,dats_base,wbs,file_wbs,file_out)
    
    #这是基础函数
    def _getImportFile(self,info_dict,dats_base,wbs,file_wbs,file_out):
        '''自动处理三码系统导入表基础通用函数'''
        '''wbs：导入表工程编码'''
        '''file_wbs：工程编码原始导入表'''
        '''dats_base：资产文件基础信息'''
        '''file_out：输出文件'''
        dats_log = DataFrame(columns=['等级','基础表工程编码','资源名称','资源ID','导入表工程编码','导入表资源名称','说明'])
        log_index = 0
        dats_wbs = pd.read_excel(file_wbs,
                                 dtype = {'固定资产目录' : str,
                                          '实物ID':str})
        ziyuan_num = dats_wbs.shape[0]-1
        print('-----> 共需处理%d条数据...'%(ziyuan_num))
        '''逐条分析资源编码'''
        for index in dats_wbs.index:
            ziyuan_id = dats_wbs.loc[index]['实物ID']
            ziyuan_name = dats_wbs.loc[index]['资源名称']
            
            if index == 0:
                continue
            for key in info_dict:
                dats_wbs.loc[index][key] = info_dict[key]
            dats_id = dats_base[dats_base['资源ID']==ziyuan_id]
            if dats_id.shape[0] == 0:#未在基础表中找到对应的资源编码
                print('-----> ID【%s】'%(ziyuan_id))
                print('       资源【%s】未在基础表中匹配到相应信息！'%(ziyuan_name))
                dats_log.loc[log_index] = ['E','NONE','NONE',ziyuan_id,wbs,ziyuan_name,
                            '资源编码未在基础表中找到对应信息']
                log_index += 1
            elif dats_id.shape[0] > 1:#在基础表中找到多于一个资源编码
                print('-----> ID【%s】'%(ziyuan_id))
                print('       资源【%s】在基础表中匹配到%d个相应信息：'%(ziyuan_name,dats_id.shape[0]))
                for inx in dats_id.index:
                    print('       %d:资源名称【%s】'%(inx,dats_id.loc[inx,'资源名称']))
                    dats_log.loc[log_index] = ['E',dats_id.loc[inx,'工程编码'],
                                 dats_id.loc[inx,'资源名称'],
                                 ziyuan_id,wbs,ziyuan_name,
                                 '资源编码在基础表中找到重复信息']
                    log_index += 1
            else:
                wbs_base = dats_id.loc[dats_id.index[0],'工程编码']
                if wbs != wbs_base:    
                    if wbs + 'N' == wbs_base:
                        print('-----> ID【%s】'%(ziyuan_id))
                        print('       资源【%s】在基础表中拟不转固，请核实！'%(ziyuan_name))
                        dats_log.loc[log_index] = ['E',ziyuan_name,wbs,ziyuan_id,wbs,ziyuan_name,
                            '资源拟不转固']
                        log_index += 1
                    else:
                        print('-----> ID【%s】'%(ziyuan_id))
                        print('       资源【%s】在基础表中工程编码不同，请核实！'%(ziyuan_name))
                        dats_log.loc[log_index] = ['E',ziyuan_name,wbs_base,ziyuan_id,wbs,ziyuan_name,
                            '资源拟不转固']
                        log_index += 1
                dats_wbs.loc[index]['规格、型号、结构'] = dats_id.loc[dats_id.index[0]]['规格程式']
                dats_wbs.loc[index]['所在地点'] = dats_id.loc[dats_id.index[0]]['所在地点']
                dats_wbs.loc[index]['生产厂家'] = dats_id.loc[dats_id.index[0]]['厂家(全)']
                dats_wbs.loc[index]['固定资产目录'] = dats_id.loc[dats_id.index[0]]['固定资产目录']
        dats_wbs.to_excel(file_out,header=True,index=False)
        print('-----> 导入表处理完成，已存入：%s'%(file_out))
        if dats_log.shape[0] == 0:
            print('-----> 匹配完全成功，无相关日志输出')
        else:
            log_out = self.dir_log + '转固导入表生成日志' + LteBase.getTimeStr() + '.csv'
            dats_log.to_csv(log_out,header=True,index=False)
            print('-----> 请查看相关日志:%s'%(log_out)) 
        return dats_wbs
    '''====================================================================='''
if __name__ == '__main__':
    dir_base = '..\\zhuangu\\'
    dir_log = '..\\zhuangu\\log\\'
    op = LteImport(dir_base,dir_log)
    wbs_ids = [
        '17SD002342005'
        ]
    tmp = op.operateLteImport('LTE五期.xlsx',wbs_ids)

