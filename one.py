# -*- coding: utf-8 -*-
import re
import os
import urllib2
from urllib import urlretrieve
import bs4
from bs4 import BeautifulSoup

start=1  # 起始期刊号
stop=10  # 终止期刊号

#  将字符串中的</br>和<p></p>去掉
#  并将相关的特殊字符转换为tex中能够被识别的字符
#  并将各种未能正确处理掉的html标签去掉
#  ‘一个’的官方页面上有些乱七八糟的代码
def text_with_newlines(elem):
    text = ''
    for e in elem.recursiveChildGenerator():
        if isinstance(e, basestring):
            text += e.strip()
        elif e.name == 'br':
            text += '\n\n'
    text = text.replace('\\','\\textbackslash ')
    text = text.replace('%','\%')
    text = text.replace('_','\_')
    text = text.replace('#','\#')
    text = text.replace('&','\&')
    text = text.replace('<div>','')
    text = text.replace('</div>','')
    text = text.replace('</p>','')
    text = text.replace('<p class="p0" style="margin-bottom:0pt; margin-top:0pt; ">','')
    text = text.replace('</span>','')
    text = text.replace('<span style=" font-size:10.5000pt; ;">','')
    text = text.replace('<span style="font-size: 10.5pt;">','')
	#  这儿找不到更好的方式把这些标签去除掉，只能这样一个一个的替换掉  -_-|||
    return text

def main():
	#  定义图片文件夹
	imagepath=os.getcwd()+'\images'
	if os.path.exists(imagepath) is False:
		os.mkdir(imagepath)

	# 定义保存的tex文件
	filepath="D:\\project\\python\\test\\"+str(start)+r"_"+str(stop-1)+r".tex"
	f=open(filepath,'w+')
	# 在这里可以对tex文件写入一些格式控制代码
	f.write(r'\begin{document}'+'\n')

	for titlenumb in range(start,stop):
		contenturl=r"http://wufazhuce.com/one/vol."+str(titlenumb)
		req=urllib2.Request(contenturl)
		response=urllib2.urlopen(req).read()
		contentsoup=BeautifulSoup(''.join(response))

		vol = contentsoup.find("div",{"class" : "one-titulo"}).string.strip()
		print vol
		# 写入期刊号到tex文档，并添加链接
		f.write(r'\section{\href{http://wufazhuce.com/one/vol.'+str(titlenumb)\
			+'}{'+vol+r'}}'+'\n')

		# 获得发布日期
		date = contentsoup.find("div",{"class" : "one-pubdate"})
		day, month = date.findAll('p')
		day = text_with_newlines(day)
		month = text_with_newlines(month)


		############# 一个：图片

		# 获得图片的标题和作者信息
		imgauthor = text_with_newlines(contentsoup.find("div",{"class" : "one-imagen-leyenda"}))

		# 获得每日图片链接并下载
		imgsoup=contentsoup.find("div", {"class" : "one-imagen"})
		imageurl= imgsoup.find('img')['src']
		temp=imagepath+'\%s.jpg' %titlenumb
		urlretrieve(imageurl,temp)  # 下载图片

		#  得到图片说明
		imagedescript = contentsoup.find("div",{"class":"one-cita"}).string.strip()
		# \oneimage{img}{day}{month}{title and author}{description}
		f.write(r'\oneimage{'+str(titlenumb)+r'.jpg}{'+ day.encode('utf-8') +'}{' + month.encode('utf-8') \
			+ '}{' + imgauthor.encode('utf-8') + '}{' + imagedescript.encode('utf-8') + '}'+'\n')


		################# 一个：文章

		# 得到“一个：文章”标题写入tex文档并添加链接
		contenttitle=contentsoup.find("h2", {"class" : "articulo-titulo"}).string.strip()
		f.write(r'\subsection{\href{http://wufazhuce.com/one/vol.'+str(titlenumb)\
			+r'\#articulo}{'+contenttitle.encode('utf-8')+'}}'+'\n')
		print contenttitle
		# 得到“一个：文章”作者写入tex文档并添加链接
		contentauthor=contentsoup.find("p", {"class" : "articulo-autor"}).string.strip()
		f.write(r'\centerline{\heiti '+contentauthor.encode('utf-8')+'}'+'\n')
		# 得到文章的全部(包含若干tag)
		textsoup=contentsoup.find("div", {"class" : "articulo-contenido"})
		if len(textsoup.findAll('p')):
			for each_p in textsoup.findAll('p'):
				f.write(text_with_newlines(each_p).encode('utf-8'))
				f.write('\n\n')
		elif len(textsoup.findAll('div')) :
			for each_p in textsoup.findAll('div'):
				f.write(text_with_newlines(each_p).encode('utf-8'))
				f.write('\n\n')
		else:
			f.write(text_with_newlines(textsoup).encode('utf-8'))
			f.write('\n\n')


		################## 一个：问题
		asktitle=contentsoup.find("div", {"class" : "one-cuestion"})
		title_asker=asktitle.findAll('h4')
		title=title_asker[0].string.strip()
		answerer=title_asker[1].string.strip()
		print title # 得到“一个：问题”标题title 和回答者answerer
		f.write(r'\subsection{\href{http://wufazhuce.com/one/vol.'+str(titlenumb)\
			+r'\#cuestion}{'+title.encode('utf-8')+'}}'+'\n')

		#  得到“一个：问题”的问题内容
		askdetail=contentsoup.findAll("div",{"class" : "cuestion-contenido"})
		question = text_with_newlines(askdetail[0])
		f.write(question.encode('utf-8')+r'\\[.5ex]'+'\n')

		f.write(r'\textbf{'+answerer.encode('utf-8')+'}'+'\n\n')

		if len(askdetail[1].findAll('p')):
			for each_soup in askdetail[1].findAll('p'):
				f.write(text_with_newlines(each_soup).encode('utf-8')+'\n\n')
		else:
			f.write(text_with_newlines(askdetail[1]).encode('utf-8')+'\n\n')
		f.write(r'\newpage'+'\n')
	f.write(r'\end{document}')
	f.close()

#--------------------------------#
if __name__=="__main__":
    main()
