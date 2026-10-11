import os
import struct
import sys

sys.stdout.reconfigure(encoding ="utf-8")

ORIG_EXE =r"input/AreYouFw.exe"
OUT_EXE ="build/patched_exe_base.exe"

POOL_BASE_VA =0x00950000
POOL_BASE_FOFF =0x499000

EXE_STRING_PATCHES =[
(0x00657504 ,0x257504 ,14 ,"        智慧树","Дерево Глупости"),
(0x00657B7C ,0x257B7C ,2 ,"好","ОК"),
(0x00657CBC ,0x257CBC ,6 ," 取消 ","Отмена"),
(0x00657CC4 ,0x257CC4 ,18 ,"继续游戏？        ","Продолжить игру?"),
(0x00657CD8 ,0x257CD8 ,63 ,"你想继续当前游戏还是重玩此关卡？                               ","Вы хотите продолжить текущую игру или начать уровень заново?"),
(0x00657D18 ,0x257D18 ,8 ,"  继续  ","Продолжить"),
(0x00657D24 ,0x257D24 ,13 ,"   重玩关卡  ","Переиграть"),
(0x00657D34 ,0x257D34 ,62 ,"你想继续当前游戏进度还是开始新的游戏？                        ","Вы хотите продолжить текущую игру или начать новую игру?"),
(0x00657D74 ,0x257D74 ,8 ," 新游戏 ","Новая игра"),
(0x00657D80 ,0x257D80 ,48 ,"你真的要重玩此关？                              ","Вы уверены, что хотите начать уровень заново?"),
(0x00657DB4 ,0x257DB4 ,14 ,"重新开始关卡？","Переиграть уровень?"),
(0x00657DD8 ,0x257DD8 ,47 ,"你真的要开始新的游戏？                         ","Вы уверены, что хотите начать новую игру?"),
(0x00657E08 ,0x257E08 ,9 ,"新游戏?  ","Новая игра?"),
(0x006674E0 ,0x2674E0 ,18 ,"植物大战僵尸废物版","Plants vs.Zombies: Мусорное Издание"),
(0x00667500 ,0x267500 ,65 ,"你想返回主菜单吗？\n\n你的游戏进度将被保存。                       ","Вернуться в главное меню?\n\nВаш прогресс будет сохранён."),
(0x00667544 ,0x267544 ,11 ," 离开游戏？","Выйти в меню?"),
(0x00667578 ,0x267578 ,11 ," 返回游戏  ","Вернуться"),
(0x00667584 ,0x267584 ,20 ,"    点击返回游戏    ","Вернуться к игре"),
(0x0066759C ,0x26759C ,11 ," 游戏暂停  ","Игра на паузе"),
(0x006675A8 ,0x2675A8 ,98 ,"请输入你的名字,以创建新的用户档案.档案用于保存游戏积分和进度.                                     ","Пожалуйста, введите ваше имя, чтобы создать профиль игрока для сохранения прогресса."),
(0x0066760C ,0x26760C ,15 ," 输入你的名字  ","Введите имя"),
(0x00667620 ,0x267620 ,79 ,"你输入的名字已经被使用了.请输入一个与众不同的玩家名.                          ","Это имя уже занято.Пожалуйста, введите другое имя игрока."),
(0x00667670 ,0x267670 ,13 ,"  名字冲突   ","Имя занято"),
(0x00667680 ,0x267680 ,57 ,"将从玩家簿中永久删除'%s'！                               ","Профиль '%s' будет навсегда удалён из списка игроков!"),
(0x006676BC ,0x2676BC ,13 ,"  你确定吗？ ","Вы уверены?"),
(0x00667AC8 ,0x267AC8 ,17 ,"    点击继续     ","Нажмите далее"),
(0x00667EA4 ,0x267EA4 ,2 ,"是","Да"),
(0x00667EA8 ,0x267EA8 ,2 ,"否","Нет"),
(0x00667EAC ,0x267EAC ,2 ,"好","ОК"),
(0x00667EB0 ,0x267EB0 ,6 ," 取消 ","Отмена"),
(0x00668378 ,0x268378 ,5 ,"音乐 ","Музыка"),
(0x00668380 ,0x268380 ,8 ,"音效    ","Звуки"),
(0x0066838C ,0x26838C ,15 ,"3D 加速        ","3D-ускорение"),
(0x0066839C ,0x26839C ,11 ,"全屏       ","Полный экран"),
(0x006686A8 ,0x2686A8 ,7 ," 重来  ","Заново"),
(0x0066880C ,0x26880C ,23 ,"    请输入你的名字：   ","Введите ваше имя:"),
(0x00668824 ,0x268824 ,11 ," 重命名用户","Переименовать"),
(0x00668830 ,0x268830 ,8 ," 新用户 ","Новый игрок"),
(0x0066D9A0 ,0x26D9A0 ,67 ,"你现在还买不起这个物品。\n去杀僵尸赚取更多钱币。                    ","У вас пока не хватает монет на этот предмет.\nУбивайте зомби!"),
(0x0066D9E4 ,0x26D9E4 ,16 ,"    资金不足    ","Не хватает монет"),
(0x0066D9F8 ,0x26D9F8 ,39 ,"你真的要买下这个物品吗？               ","Вы действительно хотите купить это?"),
(0x0066DA20 ,0x26DA20 ,14 ,"买下这个物品？","Купить предмет?"),
(0x0066DA30 ,0x26DA30 ,38 ,"你现在可以在每个关卡中选用%d个种子了！","Теперь доступно слотов под семена: %d!"),
(0x0066DA68 ,0x26DA68 ,11 ,"更多卡槽！ ","Новые слоты!"),
(0x0066E4B4 ,0x26E4B4 ,12 ,"  你叫啥？  ","Кто играет?"),
(0x0066E4C4 ,0x26E4C4 ,6 ,"重命名","Переименовать"),
(0x0066E4CC ,0x26E4CC ,6 ," 删除 ","Удалить"),
(0x0066E4D4 ,0x26E4D4 ,19 ,"（建立一位新用户） ","(Создать профиль)"),

(0x00795561 ,0x2DE561 ,8 ,"简单模式","Лёгкий режим"),
(0x0079556A ,0x2DE56A ,8 ,"普通模式","Обычный режим"),
(0x00795573 ,0x2DE573 ,8 ,"困难模式","Сложный режим"),
(0x0079557C ,0x2DE57C ,8 ,"地狱模式","Адский режим"),
(0x00795585 ,0x2DE585 ,8 ,"自动收集","Автосбор солнца"),
(0x0079558E ,0x2DE58E ,12 ,"植物血量显示","Здоровье растений"),
(0x0079559B ,0x2DE59B ,12 ,"僵尸血量显示","Здоровье зомби"),
(0x007955A8 ,0x2DE5A8 ,22 ,"提示：游戏出怪难度中途","Смена сложности волн"),
(0x007955BF ,0x2DE5BF ,10 ,"修改不生效","в бою не работает"),
(0x00795A86 ,0x2DEA86 ,15 ,"         控制台","        Консоль"),
(0x00795A96 ,0x2DEA96 ,15 ,"  控制台(第2页)","Консоль(страница 2)"),
(0x00795AA6 ,0x2DEAA6 ,15 ,"  控制台(第3页)","Консоль(страница 3)"),
(0x00795CA1 ,0x2DECA1 ,8 ,"简单模式","Лёгкий режим"),
(0x00795CAA ,0x2DECAA ,8 ,"普通模式","Обычный режим"),
(0x00795CB3 ,0x2DECB3 ,8 ,"困难模式","Сложный режим"),
(0x00795CBC ,0x2DECBC ,8 ,"地狱模式","Адский режим"),
(0x0079F04F ,0x2E804F ,8 ,"冒险模式","Приключение"),
(0x0079F178 ,0x2E8178 ,6 ,"第%d关","Уровень %d"),
(0x0079F182 ,0x2E8182 ,15 ,"第45关\x00\x00\x00\x00\x00\x00\x00\x00\x00","Уровень 45"),
]

def patch_push_length_near_ref(exe ,idx ,orig_len ,new_len ):

    if exe[idx -1 ]==0x68 and exe[idx -3 ]==0x6A :
        old_pushed_len =exe[idx -2 ]
        if 1 <=old_pushed_len <=max(orig_len +4 ,100 ):
            exe[idx -2 ]=new_len
            return True

    if exe[idx -1 ]==0x68 and exe[idx -2 ]==0x50 and exe[idx -4 ]==0x6A :
        old_pushed_len =exe[idx -3 ]
        if 1 <=old_pushed_len <=max(orig_len +4 ,100 ):
            exe[idx -3 ]=new_len
            return True
    return False

def main():
    with open(ORIG_EXE ,"rb")as f :
        exe =bytearray(f.read())

    pool_check =exe[POOL_BASE_FOFF :POOL_BASE_FOFF +0x10000 ]
    assert all(b ==0 for b in pool_check ),"Pool region at 0x499000 is not all zeros!"

    pool_cursor_foff =POOL_BASE_FOFF
    pool_cursor_va =POOL_BASE_VA

    in_place_count =0
    relocated_count =0
    total_refs_patched =0
    len_pushes_patched =0

    for va ,foff ,orig_len ,zh_expected ,ru_text in EXE_STRING_PATCHES :
        actual_bytes =bytes(exe[foff :foff +orig_len ])
        actual_zh =actual_bytes.decode("gbk",errors ="replace")
        assert actual_zh ==zh_expected ,f"Mismatch at 0x{foff :x}: expected {repr(zh_expected )}, got {repr(actual_zh )}"

        ru_bytes =ru_text.encode("cp1251")
        assert b"\x9f"not in ru_bytes ,f"Reserved 0x9F in {ru_text }"

        old_ptr =struct.pack("<I",va )

        if len(ru_bytes )<=orig_len :
            exe[foff :foff +orig_len +1 ]=ru_bytes +b"\x00"*(orig_len +1 -len(ru_bytes ))

            if va ==0x0079F182 :
                exe[0x2E8192 ]=len(ru_bytes )

            search_pos =0
            while True :
                idx =exe.find(old_ptr ,search_pos ,0x16AF000 )
                if idx ==-1 :
                    break
                if patch_push_length_near_ref(exe ,idx ,orig_len ,len(ru_bytes )):
                    len_pushes_patched +=1
                search_pos =idx +4

            in_place_count +=1
            print(f"  [IN-PLACE ] VA 0x{va :08x} (len {len(ru_bytes ):2d}/{orig_len :2d}): {repr(ru_text )}")
        else :
            new_va =pool_cursor_va
            new_foff =pool_cursor_foff
            exe[new_foff :new_foff +len(ru_bytes )+1 ]=ru_bytes +b"\x00"
            step =(len(ru_bytes )+4 )&~3
            pool_cursor_foff +=step
            pool_cursor_va +=step

            new_ptr =struct.pack("<I",new_va )
            refs_updated =0
            search_pos =0
            while True :
                idx =exe.find(old_ptr ,search_pos ,0x16AF000 )
                if idx ==-1 :
                    break
                exe[idx :idx +4 ]=new_ptr
                if patch_push_length_near_ref(exe ,idx ,orig_len ,len(ru_bytes )):
                    len_pushes_patched +=1
                refs_updated +=1
                search_pos =idx +4

            if va !=0x0079557C :
                assert refs_updated >0 ,f"No references found for relocated string VA 0x{va :08x}"
            exe[foff :foff +orig_len +1 ]=ru_bytes[:orig_len ]+b"\x00"
            relocated_count +=1
            total_refs_patched +=refs_updated
            print(f"  [RELOCATED] VA 0x{va :08x} -> 0x{new_va :08x} ({refs_updated } refs, len {len(ru_bytes ):2d}>{orig_len :2d}): {repr(ru_text )}")

    options_ui_x_patches = [
        (0x5CA07, 199, 180),
        (0x5CA28, 199, 180),
        (0x5CA46, 283, 240),
        (0x5CA64, 284, 240),
    ]
    for off, old_x, new_x in options_ui_x_patches:
        cur_x = struct.unpack("<I", exe[off:off + 4])[0]
        assert cur_x == old_x, f"Expected {old_x} at 0x{off:x}, got {cur_x}"
        exe[off:off + 4] = struct.pack("<I", new_x)

    for off in(0x5CC59, 0x5CD33, 0x5CE0D, 0x5CEF2):
        assert exe[off] == 0xB9 and exe[off + 5:off + 7] == b"\x2b\xc8"
        exe[off:off + 7] = b"\xb9" + struct.pack("<I", 115) + b"\x90\x90"

    os.makedirs(os.path.dirname(OUT_EXE ),exist_ok =True )
    with open(OUT_EXE ,"wb")as f :
        f.write(exe )

    print(f"\nSummary: {in_place_count } in-place, {relocated_count } relocated({total_refs_patched } ptrs, {len_pushes_patched } push-lengths updated).")

if __name__ =="__main__":
    main()
