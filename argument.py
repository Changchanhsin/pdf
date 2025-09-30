from sys import argv
import sys

helpCopyright=""
helpDescription=""
helpExample=""
helpSerial=[]
helpSerialDesc=[]
helpKey=[]
helpKeyName=[]
helpKeyNeedValue=[]
helpKeyDesc=[]
paraSerial=[]
paraKey=[]
paraValue=[]
paraHelp=[]
paraName=""

# utility
# Set text color : "\033["+x+";"+yy+";"+zz"+"m"+text+"\033[m"
#   x = 0 default, 1 Highlight, 4 underline, 5 blink, 7 reverse, 8 hide;
#   yy (x=0/1) = 30 black/darkgray, 31 red/light, 32 green/light, 33 brown/yellow, 34 blue/light, 35 purple/light, 36 cyan/light, 37 lightgray/white
#   zz = 40 black, 41 red, 42 Green, 43 Yellow, 44 Blue, 45 Purple, 46 Cyan, 47 White
R = "\033[31m"
G = "\033[32m"
B = "\033[1;34m"
C = "\033[36m"
P = "\033[35m"
Y = "\033[33m"
L = "\033[37m"
W = "\033[m"



# set help description

def progress_bar(pg_title, pg_now, pg_finish, passed="="):
  percentage = round(pg_now / pg_finish * 100)
  bar = passed * (percentage//2) + " " * (50-percentage//2)
  print(f"\r{pg_title}: [{bar}]{percentage}% {pg_now}/{pg_finish}", end="")
  if pg_now < pg_finish:
    sys.stdout.flush()
  else:
    print("")

def setCopyright(desc):
  global helpCopyright
  helpCopyright=desc

def addDescription(desc):
  global helpDescription
  if helpDescription=="":
    helpDescription=desc
  else:
    helpDescription=helpDescription+"\n"+desc

def addExample(desc):
  global helpExample
  if helpExample=="":
    helpExample=desc
  else:
    helpExample=helpExample+"\n"+desc

# set para

def addSerial(k, desc):
  global paraHelp
  global helpSerial
  global helpSerialDesc
  paraHelp.append(k + " = " + desc)
  helpSerial.append(k)
  helpSerialDesc.append(desc)

def addKey(k, desc, needvalue):
  global paraHelp
  global helpKey
  global helpKeyName
  global helpKeyDesc
  paraHelp.append("/"+ k[0:1] + " = " + desc)
  helpKey.append(k[0:1])
  helpKeyName.append(k)
  helpKeyDesc.append(desc)
  helpKeyNeedValue.append(needvalue)


# get para

def serial(i, default):
  if i in range(1,len(paraSerial)):
    return paraSerial[i]
  else:
    return default

def key(k, df):
  if k in paraKey:
    return paraValue[paraKey.index(k)]
  else:
    return df


def printHelp(num):
  if num.isdigit():
    if int(num)-1 in range(0,len(helpSerial)):
      print(R+"[Error "+num+"]"+W+" on " + Y + helpSerial[int(num)-1] + W)
  if num.isalpha():
    if num in helpKey:
      print(R+"[Error 201]"+W+" on para '" + num + "', " + helpKeyDesc[helpKey.index(num)])

  print(C + paraName + W + " by ZZX")
  if helpDescription!="":
    print(G + " Functional:" + W)
    print(helpDescription)
  print(G + " Usage:" + W)
  s = ""
  for i in helpKey:
    if helpKeyNeedValue[helpKey.index(i)]:
      s = s + " [/" + i + " " + helpKeyName[helpKey.index(i)] + "]"
    else:
      s = s + " [/" + i + "]"
  for i in helpSerial:
    s = s + " " + i
  print("  " + paraName + s)
  print(G + " where:" + W)
  for i in paraHelp:
    print("  " + i)
  if helpExample!="":
    print(G+" Example:"+W)
    print(helpExample.replace("%file%",paraName))
  print(G+" Copyright(C) " + helpCopyright + W)
  sys.exit()

def printall():
  print("helpSerial:")
  print(helpSerial)
  print("helpSerialDesc:")
  print(helpSerialDesc)
  print("helpKey:")
  print(helpKey)
  print("helpKeyDesc:")
  print(helpKeyDesc)
  print("paraSerial:")
  print(paraSerial)
  print("paraKey:")
  print(paraKey)
  print("paraValue:")
  print(paraValue)
  print("paraHelp:")
  print(paraHelp)
  print("paraName:")
  print(paraName)

# parse

def parse(a):
  global paraName
  global paraSerial
  global paraKey
  global paraValue
  global R
  global G
  global B
  global C
  global P
  global Y
  global L
  global W

  iskey=False
  paraError=False
  k=0
  s=0
  paraName=a[0]
  if paraName == paraName.upper():
    R = ""
    G = ""
    B = ""
    C = ""
    P = ""
    Y = ""
    L = ""
    W = ""
  for i in a:
    if ((i[0:1]=='/') and len(i)>=2):
      if iskey==False:
        paraKey.append(i[1:])
        iskey = True
        if i[1:] in helpKey:
          if helpKeyNeedValue[helpKey.index(i[1:])]==0:
            paraValue.append("True")
            iskey = False
      else:
        print("\033[31m[Error 101]\033[m "+i[1:]+" need value.")
        printHelp("")
    elif iskey==True:
      paraValue.append(i)
      iskey=False
      k=k+1
    else:
      paraSerial.append(i)
      s=s+1
  if iskey==True:
    if i[1:] in helpKey:
      if helpKeyNeedValue[helpKey.index(i[1:])]==0:
        paraValue.append("True")
        iskey = False
      else:
        print("\033[31m[Error 102]\033[m Para '"+Y+"/"+ i[1:]+W+"' need value.")
        printHelp("")
    else:
      if i[1:]!="?":
        print("\033[31m[Error 103]\033[m Unknown para '"+Y+"/" + i[1:] + W +"'")
      printHelp("")
  if key("h", "False")=="True":
    printHelp("")
    sys.exit()
  #if len(helpSerial) > len(paraSerial):
  #  print("\033[31m[Error 100]\033[m Need more para.")
  #  printHelp("")
  #  sys.exit()

'''

#example
import argument

# set paras
argument.addSerial("input_file_name", "input file name")
argument.addSerial("output_file_name", "output file name")
argument.addSerial("page", "output file name")
argument.addKey("input", "input file name",1)
argument.addKey("output", "output file name",1)
argument.addKey("help", "help",0)

# parse
argument.parse(argv)

# get paras
print(argument.serial(1,"f.pdf"))
print(argument.serial(2,"f2.pdf"))
print(int(argument.serial(3, "12")))

# if error, print help
try:
  ...
except IOError as e:
  argument.printHelp("1")

'''
