import json
import os
import re
import sys

sys.stdout.reconfigure(encoding ="utf-8")
sys.path.insert(0 ,os.path.dirname(os.path.abspath(__file__ )))
from translations.part1_plants import PLANTS_TRANSLATIONS
from translations.part2_zombies import ZOMBIES_TRANSLATIONS
from translations.part3_other_keys import OTHER_TRANSLATIONS

def has_cjk(text :str )->bool :
    return any(0x4E00 <=ord(c )<=0x9FFF or 0x3000 <=ord(c )<=0x303F or 0xFF00 <=ord(c )<=0xFFEF for c in text )

def extract_tags(text :str ):
    return re.findall(r"\{[A-Za-z0-9_]+\}",text )

def normalize_for_russian_ttf(text :str )->str :

    return(
    text.replace("«",'"')
    .replace("»",'"')
    .replace("“",'"')
    .replace("”",'"')
    .replace("„",'"')
    .replace("—","-")
    .replace("–","-")
    .replace("№","#")
    .replace("…","...")
    )

def main():
    with open("build/strings/waste_entries_ordered.json","r",encoding ="utf-8")as f :
        waste_entries =json.load(f )

    with open("build/rus_reference/rus_lawnstrings_full.json","r",encoding ="utf-8")as f :
        rus_ref =json.load(f )

    combined ={}
    combined.update(PLANTS_TRANSLATIONS )
    combined.update(ZOMBIES_TRANSLATIONS )
    combined.update(OTHER_TRANSLATIONS )

    missing_keys =[]
    cjk_leaks =[]
    tag_mismatches =[]
    cp1251_errors =[]

    out_lines =[]
    translated_count =0
    from_custom_dict =0
    from_rus_ref =0

    for clean_key ,raw_key ,zh_val in waste_entries :
        if clean_key in combined :
            ru_val =combined[clean_key ]
            from_custom_dict +=1
        elif clean_key in rus_ref :
            ru_val =rus_ref[clean_key ]
            from_rus_ref +=1
        else :
            missing_keys.append(clean_key )
            continue

        ru_val =normalize_for_russian_ttf(ru_val )
        ru_val =ru_val.replace("\r\n","\n").replace("\r","\n").replace("\n","\r\n")

        if has_cjk(ru_val ):
            cjk_leaks.append((clean_key ,ru_val ))

        zh_full =(raw_key[len(clean_key ):]if raw_key.startswith(clean_key )else "")+"\n"+zh_val
        zh_tags =set(extract_tags(zh_full ))
        ru_tags =set(extract_tags(ru_val ))
        formatting_tags ={"{SHORTLINE}","{KEYWORD}","{STAT}","{FLAVOR}","{NOCTURNAL}","{AQUATIC}","{KEYMETAL}","{METAL}"}
        zh_dynamic =zh_tags -formatting_tags
        ru_dynamic =ru_tags -formatting_tags
        if zh_dynamic !=ru_dynamic :
            tag_mismatches.append((clean_key ,sorted(zh_dynamic ),sorted(ru_dynamic )))

        try :
            encoded =ru_val.encode("cp1251")
            if b"\x9f"in encoded :
                cp1251_errors.append((clean_key ,"Contains reserved 0x9F byte"))
        except UnicodeEncodeError as e :
            cp1251_errors.append((clean_key ,str(e )))

        out_lines.append(f"[{clean_key }]\r\n{ru_val }\r\n")
        if raw_key !=clean_key and raw_key.strip()==clean_key :
            out_lines.append(f"[{raw_key }]\r\n{ru_val }\r\n")

        translated_count +=1

    print(f"Total entries processed: {translated_count } / {len(waste_entries )}")
    print(f"  From custom Waste RU translations: {from_custom_dict }")
    print(f"  From official PvZ RU reference:    {from_rus_ref }")
    print(f"Missing keys:    {len(missing_keys )}")
    print(f"CJK leaks:       {len(cjk_leaks )}")
    print(f"Tag mismatches:  {len(tag_mismatches )}")
    print(f"CP1251 errors:   {len(cp1251_errors )}")

    if missing_keys or cjk_leaks or tag_mismatches or cp1251_errors :
        sys.exit(1 )

    full_text ="\r\n".join(out_lines )
    os.makedirs("build/strings",exist_ok =True )
    with open("build/strings/LawnStrings_ru_utf8.txt","w",encoding ="utf-8",newline ="")as f :
        f.write(full_text )

    target_pak_path ="build/unpacked_pak/properties/LawnStrings.txt"
    with open(target_pak_path ,"wb")as f :
        f.write(full_text.encode("cp1251"))

    print(f"Successfully wrote {target_pak_path } ({os.path.getsize(target_pak_path ):,} bytes in CP1251)")

if __name__ =="__main__":
    main()
