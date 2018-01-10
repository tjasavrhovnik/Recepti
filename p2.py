import math
import csv
import json
import re
import requests
import os


re_bloka = re.compile(
    r"<a href='/recepti/(?P<id>\d+).*?objavljeno.*?</p>"
    ,
    flags=re.DOTALL
    )

vzorec = re.compile(
    r"single-line.*?Objava recepta.*?'>"
    r'(?P<jed>.*?)' #jed
    r'</a>'
    r'.*?'
    r"<p class='objava no-mobile-640'>objavljeno: "
    r'(?P<datum>.*?)' #datum
    r'</p>'
    ,
    flags=re.DOTALL
    )

re_kolicine = re.compile(
    r"<p class='kolicina no-mobile-640'>.*?: (?P<kolicina>.*?)</p>"
    ,
    flags=re.DOTALL
    )

re_tezavnosti = re.compile(
    r"<p class='tezavnost'>(?P<tezavnost>.*?)</p>"
    ,
    flags=re.DOTALL
    )

re_casa = re.compile(
    r"<span class='cas'>(?P<cas>.*?)</span>"
    ,
    flags=re.DOTALL
    )

re_vrste = re.compile(
    r"<p class='kategorija no-mobile-640'>mesne jedi: (?P<vrsta>.*?)</p>"
    ,
    flags=re.DOTALL
    )

re_avtorja = re.compile(
    r"href='/uporabniki.*?>(?P<avtor>.*?)</a>"
    ,
    flags=re.DOTALL
    )

def leto(niz):
    niz = niz.strip().split('.')
    return int(niz[2])

def minut_priprave(niz):
    niz = niz.strip().split(' ')
    if niz[0].isdigit():
        stevilo = int(niz[0])
        if stevilo // 10 >= 1:
            minute = stevilo
        else:
            minute = 60 * stevilo
    else:
        minute = 60 * int(niz[0][0])
    return minute

#kolicina enakomerno
def st_oseb(niz):
    niz = niz.strip().split(' ')
    if len(niz) == 1:
        if niz[0].isdigit():
            return int(niz[0])
        elif '-' in niz[0]:
            niz = niz[0].split('-')
            niz1, niz2 = niz[0], niz[-1]
            if niz1.isdigit() and niz2.isdigit():
                return math.ceil((int(niz1) + int(niz2)) / 2)
    pravi = ['oseba', 'osebo', 'osebi', 'osebe', 'oseb', 'OSEBE', 'OSEB',
             'jedce', 'ljudi', 'ljudje', 'lačna', 'lačne',
             'porcij', 'porcije', 'kos', 'kosov', 'KOSOV']
    opisno = ['eno', 'dve', 'tri', 'štiri', 'pet',
              'šest', 'sedem', 'osem', 'devet', 'deset']
    if niz[-1] in pravi:
        if niz[-2].isdigit():
            return int(niz[-2])
        elif '-' in niz[-2]:
            niz = niz[-2].split('-')
            niz1, niz2 = niz[0], niz[-1]
            if niz1.isdigit() and niz2.isdigit():
                return math.ceil((int(niz1) + int(niz2)) / 2)
        elif niz[-2] in opisno:
            return opisno.index(niz[-2]) + 1
    else:
        return None

def podatki(blok):
    ujemanje = vzorec.search(blok)
    if ujemanje:
        jed = ujemanje.groupdict()

        tezavnost_match = re_tezavnosti.search(blok)
        jed['tezavnost'] = tezavnost_match.groupdict()['tezavnost']
        zahtevnost = 10
        for i in jed['tezavnost'].strip():
            if i == '-':
                zahtevnost -= 1
        jed['zahtevnost'] = zahtevnost
        del jed['tezavnost']
            
        kolicina_match = re_kolicine.search(blok)
        if kolicina_match is None:
            jed['kolicina'] = None
        else:
            jed['kolicina'] = kolicina_match.groupdict()['kolicina']

        cas_match = re_casa.search(blok)
        if cas_match is None:
            jed['cas'] = None
        else:
            jed['cas'] = cas_match.groupdict()['cas']

        vrsta_match = re_vrste.search(blok)
        if vrsta_match is None:
            jed['vrsta'] = None
        else:
            jed['vrsta'] = vrsta_match.groupdict()['vrsta']

        avtor_match = re_avtorja.search(blok)
        if avtor_match is None:
            jed['avtor'] = None
        else:
            jed['avtor'] = avtor_match.groupdict()['avtor']

        jed['leto'] = leto(jed['datum'])

        jed['cas priprave [min]'] = minut_priprave(jed['cas']) if jed['cas'] else None
        del jed['cas']

        jed['st. porcij'] = st_oseb(jed['kolicina']) if jed['kolicina'] else None
            
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


def zapisi_json(podatki, ime_datoteke):
    with open(ime_datoteke, 'w') as datoteka:
        json.dump(podatki, datoteka, indent=2)

def zapisi_csv(podatki, polja, ime_datoteke):
    with open(ime_datoteke, 'w') as datoteka:
        pisalec = csv.DictWriter(datoteka, polja, extrasaction='ignore')
        pisalec.writeheader()
        for podatek in podatki:
            pisalec.writerow(podatek)

#shrani_jedi_v_imenik('test', 2, 2)
#shrani_jedi_v_imenik('jedi')
jedi = preberi_iz_imenika('jedi')

zapisi_json(jedi, 'jedi.json')
polja = [
    'jed', 'vrsta', 'cas priprave [min]', 'zahtevnost', 'kolicina',
    'st. porcij', 'avtor', 'datum', 'leto',
    ]

zapisi_csv(jedi, polja, 'jedi.csv')
