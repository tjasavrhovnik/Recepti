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
#shrani_jedi_v_imenik('test2', 10, 12)
#shrani_jedi_v_imenik('test3', 50, 12)
#shrani_jedi_v_imenik('jedi')
#preberi_iz_imenika('test')

jedi = preberi_iz_imenika('jedi')
#print(jedi)

def zapisi_json(podatki, ime_datoteke):
    with open(ime_datoteke, 'w') as datoteka:
        json.dump(podatki, datoteka, indent=2)

def zapisi_csv(podatki, polja, ime_datoteke):
    with open(ime_datoteke, 'w') as datoteka:
        pisalec = csv.DictWriter(datoteka, polja, extrasaction='ignore')
        pisalec.writeheader()
        for podatek in podatki:
            pisalec.writerow(podatek)
