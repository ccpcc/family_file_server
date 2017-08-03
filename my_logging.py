import time
import json
import os

def write_file(name,content):
    if os.path.exists(name):
        fo=open(name,'a')
        fo.write(content)
        fo.close()
    else:
        fo=open(name,'w')
        fo.write(content)
        fo.close()

def add_time(content,detail_t):
    content["time"]=detail_t
    content=json.dumps(content)+'\n'
    return content

def create(content,day_t,ass_path):
    i=day_t.split('-')
    year=i[0]
    month=i[1]
    day=i[2]
    path=ass_path+'/'+year+'/'+month
    if not os.path.exists(path):
        os.makedirs(path)
    write_file(path+'/'+day_t,content)
    
    
def write_log(content,ass_path):#传入一个字典 不带'/'的path
    detail_t=time.strftime('%Y-%m-%d-[%H:%M:%S]',time.localtime(time.time()))
    day_t=time.strftime('%Y-%m-%d',time.localtime(time.time()))    
    content=add_time(content,detail_t)#内容字符串
    create(content,day_t,ass_path)
    