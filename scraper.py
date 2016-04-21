import webbrowser
from lxml import html
import requests
import urllib.request
import os
import sys

def getfrompage(page):
    if page.status_code == requests.codes.ok:
        if not os.path.isdir(os.path.expanduser('~\\Desktop\\' + name)):
            os.mkdir(os.path.expanduser('~\\Desktop\\' + name))
        newdir = os.path.expanduser('~\\Desktop\\' + name + '\\')
        tree = html.fromstring(page.content)
        pictures = tree.xpath('//a/@href')
        finalpics = []
        for picture in pictures:
            if name + '.deviantart.com/art' in picture and picture not in finalpics:
                newpage = requests.get(picture)
                if newpage.status_code == requests.codes.ok:
                    tree = html.fromstring(newpage.content)
                    imgurl = tree.xpath('//div[@class="dev-view-deviation"]/img/@src')
                    filename = ''
                    if len(imgurl) == 2:
                        filename = imgurl[1].split('/')[-1]
                        # filename = 'E:Users\\Sam\\Desktop\\' + filename
                    elif len(imgurl) == 1:
                        filename = imgurl[0].split('/')[-1]
                    if filename != '':
                        file = urllib.request.urlopen(imgurl[1])
                        imgname = filename.split('_by_')[0]
                        filending = filename.split('.')[-1]
                        try:
                            out = open(newdir + imgname + '.' + filending, "wb")
                            out.write(file.read())
                            out.close()
                        except OSError:
                            return
                finalpics.append(picture)
        print(finalpics)
        print(len(finalpics))
    else:
        print('Bad Url')
    return

name = sys.argv[1]
offset = ''
curpage = requests.get('http://' + name + '.deviantart.com/gallery/' + offset)
counter = 24
while curpage.status_code == requests.codes.ok:
    getfrompage(curpage)
    offset = '?offset=' + str(counter)
    counter += 24
    curpage = requests.get('http://' + name + '.deviantart.com/gallery/' + offset)
