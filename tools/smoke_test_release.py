import ctypes
import struct
import subprocess
import time
import winreg
from pathlib import Path
from PIL import Image

kernel32 =ctypes.windll.kernel32
user32 =ctypes.windll.user32
PROCESS_ALL_ACCESS =0x1F0FFF

RELEASE_DIR =Path(r".\build\release")
EXE_PATH =RELEASE_DIR /"PvZ_Waste_RU.exe"
SHOTS_DIR =Path(r".\build\qa_screenshots")
SHOTS_DIR.mkdir(parents =True ,exist_ok =True )

def ensure_windowed_registry():
    for subkey in[
    r"Software\PopCap\PlantsVsZombies",
    r"Software\PopCap\Plants vs.Zombies",
    r"Software\SexyAppFramework\PlantsVsZombies",
    r"Software\PlantsVsZombies",
    ]:
        for root in(winreg.HKEY_CURRENT_USER ,winreg.HKEY_LOCAL_MACHINE ):
            try :
                key =winreg.CreateKey(root ,subkey )
                winreg.SetValueEx(key ,"ScreenMode",0 ,winreg.REG_DWORD ,0 )
                winreg.SetValueEx(key ,"Is3DAccelerated",0 ,winreg.REG_DWORD ,0 )
                winreg.CloseKey(key )
            except Exception :
                pass

def rpm(hproc ,addr ,size ):
    buf =ctypes.create_string_buffer(size )
    nread =ctypes.c_size_t(0 )
    ok =kernel32.ReadProcessMemory(hproc ,ctypes.c_void_p(addr ),buf ,size ,ctypes.byref(nread ))
    if not ok or nread.value !=size :
        return None
    return buf.raw

def read_u32(hproc ,addr ):
    raw =rpm(hproc ,addr ,4 )
    return struct.unpack("<I",raw )[0 ]if raw else 0

def capture_backbuffer(hproc ,out_path ):
    g_app =read_u32(hproc ,0x006A9EC0 )
    wm =read_u32(hproc ,g_app +0x320 )
    wm_img =read_u32(hproc ,wm +0x60 )
    surf_ptr =read_u32(hproc ,wm_img +0xA4 )
    if not surf_ptr :
        surf_ptr =read_u32(hproc ,wm_img +0x48 )
    best_im =None
    best_score =-1
    for _ in range(4 ):
        pix =rpm(hproc ,surf_ptr ,800 *600 *4 )
        if pix :
            im =Image.frombuffer("RGBA",(800 ,600 ),pix ,"raw","BGRA",0 ,1 ).convert("RGB")

            crop =im.crop((200 ,120 ,600 ,480 ))
            extrema =crop.getextrema()
            score =sum(hi -lo for lo ,hi in extrema )
            if score >=best_score :
                best_score =score
                best_im =im
        time.sleep(0.007 )
    if best_im :
        best_im.save(out_path )
        print(f"Captured {out_path.name } ({best_im.size }) from 0x{surf_ptr :08X}")
        return True
    return False

def keep_active_sleep(hwnd ,seconds ):
    steps =max(1 ,int(seconds /0.25 ))
    for _ in range(steps ):
        user32.PostMessageW(hwnd ,0x001C ,1 ,0 )
        user32.PostMessageW(hwnd ,0x0006 ,1 ,0 )
        user32.PostMessageW(hwnd ,0x0007 ,0 ,0 )
        time.sleep(0.25 )

def click(hwnd ,x ,y ):
    lparam =(int(y )<<16 )|(int(x )&0xFFFF )
    user32.PostMessageW(hwnd ,0x001C ,1 ,0 )
    user32.PostMessageW(hwnd ,0x0200 ,0 ,lparam )
    time.sleep(0.08 )
    user32.PostMessageW(hwnd ,0x0201 ,1 ,lparam )
    time.sleep(0.08 )
    user32.PostMessageW(hwnd ,0x0202 ,0 ,lparam )
    time.sleep(0.1 )

def hover(hwnd ,x ,y ):
    lparam =(int(y )<<16 )|(int(x )&0xFFFF )
    user32.PostMessageW(hwnd ,0x001C ,1 ,0 )
    user32.PostMessageW(hwnd ,0x0200 ,0 ,lparam )

def type_text(hwnd ,text ):
    for ch in text :
        user32.PostMessageW(hwnd ,0x0102 ,ord(ch ),0 )
        time.sleep(0.05 )

def main():
    subprocess.run(["taskkill","/F","/IM","PvZ_Waste_RU.exe"],capture_output =True )
    ensure_windowed_registry()

    proc =subprocess.Popen([str(EXE_PATH )],cwd =str(RELEASE_DIR ))
    print(f"Launched PvZ_Waste_RU.exe(PID={proc.pid })")
    time.sleep(2.5 )

    hproc =kernel32.OpenProcess(PROCESS_ALL_ACCESS ,False ,proc.pid )
    g_app =read_u32(hproc ,0x006A9EC0 )
    hwnd =read_u32(hproc ,g_app +0x350 )
    print(f"gLawnApp=0x{g_app :08X}, hwnd=0x{hwnd :08X}")

    keep_active_sleep(hwnd ,7.5 )
    capture_backbuffer(hproc ,SHOTS_DIR /"01_title_screen_ru.png")

    click(hwnd ,400 ,545 )
    keep_active_sleep(hwnd ,5.0 )
    capture_backbuffer(hproc ,SHOTS_DIR /"02_main_menu_ru.png")

    click(hwnd ,180 ,250 )
    keep_active_sleep(hwnd ,1.0 )
    capture_backbuffer(hproc ,SHOTS_DIR /"03_user_dialog_ru.png")

    click(hwnd ,490 ,500 )
    keep_active_sleep(hwnd ,0.8 )

    click(hwnd ,275 ,475 )
    keep_active_sleep(hwnd ,1.0 )
    capture_backbuffer(hproc ,SHOTS_DIR /"04_console_page1_ru.png")

    click(hwnd ,720 ,520 )
    keep_active_sleep(hwnd ,0.8 )
    capture_backbuffer(hproc ,SHOTS_DIR /"05_console_page2_ru.png")

    click(hwnd ,85 ,570 )
    keep_active_sleep(hwnd ,1.0 )

    click(hwnd ,600 ,500 )
    keep_active_sleep(hwnd ,1.0 )
    capture_backbuffer(hproc ,SHOTS_DIR /"06_options_dialog_ru.png")

    click(hwnd ,400 ,495 )
    keep_active_sleep(hwnd ,0.8 )

    click(hwnd ,672 ,525 )
    keep_active_sleep(hwnd ,1.8 )
    capture_backbuffer(hproc ,SHOTS_DIR /"07_help_screen_ru.png")

    assert proc.poll()is None ,f"Process exited unexpectedly with {proc.returncode }"
    kernel32.CloseHandle(hproc )
    proc.terminate()
    print("Full live smoke test completed cleanly(0 crashes)!")

if __name__ =="__main__":
    main()
