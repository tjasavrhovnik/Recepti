import re
import requests
import os

odlomek = """<a href='/recepti/21479/mesne-jedi/mehiska-tortilja/'
title='Objava recepta: 20.10.2017<br>Število fotografij: 1'>
<img src='/slikerecepti/21479/1-200x150.jpg'>
</a></div><h3 class='single-line'>
<a href='/recepti/21479/mesne-jedi/mehiska-tortilja/'
title='Objava recepta: 20.10.2017<br>Število fotografij: 1'>Mehiška tortilja</a>
</h3><div class='recept_vsebina1'>
<p class='tezavnost'>
<img src='/grafika6/ikona-utez.png' alt='Zahtevnost' title='zahtevnost'>
<img src='/grafika6/ikona-utez.png' alt='Zahtevnost' title='zahtevnost'>
<img src='/grafika6/ikona-utez-prazna.png' alt='Zahtevnost' title='zahtevnost'>
<img src='/grafika6/ikona-utez-prazna.png' alt='Zahtevnost' title='zahtevnost'>
<img src='/grafika6/ikona-utez-prazna.png' alt='Zahtevnost' title='zahtevnost'>
</p><p class='cas'><img class='ura' src='/grafika6/ikona-ura.png'
title='30 minut' /><span class='cas'>30 minut</span></p>
<p class='kolicina no-mobile-640'>količina: za 3 porcije</p>
</div><div class='recept_vsebina2'><span class='avtor'>
<a class='username' href='/uporabniki/seznam/rbj897zs2mnenu6i/'>Schär</a>
&#160;</span><p class='kategorija no-mobile-640'>mesne jedi: govedina</p>
<p class='objava no-mobile-640'>objavljeno: 20.10.2017</p>
</div></article><article class='en_recept'><div class='image-wrap'>
<a href='/recepti/21418/mesne-jedi/piscancja-rizota-s-korenjem/'
title='Objava recepta: 31.8.2017<br>Število mnenj: 5<br>Število fotografij: 1'>
<img src='/slikerecepti/21418/1-200x150.jpg'></a></div><h3 class='single-line'>
<a href='/recepti/21418/mesne-jedi/piscancja-rizota-s-korenjem/'
title='Objava recepta: 31.8.2017<br>Število mnenj: 5<br>
Število fotografij: 1'>Piščančja rižota s korenjem</a></h3>
<div class='recept_vsebina1'><p class='tezavnost'>
<img src='/grafika6/ikona-utez.png' alt='Zahtevnost' title='zahtevnost'>
<img src='/grafika6/ikona-utez.png' alt='Zahtevnost' title='zahtevnost'>
<img src='/grafika6/ikona-utez-prazna.png' alt='Zahtevnost' title='zahtevnost'>
<img src='/grafika6/ikona-utez-prazna.png' alt='Zahtevnost' title='zahtevnost'>
<img src='/grafika6/ikona-utez-prazna.png' alt='Zahtevnost' title='zahtevnost'>
</p><p class='cas'><img class='ura' src='/grafika6/ikona-ura.png'
title='45 minut' /><span class='cas'>45 minut</span></p>
<p class='kolicina no-mobile-640'>količina: za eno osebo</p></div>
<div class='recept_vsebina2'><span class='avtor'>
<img class='spol' src='/grafika6/ikona-spol-brez.png'
title='spol ni določen oz. marsovec'><a class='username'
href='/uporabniki/seznam/baterija/'>baterija</a>&#160;</span>
<p class='kategorija no-mobile-640'>mesne jedi: perutnina</p>
<p class='objava no-mobile-640'>objavljeno: 31.8.2017</p>"""

re_bloka = re.compile(
    #r"<a href='/recepti/(?P<id>\d+).*?'.*?objavljeno.*?</p>"
    r"<a href='/recepti/(?P<id>\d+).*?objavljeno.*?</p>"
    ,
    flags=re.DOTALL
    )

vzorec = re.compile(
    r"<a href='/recepti/\d+/mesne-jedi/(?P<ime>.*?)/" #ime
    #r"<h3 class='single-line'>"
    #r'.*?'
    #r'Število fotografij.*?>'
    #r'(?P<ime>.*?)' #ime
    #r'</a>'
    r'.*?'
    r"<span class='cas'>"
    r'(?P<cas>.*?)' #cas
    r'</span>'
    r'.*?'
    r"(<p class='kolicina no-mobile-640'>količina: )?"
    r'(?P<kolicina>.*?)?' #kolicina ne nastopi vedno
    r'</p>'
    r'.*?'
    r"href='/uporabniki.*?>"
    r'(?P<avtor>.*?)' #avtor
    r'</a>'
    r'.*?'
    r"<p class='kategorija no-mobile-640'>mesne jedi: "
    r'(?P<vrsta>.*?)' #vrsta
    r'</p>'
    r'.*?'
    r"<p class='objava no-mobile-640'>objavljeno: "
    r'(?P<datum>.*?)' #datum
    r'</p>'
    ,
    flags=re.DOTALL
    )

for ujemanje in vzorec.finditer(odlomek):
    print(ujemanje.groupdict())

def podatki(blok):
    ujemanje = vzorec.search(blok)
    if ujemanje:
        jed = ujemanje.groupdict()
        return jed
    else:
        print('napaka')
        print(blok)

def shrani_jedi_v_imenik(imenik, stevilo_strani=141, stevilo_jedi_na_stran=12):
    os.makedirs(imenik, exist_ok=True)
    for stevilka_strani in range(1, stevilo_strani + 1):
        naslov_strani = (
            'https://www.kulinarika.net/recepti/seznam/?'
            'ImeRecepta=&'
            'Avtor=&'
            'datumod=&'
            'datumdo=&'
            'besede=&'
            'crka=&'
            'priprava=%25&'
            'slika=0&'
            'as_values_sestavine=&'
            'kategorija=7&kategorija1=&priloznost=%25&'
            'receptisplosno=Iskanje&'
            'sort=datum&'
            'cas=0&'
            'nacin=desc&'
            'datum_kriterij=objava&'
            'datumi=vsi&'
            'offset={}'
        ).format((stevilka_strani - 1) * 12)
        stran = requests.get(naslov_strani)
        ime_datoteke = 'stran-{}.html'.format(stevilka_strani)
        cela_pot = os.path.join(imenik, ime_datoteke)
        with open(cela_pot, 'w', encoding='utf-8') as datoteka:
            datoteka.write(stran.text)

def preberi_iz_imenika(imenik):
    jedi = []
    for ime_datoteke in os.listdir(imenik):
        cela_pot = os.path.join(imenik, ime_datoteke)
        with open(cela_pot) as datoteka:
            vsebina_datoteke = datoteka.read()
            for blok in re_bloka.finditer(vsebina_datoteke):
                jedi.append(podatki(blok.group(0)))
    return jedi

#shrani_jedi_v_imenik('test', 2, 2)
preberi_iz_imenika('test')
