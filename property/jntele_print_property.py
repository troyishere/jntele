# -*- coding: utf-8 -*-
"""
Created on Sat Apr  7 23:11:27 2018
生成PDF版的验收报告和资产明细
@author: lenovo
"""

import sys
sys.path.append('..\\')
import os
from jntele_base import LteBase
from pandas import Series,DataFrame
import pandas as pd
import pdfkit
from PyPDF2.pdf import PdfFileReader,PdfFileWriter
from pdfminer.pdfparser import PDFParser,PDFDocument
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager,PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator

HH_NUM1=10;         #自动换行字符长度1
HH_NUM2=12;         #自动换行字符长度2
HH_NUM3=29;         #自动换行字符长度3
#HH_NUM4=10;         #自动换行字符长度4
#HH_NUM5=20;         #自动换行字符长度5

def get_td_str(strinfo):
    return "           <td>%s</td>\n"%strinfo
def get_td_5ok(strinfo):
    return "           <td><div class=\"divcent\"><font size=\"5\">%s</font></div></td>\n"%strinfo
def get_td_4ok(strinfo):
    return "           <td><div class=\"divcent\"><font size=\"4\">%s</font></div></td>\n"%strinfo
def get_td_3ok(strinfo):
    return "           <td><div class=\"divcent\"><font size=\"3\">%s</font></div></td>\n"%strinfo


def get_kongge(num):
    strkg="&nbsp;"
    strres=""
    for n in range(num):
        strres="%s%s"%(strres,strkg);
    return strres
def add_kongge(strkg,num):
    return "%s%s%s"%(get_kongge(num),strkg,get_kongge(num))
def get_cent_str(strinfo):
    return "<div class=\"divcent\">%s</div>"%strinfo
def get_font_str(strinfo,num=5):
    return "<font size=\"%d\">%s</font>"%(num,strinfo)
def get_fontsize2(strinfo):
    return "<span class=\"fontsize\">%s</span>"%strinfo
def get_huanhang1(strhh):
    strok="";
    m=range(0,len(strhh),HH_NUM1);
    for n in range(len(m)-1):
        strok="%s%s<br />"%(strok,strhh[m[n]:m[n+1]])
    strok="%s%s"%(strok,strhh[m[len(m)-1]:len(strhh)])
    return strok
    
def get_huanhang2(strhh):
        
    strok="";
    m=range(0,len(strhh),HH_NUM2);
    for n in range(len(m)-1):
        strok="%s%s<br />"%(strok,strhh[m[n]:m[n+1]])
    strok="%s%s"%(strok,strhh[m[len(m)-1]:len(strhh)])
    return strok

def get_huanhang3(strhh):
    strok="";
    m=range(0,len(strhh),HH_NUM3);
    for n in range(len(m)-1):
        strok="%s%s<br />"%(strok,strhh[m[n]:m[n+1]])
    strok="%s%s"%(strok,strhh[m[len(m)-1]:len(strhh)])
    return strok


class LtePrint(object):
    
    def __init__(self,dir_base,dir_log):
        self.dir_base = dir_base
        self.dir_log = dir_log
        self.ltebase = LteBase()
        self.key_yanshou = 'WBSD'
        self.dats_log = DataFrame(columns=['等级','工程编码','资源名称','说明'])
        self.log_index = 0
    
    # 无线网CMD调用函数    
    def printLteProperty(self,file_base,wbs_ids,dir_out = 'print_ok\\',saveOne=True):
        '''file_base为资产信息存储文件'''
        '''wbs_ids为工程编码列表'''
        dats_base = pd.read_excel(self.dir_base+file_base,
                                  dtype = {'资源ID':str,'固定资产目录':str})
        print('===================================================')
        print('-> 开始自动生成无线网工程资产明细表PDF版')
        for wbs_id in wbs_ids:
            print('---> 开始生成%s的资产明细表'%(wbs_id))
            dats_tmp = dats_base[dats_base['工程编码']==wbs_id + 'N']
            if dats_tmp.shape[0] !=0:
                print('-----> 该工程有%d条资源拟不转固资产'%(dats_tmp.shape[0]))
            dats_wbs = dats_base[dats_base['工程编码']==wbs_id]
            print('-----> 该工程有%d条资产明细'%(dats_wbs.shape[0]))
            dats_tmp = dats_wbs[dats_wbs['资源ID'] == 'none']
            if dats_tmp.shape[0] !=0:
                print('-----> 该工程有%d条资产未匹配资源ID:')
                for inx in dats_tmp.index:
                    print('       %d:资源名称【%s】'%(inx,dats_tmp.loc[inx,'资源名称']))
                    self.dats_log.loc[self.log_index] = ['E',wbs_id,dats_tmp.loc[inx,'资源名称'],
                                 '对应资源ID为空']
                    self.log_index += 1
            fuzes = Series(dats_wbs['单位'].unique())
            fuze_list = Series(dats_wbs['单位'])
            if saveOne:
                print('-----> 该工程编码生成一张总的资产明细表')
                fuze_dir = {}
                for fuze in fuzes:
                    fuze_dir[fuze] = len(fuze_list[fuze_list==fuze])
                fuze = max(fuze_dir, key=fuze_dir.get)
                print('       负责人为%s'%(fuze))
                df_zichan = dats_wbs[['资源ID','资产名称','规格程式','厂家(简)','所在地点']]
                file_out = '%s%s%s-%s-资产明细原始.pdf'%(self.dir_base,dir_out,wbs_id,fuze)
                file_end = '%s%send//%s-%s-资产明细打印.pdf'%(self.dir_base,dir_out,wbs_id,fuze)
                self._getLteProperty(wbs_id,fuze,df_zichan,file_out)
                self._getLtePropertyPrintPage(wbs_id,file_out,file_end)
                
                
            else:
                print('-----> 该工程编码按照施工单位生成资产明细表')
                for fuze in fuzes:
                    df_zichan = dats_wbs[dats_wbs['单位']==fuze]
                    df_zichan = df_zichan[['资源ID','资产名称','规格程式','厂家(简)','所在地点']]
                    file_out = '%s%s%s-%s-资产明细原始.pdf'%(self.dir_base,dir_out,wbs_id,fuze)
                    self._getLteProperty(wbs_id,fuze,df_zichan,file_out)
                    
        if self.dats_log.shape[0] == 0:
            print('---> 匹配完全成功，无相关日志输出')
        else:
            log_out = self.dir_log + '资产明细PDF日志' + LteBase.getTimeStr() + '.csv'
            self.dats_log.to_csv(log_out,header=True,index=False)
            print('---> 请查看相关日志:%s'%(log_out))             
        print('-> 无线网工程资产明细表PDF版已生成')
        print('===================================================')
        
    # 这是基础函数，仅限LTE使用，其他专业使用需变更
    def _getLteProperty(self, wbs_id,fuze,df_zichan,file_out):
        htmls =[
        "<html>",
        "<style>",
        "   .divcent{text-align:center}",
        "   .fontsize{ font-size:22px}",
        "</style>",
        "<body>",
        get_cent_str("<h2><b>工程项目资产明细统计表</b></h2>"),
        get_font_str("工程名称："+ self.ltebase.getWBSName(wbs_id),4),
        "<br />",
        get_font_str("工程编码："+wbs_id,4),
        get_kongge(98),
        get_font_str("项目经理：赵宗良",4),
        "<br />",
        get_font_str("施工单位："+self.ltebase.getDanweiAll(fuze),4),
        get_kongge(70),
        get_font_str("施工人员：",4),
        "   <table border=\"2\" bordercolor=\"#000000\" cellspacing=\"0\"",
        "cellpadding=\"2\" style=\"border-collapse:collapse;\">",
        "        <tr>",
        get_td_3ok('序号'),
        get_td_3ok('资源编号'),
        get_td_3ok('资产名称'),
        get_td_3ok(add_kongge('规格型号',10)),
        get_td_3ok('数量'),
        get_td_3ok('生产厂家'),
        get_td_3ok('专业归属'),
        get_td_3ok('站点及设备安<br />装位置'),
        get_td_3ok('局端/用户端'),
        "        </tr>"
        ]
        num = 1
        for index in df_zichan.index:
            htmls.append("        <tr>")
            infos = df_zichan.loc[index].values.tolist()
            htmls.append(get_td_3ok(str(num)))
            htmls.append(get_td_3ok(get_huanhang2(str(infos[0]))))
            htmls.append(get_td_3ok(infos[1]))
            htmls.append(get_td_3ok(infos[2]))
            htmls.append(get_td_3ok('1'))
            htmls.append(get_td_3ok(get_huanhang2(infos[3])))
            htmls.append(get_td_3ok('无线'))
            htmls.append(get_td_3ok(infos[4]))
            htmls.append(get_td_3ok('局端'))
            htmls.append("        </tr>")
            num = num + 1
#        htmls.append("        <tr>")
#        htmls.append(get_td_3ok(''))
#        htmls.append(get_td_3ok(fuze))
#        htmls.append(get_td_3ok('WBSID'))
#        htmls.append(get_td_3ok(wbs_id))
#        
#        htmls.append("        </tr>")
        htmls_end = [
        "   </table>",
#        "<br />",
        get_font_str(fuze + ' | ' + self.key_yanshou + ' | '+wbs_id,4),
        "<br />",
        get_font_str("施工单位签字/盖章：",4),
        get_kongge(30),
        get_font_str("监理单位签字/盖章：",4),
        get_kongge(30),
        get_font_str("维护验收人员签字/盖章：",4),
        "<br />",
        get_font_str("专业主管签字：",4),
        get_kongge(41),
        get_font_str("监理单位验收日期：",4),
        get_kongge(31),
        get_font_str("维护验收人员验收日期：",4),
        "<br />",
        get_font_str("建设部项目经理签字：",4),
        get_kongge(100),
        get_font_str("网运部资产管理签字：",4),

        "</body>",
        "</html>"
        ]
        htmls += htmls_end
        yanshou_strs = ''.join(map(str,htmls))
        options = {
            'page-size':'Letter',
            'margin-top':'0.5in',
            'margin-right':'0.5in',
            'margin-bottom':'0.6in',
            'margin-left':'0.9in',
#            'encoding':"GB2312",
            'encoding':'utf-8',
            'no-outline':None
        }
    
        try:
            pdfkit.from_string(yanshou_strs,file_out,options=options)
            print('-----> 资产明细已保存：【%s】'%(file_out))
        except LookupError as err:
            print('-----> PDF操作中存在错误！')
            pass
        
        
        return htmls
    
    def _getLtePropertyPrintPage(self,wbs_id,file_pdf,file_end):
        '''生成要打印签字的资产明细页'''
        print('---> 开始生成%s要打印签字的资产明细页'%(wbs_id))
        (page_num,page_end) = self._getYanshouKeyPage(file_pdf,self.key_yanshou)
        fp_in = open(file_pdf, "rb")
        pdf_in = PdfFileReader(fp_in)
        pageCount = pdf_in.getNumPages()
        if pageCount != page_num+1:
            print('     > PyPDF2(%d)及pdfminer(%d)判定文件页数不同'%(pageCount,page_num))
            self.dats_log.loc[self.log_index] = ['E',wbs_id,'PDF文件',
                             'PyPDF2(%d)及pdfminer(%d)判定文件页数不同,未生成最后签字页'%(pageCount,page_num)]
            self.log_index += 1
            return
        if page_end == -1:
            print('   > 未找到关键字【%s】所在的页，也即未找到最后签字页'%(self.key_yanshou))
            self.dats_log.loc[self.log_index] = ['E',wbs_id,'PDF文件',
                             '未找到关键字【%s】所在的页，也即未找到最后签字页'%(self.key_yanshou)]
            self.log_index += 1
            return 
        page = pdf_in.getPage(page_end)
        pdf_out = PdfFileWriter()
        pdf_out.addPage(page)
        fp_out = open(file_end, 'wb')
        pdf_out.write(fp_out)
        fp_in.close()
        fp_out.close()
        print('---> 已获取资产明细最后一页并已保存至%s'%(file_end))
        
        if page_num == page_end + 1:
            print('   > 需把%s文件删除最后1页'%(file_pdf))
            self._removeYanshouEndPage(file_pdf)
#        
#        pdf_file = 'pdf\\17SD002341003-资产明细.pdf'
#        pdf_save = 'pdf\\17SD002341003-打印.pdf'
#        pdf_in = PdfFileReader(open(pdf_file, "rb"))
#        pageCount_in = pdf_in.getNumPages()
#        pdf_out = PdfFileWriter()
#        page = pdf_in.getPage(pageCount_in-1)
#        pdf_end = PdfFileWriter() 
#        pdf_end.addPage(page)
#        pdf_end.write(open(pdf_save, 'wb'))
#        print('---> 已获取资产明细最后一页并已保存至%s'%(pdf_file))
        
    def _removeYanshouEndPage(self,file_pdf):
        '''移除资产明细表中的无用页'''
        fd_in = open(file_pdf, "rb")
        pdf_in = PdfFileReader(fd_in)
        page_num = pdf_in.getNumPages()
        pdf_out = PdfFileWriter()
        for num in range(page_num-1):
            page = pdf_in.getPage(num)
            pdf_out.addPage(page)
        fd_out = open(file_pdf+'tmp.pdf', "wb")
        pdf_out.write(fd_out)
        fd_in.close()
        fd_out.close()
        os.remove(file_pdf)
        os.rename(os.path.join('',file_pdf+'tmp.pdf'),os.path.join('',file_pdf))
        print('   > 已把最后一页删除')
            
    def _getYanshouKeyPage(self,pdf_file,key='WBID'):
        '''获取关键字所在的页数'''
        # 创建一个与文档关联的解释器
        praser = PDFParser(open(pdf_file,'rb'))
        # 创建PDF文档的对象
        doc = PDFDocument()
        # 连接文档对象和解析器
        
        praser.set_document(doc)
        doc.set_parser(praser)
        # 初始化文档， 可以设置密码
        doc.initialize()
        
        # 获取文档页数
        page_num = 0
        for page in doc.get_pages():
            page_num += 1
        page_num -= 1
        
        # 创建PDF的资源管理器
        resource = PDFResourceManager()
        # 设定参数进行分析
        laparam=LAParams()
        # 创建一个聚合器
        device = PDFPageAggregator(resource, laparams=laparam)
        # 创建PDF页面解释器
        interpreter = PDFPageInterpreter(resource, device)
        # 处理每一页
        i = 0
        isEnd = False
        for page in doc.get_pages():
            if i == page_num:
                # 使用页面解析器来读取 
                interpreter.process_page(page) 
                # 使用聚合器来获取内容 
                layout = device.get_result()
                for out in layout:
                    if hasattr(out, "get_text") and key in out.get_text():
                        isEnd = True
            i += 1
        if isEnd:
            page_end = page_num
        elif page_num != 0:
            i = 0
            for page in doc.get_pages():
                if i == page_num-1:
                    # 使用页面解析器来读取 
                    interpreter.process_page(page) 
                    # 使用聚合器来获取内容 
                    layout = device.get_result()
                    for out in layout:
                        if hasattr(out, "get_text") and key in out.get_text():
                            isEnd = True
                i += 1
            if isEnd:
                page_end = page_num - 1
        if not isEnd:
            print('   > 未发现含有关键字【%s】的页面，请核实'%(key))
            page_end = -1
        print('   > 本文档最大页为%d，关键字在%d页'%(page_num,page_end))
        return (page_num,page_end)
    
    
    
    # 获取LTE总验收报告
    def getLteMultipleReport(self,file_in,dir_in='report_in\\',dir_out='report_ok\\'):
        '''创建总验收报告'''
        print('=================================================')
        print('-> 开始生成多站验收报告:')
        dats = pd.read_excel(self.dir_base+dir_in+file_in)
        wbs_ids = Series(dats['wbs_id'].unique())
        for wbs_id in wbs_ids:
            print('---> 工程编码：%s'%(wbs_id))
            dats_id = dats[dats['wbs_id']==wbs_id]
            fuzes = Series(dats_id['fuze'].unique())
            [startdate,enddate,cydate,zydate] = self.ltebase.getWBSDates(wbs_id)
            for fuze in fuzes:
                print('---> 负责人：%s'%(fuze))
                dats_station = dats_id[dats_id['fuze']==fuze]
                wbs_info = self.private_getMultInfos(dats_station)
                pdfname = "%s%s%s-%s-验收报告.pdf"%(self.dir_base,dir_out,wbs_id,fuze)
                self._getYanshou(wbs_id,fuze,wbs_info,pdfname,
                                        startdate,enddate,cydate,zydate)
        print('-> 多站验收报告创建完成')
        print('=================================================')    
    
    # 获取LTE单站验收报告
    def getLteSingleReport(self,file_in,dir_in='report_in\\',dir_out='report_ok\\'):
        '''创建单站验收报告'''
        print('=================================================')
        print('--> 开始生成单站验收报告:')
        df = pd.read_excel(self.dir_base+dir_in+file_in)
        for index in df.index:
           [station_name,fuze,wbs_id,station_class] = df.loc[index].values
           print('---> %s基站...'%(station_name))           
           wbs_info = '在%s基站施工%s设备、天线。'%(station_name,station_class)
           pdfname = "%s%s%s-%s-验收报告.pdf"%(self.dir_base,dir_out,fuze,station_name)
           self._getYanshou(wbs_id,fuze,wbs_info,pdfname)
        print('--> 单站验收报告创建完成')
        print('=================================================')
    
    # 获取验收报告通用函数
    def getCommonReport(self,wbs_id,fuze,wbs_info,dir_out='report_ok\\'):
        '''创建通用验收报告'''
        print('=================================================')
        print('--> 开始生成通用验收报告:')
        pdfname = "%s%s%s-%s-验收报告.pdf"%(self.dir_base,dir_out,wbs_id,fuze)
        [startdate,enddate,cydate,zydate] = self.ltebase.getWBSDates(wbs_id)
        self._getYanshou(wbs_id,fuze,wbs_info,pdfname,
                                startdate,enddate,cydate,zydate)
        print('--> 已生成通用验收报告')
        print('=================================================')
    
    # 获取验收报告通用模板（非LTE需做适当变更）
    def _getYanshou(self,wbs_id,fuze,wbs_info,pdf_name,
                           startdate='',enddate='',cydate='',zydate=''):
        
        wbs_name = get_huanhang2(self.ltebase.getWBSName(wbs_id))
        danwei_name = get_huanhang2(self.ltebase.getDanweiAll(fuze)); 
        if wbs_id == '':
               wbs_id = 'LTE2018001'        
        kgstr10=get_kongge(10);
        htmls =[
        "<html>",
        "<style>",
        "   .divcent{text-align:center}",
        "   .fontsize{ font-size:22px}",
        "</style>",
        "<body>",
        "   <table border=\"2\" bordercolor=\"#000000\" cellspacing=\"0\"",
        "cellpadding=\"2\" style=\"border-collapse:collapse;\">",
        "     <caption><h1><b>工程验收证书</b></h1><br /></caption>",
        "        <tr>",
        get_td_5ok(add_kongge(u"工程名称",2)),
        get_td_5ok(wbs_name),
        get_td_5ok(add_kongge(u"项目编码",2)),
        get_td_5ok(add_kongge(wbs_id,8)),       
        "        </tr>",
        "        <tr>",
        "           <td height=\"45px\">",
        get_cent_str(get_font_str(u"施工单位")),
        "           </td>",
        get_td_5ok(danwei_name),
        get_td_5ok(u"建设地址"),
        get_td_5ok(u"济南市"),
        "        </tr>", 
        "        <tr>",
        "           <td height=\"85px\">",
        get_cent_str(get_font_str(u"工程内容<br />简要说明")),
        "           </td>" ,
        "           <td colspan=\"3\">",
        get_cent_str(get_fontsize2(get_huanhang3(wbs_info))),
        "           </td>" ,
        "        </tr>",
        "        <tr>",
        "           <td height=\"45px\">",
        get_cent_str(get_font_str(u"开工时间")),
        "           </td>",
        get_td_5ok(startdate),
        get_td_5ok(u"完工时间"),
        get_td_5ok(enddate),
        "        </tr>",
        "        <tr>",
        "           <td height=\"45px\">",
        get_cent_str(get_font_str(u"初验时间")),
        "           </td>",
        get_td_5ok(cydate),
        get_td_5ok(u"终验时间"),
        get_td_5ok(zydate),
        "        </tr>",
        "        <tr>",
        "          <td colspan=\"4\">",
        get_font_str(u"施工中重大质量事故处理的审查意见<br /><br /><br />"),
        "          </td>",
        "        </tr>",
        "        <tr>",
        "          <td colspan=\"4\">",
        get_font_str(u"<b>验收情况</b>(包括工程质量进度等方面的评价和分析)<br /><br /><br /><br />"),
        "          </td>",
        "        </tr>",
        "        <tr>",
        "          <td colspan=\"4\">",
        get_font_str(u"<b>建议</b>(包括对使用维护等注意事项，对工程遗留问题的处理意见)<br /><br /><br />"),
        "          </td>",
        "        </tr>",
        "        <tr>",
        "          <td colspan=\"4\">",
        get_font_str(u"<b>验收结论: </b><br /><br /><br />"),
        "          </td>",
        "        </tr>",
        "        <tr>",
        "          	  <td colspan=\"4\">",
        get_font_str(u"<b>验收人员签字：</b><br /><br />"),
        get_font_str("%s%s%s%s%s%s%s"%(kgstr10,u"建设部门：(章)",kgstr10,u"维护部门：(章)",kgstr10,u"财务部门：(章)",kgstr10)),
        get_font_str("<br /><br /><br /><br /><br />"),
        get_font_str("%s%s%s%s%s%s%s"%(kgstr10,u"施工单位：(章)",kgstr10,u"设计单位：(章)",kgstr10,u"监理单位：(章)",kgstr10)),
        get_font_str("<br /><br /><br /><br /><br />"),
                    
        "          	  </td>",
        "        </tr>",
        "   </table>",
        "</body>",
        "</html>"
        ]
        yanshou_strs = ''.join(map(str,htmls))
                
        options = {
            'page-size':'Letter',
            'margin-top':'0.5in',
            'margin-right':'0.5in',
            'margin-bottom':'0.6in',
            'margin-left':'0.6in',
            # 'encoding':"GB2312",
            'encoding':'utf-8',
            'no-outline':None
        }
    
        try:
            # pdfkit.from_file(htmlname,pdf_name,options=options)
            pdfkit.from_string(yanshou_strs, pdf_name, options=options)
            print('---> 验收报告已保存【%s】' % (pdf_name))
        except LookupError as err:
            pass
    
    
    

    def private_getMultInfos(self,dats_station):
        '''获取多站验收报告验收内容'''
        station_classes = Series(dats_station['station_class'].unique())
        wbs_infos = []
        for station_class in station_classes:
            wbs_infos.append('在')
            dats_ok = dats_station[dats_station['station_class']==station_class]
            for station in dats_ok['station_name']:
                wbs_infos.append(station)
                wbs_infos.append('、')
            del(wbs_infos[-1])
            wbs_infos.append('等基站施工%s主设备、天线；'%(station_class))
        return ''.join(map(str,wbs_infos)) 

