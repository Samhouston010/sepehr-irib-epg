# -*- coding: utf-8 -*-
import json, urllib.request, csv, io

def dl(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"}), timeout=30).read().decode("utf-8")

logos = {}
for row in csv.DictReader(io.StringIO(dl("https://raw.githubusercontent.com/iptv-org/database/master/data/logos.csv"))):
    c,u = row.get("channel",""), row.get("url","")
    if c and u and (c not in logos or u.endswith(".png")): logos[c]=u

TW = "https://static.televebion.net/web/content_images/channel_images/thumbs/new/240/v4/{}.png"

main = [
 ("tv1",31,"IRIB1.ir","شبکه یک","سراسری"),("tv2",32,"IRIB2.ir","شبکه دو","سراسری"),
 ("tv3",36,"IRIB3.ir","شبکه سه","سراسری"),("tv4",37,"IRIB4.ir","شبکه چهار","سراسری"),
 ("tehran",38,"TehranTV.ir","شبکه پنج (تهران)","سراسری"),("varzesh",39,"VarzeshTV.ir","شبکه ورزش","ورزشی"),
 ("ofogh",40,"OfoghTV.ir","شبکه افق","سراسری"),("amouzesh",41,"AmouzeshTV.ir","شبکه آموزش","سراسری"),
 ("irinn",42,"IRINN.ir","شبکه خبر","خبری"),("nasim",43,"Nasim.ir","شبکه نسیم","سرگرمی"),
 ("namayesh",44,"NamayeshTV.ir","شبکه نمایش","سرگرمی"),("mostanad",45,"IRIBMostanad.ir","شبکه مستند","مستند"),
 ("ifilm",46,"iFilmPersian.ir","آی‌فیلم","سرگرمی"),("quran",47,"","شبکه قرآن","مذهبی"),
 ("salamat",48,"SalamatTV.ir","شبکه سلامت","سراسری"),("pooya",49,"PooyaTV.ir","شبکه پویا","کودک"),
 ("omid",50,"IRIBOmid.ir","شبکه امید","سرگرمی"),("sepehr",51,"SepehrTV.ir","شبکه سپهر","سرگرمی"),
 ("irinn2",52,"IRINN2.ir","شبکه خبر ۲","خبری"),("faratar",53,"IRIBUHD.ir","شبکه فراتر (UHD)","سراسری"),
 ("tamasha",54,"Tamasha.ir","شبکه تماشا","سرگرمی"),
]

prov = [
 ("abadan","AbadanTV.ir","شبکه آبادان"),("aflak","AflakTV.ir","شبکه افلاک (لرستان)"),
 ("aftab","AftabTV.ir","شبکه آفتاب (مرکزی)"),("alborz","AlborzTV.ir","شبکه البرز"),
 ("ara","AraTV.ir","شبکه آرا (چهارمحال)"),("atrak","AtrakTV.ir","شبکه اترک (خراسان شمالی)"),
 ("azarbayjangharbi","WestAzerbaijanTV.ir","شبکه آذربایجان غربی"),("baran","BaranTV.ir","شبکه باران (گیلان)"),
 ("bushehr","BoushehrTV.ir","شبکه بوشهر"),("dena","DenaTV.ir","شبکه دنا (کهگیلویه)"),
 ("eshragh","EshraghNetwork.ir","شبکه اشراق (زنجان)"),("fars","FarsTV.ir","شبکه فارس"),
 ("hamoon","HamoonTV.ir","شبکه هامون (سیستان)"),("sina","HamedanTV.ir","شبکه همدان (سینا)"),
 ("ilam","IlamTV.ir","شبکه ایلام"),("iraneman","Iraneman.ir","شبکه ایران‌من"),
 ("esfahan","IsfahanTV.ir","شبکه اصفهان"),("jahanbin","JahanbinTV.ir","شبکه جهان‌بین"),
 ("karoon","KaroonTV.ir","شبکه کارون"),("kerman","KermanTV.ir","شبکه کرمان"),
 ("khalijefars","KhalijeFarsTV.ir","شبکه خلیج فارس (هرمزگان)"),("khavaran","KhavaranTV.ir","شبکه خاوران (خراسان جنوبی)"),
 ("khorasanrazavi","KhorasanRazaviTV.ir","شبکه خراسان رضوی"),("khoozestan","KhozestanTV.ir","شبکه خوزستان"),
 ("kish","KishTV.ir","شبکه کیش"),("kordestan","KordestanTV.ir","شبکه کردستان"),
 ("mahabad","MahabadTV.ir","شبکه مهاباد"),("nesfejahan","","شبکه نصف جهان (اصفهان)"),
 ("qazvin","QazvinTV.ir","شبکه قزوین"),("sabalan","SabalanTV.ir","شبکه سبلان (اردبیل)"),
 ("sahand","SahandTV.ir","شبکه سهند (آذربایجان شرقی)"),("sarbedaran","SarbedaranTV.ir","شبکه سبزوار"),
 ("semnan","SemnanTV.ir","شبکه سمنان"),("tabarestan","TabarestanTV.ir","شبکه مازندران (طبرستان)"),
 ("taban","YazdTV.ir","شبکه یزد (تابان)"),("zagros","ZagrosTV.ir","شبکه زاگرس (لرستان)"),
 ("iribu","RoyaTV.ir","شبکه رویا"),
]

out = []
for slug,cid,tvg,name,grp in main:
    out.append({"slug":slug,"channel_id":cid,"tvg_id":tvg,"name":name,"name_en":name,"group":grp,
                "logo":logos.get(tvg,"") or TW.format(slug)})
prov.sort(key=lambda x:x[2])
for slug,tvg,name in prov:
    out.append({"slug":slug,"channel_id":None,"tvg_id":tvg,"name":name,"name_en":name,"group":"استانی",
                "logo":logos.get(tvg,"") or TW.format(slug)})

with open("channels.json","w",encoding="utf-8") as f:
    json.dump(out,f,ensure_ascii=False,indent=2)
print(f"channels.json ساخته شد: {len(out)} کانال")
