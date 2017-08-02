import web
import random
import os
import json

urls=("/ok","Index",
"/upload/(.*)","Upload",
"/download/(.*)","Down",
"/new/(.*)","New",
"/","Login",
"/app/","App",
"/icons/(.*)","Ico")
#render=web.template.render("htmls")
def find_rootpath():
    
    path_list = os.listdir('/media/pi')
    for path in path_list:
        real_path='/media/pi/'+path
        if os.path.isdir(real_path):
            file_list=os.listdir(real_path)
            if ("main_dir.txt" in file_list) and ('static' in file_list):
                return real_path+"/"+"static"
    

app=web.application(urls,globals())
root=find_rootpath()
print(root)
    
def jiami(a):
    re=[]
    l1=["000","001","010","011","100","101","110","111"]
    for x in range(0,len(a),3):
        ob=a[x:x+3]
        if ob in l1:
            ran=random.randint(0,99)
            re.append(str(((l1.index(ob)+1)*100)+ran))
        else:
            ran=random.randint(0,1)
            if ran==0:
                re.append(ob.replace(" ","s"))
            else:
                re.append(ob.replace(" ","r"))
    return("".join(re))

def jiemi(mi):
    re=[]
    l1=["000","001","010","011","100","101","110","111"]
    for x in range(0,len(mi),3):
        ob=mi[x:x+3]
        if "s" in ob:
            re.append(ob.replace("s"," "))
        elif "r" in ob:
            re.append(ob.replace("r"," "))
        else:
            if len(ob)==3:
                re.append(l1[int(ob[0])-1])
            else:
                re.append(ob)
    return("".join(re))
    
def encp(text):
    text=text.encode("utf-8")
    result=[]
    for letter in text:
        result.append(str(bin(letter)).replace("0b",""))
    result=" ".join(result)
    return jiami(result)
    
def decp(text):
    text=jiemi(text).split(" ")
    result=b''
    for letter in text:
        result=result+bytes((int(letter,2),))
    return result.decode("utf-8")
    

def check_rights(cookie,path):#计算机路径
    try:
        if path==root:
            return True
        root_path=root+"/"
        cookie=decp(cookie).split(" ")
        name=cookie[0]
        ckpath=path.replace(root_path,"",1)
        ckpath=ckpath.split("/")[0]
        if name=="root" or ckpath==name or ckpath=="" or ckpath=="share":
            return True
        else:
            return False
    except:
        return False
        
def check_cookie(cookie):
    try:
        cookie=decp(cookie).split(" ")
        name=cookie[0]
        key=cookie[1]
        c=load_conf()
        if name in c:
            if key == c[name]:
                return True
            else:
                return False
        else:
            return False
    except:
        return False

def load_conf():
    fo=open("SAM.json","r")
    c=fo.read()
    fo.close()
    c=json.loads(c)
    return c
 
def have_chinese(text):
    if len(text.encode("utf-8"))==len(text):
        return False
    else:
        return True 

def ch_to_bytes(ch):
    ch=ch.encode("utf-8")
    result=[]
    for letter in ch:
        letter=str(hex(letter)).replace("0x","")
        result.append(letter)
    result="-".join(result)
    result="<"+result+">"
    return result

def bytes_to_ch(bs):
    bs=bs[1:len(bs)-1].split("-")
    result=[]
    for number in bs:
        result.append(int(number,16))
    result=bytes(result).decode("utf-8")
    return result

def url_to_path(url):#输入 download/ 后的内容
    if len(url)==0:
        return root
    url_list=url[0:len(url)-1].split("/")
    path=root+'/'
    for word in url_list:
        if word[0]=="<" and word[-1]==">":
            path=path+bytes_to_ch(word)+"/"
        else:
            path=path+word+"/"
    print(path.strip("/"))
    return '/'+path.strip("/")#返还电脑路径

def path_to_url(path):#输入电脑路径
    root_path=root+'/'
    url="http://192.168.1.100:8080/download/"
    path='/'+path.strip("/")
    path=path.replace(root_path,"")
    path_list=path.split("/")
    for word in path_list:
        if have_chinese(word):
            url=url+ch_to_bytes(word)+"/"
        else:
            url=url+word+"/"
    return url #返还真实网址
    
class Index:
    def POST(self):
        i=web.input()
        name=i.get("name")
        key=i.get("key")
        c=load_conf()
        web.header('Content-Type','text/html;charset=UTF-8')
        if name in c:
            if key==c[name]:
                web.setcookie("check",encp(name+" "+key))
                fo=open("htmls/Index.html","rb").read()
                return fo
            else:
                return "密码错误"
        else:
            return "账号不存在"    
                    
class Upload:
    def POST(self,name):
        rp=url_to_path(name)
        i=web.input(file={})
        file_name=i.file.filename
        file=i.file.file.read()
        fo=open(rp+"/"+file_name,"wb")
        fo.write(file)
        fo.close()
        fo=open("htmls/success.html","rb")
        htm=fo.read()
        fo.close()
        web.header('Content-Type','text/html;charset=UTF-8')
        return htm
        
    def GET(self,name):
        cookie=web.cookies().get("check")
        if check_cookie(cookie):#通过身份验证
            htm="""
            <Doctype html>
            <html>
            <head>
             <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
            <title>文件共享</title>
            </head>
            <body>
            <p>文件上传</p>
            <form action="/upload/%s" method="POST" enctype="multipart/form-data">
                <input type="file" name="file">
                <input type="submit" value="POST">
            </form><br>
            </body>
            </html>
            """%name
            web.header('Content-Type','text/html;charset=UTF-8')
            return htm.encode("utf-8")
        else:
            web.header('Content-Type','text/html;charset=UTF-8')
            fo=open("htmls/fail.html","rb")
            htm=fo.read()
            fo.close()
            return htm
        
class Down:
    def GET(self,name):
        cookie=web.cookies().get("check")
        checkrp=url_to_path(name)#电脑路径
        rp=checkrp+"/"
        if check_cookie(cookie) and check_rights(cookie,checkrp):#通过身份验证
            htm="""
            <!Doctype html>
            <html>
            <head>
            <title>文件</title>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
            </head>
            <body>
            <table width="98%" border="0" align="center" style="word-break:break-all; word-wrap:break-all;">
                <tr>
                <td colspan="3" ><h1>文件:</h1></td>
                </tr>
                [file]
                <tr>
                <td colspan="3" ><h1>文件夹:</h1></td>
                </tr>
                [path]
                <tr>
                <td colspan="3" ><h1>操作</h1></td>
                </tr>
                [link]
            </table></body></html>
            """

            if os.path.isfile(checkrp):#是文件
                #添加header
                if "." in checkrp:
                    extra_name=checkrp.split(".")[-1]
                    if extra_name=="jpe" or extra_name=="jpeg" or extra_name=="jpg":
                        web.header('Content-Type',"image/jpeg")
                        #http://tool.oschina.net/commons
                    elif extra_name=="gif":
                        web.header('Content-Type',"image/gif")
                    elif extra_name=="png":
                        web.header('Content-Type',"image/png")
                    elif extra_name=="tif" or extra_name=="tiff":
                        web.header('Content-Type',"image/tif")
                    else:#其他扩展名
                        web.header('Content-Type',"application/octet-stream")
                else:#无扩展名
                    web.header('Content-Type',"	application/octet-stream")
                return open(checkrp,"rb").read()
            else:#是路径
                file_list = os.listdir(checkrp) #列出文件夹下所有的目录与文件
                for i in range(0,len(file_list)):#遍历该路径
                    path = rp+file_list[i]
                    real_url=path_to_url(path)#path电脑子路径 file_list文件名
                    if os.path.isfile(path):#是文件
                        file_size=os.path.getsize(path)
                        if "." in path:
                            checkp=path.split(".")[-1]
                            if checkp=="jpe" or checkp=="jpeg" or checkp=="jpg" or checkp=="gif" or checkp=="png" or checkp=="tif" or checkp=="tiff" :
                                htm=htm.replace("[file]",'<tr style="background-color:#FFFFCC"><td style="height:200px;width:260px"><a href="%s"><img src="%s" alt="%s" width="250" height="150"/></a></td>[file]'%(real_url,real_url,file_list[i]))
                                htm=htm.replace("[file]",'<td style="text-align:center;"><h2>%s</h2></td><td width="100px"><a href="%s"><img src="http://192.168.1.100:8080/icons/download.jpg" alt="downlaod" width="100" height="100"></a></td></tr>[file]'%(file_list[i],real_url))
                            else:#非图片
                                htm=htm.replace("[file]",'<tr style="background-color:#FFFFCC"><td style="height:200px;width:260px"><img src="http://192.168.1.100:8080/icons/erro.jpg" alt="%s" width="250" height="150"/></td>[file]'%(file_list[i]))
                                htm=htm.replace("[file]",'<td style="text-align:center;"><h2>%s</h2></td><td width="100px"><a href="%s"><img src="http://192.168.1.100:8080/icons/download.jpg" alt="downlaod" width="100" height="100"></a></td></tr>[file]'%(file_list[i],real_url))
                        else:#无扩展名
                            htm=htm.replace("[file]",'<tr style="background-color:#FFFFCC"><td style="height:200px;width:260px"><img src="http://192.168.1.100:8080/icons/erro.jpg" alt="%s" width="250" height="150"/></td>[file]'%(file_list[i]))
                            htm=htm.replace("[file]",'<td style="text-align:center;"><h2>%s</h2></td><td width="100px"><a href="%s"><img src="http://192.168.1.100:8080/icons/download.jpg" alt="downlaod" width="100" height="100"></a></td></tr>[file]'%(file_list[i],real_url))
                    else:#是文件夹
                        htm=htm.replace("[path]",'<tr style="background-color:#FFFFCC"><td style="height:200px;width:260px"><img src="http://192.168.1.100:8080/icons/dir.jpg" alt="%s" width="250" height="150"/></td>[path]'%(file_list[i]))
                        htm=htm.replace("[path]",'<td style="text-align:center;"><h2>%s</h2></td><td width="100px"><a href="%s"><img src="http://192.168.1.100:8080/icons/open.jpg" alt="open" width="100" height="100"></a></td></tr>[path]'%(file_list[i],real_url))
                htm=htm.replace("[link]",'<tr><td><img src="http://192.168.1.100:8080/icons/upload.jpg" alt="upload" width="200" height="150"/></td><td colspan="2"><a href="http://192.168.1.100:8080/upload/%s"><h2>在此上传</h2></a></td></tr>[link]'%name)
                htm=htm.replace("[link]",'<tr><td><img src="http://192.168.1.100:8080/icons/new.jpg" alt="new" width="200" height="150"/></td><td colspan="2"><a href="http://192.168.1.100:8080/new/%s"><h2>新建文件夹</h2></a></td></tr>'%name)
                htm=htm.replace("[file]","")
                htm=(htm.replace("[path]","")).encode("utf-8")
                web.header('Content-Type','text/html;charset=UTF-8')
                return htm
    
        else:#身份不对
            web.header('Content-Type','text/html;charset=UTF-8')
            fo=open("htmls/fail.html","rb")
            htm=fo.read()
            fo.close()
            return htm

class New:
    def GET(self,name):
        cookie=web.cookies().get("check")
        if check_cookie(cookie):#通过身份验证
            htm="""
            <Doctype html>
            <html>
            <head>
             <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
            <title>文件共享</title>
            </head>
            <body>
            <p>新建文件夹</p>
            <form action="/newfile/%s" method="POST" enctype="multipart/form-data">
            文件夹名称：<input type="text" name="name"><br>
            <input type="submit" value="新建"><br>
            </form>
            </body>
            </html>
            """%name
            web.header('Content-Type','text/html;charset=UTF-8')
            return htm.encode("utf-8")
        else:
            web.header('Content-Type','text/html;charset=UTF-8')
            fo=open("htmls/fail.html","rb")
            htm=fo.read()
            fo.close()
            return htm
            
    def POST(self,name):
        web.header('Content-Type','text/html;charset=UTF-8')
        path=url_to_path(name)
        i=web.input()
        file_name=i.get("name")
        path=path+"/"+file_name
        if os.path.exists(path):
            return "创建失败，路径已存在！"
        else:
            os.mkdir(path)
            return "创建成功！"
            
class Login:
    def GET(self):
        web.header('Content-Type','text/html;charset=UTF-8')
        fo=open("htmls/log.html","rb").read()
        return fo
        
class App:
    def GET(self):
        cookie=web.cookies().get("check")
        if check_cookie(cookie):#通过身份验证
            web.header('Content-Type','text/html;charset=UTF-8')
            fo=open("htmls/app.html","rb")
            htm=fo.read()
            fo.close()
            return htm
        else:#身份不对
            web.header('Content-Type','text/html;charset=UTF-8')
            fo=open("htmls/fail.html","rb")
            htm=fo.read()
            fo.close()
            return htm
 
class Ico:
    def GET(self,name):
        web.header('Content-Type',"	image/jpeg")
        fo=open('icons/'+name,"rb")
        c=fo.read()
        fo.close()
        return c
        
if __name__ == "__main__":
    app.run()
