from pathlib import Path
from PIL import Image ,ImageDraw ,ImageFont
import numpy as np

ROOT =Path(r".")
SETTING_PATH =ROOT /"build"/"unpacked_pak"/"new_images"/"Settingon.png"
ARTIST_ORIG =ROOT /"ui_for_artist"/"01_originals_chinese"/"new_images__Settingon.png"
ARTIST_CURR =ROOT /"ui_for_artist"/"03_current_ru_build"/"new_images__Settingon.png"
TTF_PATH =ROOT /"build"/"Russian_augmented.ttf"

def fix_settingon():
    im =Image.open(ARTIST_ORIG ).convert("RGBA")
    arr =np.array(im )
    h ,w ,_ =arr.shape

    sub =arr[40 :71 ,52 :106 ]
    mask_bright =(sub[:,:,2 ]>155 )&(sub[:,:,1 ]>145 )&(sub[:,:,3 ]>200 )

    full_bright =np.zeros((h ,w ),dtype =bool )
    full_bright[40 :71 ,52 :106 ]=mask_bright

    inpaint_mask =np.zeros((h ,w ),dtype =bool )
    for y in range(41 ,70 ):
        for x in range(54 ,104 ):
            if full_bright[max(0 ,y -3 ):min(h ,y +4 ),max(0 ,x -3 ):min(w ,x +4 )].any():
                r ,g ,b ,_ =arr[y ,x ]
                is_bright =(b >145 and g >135 )
                is_outline =(r <92 and g <96 and b <98 )
                is_blue_tint =(int(b )-int(r )>10 )
                if is_bright or is_outline or is_blue_tint :
                    inpaint_mask[y ,x ]=True

    rgb =arr[:,:,:3 ].astype(np.float32 )
    for _ in range(200 ):
        up =np.roll(rgb ,-1 ,axis =0 )
        dn =np.roll(rgb ,1 ,axis =0 )
        lf =np.roll(rgb ,-1 ,axis =1 )
        rt =np.roll(rgb ,1 ,axis =1 )
        avg =0.25 *(up +dn +lf +rt )
        rgb[inpaint_mask ]=avg[inpaint_mask ]

    rng =np.random.default_rng(7 )
    noise =rng.normal(0 ,1.2 ,size =(h ,w ,1 ))
    rgb[inpaint_mask ]=np.clip(rgb[inpaint_mask ]+noise[inpaint_mask ],0 ,255 )
    arr[:,:,:3 ]=rgb.astype(np.uint8 )

    clean_im =Image.fromarray(arr ,"RGBA")
    draw =ImageDraw.Draw(clean_im )

    text ="КОНСОЛЬ"
    font =ImageFont.truetype(str(TTF_PATH ),12 )
    bbox =draw.textbbox((0 ,0 ),text ,font =font )
    tw =bbox[2 ]-bbox[0 ]
    th =bbox[3 ]-bbox[1 ]
    cx =84
    cy =55
    tx =cx -tw //2 -bbox[0 ]
    ty =cy -th //2 -bbox[1 ]

    for ox in(-2 ,-1 ,0 ,1 ,2 ):
        for oy in(-2 ,-1 ,0 ,1 ,2 ):
            if ox ==0 and oy ==0 :
                continue
            if abs(ox )+abs(oy )<=3 :
                draw.text((tx +ox ,ty +oy ),text ,font =font ,fill =(22 ,26 ,32 ,255 ))

    draw.text((tx ,ty ),text ,font =font ,fill =(202 ,224 ,252 ,255 ))

    clean_im.save(SETTING_PATH )
    clean_im.save(ARTIST_CURR )
    print(f"Updated {SETTING_PATH } (text='{text }', width={tw }px)")

if __name__ =="__main__":
    fix_settingon()
