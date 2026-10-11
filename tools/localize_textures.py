import shutil
from pathlib import Path
from PIL import Image ,ImageDraw ,ImageFont
import numpy as np

BASE =Path(r".\build")
UNPACKED =BASE /"unpacked_pak"
RUS_REF =BASE /"rus_reference"
BACKUP =BASE /"textures_backup"
FONT_PATH =str(Path(r"build/Russian_augmented.ttf"))

DIRECT_COPY_FILES =[
"images/Almanac.png",
"images/FlagMeterLevelProgress.png",
"images/options_menuback.jpg",
"images/SelectorScreen_Almanac.png",
"images/SelectorScreen_AlmanacHighlight.png",
"images/SelectorScreen_Help1.png",
"images/SelectorScreen_Help2.png",
"images/SelectorScreen_Options1.png",
"images/SelectorScreen_Options2.png",
"images/SelectorScreen_Quit1.png",
"images/SelectorScreen_Quit2.png",
"images/SelectorScreen_Store.png",
"images/SelectorScreen_StoreHighlight.png",
"images/SelectorScreen_ZenGarden.png",
"images/SelectorScreen_ZenGardenHighlight.png",
"images/Store_NextButton.png",
"images/Store_NextButtonHighlight.png",
"images/Store_PrevButton.png",
"images/Store_PrevButtonHighlight.png",
"images/Store_Sign.png",
"images/zenshopbutton.png",
"images/zenshopbutton_highlight.png",
"images/ZombieNote4.png",
"reanim/FinalWave.png",
"reanim/StartPlant.png",
"reanim/StartReady.png",
"reanim/StartSet.png",
"reanim/SelectorScreen_StartAdventure_Button1.png",
"reanim/SelectorScreen_StartAdventure_Highlight.png",
"reanim/SelectorScreen_Challenges_button.png",
"reanim/SelectorScreen_Challenges_highlight.png",
"reanim/SelectorScreen_Survival_button.png",
"reanim/SelectorScreen_Survival_highlight.png",
"reanim/SelectorScreen_Vasebreaker_button.png",
"reanim/SelectorScreen_vasebreaker_highlight.png",
"reanim/SelectorScreen_WoodSign1.png",
"reanim/SelectorScreen_WoodSign2.png",
"reanim/SelectorScreen_WoodSign2_press.png",
"reanim/Credits_MTV.png",
"reanim/Credits_wearetheundead.jpg",
"reanim/Credits_wearetheundead_.png",
"particles/Doom.png",
"particles/ExplosionPowie.png",
"particles/ExplosionSpudow.png",
"particles/Pow.png",
"particles/Sproing.png",
]

CUSTOM_FILES =[
"images/PvZ_Logo.jpg",
"images/PvZ_Logo_.png",
"reanim/SelectorScreen_Adventure_button.png",
"reanim/SelectorScreen_Adventure_highlight.png",
"images/Taco.png",
"reanim/ZombiesWon.jpg",
"reanim/ZombiesWon_.png",
"images/ZombieNote1.png",
"images/ZombieNote2.png",
"images/ZombieNote3.png",
"images/Zombiefinalnote.png",
"images/ZombieNoteHelp.png",
"images/Credits_ZombieNote.png",
"images/Tombstones.jpg",
]

def ensure_backups():
    BACKUP.mkdir(parents =True ,exist_ok =True )
    for rel in DIRECT_COPY_FILES +CUSTOM_FILES :
        src =UNPACKED /rel
        dst =BACKUP /rel
        if src.exists()and not dst.exists():
            dst.parent.mkdir(parents =True ,exist_ok =True )
            shutil.copy2(src ,dst )

def draw_gradient_text(
size ,
pos ,
text ,
font ,
top_color ,
bot_color ,
outline_color ,
outline_width =3 ,
shadow_offset =(2 ,2 ),
shadow_color =(0 ,0 ,0 ,200 ),
extrude_offsets =None ,
extrude_color =None ,
):

    w ,h =size
    layer =Image.new("RGBA",(w ,h ),(0 ,0 ,0 ,0 ))

    mask_im =Image.new("L",(w ,h ),0 )
    mdraw =ImageDraw.Draw(mask_im )
    mdraw.text(pos ,text ,font =font ,fill =255 )
    mask_arr =np.array(mask_im )

    ys =np.where(mask_arr >0 )[0 ]
    if len(ys )==0 :
        return layer
    y_min ,y_max =ys.min(),max(ys.max(),ys.min()+1 )

    out_im =Image.new("RGBA",(w ,h ),(0 ,0 ,0 ,0 ))
    odraw =ImageDraw.Draw(out_im )
    if shadow_offset :
        sx ,sy =shadow_offset
        odraw.text(
        (pos[0 ]+sx ,pos[1 ]+sy ),
        text ,
        font =font ,
        fill =shadow_color ,
        stroke_width =outline_width +1 ,
        stroke_fill =shadow_color ,
        )
    if extrude_offsets and extrude_color :
        for ex ,ey in extrude_offsets :
            odraw.text(
            (pos[0 ]+ex ,pos[1 ]+ey ),
            text ,
            font =font ,
            fill =extrude_color ,
            stroke_width =outline_width ,
            stroke_fill =outline_color ,
            )
    odraw.text(
    pos ,
    text ,
    font =font ,
    fill =outline_color ,
    stroke_width =outline_width ,
    stroke_fill =outline_color ,
    )

    grad_arr =np.zeros((h ,w ,4 ),dtype =np.uint8 )
    for y in range(y_min ,y_max +1 ):
        t =(y -y_min )/(y_max -y_min )
        r =int(top_color[0 ]*(1 -t )+bot_color[0 ]*t )
        g =int(top_color[1 ]*(1 -t )+bot_color[1 ]*t )
        b =int(top_color[2 ]*(1 -t )+bot_color[2 ]*t )
        grad_arr[y ,:,0 ]=r
        grad_arr[y ,:,1 ]=g
        grad_arr[y ,:,2 ]=b
    grad_arr[:,:,3 ]=mask_arr

    layer.alpha_composite(out_im )
    layer.alpha_composite(Image.fromarray(grad_arr ,"RGBA"))
    return layer

def localize_taco():

    orig =Image.open(BACKUP /"images/Taco.png").convert("RGBA")
    arr =np.array(orig )

    arr[:30 ,:,:]=0

    for y in range(30 ,39 ):
        for x in range(107 ):
            r ,g ,b ,a =arr[y ,x ]
            if a >0 and(int(r )-int(b )>25 or int(g )-int(b )>20 ):
                if y <=34 :
                    arr[y ,x ]=[0 ,0 ,0 ,0 ]
                else :

                    gray =int(min(r ,g ,b )*0.7 )
                    arr[y ,x ]=[gray ,gray ,min(255 ,gray +10 ),a ]

    bag_canvas =Image.fromarray(arr ,"RGBA")
    font =ImageFont.truetype(FONT_PATH ,21 )
    text_layer =draw_gradient_text(
    (107 ,90 ),
    (14 ,11 ),
    "МУСОР",
    font ,
    top_color =(255 ,245 ,30 ),
    bot_color =(255 ,130 ,0 ),
    outline_color =(15 ,95 ,35 ,255 ),
    outline_width =2 ,
    shadow_offset =(1 ,1 ),
    shadow_color =(0 ,40 ,10 ,220 ),
    )
    out =Image.new("RGBA",(107 ,90 ),(0 ,0 ,0 ,0 ))
    out.alpha_composite(text_layer )
    out.alpha_composite(bag_canvas )
    out.save(UNPACKED /"images/Taco.png")
    return out

def localize_pvz_logo(clean_taco_im ):

    orig_rgb =Image.open(BACKUP /"images/PvZ_Logo.jpg").convert("RGB")
    orig_mask =np.array(Image.open(BACKUP /"images/PvZ_Logo_.png").convert("RGBA"))[:,:,0 ]
    orig_rgba =orig_rgb.convert("RGBA")
    orig_rgba.putalpha(Image.fromarray(orig_mask ,"L"))

    canvas =Image.new("RGBA",(700 ,260 ),(0 ,0 ,0 ,0 ))

    rus_logo_rgb =Image.open(RUS_REF /"images/PvZ_Logo.jpg").convert("RGBA")
    rus_logo_mask =Image.open(RUS_REF /"images/PvZ_Logo_.png").convert("L")
    rus_logo_rgb.putalpha(rus_logo_mask )
    tomb_crop =rus_logo_rgb.crop((292 ,18 ,372 ,112 )).resize((88 ,94 ),Image.Resampling.LANCZOS )
    t_arr =np.array(tomb_crop )
    for ty in range(t_arr.shape[0 ]):
        for tx in range(t_arr.shape[1 ]):
            r ,g ,b ,a =t_arr[ty ,tx ]

            if(tx <26 and ty <82 and(int(g )>int(r )+16 or tx <15 ))or(tx >74 and ty <34 ):
                t_arr[ty ,tx ]=[0 ,0 ,0 ,0 ]
            elif r <38 and g <38 and b <38 :
                t_arr[ty ,tx ]=[0 ,0 ,0 ,0 ]
    tomb_clean =Image.fromarray(t_arr ,"RGBA")

    font_main =ImageFont.truetype(FONT_PATH ,62 )
    plants_layer =draw_gradient_text(
    (700 ,260 ),
    (34 ,20 ),
    "РАСТЕНИЯ",
    font_main ,
    top_color =(195 ,255 ,35 ),
    bot_color =(65 ,205 ,15 ),
    outline_color =(10 ,65 ,15 ,255 ),
    outline_width =5 ,
    shadow_offset =(3 ,5 ),
    shadow_color =(0 ,0 ,0 ,235 ),
    extrude_offsets =[(0 ,3 ),(1 ,3 ),(-1 ,3 )],
    extrude_color =(25 ,125 ,25 ,255 ),
    )

    font_zomb =ImageFont.truetype(FONT_PATH ,74 )
    zombies_layer =draw_gradient_text(
    (700 ,260 ),
    (398 ,12 ),
    "ЗОМБИ",
    font_zomb ,
    top_color =(225 ,230 ,230 ),
    bot_color =(140 ,148 ,148 ),
    outline_color =(15 ,15 ,15 ,255 ),
    outline_width =5 ,
    shadow_offset =(4 ,6 ),
    shadow_color =(0 ,0 ,0 ,235 ),
    extrude_offsets =[(-3 ,2 ),(-5 ,3 ),(-4 ,4 )],
    extrude_color =(165 ,20 ,15 ,255 ),
    )

    canvas.alpha_composite(tomb_clean ,(308 ,12 ))
    canvas.alpha_composite(plants_layer )
    canvas.alpha_composite(zombies_layer )

    mushroom_crop =orig_rgba.crop((374 ,70 ,398 ,100 ))
    m_arr =np.array(mushroom_crop )

    dark_bg =(m_arr[:,:,0 ]<35 )&(m_arr[:,:,1 ]<35 )&(m_arr[:,:,2 ]<35 )
    m_arr[dark_bg ,3 ]=0
    canvas.alpha_composite(Image.fromarray(m_arr ,"RGBA"),(374 ,70 ))

    scaled_bag =clean_taco_im.resize((132 ,134 ),Image.Resampling.LANCZOS )
    canvas.alpha_composite(scaled_bag ,(246 ,126 ))

    shroom_crop =orig_rgba.crop((375 ,106 ,436 ,146 ))
    s_arr =np.array(shroom_crop )
    for y in range(s_arr.shape[0 ]):
        for x in range(s_arr.shape[1 ]):
            r ,g ,b ,a =s_arr[y ,x ]

            if(r <28 and g <28 and b <28 )or(y >=28 and int(r )>int(g )+20 and int(g )>int(b )+12 ):
                s_arr[y ,x ]=[0 ,0 ,0 ,0 ]
    shroom_clean =Image.fromarray(s_arr ,"RGBA")

    font_izd =ImageFont.truetype(FONT_PATH ,38 )
    izd_layer =draw_gradient_text(
    (700 ,260 ),
    (376 ,144 ),
    "ИЗД.",
    font_izd ,
    top_color =(215 ,165 ,90 ),
    bot_color =(135 ,85 ,30 ),
    outline_color =(25 ,15 ,5 ,255 ),
    outline_width =3 ,
    shadow_offset =(2 ,3 ),
    shadow_color =(0 ,0 ,0 ,230 ),
    )
    canvas.alpha_composite(izd_layer )
    canvas.alpha_composite(shroom_clean ,(375 ,106 ))

    arr =np.array(canvas )
    alpha =arr[:,:,3 ]
    rgb_arr =arr[:,:,:3 ].copy()
    rgb_arr[alpha ==0 ]=0
    Image.fromarray(rgb_arr ,"RGB").save(UNPACKED /"images/PvZ_Logo.jpg",quality =95 )

    mask_rgba =np.stack([alpha ,alpha ,alpha ,np.full_like(alpha ,255 )],axis =2 )
    Image.fromarray(mask_rgba ,"RGBA").save(UNPACKED /"images/PvZ_Logo_.png")

def localize_adventure_buttons():

    for fname in["SelectorScreen_Adventure_button.png","SelectorScreen_Adventure_highlight.png"]:
        w_im =Image.open(BACKUP /"reanim"/fname ).convert("RGBA")
        r_im =Image.open(RUS_REF /"reanim"/fname ).convert("RGBA")
        w_arr =np.array(w_im )
        r_arr =np.array(r_im )

        w_arr[80 :102 ,105 :157 ]=r_arr[21 :43 ,106 :158 ]

        for y in range(14 ,98 ):
            row_rgb =w_arr[y ,22 :296 ,:3 ]
            row_lum =row_rgb.mean(axis =1 )
            clean_pixels =row_rgb[(row_lum >=78 )&(row_lum <=128 )]
            if len(clean_pixels )>0 :
                med_color =np.median(clean_pixels ,axis =0 ).astype(np.uint8 )
            else :
                med_color =np.array([102 ,103 ,120 ],dtype =np.uint8 )
            for x in range(24 ,294 ):
                if y <21 and x >185 :
                    continue

                if y >=74 and x <160 :
                    continue
                if y >=82 and x <198 :
                    continue
                if y >=86 and x <228 :
                    continue
                px_lum =w_arr[y ,x ,:3 ].mean()
                if px_lum <78 or(px_lum >130 and 18 <=y <=74 and x <288 ):
                    w_arr[y ,x ,:3 ]=med_color

        r_crop =r_arr[44 :122 ,14 :292 ]
        r_crop_im =Image.fromarray(r_crop ,"RGBA").resize((274 ,52 ),Image.Resampling.LANCZOS )
        r_S =np.array(r_crop_im )
        r_S_lum =r_S[:,:,:3 ].mean(axis =2 )

        target =w_arr[19 :71 ,18 :292 ,:3 ].astype(np.float32 )
        carve_w =np.clip((80.0 -r_S_lum )/38.0 ,0.0 ,1.0 )[:,:,None ]
        valid =(r_S[:,:,3 ]>200 )[:,:,None ]
        carve_w =carve_w *valid

        bevel_w =np.roll(np.roll(carve_w[:,:,0 ],1 ,axis =0 ),1 ,axis =1 )*(1.0 -carve_w[:,:,0 ])
        target =target +bevel_w[:,:,None ]*34.0
        target =target *(1.0 -carve_w )+r_S[:,:,:3 ].astype(np.float32 )*carve_w
        w_arr[19 :71 ,18 :292 ,:3 ]=np.clip(target ,0 ,255 ).astype(np.uint8 )

        Image.fromarray(w_arr ,"RGBA").save(UNPACKED /"reanim"/fname )

def localize_zombies_won():

    w ,h =564 ,468
    canvas =Image.new("RGBA",(w ,h ),(0 ,0 ,0 ,0 ))

    lines =[
    ("ТЫ СЪЕЛ",86 ,28 ),
    ("МОЗГИ",104 ,148 ),
    ("ЗОМБИ!",112 ,282 ),
    ]
    for text ,fsize ,y in lines :
        font =ImageFont.truetype(FONT_PATH ,fsize )
        dummy =ImageDraw.Draw(canvas )
        bbox =dummy.textbbox((0 ,0 ),text ,font =font )
        tw =bbox[2 ]-bbox[0 ]
        x =(w -tw )//2
        layer =draw_gradient_text(
        (w ,h ),
        (x ,y ),
        text ,
        font ,
        top_color =(190 ,255 ,45 ),
        bot_color =(95 ,215 ,10 ),
        outline_color =(15 ,75 ,5 ,255 ),
        outline_width =5 ,
        shadow_offset =(0 ,4 ),
        shadow_color =(10 ,50 ,0 ,255 ),
        )
        canvas.alpha_composite(layer )

    rus_rgb =Image.open(RUS_REF /"reanim/ZombiesWon.jpg").convert("RGBA")
    rus_a =Image.open(RUS_REF /"reanim/ZombiesWon_.png").convert("L")
    rus_rgb.putalpha(rus_a )
    splat =rus_rgb.crop((450 ,380 ,558 ,466 ))
    canvas.alpha_composite(splat ,(450 ,380 ))

    arr =np.array(canvas )
    alpha =arr[:,:,3 ]
    rgb =arr[:,:,:3 ].copy()
    rgb[alpha ==0 ]=0

    Image.fromarray(rgb ,"RGB").save(UNPACKED /"reanim/ZombiesWon.jpg",quality =95 )
    Image.fromarray(alpha ,"L").save(UNPACKED /"reanim/ZombiesWon_.png")

def render_note_image(size ,lines_spec ,base_im =None ):
    if base_im is not None :
        im =base_im.copy().convert("RGBA")
    else :
        im =Image.new("RGBA",size ,(0 ,0 ,0 ,255 ))
    draw =ImageDraw.Draw(im )
    for x ,y ,fsize ,text in lines_spec :
        font =ImageFont.truetype(FONT_PATH ,fsize )
        draw.text((x ,y ),text ,font =font ,fill =(255 ,255 ,255 ,255 ))
    return im

def localize_zombie_notes():

    note1 =render_note_image(
    (537 ,344 ),
    [
    (28 ,18 ,32 ,"Привет!"),
    (24 ,72 ,24 ,"Твой летучий дом нам вообще не интересен —"),
    (24 ,114 ,24 ,"мы устраиваем массовый побег!"),
    (24 ,195 ,26 ,"Прощай навсегда,"),
    (260 ,255 ,30 ,"Умные зомби"),
    ],
    )
    note1.save(UNPACKED /"images/ZombieNote1.png")

    note2 =render_note_image(
    (550 ,343 ),
    [
    (24 ,14 ,30 ,"Привет,"),
    (20 ,62 ,22 ,"Тебе случайно повезло нас победить, но теперь"),
    (20 ,100 ,22 ,"мы пойдём в атаку всерьёз! Пожалуйста, убери"),
    (20 ,138 ,22 ,"оборону с лужайки и приготовь пломбир..."),
    (20 ,176 ,22 ,"то есть мозги."),
    (240 ,232 ,25 ,"С уважением,"),
    (330 ,275 ,30 ,"Зомби"),
    ],
    )
    note2.save(UNPACKED /"images/ZombieNote2.png")

    note3 =render_note_image(
    (574 ,361 ),
    [
    (24 ,16 ,30 ,"Привет!"),
    (20 ,66 ,23 ,"Это Дин Чжэнь и пони Перл.Твой задний двор"),
    (20 ,106 ,23 ,"очень удобный — пожалуйста, построй мостик"),
    (20 ,146 ,23 ,"через бассейн и убери все растения!"),
    (240 ,228 ,25 ,"С уважением,"),
    (205 ,274 ,27 ,"Дин Чжэнь(не зомби)"),
    ],
    )
    note3.save(UNPACKED /"images/ZombieNote3.png")

    rus_final =Image.open(RUS_REF /"images/Zombiefinalnote.png").convert("RGBA")
    arr_f =np.array(rus_final )
    arr_f[44 :238 ,:,:3 ]=0
    arr_f[210 :260 ,:180 ,:3 ]=0
    arr_f[:,:,3 ]=255
    base_final =Image.fromarray(arr_f ,"RGBA")
    final_note =render_note_image(
    (546 ,321 ),
    [
    (18 ,56 ,21 ,"Твои растения выросли совершенно бесполезными"),
    (18 ,92 ,21 ,"и ни за что нас не остановят."),
    (18 ,138 ,21 ,"Подумай ещё раз: если ты сам не отдашь нам"),
    (18 ,174 ,21 ,"свои мозги, мы примем крайние меры!"),
    ],
    base_im =base_final ,
    )
    final_note.save(UNPACKED /"images/Zombiefinalnote.png")

    help_note =render_note_image(
    (529 ,323 ),
    [
    (16 ,18 ,19 ,"ПАМЯТКА МУСОРНОГО ИЗДАНИЯ"),
    (16 ,68 ,17 ,"1 -> Быстро взять лопату"),
    (16 ,102 ,17 ,"2 -> Ускорить игру"),
    (16 ,136 ,17 ,"3 -> Остановка времени"),
    (16 ,170 ,17 ,"4 -> Показать здоровье растений"),
    (16 ,204 ,17 ,"5 -> Показать здоровье зомби"),
    (16 ,238 ,17 ,"6 -> Автосбор ресурсов"),
    (286 ,20 ,19 ,"КОМАНДА АВТОРОВ"),
    (286 ,68 ,15 ,"Геймдизайн: Злорадная Птичка"),
    (286 ,100 ,14 ,"Главный программист: TianDouHuaEr"),
    (286 ,132 ,15 ,"Код: Peter, Лин, Процион А"),
    (286 ,164 ,15 ,"Анимации: Мэн Саньго, 4545"),
    (286 ,202 ,15 ,"Особая благодарность:"),
    (286 ,228 ,15 ,"Тексты: Третий Апельсин"),
    (286 ,254 ,15 ,"Материалы: Pask"),
    ],
    )
    help_note.save(UNPACKED /"images/ZombieNoteHelp.png")

    cred_note =render_note_image(
    (537 ,359 ),
    [
    (36 ,28 ,28 ,"Думаешь, ты победил?"),
    (28 ,86 ,24 ,"Даже не оценив разницу в силе,"),
    (28 ,132 ,24 ,"ты посмел бросить вызов зомби?"),
    (28 ,184 ,25 ,"Лови мою фирменную доставку!"),
    (310 ,246 ,28 ,"Мудрые"),
    (330 ,290 ,32 ,"Зомби"),
    ],
    )
    cred_note.convert("RGB").save(UNPACKED /"images/Credits_ZombieNote.png")

def localize_tombstones():
    im =Image.open(BACKUP /"images/Tombstones.jpg").convert("RGB")
    arr =np.array(im )
    arr[10 :70 ,:,:]=arr[192 :252 ,:,:]

    canvas =Image.fromarray(arr ).convert("RGBA")
    epitaphs =[
    (46 ,22 ,14 ,["УСОП"]),
    (124 ,24 ,10 ,["ПОКИНУЛ","ЭТОТ","МИР"]),
    (296 ,22 ,11 ,["ПРОСТО","УСНУЛ"]),
    (382 ,18 ,12 ,["ПАЛ В","БОЮ"]),
    ]
    draw =ImageDraw.Draw(canvas )
    for cx ,ty ,fsize ,lines in epitaphs :
        font =ImageFont.truetype(FONT_PATH ,fsize )
        y =ty
        for line in lines :
            bbox =draw.textbbox((0 ,0 ),line ,font =font )
            tw =bbox[2 ]-bbox[0 ]
            th =bbox[3 ]-bbox[1 ]
            x =cx -tw //2
            draw.text((x +1 ,y +1 ),line ,font =font ,fill =(165 ,170 ,175 ,220 ))
            draw.text((x ,y ),line ,font =font ,fill =(32 ,35 ,38 ,240 ))
            y +=th +2

    canvas.convert("RGB").save(UNPACKED /"images/Tombstones.jpg",quality =95 )

def main():
    ensure_backups()

    copied =0
    for rel in DIRECT_COPY_FILES :
        src =RUS_REF /rel
        dst =UNPACKED /rel
        shutil.copy2(src ,dst )
        copied +=1
    print(f"Copied {copied } canonical Russian UI textures from rus_reference.")

    clean_taco_im =localize_taco()
    print("Localized images/Taco.png")

    localize_pvz_logo(clean_taco_im )
    print("Localized images/PvZ_Logo.jpg & PvZ_Logo_.png")

    localize_adventure_buttons()
    print("Localized reanim/SelectorScreen_Adventure_button.png & highlight.png")

    localize_zombies_won()
    print("Localized reanim/ZombiesWon.jpg & ZombiesWon_.png")

    localize_zombie_notes()
    print("Localized ZombieNote1..3, Zombiefinalnote, ZombieNoteHelp, Credits_ZombieNote")

    localize_tombstones()
    print("Localized images/Tombstones.jpg")

if __name__ =="__main__":
    main()
