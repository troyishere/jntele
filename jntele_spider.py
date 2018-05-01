# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 18:42:01 2018

@author: lenovo
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pandas import DataFrame
import math
import pandas as pd

class OperateHuanbao(object):
    
    
    def __init__(self,dir_out='huanbao\\'):
        self.dir_out = dir_out
        self.web_out = self.dir_out + 'web\\'
        # 城市所对应的编码
        self.citys_id = {
                '济南':'370100',
                '青岛':'370200',
                '淄博':'370300',
                '枣庄':'370400',
                '东营':'370500',
                '烟台':'370600',
                '潍坊':'370700',
                '济宁':'370800',
                '泰安':'370900',
                '威海':'371000',
                '日照':'371100',
                '莱芜':'371200',
                '临沂':'371300',
                '德州':'371400',
                '聊城':'371500',
                '滨州':'371600',
                '菏泽':'371700'
                }
        #济南区县所对应编码
        self.jncountys_id = {
                '历下':'370102',
                '市中':'370103',
                '槐荫':'370104',
                '天桥':'370105',
                '高新':'37010001',
                '历城':'370112',
                '长清':'370113',
                '平阴':'370124',
                '济阳':'370125',
                '商河':'370126',
                '章丘':'370181',
                '':''}
        self.jncountys_name = [
                '平阴',
                '历下',
                '市中',
                '槐荫',
                '天桥',
                '高新',
                '历城',
                '长清',
                '济阳',
                '商河',
                '章丘']
        self.url = 'http://58.56.98.90/REG/f/announcement/announcementShow'
        self.ses_datas = {
                'buildCity': '',
                'buildCounty':'',
                'buildProvince':'370000',
                'orderBy':'',
                'pageNo':'1',
                'pageSize':'10',
                'projectName':'',
                'recordNumber':''
                }
        self.ses_header={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:55.0) Gecko/20100101 Firefox/55.0'}
        self.session = requests.Session()
        
        
    def private_get_web_num(self,city_name='济南',county_name='',key=''):
        '''【私有】获取满足要求的环保申报的条数'''
        print('================================================')
        print('---> 开始获取%s%s环保申报的总条数:'%(city_name,county_name))
        if key != '':
            print('---->关键字为:%s'%(key))
        self.ses_datas['buildCity'] = self.citys_id[city_name]
        self.ses_datas['buildCounty'] = self.jncountys_id[county_name]
        sres = self.session.post(self.url, data=self.ses_datas ,headers = self.ses_header)
        html_text = sres.text
        bs = BeautifulSoup(html_text, "lxml")
        body_tag = bs.body
        div_tag = body_tag.find('div',{'class':"pagination",'style':"text-align: right;"})
        tmp_index = ((div_tag.text).find('共'))+2
        tmp_str = (div_tag.text)[tmp_index:]
        tmp_index = tmp_str.find('条')-1
        nums = int(tmp_str[:tmp_index])
        print('---> %s%s%s共获取%d条环保申报'%(city_name,county_name,key,nums))
        print('================================================')
        return nums
    
    def private_get_detail(self,html_text):
        '''【私有】获取环保申报详细信息'''
        
        bs = BeautifulSoup(html_text, "lxml")
        body_tag = bs.body
        table_tag = body_tag.find('table')
        tbody_tag = table_tag.find('tbody')
        flag1 = 0
        tmp = []
        for tr_tag in tbody_tag.findAll('tr'):
            if flag1 == 3:
                flag2 = 0
                for cell in tr_tag.findAll('td'):
                    if flag2 == 1:
                        tmp.append(cell.string)
                    flag2 += 1
            elif flag1 == 8:
                flag2 = 0
                for cell in tr_tag.findAll('td'):
                    if flag2 == 1:
                        tmp.append(cell.string)
                    flag2 += 1
            flag1 += 1
        return tmp
    
    def private_getJnteleByConty(self,city_name='济南',county_name='',
                                 company='中国电信股份有限公司济南分公司',
                                 date='',ifAll=False):
        '''【私有】按照区县获取济南电信环保申报信息
            date，str，从哪天开始获取，默认为所有申报
            ifAll，是否获取申报详细信息，默认为非详细信息
        '''
        print('================================================')
        if(ifAll):
            if_all = '需要获取详细信息'
        else:
            if_all = '不需要获取详细信息'
        if date == '':
            print('-->开始获取系统所有申报信息:%s'%(if_all))
            
        else:
            print('-->开始获取申报信息:%s，起始日期：%s'%(if_all,date))
            date_end = datetime.strptime(date,'%Y-%m-%d')
        shenbao_num = self.private_get_web_num(city_name,county_name,key)
        shanbao_pages = int(math.ceil(shenbao_num/100))
        self.ses_datas['pageSize'] = '100'
        print('-->%s%s%s共%d页环保申报信息'%(city_name,county_name,key,shanbao_pages))
        num_id = 0
        num_ok = 0
        all_infos = []
        
        for shanbao_page in range(1,shanbao_pages+1):
            print('---->开始获取第%d页信息...'%shanbao_page)

            self.ses_datas['pageNo'] = '%d'%shanbao_page
            sres = self.session.post(self.url, data=self.ses_datas ,headers = self.ses_header)
            html_text = sres.text
            bs = BeautifulSoup(html_text, "lxml")
            body_tag = bs.body
            table_tag = body_tag.find('table',{'id':'index_table'})
            tbody_tag = table_tag.find('tbody')
            url_all = 'http://58.56.98.90'
            ok_flag = True
            get_date = False
            for tr_tag in tbody_tag.findAll('tr'):
                tmp = []
                n = 0
                num_id += 1
                for cell in tr_tag.findAll('td'):
                    if ok_flag:
                        if n==2:
                            tmp.append('ID'+cell.string.strip())
                            
                        elif n==3:
                            if cell.string.strip() == company:
                                tmp.append(cell.string.strip())
                                print('--> 共%d信息，第%d信息：%s,ok'%(shenbao_num,num_id,cell.string.strip()))
                                num_ok = num_ok+1
                            else:
                                print('--> 共%d信息，第%d信息：%s,Pass'%(shenbao_num,num_id,cell.string.strip()))
                                ok_flag = False
                                n += 1
                                continue
                        elif n==5:
                            if date != '':
                                date_now = datetime.strptime(cell.string.strip(),'%Y-%m-%d')
                                if date_now > date_end:
                                    tmp.append(cell.string.strip())
                                else:
                                    get_date = True
                                    break
                            else:
                                tmp.append(cell.string.strip())
                                
                        elif n==6:
                            info = (cell.findAll('a')[0])['href']
                            tmp.append(info[(info.find('id=')+3):])
                            if ifAll:
                                res = self.session.get(url_all+info,headers = self.ses_header)
#                                print(info)
                                print('--> 获取%d详细信息：%s'%(num_id,res))
                                tmp_all = self.private_get_detail(res.text)
                                tmp.append(tmp_all[0])
                                tmp.append(tmp_all[1])
                        else:
                            tmp.append(cell.string.strip())
                        n += 1
                if get_date:
                    break
                if ok_flag:
                    all_infos.append(tmp)
                else:
                    ok_flag =True
            if get_date:
                break    
            print('---->第%d页信息获取完成...'%shanbao_page)
        cols_name = ['序号','项目名称','备案号','建设单位/个人','建设地点','公示日期','环评文件']
        if ifAll:
            cols_name.append('联系人')
            cols_name.append('建设内容及规模')
        print('---> 已收入%d条申报'%len(all_infos))
        
        list_df = DataFrame(all_infos,columns=cols_name)
        list_df = list_df[list_df['建设单位/个人']==company]
      
        file_out = city_name+county_name+key+datetime.now().strftime("%Y%m%d")+'.xlsx'
        list_df.to_excel(self.web_out+file_out,header=True,index=False)
        print('-->申报信息已获取完成，共%d条，数据已保存入%s'%(len(all_infos),file_out))
        print('================================================')
        
        return file_out

        
    def getJnteleWebInfo(self,countys='',date='',ifAll=False):
        '''获取环保申报信息入口'''
        if countys == '':
            countys = self.jncountys_name
        dats = DataFrame()
        print('****************************************************')
        print('--> 开始获取济南电信环保申报信息：（各区县数据单独保存）')
        for county in countys:
            tmp = self.private_getJnteleByConty(county_name=county,date=date,ifAll=ifAll)
            
            dats_tmp = pd.read_excel(self.web_out+tmp)
            dats = pd.concat([dats,dats_tmp],axis=0)
        dats
        file_out = 'ALL'+datetime.now().strftime("%Y%m%d")+'.xlsx'
        dats.to_excel(self.web_out+file_out,header=True,index=False) 
        print('--> 济南电信环保申报信息已保存,合计共%d条'%(dats.shape[0]))
        print('****************************************************')
        return dats
    
    def matchJnteleInfo(self,key='',file_in='',stations_in='stations.xlsx'):
        '''处理取得的环保数据'''
        print('****************************************************')
        print('--> 开始将基站名与环保申报数据相匹配')
        if file_in == '':
            file_in = 'ALL'+datetime.now().strftime("%Y%m%d")+'.xlsx'
        dats = pd.read_excel(self.web_out + file_in)
        if key == '':
            print('---> 无项目关键词过滤')
        else:
            print('---> 已根据项目关键词【%s】进行过滤'%(key))
            dats = dats[[key in project_name for project_name in dats.loc[:,'项目名称']]]
        stations = pd.read_excel(self.dir_out+stations_in)
        print('---> 共%d站点信息'%(stations.shape[0]))
        df_ok = DataFrame(columns=['区县','站点设计名','申报编码'])
        num = 0
        for county_name in self.jncountys_name:
            print('---> 开始匹配'+county_name+'环保申报信息>>>>>>>>>>>>>>')
            stations_county = stations[stations['区县'] == county_name]
            print('----> 共获得'+county_name+'站点数：【%d】'%(stations_county.shape[0]))
            dats_county = dats[[county_name in position_name for position_name in dats.loc[:,'建设地点']]]
            print('----> 共获得'+county_name+'申报数：【%d】'%(dats_county.shape[0]))
            
            for station in stations_county.loc[:,'设计名称'].unique():
                station_info = '，'+station + '基站'
                for infos,huanbao_id in zip(dats_county['建设内容及规模'], dats_county['备案号']):
                    if station_info in infos:
                        df_ok.loc[num] = [county_name,station,huanbao_id]
                        num = num+1
            print('---> %s-%s共有%d的申请，实际匹配到%s站'%(key,county_name,dats_county.shape[0],df_ok[df_ok['区县']==county_name].shape[0]))
        writer = pd.ExcelWriter('%s%s-ok.xlsx'%(self.dir_out,key))
        df_ok.to_excel(writer,'OK',header=True,index=False)
        print('--> 处理完成，共获取%d个基站的环保信息'%(df_ok.shape[0]))
        
 
if __name__ == '__main__':
    city_name = '济南'
    county_name = '平阴'
    key=''
    company='中国电信股份有限公司济南分公司'
    huanbao_operate = OperateHuanbao()
#    huanbao_file = huanbao_operate.getJnteleWebInfo(date='2018-4-1',ifAll=True)
#    huanbao_operate.private_getJnteleByConty(county_name='平阴',date='2018-4-1')
#    huanbao_operate.session.close()
#    huanbao_operate.matchJnteleInfo(file_in='ALL20180420.xlsx',stations_in='stations2.xlsx')
#    dateend = '2018-4-1'
#    datenow = '2018-4-3'
#    tmp = datestr.split('-')
#    date_time = datetime.strptime(dateend,'%Y-%m-%d')
    

    
    
