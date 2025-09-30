#!/usr/bin/env python

# Private including:
#  argument.py
# Install libs:
#  pip install pypdf2
#  pip install Pillow
# Make binary:
#  pyinstaller pdf.py -F --hidden-import=PIL
# by ZZX
#  2024-11-28 v0.1  First edition. Functions: add, overlap, pickup, remove, replace, rotate, watermark
#  2025-03-21 v0.2  Add Functions: extract, merge
#  2025-04-10 v0.21 Refactoring

import os
from sys import argv
from PyPDF2 import PdfReader, PdfWriter
from copy import copy
from PIL import Image
import argument

import inspect

def pagelist(s):
  p = []
  a = s.split(',')
  for i in a:
    j = i.split('-')
    if len(j) == 1:
      p.append(int(j[0]))
    if len(j) == 2:
      p.extend(range(int(j[0]),int(j[1])+1))
  return p

print(pagelist("5-10,20"))


argument.setCopyright("2024, Chanhsin")
argument.addDescription("  Add(insert) PDF pages from file2 into file1")
argument.addDescription("  Remove(delete) pages of file1")
argument.addDescription("  Pickup pages from file1 and save as file2")
argument.addDescription("  Replace pages of file1 by file2")
argument.addDescription("  Overlap pages of file1 by file2")
argument.addDescription("  Watermark pages of file1 by file2")
argument.addDescription("  Rotate pages of file1")
argument.addDescription("  Extract text and pictures from file1")
argument.addDescription("  Merge pictures from path file1")
argument.addSerial("method", "'add', 'remove', 'pickup', 'replace', 'overlap', 'watermark', 'rotate', 'extract' or 'merge'")
argument.addSerial("file1", "input file name 1")
argument.addSerial("file2", "input file name 2, useless on remove/rotate/extract/merge")
argument.addKey("page", "add/remove/pickup/replace/overlap/rotate start page of f1, default is -1(add) or 1(remove/replace/rotate)", 1)
argument.addKey("start_page", "add/replace/overlap start page of f2, default is 1", 1)
argument.addKey("end_page", "add/replace/overlap end page of f2 or pickup/remove/watermark/rotate end page of f1, default is -1", 1)
argument.addKey("rotate_degree", "rotate degree, must be a multiple of 90, default is 0",1)
argument.addKey("output_file", "output file name, default is input file name 1 + '.' + method + '.pdf'", 1)
#argument.addKey("debug", "show debug message", 0)
argument.addKey("help", "help", 0)
argument.addExample("  pdf.py add /p 2 file1.pdf /s 3 /e 4 file2.pdf /o output.pdf")

argument.parse(argv)

method = argument.serial(1,"window_mode")
file_name_1 = argument.serial(2,"f.pdf")
file_name_2 = argument.serial(3,"f2.pdf")
page_default = "-1"
if method=="add":
  page_default="-1"
else:
  page_default="1"

pg  = int(argument.key("p", page_default))
pgs = int(argument.key("s", "1"))
pge = int(argument.key("e", "-1"))
fno = argument.key("o", file_name_1+"."+method+".pdf")
try:
  rot = int(argument.key("r",0))
  if (rot % 90)>0:
    argument.printHelp("r")
except IOError as e:
  argument.printHelp("r")

#if argument.key("d", "False")=="True":
#  argument.printall()


def iterable(obj):
  #print(hasattr(obj, '__iter__'))
  #print(not isinstance(obj, (str, bytes)))
  print("string?",isinstance(obj,str))
  print("array?",isinstance(obj,tuple))
  print("list?",isinstance(obj,list))
  print("dict?",isinstance(obj,dict))
  print("set?",isinstance(obj,set))
  try:
    #iter(obj)
    if isinstance(obj,str):
      return 0
    if isinstance(obj,list):
      return 1
    if isinstance(obj,dict):
      return 2
    if isinstance(obj,tuple):
      return 3
    if isinstance(obj,set):
      return 4
    return 2
  except TypeError:
    return 0

def iterItems(obj,ind):
  if(len(ind)>=40):
    print(ind,obj)
    return
  key_max_len=0
  for i in obj:
    if len(i)> key_max_len:
      key_max_len=len(i)
  key_format = "{0:<" + str(key_max_len) + "}"
  for i in obj:
    t = iterable(obj[i])
    if (t==2):
      try:
        if(len(obj[i][0])==1):
          print(ind+key_format.format(i), "=",obj[i])
      except:
        if isinstance(obj[i], dict):
          print(ind+key_format.format(i),":")
          iterItems(obj[i],ind + "  ")
        else:
          print(ind+key_format.format(i), "=",obj[i])
    elif (t==1):
      print(ind+key_format.format(i),":")
      for j in obj[i]:
        print(j)
        print(ind+key_format.format(""),j)
    else:
      print(ind+key_format.format(i),"=", obj[i])

if method=="info":
  try:
    file1 = PdfReader(file_name_1)
  except IOError as e:
    argument.printHelp("2")

  print(" [Info]")
  print("/Encrypted =",file1.is_encrypted)
  print("/Header    =",file1.pdf_header)
  print("/Layout    =",file1.page_layout)
  print("/Mode      =",file1.page_mode)
  print("/Pages     =",len(file1.pages))
  print("/Strict    =",file1.strict)
  print("/Threads   =",file1.threads)

  print(" [Trailer]")
  iterItems(file1.trailer,"")
  #print(" [Metadata]")
  #iterItems(file1.metadata,"")
  #for i in file1.metadata:
  #  print('{0:<13}'.format(i),"=",file1.metadata[i])
  #print(f"/Rotate = {file1}")
  #print(" [Root]")
  #iterItems(file1.trailer["/Root"],"")

  print(" [Pages]")
  print('{0:<6}{1:<8}{2:<8}{3:<8}'.format('page','width','height','rotate'))
  oldx=0
  oldy=0
  oldr=0
  last=0
  for i in range(0,len(file1.pages)):
    x = file1.pages[i].mediabox[2]
    y = file1.pages[i].mediabox[3]
    r = file1.pages[i].get('/Rotate')
    if (r is None):
      r = 0
    if (x==oldx and y==oldy and r==oldr):
      if last==0:
        print(".. to ", end="")
      last = i
    else:
      if last!=0:
        print(i)
      last = 0
      oldx=x
      oldy=y
      oldr=r
      print('{0:<6}{1:<8.2f}{2:<8.2f}{3:<8}{4:<8}{5:<8}'.format(i+1, x, y, r, file1.pages[i].user_unit,0))
      #print(file1.pages[i].raw_get)
  if last!=0:
    print(i+1)
  #print(f"/Pagesize = {file1.pages[0].mediabox[2]} x {file1.pages[0].mediabox[3]}")
  #print(f"/artbox = {file1.pages[0].artbox}")
  #print(f"/bleedbox = {file1.pages[0].bleedbox}")
  #print(f"/cropbox = {file1.pages[0].cropbox}")
  #print(f"/trimbox = {file1.pages[0].trimbox}")
  #print(f"/Rotate = {file1.pages[0].get('/Rotate')}")
  #for i in file1.xmp_metadata:
  #  print(i)

  #print("[Dir]")
  #print(dir(file1))
  #for member in inspect.getmembers(file1):
  #  print(member)
  #print(dir(file1.pages[0]))
  exit()

if method!="merge":
  try:
    file1 = PdfReader(file_name_1)
  except IOError as e:
    argument.printHelp("2")

if method=="add" or method=="replace" or method=="overlap" or method=="watermark":
  try:
    file2 = PdfReader(file_name_2)
  except IOError as e:
    argument.printHelp("3")

file_writer = PdfWriter()

def r13n(page, max, overmin, overmax):
  if page > max:
    page = overmax
  if page <= 0:
    page = overmin
  return page

def order(min, max):
  if min> max:
    return max, min
  else:
    return min, max

def r13n_one(page, end, max):
  # 'page', 'end' start with '1'
  page = r13n(page, max, 1,   max)
  end  = r13n(end, max, max, max)
  page, end = order(page, end)
  return page, end

def r13n_two(page, start, end, max1, max2):
  # 'page', 'start', 'end' start with '1'
  page  = r13n(page,  max1, max1+1, max1+1)
  start = r13n(start, max2, 1,      max2  )
  end   = r13n(end,   max2, max2,   max2  )
  start, end = order(start, end)
  return page, start, end

def r13n_twoinone(page, start, end, max1, max2):
  # 'page', 'start', 'end' start with '1'
  if page > max1 or page <= 0:
    argument.printHelp("p")
  if start > max2 or start <= 0:
    argument.printHelp("s")
  if end > max2 or end <= 0:
    end = max2
  if start > end:
    argument.printHelp("e")
  if page+end-start > max1:
    end = max1-page+start
  return page, start, end

def pdf_add(f1, f2, pg, pgs, pge, pf1, pf2, pfa):
  page=1
  for page1 in range(pf1+1):
    if (page1 == pg-1):
      # insert start with pg, pg=2 -> page1[0], page2[0]...page2[n], page1[1] 
      for page2 in range(pgs-1, pge):
        file_writer.add_page(f2.pages[page2])
        argument.progress_bar(method, page, pfa)
        page = page+1
    if page1<pf1:
      file_writer.add_page(f1.pages[page1])
      argument.progress_bar(method, page, pfa)
      page = page+1

def pdf_remove(f1, pg, pge, pf1, pfa):
  page=1
  for page1 in range(pf1):
    if (page1 < pg-1) or (page1 >= pge):
      file_writer.add_page(f1.pages[page1])
      argument.progress_bar(method, page, pfa)
      page=page+1

def pdf_pickup(f1, pg, pge, pf1, pfa):
  page=1
  for page1 in range(pg-1,pge):
    file_writer.add_page(f1.pages[page1])
    argument.progress_bar(method, page, pfa)
    page=page+1

def pdf_replace(f1, f2, pg, pgs, pge, pf1, pf2, pfa):
  page=1
  page2 = pgs-1
  for page1 in range(pf1):
    argument.progress_bar(method, page1+1, pfa)
    if (page1 >= pg-1) and (page1 <= pg+pge-pgs-1):
      file_writer.add_page(f2.pages[page2])
      page2 = page2 + 1
    else:
      file_writer.add_page(f1.pages[page1])
    page = page+1

def pdf_overlap(f1, f2, pg, pgs, pge, pf1, pf2, pfa):
  page=1
  page2 = pgs-1
  for page1 in range(pf1):
    argument.progress_bar(method, page1+1, pfa)
    if (page1 >= pg-1) and (page1 <= pg+pge-pgs-1):
      source_page = f1.pages[page1]
      overlap_page = f2.pages[page2]
      source_page.merge_page(overlap_page)
      file_writer.add_page(source_page)
      page2 = page2 + 1
    else:
      file_writer.add_page(f1.pages[page1])
    page = page+1

def pdf_watermark(f1, f2, pg, pgs, pge, pf1, pf2, pfa):
  page = 1
  page2 = pgs-1
  for page1 in range(pf1):
    argument.progress_bar(method, page1+1, pfa)
    if (page1 >= pg-1):
      source_page = f1.pages[page1]
      mark_page = f2.pages[page2]
      new_page = copy(mark_page)
      new_page.merge_page(source_page)
      file_writer.add_page(new_page)
      page2 = page2+1
      if page2 > pge-1:
        page2 = pgs-1
    else:
      file_writer.add_page(f1.pages[page1])
    page = page+1

def pdf_rotate(f1, pg, pge, pf1, pfa):
  page = 1
  for page1 in range(pf1):
    argument.progress_bar(method, page, pfa)
    if (page1 >= pg-1) and (page1 < pge):
      file_writer.add_page(f1.pages[page1].rotate(rot))
    else:
      file_writer.add_page(f1.pages[page1])
    page=page+1

if method=="add":
  pf1 = len(file1.pages)
  pf2 = len(file2.pages)
  pg, pgs, pge = r13n_two(pg, pgs, pge, pf1, pf2)
  pfa = pf1 + pge - pgs + 1
  pdf_add(file1,file2,pg,pgs,pge, pf1,pf2,pfa)

elif method=="remove":
  pf1 = len(file1.pages)
  pg, pge = r13n_one(pg, pge, pf1)
  pfa = pf1 + pg - pge - 1
  pdf_remove(file1, pg, pge, pf1, pfa)

elif method=="pickup":
  pf1 = len(file1.pages)
  pg, pge = r13n_one(pg, pge, pf1)
  pfa = pge - pg + 1
  pdf_pickup(file1, pg, pge, pf1, pfa)

elif method=="replace":
  pf1 = len(file1.pages)
  pf2 = len(file2.pages)
  pg, pgs, pge = r13n_twoinone(pg, pgs, pge, pf1, pf2)
  pfa = pf1
  pdf_replace(file1, file2, pg, pgs, pge, pf1, pf2, pfa)

elif method=="overlap":
  pf1 = len(file1.pages)
  pf2 = len(file2.pages)
  pg, pgs, pge = r13n_twoinone(pg, pgs, pge, pf1, pf2)
  pfa = pf1
  pdf_overlap(file1, file2, pg, pgs, pge, pf1, pf2, pfa)

elif method=="watermark":
  pf1 = len(file1.pages)
  pf2 = len(file2.pages)
  pg, pg = r13n_one(pg, pg, pf1)
  pgs, pge = r13n_one(pgs, pge, pf2)
  pfa = pf1
  pdf_watermark(file1, file2, pg, pgs, pge, pf1, pf2, pfa)

elif method=="rotate":
  pf1 = len(file1.pages)
  pg, pge = r13n_one(pg, pge, pf1)
  pfa = pf1
  pdf_rotate(file1, pg, pge, pf1, pfa)

elif method=="extract":
  page=1
  pf1 = len(file1.pages)
  pg, pge = r13n_one(pg, pge, pf1)
  pfa = pge-pg+1
  pic=0
  pp=0
  text = ""
  if not os.path.exists(file_name_1+"_extracted"):
    os.makedirs(file_name_1+"_extracted")
  for page1 in range(pg-1, pge):
    argument.progress_bar(method, page, pfa)
    pag = file1.pages[page1]
    pp = 1
    try:
      for obj in pag.images:
        fimgnm = file_name_1 + "_extracted/" + "page" + str(page1+1).zfill(5) + "_"+ obj.name
        with open(f"{fimgnm}","wb") as f:
          f.write(obj.data)
        text += "\n[["+obj.name+"]]\n"
        pic=pic+1
        pp=pp+1
    except Exception as e:
      print("page",page,"error:",e)
    text += pag.extract_text()
    page = page+1
  slog = "Extract " + str(page) + " pages of file '"+file_name_1 + "', "
  if text != "":
    with open(f"{file_name_1}.txt","wb") as f:
      f.write(text.encode())
    slog = slog + "text into file '"+file_name_1+".txt', "
  else:
    slog = slog + "no text extracted, "
  if pic!= 0:
    slog = slog + str(pic) + " pictures into folder '"+ file_name_1 + "_extracted/' "
  else:
    slog = slog + "no picture extracted, "
  slog = slog + "success."
  print(slog)

elif method=="merge":
  if not os.path.exists(file_name_1):
    argument.printHelp("2")
  fs = []
  for pth in os.listdir(file_name_1):
    if os.path.isfile(os.path.join(file_name_1,pth)):
      fs.append(pth)
  fs.sort()
  page=0
  while page<len(fs):
    argument.progress_bar(method, page+1, len(fs))
    im = Image.open(os.path.join(file_name_1,fs[page]))
    im.save("__.pdf", "PDF", resolution=100.0, subsampling=0)
    im.close()
    file_writer.append("__.pdf")
    os.remove("__.pdf")
    page=page+1

else:
  argument.printHelp("1")


# 写文件，加上固定后缀
if method != "extract":
  with open(fno,'wb') as out:
    file_writer.write(out)

if method=="add":
  print("Add '" + file_name_2 + "' to '" + file_name_1 + "' from page " + str(pgs) + " to " + str(pge) + " after page " + str(pg) + ", and save to file '" + fno + "' success.")
elif method=="remove":
  print("Remove '" + file_name_1 + "' page " + str(pg) + " to page " + str(pge) + ", and save to file '" + fno + "' success.")
elif method=="pickup":
  print("Pickup '" + file_name_1 + "' page " + str(pg) + " to page " + str(pge) + ", and save to file '" + fno + "' success.")
elif method=="replace":
  print("Replace '" + file_name_1 + "' page " + str(pg) +" to page " + str(pge-pgs+pg) + " from '" + file_name_2 + "' page " + str(pgs) + " to " + str(pge) + ", and save to file '" + fno + "' success.")
elif method=="overlap":
  print("Overlap '" + file_name_1 + "' page " + str(pg) +" to page " + str(pge-pgs+pg) + " from '" + file_name_2 + "' page " + str(pgs) + " to " + str(pge) + ", and save to file '" + fno + "' success.")
elif method=="watermark":
  print("Watermark '" + file_name_1 + "' page " + str(pg) +" to page " + str(pge-pgs+pg) + " by '" + file_name_2 + "' page " + str(pgs) + " to " + str(pge) + ", and save to file '" + fno + "' success.")
elif method=="rotate":
  print("Rotate page " + str(pg) + " to page " + str(pge) + " of file '" + file_name_1 + "' for " + str(rot) + " degree(s), and save to file '" + fno + "' success.")
elif method=="merge":
  print("Merge pictures in '" + file_name_1 + "' to file '" + fno + "' success.")
