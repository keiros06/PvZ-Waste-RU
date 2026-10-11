import json
import struct
import re
from pathlib import Path

EVB_DIR =Path(r".\build\extracted_evb")
UNPACK_DIR =Path(r".\build\unpacked_pak")
MANIFEST_PATH =Path(r".\build\pak_manifest.json")

def inspect_bass2_and_bass3():
    b2 =(EVB_DIR /"bass2.dll").read_bytes()

    strs =[s.decode('latin1')for s in re.findall(b"[\x20-\x7e]{5,100}",b2 )]
    interesting =[s for s in strs if any(k in s.lower()for k in["bass","font","ttf","pak","lawn","tod","draw","text","char","utf","gbk","wstring",".dll","hook","freetype"])]
    print(f"bass2.dll interesting ASCII strings({len(interesting )}):")
    for s in interesting[:60 ]:
        print("  ",s )

    u16 =[s.decode('utf-16le',errors ='ignore')for s in re.findall(b"(?:[\x20-\x7e]\x00){4,80}",b2 )]
    print(f"bass2.dll UTF-16 strings({len(u16 )}):")
    for s in u16[:60 ]:
        print("  u16:",s )

    b3 =(EVB_DIR /"bass3.dll").read_bytes()
    num_tables =struct.unpack_from(">H",b3 ,4 )[0 ]
    for i in range(num_tables ):
        tag ,csum ,off ,length =struct.unpack_from(">4sIII",b3 ,12 +i *16 )
        if tag ==b"name":
            name_tbl =b3[off :off +length ]
            fmt ,count ,str_off =struct.unpack_from(">HHH",name_tbl ,0 )
            print(f"bass3.dll 'name' table: count={count }")
            for j in range(count ):
                pid ,eid ,lid ,nid ,slen ,soff =struct.unpack_from(">HHHHHH",name_tbl ,6 +j *12 )
                raw_s =name_tbl[str_off +soff :str_off +soff +slen ]
                dec =raw_s.decode("utf-16be",errors ="replace")if pid in(0 ,3 )else raw_s.decode("latin1",errors ="replace")
                print(f"  name[{nid }] (pid={pid }, eid={eid }, lid={lid }): {dec !r }")

def sanitize_relpath(raw_name :bytes ,idx :int )->str :
    try :
        s =raw_name.decode("ascii")
        if all(c not in '<>:"|?*'and 32 <=ord(c )<=126 for c in s ):
            return s.replace("\\","/")
    except UnicodeDecodeError :
        pass

    parts =raw_name.split(b"\\")
    safe_parts =[]
    for p in parts :
        try :
            sp =p.decode("ascii")
            if all(c not in '<>:"|?*'and 32 <=ord(c )<=126 for c in sp ):
                safe_parts.append(sp )
            else :
                safe_parts.append(f"_raw_{idx }_{p.hex()[:16 ]}")
        except UnicodeDecodeError :
            safe_parts.append(f"_raw_{idx }_{p.hex()[:16 ]}")
    return "/".join(safe_parts )

def unpack_pak():
    raw =(EVB_DIR /"main.pak").read_bytes()
    decoded =bytes(b ^0xF7 for b in raw )
    magic ,version =struct.unpack_from("<II",decoded ,0 )

    pos =8
    entries =[]
    idx =0
    while pos <len(decoded ):
        flag =decoded[pos ]
        pos +=1
        if flag &0x80 :
            end_flag =flag
            break
        name_len =decoded[pos ]
        pos +=1
        raw_name =decoded[pos :pos +name_len ]
        pos +=name_len
        size ,ft_low ,ft_high =struct.unpack_from("<III",decoded ,pos )
        pos +=12
        safe_rel =sanitize_relpath(raw_name ,idx )
        entries.append({
        "index":idx ,
        "flag":flag ,
        "raw_name_hex":raw_name.hex(),
        "safe_relpath":safe_rel ,
        "size":size ,
        "ft_low":ft_low ,
        "ft_high":ft_high ,
        })
        idx +=1

    UNPACK_DIR.mkdir(parents =True ,exist_ok =True )
    cur =pos
    for e in entries :
        out_path =UNPACK_DIR /e["safe_relpath"]
        out_path.parent.mkdir(parents =True ,exist_ok =True )
        out_path.write_bytes(decoded[cur :cur +e["size"]])
        cur +=e["size"]

    MANIFEST_PATH.write_text(json.dumps({
    "magic":magic ,
    "version":version ,
    "end_flag":end_flag ,
    "entry_count":len(entries ),
    "entries":entries ,
    },indent =2 ,ensure_ascii =False ),encoding ="utf-8")

    print(f"Unpacked {len(entries )} files and saved manifest to {MANIFEST_PATH }")
    for e in entries :
        sr =e["safe_relpath"]
        if any(sr.lower().endswith(ext )for ext in[".txt",".xml",".json",".ini",".ttf",".otf"])or sr.startswith("properties/")or sr.startswith("data/"):
            print(f"  [{e['index']}] {sr } ({e['size']} bytes)")

if __name__ =="__main__":
    inspect_bass2_and_bass3()
    unpack_pak()
