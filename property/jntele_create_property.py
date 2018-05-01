# -*- coding: utf-8 -*-
"""
Created on Sun Apr 29 14:05:41 2018

@author: lenovo
"""

import sys
sys.path.append('..\\')

from jntele_base import LteBase
import pandas as pd
import numpy as np
import pypinyin
from pandas import DataFrame

class LteCreateProperty(object):
    
    def __init__(self,dir_base,dir_log):
        self.dir_base = dir_base
        self.dir_log = dir_log
        self.df_base = pd.read_excel(dir_base + 'base\\ziyuanbase.xls')
        self.df_county = pd.read_excel(dir_base + 'base\\quyu.xls')
        self.df_changjia = pd.read_excel(dir_base + 'base\\changjia.xls')
        self.resource_col = [
                '单位',
                '工程编码',
                '站点名',
                '动环名',
                '设备类型',
                '站点内编号',
                '网管中标识',
                '资源名称',
                '资源编码']
        self.prop_pre_col = [
                '单位',
                '工程编码',
                '站点名',
                '固定资产目录',
                '资产名称',
                '所在地点',
                '规格程式',
                '厂家(全)',
                '厂家(简)',
                '资源名称',
                '资源编码']
        self.prop_col = [
                '编号',
                '批次',
                '单位',
                '工程编码',
                '站点名',
                '固定资产目录',
                '资产名称',
                '所在地点',
                '规格程式',
                '厂家(全)',
                '厂家(简)',
                '资源名称',
                '资源编码',
                '资源ID',
                '物料编码']
    
    # 向资产基础管理文件追加资产条目
    def appendLteProperty(self,file_base,file_in,
                          dir_in='',dir_out='create_ok\\'):
        dats_base = pd.read_excel(self.dir_base+file_base,
                                  dtype = {'资源ID':str,'固定资产目录':str})
        print('===================================================')
        print('-> 开始向LTE资产基础管理文件追加资产条目，并资源录入表')
        print('---> 目前基础表共有%d条资产'%(dats_base.shape[0]))
        dats_new = self.createLteResource(file_in,dir_in,dir_out,saveProp = False)
        dats_log = DataFrame(columns=['等级','工程编码','资源名称','说明'])
        log_index = 0
        print('---> 本次拟追加%d条资产信息'%(dats_new.shape[0]))
        print('---> 开始核实资源名重复性')
        for res_name in dats_new['资源名称']:
            dats_tmp = dats_base[dats_base['资源名称'] == res_name]
            if dats_tmp.shape[0] != 0:
                print('-----> 资源名称【%s】在基础表里面已存在'%(res_name))
                dats_log.loc[log_index] = ['E','Nonw',res_name,'在基础表里面已经存在']
                log_index += 1
        if dats_log.shape[0] !=0 :
            print('---> 本次追加资产在基础表里有%d条已存在'%(dats_log.shape[0]))
            log_out = self.dir_log + '追加资产日志' + LteBase.getTimeStr() + '.csv'
            dats_log.to_csv(log_out,header=True,index=False)
            print('---> 请查看相关日志:%s'%(log_out))
            print('-> 由于本次拟追加有重复条目，所以不执行追加操作，请先核实')
        else:
            base_id_max = max(dats_base['编号'])
            dats_new['编号'] = [bianhao + base_id_max + 1 for bianhao in dats_new['编号']]
            dats_base = dats_base.append(dats_new)
            dats_base.to_excel(self.dir_base+file_base,header=True,index=False)
            print('---> 已将追加资产保存到基础管理文件中:%s'%(self.dir_base+file_base))
            print('---> 追加完全成功，无相关日志输出')
            print('-> 向LTE资产基础管理文件追加资产条目，并资源录入表完成')
        print('===================================================')
            
    #生成LTE资源录入表
    def createLteResource(self,file_in,
                          dir_in='',dir_out='create_ok\\',saveProp = True):
        df = pd.read_excel(self.dir_base + dir_in + file_in)
        print('---> 开始生成资源录入文件')
        print('-----> 导入资源生成模板文件成功:'+self.dir_base + dir_in + file_in)
        print('-----> 共有%d条站点信息需要处理'%(df.shape[0]))
        #站名生成编码 
        df.loc[:,'站点拼音'] = [self._toPinyin(name) for name in df.loc[:,'设计名称']]
        # 信源名生成编码
        df.loc[:,'信源拼音'] = [self._toPinyin(name) for name in df.loc[:,'信源站']]
        df_res = DataFrame(columns=self.resource_col)
        df_prop = DataFrame(columns=self.prop_pre_col)
        num = 0
        for inx in df.index:
            info = df.loc[inx]
            if info[13]==1:#BBU
                zy_name = info[2]+info[9]+self._getziyuan(info[12])+info[11].replace('-','/')
                zy_bianma = self._getcountypinyin(info[2])+info[21]+u'/'+self._getziyuan(info[12])+info[11].replace('-','/')
                df_res.loc[num]=[info[3],info[4],info[0],#head
                        info[10],info[12],info[7],info[6],
                        zy_name,
                        zy_bianma]
                df_prop.loc[num]=[info[3],info[4],info[0],#head
                        u'07030903',u'分布式基站设备',
                        info[2]+info[9]+info[11]+u'(RRU在'+info[0]+u')',
                        self._getdevice(info[12]),
                        self._getchangjiaL(self.getchangjia(info[12])),
                        self._getchangjiaS(self.getchangjia(info[12])),  
                        zy_name,
                        zy_bianma]
                num = num+1
            for n in range(1,int(info[15])+1):
                zy_name = info[2]+info[0]+self._getziyuan(info[14])+'/%02d'%n;
                zy_bianma = self._getcountypinyin(info[2])+info[20]+'/'+self._getziyuan(info[14])+'/%02d'%n
                df_res.loc[num]=[info[3],info[4],info[0],#head
                        info[1],info[14],info[7],info[5],
                        zy_name,
                        zy_bianma]
                df_prop.loc[num]=[info[3],info[4],info[0],#head
                        u'0703090304',u'分布式基站设备',
                        info[2]+info[0]+u'基站',
                        self._getdevice(info[14]),
                        self._getchangjiaL(self._getchangjia(info[14])),
                        self._getchangjiaS(self._getchangjia(info[14])),         
                        zy_name,
                        zy_bianma]
                num = num+1
                if n==1:
                    for j in range(1,info[18]+1):
                        zy_name = info[2]+info[0]+self._gettianxian(info[14])+u'基站天线%02d'%j
                        zy_bianma = self._getcountypinyin(info[2])+info[20]+u'/'+self._gettianxian(info[14])+u'JZTX0%d'%j
                        df_res.loc[num]=[info[3],info[4],info[0],#head                   
                                info[1],info[19]+u'天线',0 , 0,
                                zy_name,
                                zy_bianma]
                        df_prop.loc[num]=[info[3],info[4],info[0],#head
                                u'07030602',u'定向天线',
                                zy_name+u'基站天线',
                                info[17],
                                self._getchangjiaL(info[19]),
                                self._getchangjiaS(info[19]),
                                zy_name,
                                zy_bianma]
                        num = num+1
        print('-----> 资源录入数据已生成，共有%d条'%(df_res.shape[0]))                
        file_out = self.dir_base + dir_out + '资源录入' + LteBase.getDateStr() + '批.xlsx'
        writer = pd.ExcelWriter(file_out)
        df_res.to_excel(writer,'ziyuan',header=True,index=False)
        list_pici = []
        str_pici = LteBase.getDateStr() + '批'
        list_res_id = []
        list_wuliao_id =[]
        for i in range(df_prop.shape[0]):
            list_pici.append(str_pici)
            list_res_id.append('none')
            list_wuliao_id.append('none')
        file_out = self.dir_base + dir_out + '资产' + LteBase.getDateStr() + '批.xlsx'
        df_prop['编号'] = [i for i in range(df_prop.shape[0])]
        df_prop['批次'] = list_pici
        df_prop['资源ID'] = list_res_id
        df_prop['物料编码'] = list_wuliao_id
        df_prop = df_prop[self.prop_col]
        if saveProp:
            df_prop.to_excel(writer,'zichan',header=True,index=False)
        writer.save()
        if saveProp:
            print('-----> 资源录入数据和生成的资产数据也已存入%s'%(file_out))
        else:
            print('-----> 资源录入数据已存入:%s'%(file_out))
        print('---> 资源录入文件已生成')
        return df_prop
    # 基础函数，将名称转变为拼音首字母字符串
    def _toPinyin(self,name):
        '''按相应规则获取站点名称的拼音简称'''
        if type(name) == str:
            pinlist = pypinyin.pinyin(name, style=pypinyin.NORMAL)
            return (''.join(map(str,[pl[0] if any(c.isdigit() for c in pl[0]) else pl[0][0] for pl in pinlist])).upper())
        else:
            return ''
    def _getziyuan(self,x):
        """获取设备名资源简称"""
        tmp_df = np.array(self.df_base.loc[:,x])
        name=tmp_df.tolist()
        return name[0]
    def _getcountypinyin(self,x):
        """获取区县拼音简称"""
        tmp_df = np.array(self.df_county.loc[:,x])
        name=tmp_df.tolist()
        return name[0]
    def _getdevice(self,x):
        """获取设备类型"""
        tmp_df = np.array(self.df_base.loc[:,x])
        name=tmp_df.tolist();
        return name[2]
    
    def _getchangjia(self,x):
        """获取厂家"""
        tmp_df = np.array(self.df_base.loc[:,x]);
        name=tmp_df.tolist();
        return name[1]
    def _getchangjiaS(self,x):
        dfs= self.df_changjia.loc[:,x];
        tmp_df = np.array(dfs);
        name=tmp_df.tolist();
        return name[1];
    def _getchangjiaL(self,x):
        dfs= self.df_changjia.loc[:,x];
        tmp_df = np.array(dfs);
        name=tmp_df.tolist();
        return name[0];
    def _gettianxian(self,x):
        """获取转固天线类型"""
        dfs= self.df_base.loc[:,x];
        tmp_df = np.array(dfs);
        name=tmp_df.tolist();
        return name[3];
    '''
    def get_tianxian_data(self,file_in):
        print('----------------------------------------------------')
        print('--->开始创建天线资源表和资产表...')
        dats = pd.read_excel(self.dir_in+file_in)
        print(' -->导入模板文件成功:'+file_in)
        station_pins=[self.private_toPinyin(name) for name in dats['站点名']]
        county_pins = [self.getquyupinyin(county_pin) for county_pin in dats['区域']]
        pin_base_names = [county_pin+stationpin+'/'+tianx_class+'JZTX' 
                          for county_pin,stationpin,tianx_class in zip(county_pins,station_pins,dats['类型'])]
        station_base_names = [county_name + station_name + tianx_class+ '基站天线' 
                              for county_name,station_name,tianx_class in zip(dats['区域'],dats['站点名'],dats['类型'])]
        
        dats['资源名BASE'] = station_base_names
        dats['资源拼音BASE'] = pin_base_names
        df_ziyuan = DataFrame(columns=self.ziyuan_col)
        df_zichan = DataFrame(columns=self.zichan_col)
        num = 0
        for indexs in dats.index:
            fuze = '赵宗良'
            for n in range(1,int(dats.loc[indexs][2]+1)):
                df_ziyuan.loc[num] = [fuze,dats.loc[indexs][3],dats.loc[indexs][1],
                              '','天线',
                              '',dats.loc[indexs][7],
                              '%s%02d'%(dats.loc[indexs][8],n),'%s%02d'%(dats.loc[indexs][9],n)]
                df_zichan.loc[num] = [fuze,dats.loc[indexs][3],dats.loc[indexs][1],
                              '07030602','定向天线',
                              dats.loc[indexs][8],dats.loc[indexs][5],
                              self.getchangjiaQ(dats.loc[indexs][4]),
                              self.getchangjiaJ(dats.loc[indexs][4]),
                              '%s%02d'%(dats.loc[indexs][8],n)]
                num = num+1
        file_out = self.dir_out+file_in.split('.')[0]+'-ok.xlsx'
        writer = pd.ExcelWriter(file_out)
        df_ziyuan.to_excel(writer,'ziyuan',header=True,index=False)
        df_zichan.to_excel(writer,'zichan',header=True,index=False)
        writer.save()
        print(' --> 资源/资产文件保存完成:'+file_out) 
    '''
if __name__ == '__main__':
    
    dir_base = '..\\zhuangu\\'
    dir_log = '..\\zhuangu\\log\\'
    op = LteCreateProperty(dir_base,dir_log)
#    tmp = op.createLteResource('LTE6-0416.xlsx')
    tmp = op.appendLteProperty('LTE六期资源录入0403.xlsx','LTE6-0416.xlsx')
    
    
    
    