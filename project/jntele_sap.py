# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 08:45:13 2017
SAP文件处理程序
@author: lenovo
"""
import sys
sys.path.append('..\\')
from jntele_base import LteBase
import pandas as pd
from pandas import Series,DataFrame
import warnings

class OperateLteSAP(object):
    def __init__(self,dir_base,dir_log):
        self.dir_base = dir_base
        self.dir_log = dir_log
        #需要删除的成本行要素列表
        self.yaosus_sap_dele = [1604000000,#在建工程
                 8001999999,#在建工程.结转
                 ]
        #需要删除的成本行要素列表2
        self.yaosus_zc_dele = [1605010000,#工程物资-设备
                     1605020000,#工程物资-材料
                     ]
        #成本要素编码
        self.yaosus_id = [
                1605010000	,	#	工程物资-设备
                1605020000	,	#	工程物资-材料
                8001020000	,	#	在建工程.在安装设备投资
                8001010100	,	#	在建工程.建筑安装工程投资.材料费
                8001010200	,	#	在建工程.建筑安装工程投资.施工费
                8001030400	,	#	在建工程.待摊投资.勘察设计费
                8001030600	,	#	在建工程.待摊投资.合同公证及监理费
                8001030800	,	#	在建工程.待摊投资.社会中介机构审计费
                8001039900	,	#	在建工程.待摊投资.其他（包括厂验费、培训费、督导费等）
                8001031400	,	#	在建工程.待摊投资.安全生产费
                ];
        #成本要素名称
        self.yaosus_name = [
                '工程物资-设备',
                '工程物资-材料',
                '设备投资',
                '材料费',
                '施工费',
                '设计费',
                '监理费',
                '审计费',
                '其他费',
                '安全生产费'
                ]
        #保留的列
        self.col_sap_save = [
                'WBS 元素',	
                '成本要素',	
                '物料',
                '成本要素描述',	
                '物料描述',	
                '全部数量',	
                'CO范围货币值',
                '过帐日期']
        self.col_data_names = [
                '工程编码',
                '成本要素',
                '物料编码',
                '成本要素描述',
                '物料描述',
                '数目',
                '金额',
                '过账日期']
        #主材门限
        self.jine_min = 400
    def getLteSapData(self,file_in,zhucai_file='lte_zhucai.xlsx',dir_in='sap_old\\',dir_out='sap_ok\\'):
        '''
        获取SAP有效信息标准格式，并整理相关信息
        '''
        file_out=self.dir_base + dir_out + file_in[0:(len(file_in)-5)]+'-ok.xlsx'
        '''=================================================================='''
        print("-> 开始处理SAP文件信息，建议SAP保存格式为LIYONG")
        print("--->导入原始文件："+file_in)
        dats = pd.read_excel(self.dir_base + dir_in + file_in)
        print("   >导入原始文件成功,开始进行操作")
        status,dats = self._getSapBase(dats)
        if status:
            writer = pd.ExcelWriter(file_out)
            dats.to_excel(writer,'all',header=True,index=False)
            '''=============================================================='''
            dats_ok = self._getSapSum(dats)
            dats_ok.to_excel(writer,'sum',header=True,index=False)
            '''=============================================================='''
            dats = self._getSapZhucai(dats)
            dats.to_excel(writer,'zhucai',header=True,index=True)
            '''=============================================================='''
            dats = self._getLteZhucaiNum(dats,zhucai_file)
            dats.to_excel(writer,'zhucai_num',header=True,index=False)
            writer.save()
            print("-> SAP文件信息已解析，数据已存入:"+ file_out)
        else:
            print('-> SAP文件原始信息解析失败，请核实')
        return file_out
    
    def updateZhucaiPrice(self,file_in,zhucai_file='lte_zhucai.xlsx',dir_in='sap_old\\'):
        '''
        从SAP数据表中更新主材单价
        '''
        '''=================================================================='''
        print("-> 开始从SAP数据中更新主材单价信息，建议SAP保存格式为LIYONG")
        f =lambda x: float('%.2f' % x)
        print("--->导入SAP原始文件："+file_in)
        dats = pd.read_excel(self.dir_base + dir_in + file_in)
        print("   >导入原始文件成功,开始进行操作")
        status,dats = self._getSapBase(dats)
        if status:
            print('---> 开始获取主材单价信息')
            dats_base = pd.read_excel(self.dir_base + zhucai_file)
            zhucai_ids = dats_base['物料编码'].unique().tolist()
            zhucais = dats_base['物料编码'].tolist()
            dats = dats[-(dats['成本要素'].isin(self.yaosus_zc_dele))]
            dats = dats[['物料编码','数目','金额']]
            dats = dats[(dats['物料编码'].isin(zhucai_ids))]
            dats_ok = dats.pivot_table(index=['物料编码'],aggfunc='sum')
            dats_ok['单价'] = (dats_ok['金额']/dats_ok['数目']).apply(f)
            prices = []
            for zhucai in zhucais:
                if zhucai in dats_ok.index:
                    prices.append(dats_ok.loc[zhucai,'单价'])
                else:
                    print('   > 本SAP文件中没有主材【%s】'%(zhucai))
                    prices.append('none')
            dats_base['单价'] = prices
            dats_base.to_excel(self.dir_base + zhucai_file,header=True,index=False)
            print('   > 主材单价信息已获取')
            print('-> 主材单价已保存至：'+ self.dir_base + zhucai_file)
        else:
            print('-> SAP文件原始信息解析失败，请核实')
        return self.dir_base + zhucai_file
    
    # 将原始SAP数据处理成可用状态
    def _getSapBase(self,dats):
        
        print("--->处理原始SAP文件成标准格式...")
#        dats = dats.dropna(how='all',axis=1)
        dats = dats.fillna('')
        for inx in dats.index:#获取事实上的colunms
            if 'WBS 元素' in dats.loc[inx].tolist():
                break
        if inx == dats.index[-1]:
            print('   > 未在SAP文件内找到所需的列名列表，请核实')
            return False,dats
        col_index = inx
        col_sap_all_tmp = dats.loc[col_index].tolist()
        col_sap_all = []
        for col_name in col_sap_all_tmp:
            col_sap_all.append(col_name.strip())
        for col_name in self.col_sap_save:
            if not col_name in col_sap_all:
                print('   > 列名【%s】不在SAP文件中，请核实'%(col_name))
                return False,dats
        dats.columns = col_sap_all
        dats = dats.loc[:,self.col_sap_save]
#        dats = dats[self.col_sap_save]
        dats = dats[dats['WBS 元素'].notnull()]
        dats = dats[dats['WBS 元素']!='WBS 元素']
        dats = dats[dats['WBS 元素']!='']
        dats=dats.sort_values(by=['WBS 元素','成本要素','物料'])
        dats_ok = DataFrame(columns=dats.columns)
        # 删除不需要的在建工程要素
        dats = dats[-(dats['成本要素'].isin(self.yaosus_sap_dele))]
        bianmas = Series(dats['WBS 元素'].unique())
        # 删除各要素合计金额为0的物料
        for bianma in bianmas:
            dats_bianm_tmp = dats[dats['WBS 元素']==bianma]
            yaosus = Series(dats_bianm_tmp['成本要素']).unique()
            for yaosu in yaosus:
                dats_yaosu_tmp = dats_bianm_tmp[dats_bianm_tmp['成本要素']==yaosu]
                wuliaos = Series(dats_yaosu_tmp['物料']).unique()
                for wuliao in wuliaos:
                    dats_wuliao_tmp = dats_yaosu_tmp[dats_yaosu_tmp['物料']==wuliao]
                    if(abs(dats_wuliao_tmp['CO范围货币值'].sum())>=0.01):
                        dats_ok = dats_ok.append(dats_wuliao_tmp,ignore_index=True)
        dats_ok.columns = self.col_data_names
        print("   >已将原始文件处理好成标准格式")
        return True,dats_ok
    
    # 获取各工程编码入账数据
    def _getSapSum(self,dats):
        
        print("--->获取各工程编码入账数据...")
        col_stays = ['工程编码','成本要素','金额']
        dats_tmp = dats.loc[:,col_stays]
        dats_ok = dats_tmp.pivot_table(columns=['成本要素'],index=['工程编码'],aggfunc='sum')
        col_dir = {x:y for x,y in zip(self.yaosus_id,self.yaosus_name)}
        col_news = [col_dir[col] for col in dats_ok.columns.levels[1]]
        dats_ok.columns = col_news
        col_names = Series([col for col in self.yaosus_name if col in col_news])
        dats_ok = dats_ok.loc[:,col_names]
        col_names = col_names[-(col_names.isin(['工程物资-设备','工程物资-材料']))]
        dats_ok['SUM(不包含材料)'] = dats_ok[col_names].sum(axis=1)
        wbs_ids = dats_ok.index.tolist()
        ltebase = LteBase()
        wbs_names = []
        wbs_touzis = []
        for wbs_id in wbs_ids:
            wbs_names.append(ltebase.getWBSName(wbs_id))
            wbs_touzis.append(ltebase.getWbsInvest(wbs_id))
        col_ok = ['工程编码','工程名称','设计批复金额']
        col_ok.extend(dats_ok.columns)
        dats_ok['工程编码'] = wbs_ids
        dats_ok['工程名称'] = wbs_names
        dats_ok['设计批复金额'] = wbs_touzis
        dats_ok = dats_ok[col_ok]
        print("   >已获取各工程编码入账数据")
        return dats_ok
    # 获取SAP主材信息
    def _getSapZhucai(self,dats):
        
        print("--->求各工程编码主材信息,主材门限值为单价:【%d】"%(self.jine_min))
        f =lambda x: float('%.2f' % x)
        dats1 = dats[dats['成本要素']==8001020000]
        dats2 = dats[dats['成本要素']==8001010100]
        dats = dats1.append(dats2)
        dats = dats[['工程编码','物料编码','物料描述','数目','金额']]
        dats['单价'] = dats['金额']/dats['数目']
        dats = dats[dats['单价']>self.jine_min]
        dats = dats.drop(['单价'],axis=1)
        dats_ok = dats.pivot_table(index=['工程编码','物料编码','物料描述'],aggfunc='sum')
        dats_ok['单价'] = (dats_ok['金额']/dats_ok['数目']).apply(f)
        dats_ok['单价End'] = dats_ok['金额']-dats_ok['单价']*(dats_ok['数目']-1)
        dats_ok['物料描述'] = [dats_ok.index.levels[2][i] for i in dats_ok.index.labels[2]]
        dats_ok['物料编码'] = [dats_ok.index.levels[1][i] for i in dats_ok.index.labels[1]]
        dats_ok.index = [dats_ok.index.levels[0][i] for i in dats_ok.index.labels[0]]
        dats_ok = dats_ok.loc[:,['物料编码','物料描述','数目','金额','单价','单价End']]
        dats_ok.index.rename('工程编码',inplace=True)
        print("   > 各工程编码主材信息已处理完成")
        return dats_ok
    
    def _getLteZhucaiNum(self,dats,zhucai_file = 'lte_zhucai.xlsx'):
        print('---> 开始判定无线网主材数目（RRU和天线）')
        dats = dats[['物料编码','数目']]
        warnings.filterwarnings('ignore')
        wbs_ids = dats.index.unique()
        tmp = dats.index
        dats.index = range(len(dats.index))
        dats.loc[dats.index,'工程编码'] = tmp
        warnings.filterwarnings('default')
        print('   > 共获取%d条工程编码'%(len(wbs_ids)))       
        dats_base = pd.read_excel(self.dir_base + zhucai_file)
        dats_tmp = dats_base[dats_base['主材类型'] == '天线']
        list_tianxian = Series(dats_tmp['物料编码'].unique()).tolist()
        dats_tianxian = dats[dats['物料编码'].isin(list_tianxian)]
        dats_tianxian = dats_tianxian.pivot_table(index=['工程编码'],aggfunc='sum')
        dats_tmp = dats_base[dats_base['主材类型'] == 'RRU']
        list_rru = Series(dats_tmp['物料编码'].unique()).tolist()
        dats_rru = dats[dats['物料编码'].isin(list_rru)]
        dats_rru = dats_rru.pivot_table(index=['工程编码'],aggfunc='sum')
        dats_ok = DataFrame(columns = ['工程编码','RRU数目','天线数目'])
        ok_index = 0
        for wbs_id in wbs_ids:
            print('    > 开始获取%s主材数目'%(wbs_id))
            if wbs_id in dats_tianxian.index:
                num_tianxian = dats_tianxian.loc[wbs_id,'数目']
            else:
                num_tianxian = 0
            if wbs_id in dats_rru.index:
                num_rru = dats_rru.loc[wbs_id,'数目']
            else:
                num_rru = 0
            dats_ok.loc[ok_index] = [wbs_id,num_rru,num_tianxian]
            ok_index += 1
        print('   > 已获取无线网主材数目（RRU和天线）')
        return dats_ok

