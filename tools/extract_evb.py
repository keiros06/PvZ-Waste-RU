import struct
from pathlib import Path

EXE_PATH =Path(r"input/AreYouFw.exe")
OUT_DIR =Path(r".\build\extracted_evb")

def main():
    data =EXE_PATH.read_bytes()
    e1_rptr =0x16af000
    e1_rsize =0x4533000
    e1 =data[e1_rptr :e1_rptr +e1_rsize ]

    print("e1[:0x2f7] hex dump:")
    for off in range(0 ,0x2f7 ,32 ):
        chunk =e1[off :min(0x2f7 ,off +32 )]
        print(f"{off :04x}: {chunk.hex()}")

    data_base =0x2f7
    files =[
    ("bass.dll",0x0 ,0x00016838 ),
    ("bass2.dll",0x00016838 ,0x0025c800 ),
    ("bass3.dll",0x00273038 ,0x0030f10c ),
    ("main.pak",0x00582144 ,0x03f94366 ),
    ]
    OUT_DIR.mkdir(parents =True ,exist_ok =True )
    for fname ,rel_off ,fsize in files :
        abs_off =data_base +rel_off
        blob =e1[abs_off :abs_off +fsize ]
        out_path =OUT_DIR /fname
        out_path.write_bytes(blob )
        print(f"Extracted {fname }: size={len(blob )} (expected {fsize }), head={blob[:16 ].hex()}")

    tail_start =data_base +0x00582144 +0x03f94366
    tail =e1[tail_start :]
    non_zero =sum(1 for b in tail if b !=0 )
    print(f"Tail from {hex(tail_start )} to {hex(len(e1 ))} (len={len(tail )}): non_zero_bytes={non_zero }")
    if non_zero >0 :
        print("First non-zero in tail:",tail[:128 ].hex())

if __name__ =="__main__":
    main()
