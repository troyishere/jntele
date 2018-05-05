# -*- coding: utf-8 -*-
"""
Created on Wed May  2 13:11:38 2018
对无线网验收报告、报账单、资产明细图片文件进行处理
@author: lenovo
"""
import sys
sys.path.append('..\\')
from jntele_base import LteBase
from PIL import Image
import pytesseract
import random
import os

class OperateLteImage(object):
    
    def __init__(self,dir_base,dir_log):
        
        self.dir_base = dir_base
        self.dir_log = dir_log
        
    def matchYanshouImage(self,wbs_ids = '',
                          dir_in = 'img_yanshou_old\\',dir_out = 'img_yanshou_ok\\'):
        '''将JPG格式的验收报告扫描件命名格式化'''
        ltebase = LteBase()
        if wbs_ids == '':
            print('---> 未规定具体工程编码集，使用所有无线网工程编码')
            wbs_ids = ltebase.getAllWBSId()
            print(type(wbs_ids))
        for lists in os.listdir(self.dir_base+dir_in):   
            img_file = os.path.join(self.dir_base+dir_in, lists)
            if not img_file.endswith('.jpg'):
                continue
            
            print('---> 开始处理%s'%(img_file))
            
            img = Image.open(img_file)
            '''==================================================================='''
            region_name=img.crop((1000,300,img.size[0]-600,550))
    #        region_name=img.crop((0,0,img.size[0],550))
            text_name = pytesseract.image_to_string(region_name,lang='chi_sim')
            text_name = text_name.strip()
            if '验收证书' in text_name or '初验证书' in text_name or '验收报告' in text_name:
                print('     > 该JPG文件是验收报告扫描件')
            else:
                print('     > 该JPG文件未检索到验收报告关键字，请核实')
                print(text_name)
                region_name.show()
            '''==================================================================='''
            region_wbs=img.crop((1700,500,img.size[0]-250,700))
            text_wbs = pytesseract.image_to_string(region_wbs,lang='eng')
            text_wbs = text_wbs.strip()
            isIn = False
            for wbs_id in wbs_ids:
                if wbs_id[7:] in text_wbs: #只判定工程编码的后6位
                    isIn = True
                    print('     > 该验收报告对应工程编码为%s'%(wbs_id))
                    img_out = self.dir_base + dir_out + ltebase.getWBSName(wbs_id) + '验收证书' + ltebase.getChuyanDate(wbs_id) + '.jpg'
                    img.save(img_out,'JPEG')
                    os.remove(img_file)
                    print('     > 已将验收报告保存到：%s'%(img_out))
                    print('     > 原文件已删除')
                    break
            if not isIn:
                print('     > 未找到相应工程编码,请核实')
                region_wbs.show()
            '''==================================================================='''
    def operateBaozhangImg(self,wbs_ids,dir_in = 'img_baozhang\\'):
        '''JPG格式无线网处理报账添加签名'''
        print('-> 开始对无线网报账单进行处理')
        for wbs_id in wbs_ids:
            print('---> 开始处理%s报账单'%(wbs_id))
            file_in = self.dir_base + dir_in + wbs_id + '.jpg'
            file_out = self.dir_base + dir_in + wbs_id + '报账单.jpg'
            self._operateBaozhang(file_in,file_out)
            os.remove(file_in)
            print('     > 处理完成，已保存入：%s'%(file_out))
            print('     > 原文件已删除')
        print('-> 无线网报账单处理完成')

    def _operateBaozhang(self,file_in,file_out):
        '''处理报账单函数，将项目经理姓名添加到报账单内'''
        img_baozhang=Image.open(file_in)
        img_name = Image.open(self.dir_base + 'img_base\\name%02d.jpg'%(random.randint(1,5)))
        w_point = random.randint(500,1000)
        h_point = random.randint(950,1000)
        box = (w_point,h_point,w_point+img_name.size[0],h_point+img_name.size[1])
        img_baozhang.paste(img_name,box)
        img_baozhang.save(file_out, 'JPEG')
