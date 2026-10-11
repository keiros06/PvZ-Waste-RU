import json
import shutil
import struct
from pathlib import Path
import numpy as np

BASE =Path(r".\build")
UNPACKED =BASE /"unpacked_pak"
EVB_DIR =BASE /"extracted_evb"
MANIFEST_PATH =BASE /"pak_manifest.json"
PATCHED_EXE_BASE =BASE /"patched_exe_base.exe"
RELEASE_DIR =BASE /"release"

def build_main_pak():
    RELEASE_DIR.mkdir(parents =True ,exist_ok =True )

    for dll in["bass.dll","bass2.dll","bass3.dll"]:
        if(UNPACKED /dll ).exists()and(EVB_DIR /dll ).exists():
            shutil.copy2(EVB_DIR /dll ,UNPACKED /dll )

    manifest =json.loads(MANIFEST_PATH.read_text(encoding ="utf-8"))
    entries =manifest["entries"]

    header_parts =[struct.pack("<II",manifest["magic"],manifest["version"])]
    data_blobs =[]

    for entry in entries :
        rel_path =entry["safe_relpath"]
        file_path =UNPACKED /rel_path
        raw_bytes =file_path.read_bytes()
        size =len(raw_bytes )
        ft_low =int(entry["ft_low"])
        ft_high =int(entry["ft_high"])
        name_bytes =bytes.fromhex(entry["raw_name_hex"])

        header_parts.append(struct.pack("<BB",int(entry["flag"]),len(name_bytes )))
        header_parts.append(name_bytes )
        header_parts.append(struct.pack("<III",size ,ft_low ,ft_high ))
        data_blobs.append(raw_bytes )

    header_parts.append(struct.pack("<B",int(manifest["end_flag"])))
    raw_pak =b"".join(header_parts )+b"".join(data_blobs )

    arr =np.frombuffer(raw_pak ,dtype =np.uint8 )^0xF7
    pak_out =RELEASE_DIR /"main.pak"
    pak_out.write_bytes(arr.tobytes())
    print(f"Repacked {len(entries )} files into {pak_out } ({pak_out.stat().st_size :,} bytes)")

def build_release_exe_and_dlls():
    for dll in["bass.dll","bass2.dll","bass3.dll"]:
        shutil.copy2(EVB_DIR /dll ,RELEASE_DIR /dll )

    exe_bytes =bytearray(PATCHED_EXE_BASE.read_bytes())
    evb_targets =[
    (0x16AF2AB ,"main.pak","_ain.pak"),
    (0x16AF1A3 ,"bass2.dll","_ass2.dll"),
    (0x16AF1FD ,"bass3.dll","_ass3.dll"),
    ]
    for offset ,orig_name ,new_name in evb_targets :
        orig_u16 =orig_name.encode("utf-16le")
        new_u16 =new_name.encode("utf-16le")
        actual =bytes(exe_bytes[offset :offset +len(orig_u16 )])
        assert actual ==orig_u16 ,f"Mismatch at {hex(offset )}: {actual !r } != {orig_u16 !r }"
        exe_bytes[offset :offset +len(new_u16 )]=new_u16
        print(f"Unhooked EVB virtual file {orig_name } -> {new_name } at {hex(offset )}")

    out_exe =RELEASE_DIR /"PvZ_Waste_RU.exe"
    out_exe.write_bytes(exe_bytes )
    print(f"Built {out_exe } ({out_exe.stat().st_size :,} bytes)")

if __name__ =="__main__":
    build_main_pak()
    build_release_exe_and_dlls()
