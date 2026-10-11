import os
import re
import shutil
import struct
import sys
from PIL import ImageFont

sys.stdout.reconfigure(encoding ="utf-8")

RUSSIAN_TTF_SRC =r"build/Russian_augmented.ttf"
BASS2_ORIG ="build/extracted_evb/bass2.dll"
BASS3_TARGET ="build/extracted_evb/bass3.dll"
DATA_DIR ="build/unpacked_pak/data"

FONT_ID_PIXEL_SIZES ={
1 :13 ,
2 :17 ,
3 :32 ,
4 :32 ,
5 :16 ,
6 :16 ,
7 :12 ,
8 :15 ,
9 :18 ,
10 :18 ,
11 :18 ,
12 :18 ,
13 :24 ,
14 :36 ,
15 :36 ,
16 :16 ,
17 :20 ,
18 :28 ,
19 :12 ,
20 :12 ,
}

def inspect_and_patch_bass2():
    backup_path ="build/extracted_evb/bass2.dll.bak"
    if not os.path.exists(backup_path ):
        shutil.copy2(BASS2_ORIG ,backup_path )

    with open(backup_path ,"rb")as f :
        b2 =bytearray(f.read())

    cp_offsets =[0x2150 ,0x218B ,0x22C5 ,0x2300 ]
    for off in cp_offsets :
        cur =bytes(b2[off :off +5 ])
        assert cur ==b"\x68\xa8\x03\x00\x00",f"Unexpected bytes at 0x{off :x}: {cur.hex()}"
        b2[off :off +5 ]=b"\x68\xe3\x04\x00\x00"
        print(f"  Patched CodePage 936 -> 1251 at 0x{off :x}")

    patched_markers =0
    for pos in range(0x2100 ,0x2380 ):
        if b2[pos :pos +7 ]==b"\x6a\x00\x68\xff\x00\x00\x00":
            b2[pos +3 ]=0x9F
            patched_markers +=1
            print(f"  Patched CharWidthKern(0xFF, 0) -> CharWidthKern(0x9F, 0) at 0x{pos :x}")
    assert patched_markers ==2 ,f"Expected 2 Font ID marker pushes, found {patched_markers }"

    with open(BASS2_ORIG ,"wb")as f :
        f.write(b2 )
    print(f"Successfully wrote patched {BASS2_ORIG } ({len(b2 ):,} bytes)")

def build_augmented_font():
    try :
        from fontTools.ttLib import TTFont
        tt =TTFont(RUSSIAN_TTF_SRC )
        cmap =tt.getBestCmap()
        print(f"Loaded Russian.ttf via fontTools: {len(cmap )} mapped codepoints")
        fallbacks ={
        0x00AB :ord('"'),
        0x00BB :ord('"'),
        0x2013 :ord('-'),
        0x2014 :ord('-'),
        0x2018 :ord("'"),
        0x2019 :ord("'"),
        0x201C :ord('"'),
        0x201D :ord('"'),
        0x2116 :ord('N'),
        0x0401 :0x0415 ,
        0x0451 :0x0435 ,
        }
        added =[]
        for table in tt["cmap"].tables :
            if table.isUnicode():
                for target_cp ,fb_cp in fallbacks.items():
                    if target_cp not in table.cmap and fb_cp in table.cmap :
                        table.cmap[target_cp ]=table.cmap[fb_cp ]
                        added.append(chr(target_cp ))
        print(f"Added fallback cmap entries in Russian.ttf for: {sorted(set(added ))}")
        out_ttf ="build/Russian_augmented.ttf"
        tt.save(out_ttf )
    except ImportError :
        print("fontTools not installed; copying Russian.ttf directly...")
        out_ttf ="build/Russian_augmented.ttf"
        shutil.copy2(RUSSIAN_TTF_SRC ,out_ttf )

    backup_b3 ="build/extracted_evb/bass3.dll.bak"
    if not os.path.exists(backup_b3 ):
        shutil.copy2(BASS3_TARGET ,backup_b3 )

    shutil.copy2(out_ttf ,BASS3_TARGET )
    print(f"Copied {out_ttf } -> {BASS3_TARGET } ({os.path.getsize(BASS3_TARGET ):,} bytes)")
    return out_ttf

def update_font_metric_files(ttf_path ):
    backup_dir ="build/data_txt_backup"
    os.makedirs(backup_dir ,exist_ok =True )

    txt_files =sorted(f for f in os.listdir(DATA_DIR )if f.endswith(".txt"))
    print(f"\nUpdating {len(txt_files )} font metric files in {DATA_DIR }:")

    for fname in txt_files :
        src_path =os.path.join(DATA_DIR ,fname )
        bak_path =os.path.join(backup_dir ,fname )
        if not os.path.exists(bak_path ):
            shutil.copy2(src_path ,bak_path )

        with open(bak_path ,"rb")as f :
            raw =f.read()

        text_latin1 =raw.decode("latin1")

        m_wlist =re.search(r"Define\s+WidthList\s*\((.*?)\)\s*;",text_latin1 ,re.DOTALL )
        assert m_wlist is not None ,f"Could not find WidthList in {fname }"
        nums =re.findall(r"-?\d+",m_wlist.group(1 ))
        font_id =int(nums[-1 ])
        px_size =FONT_ID_PIXEL_SIZES.get(font_id ,18 )

        pil_font =ImageFont.truetype(ttf_path ,px_size )

        extra_chars =[]
        extra_widths =[]

        cp1251_bytes =[0x85 ,0x96 ,0x97 ,0xA8 ,0xAB ,0xB8 ,0xB9 ,0xBB ]+list(range(0xC0 ,0x100 ))
        for b_val in cp1251_bytes :
            ch =bytes([b_val ]).decode("cp1251")
            w =int(round(pil_font.getlength(ch )))
            if w <=0 :
                w =max(4 ,px_size //2 )
            extra_chars.append(f"'{chr(b_val )}'")
            extra_widths.append(str(w ))

        extra_chars.append("'\x9f'")
        extra_widths.append(str(font_id ))

        chars_tuple ="("+", ".join(extra_chars )+")"
        widths_tuple ="("+", ".join(extra_widths )+")"

        def repl_layer_widths(m ):
            full_line =m.group(0 )
            layer_name =m.group(1 )
            return f"{full_line }\nLayerSetCharWidths        {layer_name } {chars_tuple } {widths_tuple };"

        final_text ,n_layers =re.subn(
        r"LayerSetCharWidths\s+(\S+)\s+CharList\s+WidthList\s*;",
        repl_layer_widths ,
        text_latin1
        )
        assert n_layers >=1 ,f"Could not find LayerSetCharWidths <Layer> CharList WidthList; in {fname }"

        with open(src_path ,"wb")as f :
            f.write(final_text.encode("latin1"))
        print(f"  Updated {fname :38s} (Font ID={font_id :2d}, px={px_size :2d}, layers={n_layers }, +{len(extra_chars )} CP1251 widths)")

if __name__ =="__main__":
    inspect_and_patch_bass2()
    ttf_path =build_augmented_font()
    update_font_metric_files(ttf_path )
