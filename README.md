# Recepti

Pri predmetu Programiranje 1 sem pripravila projekt na temo analiza podatkov. Vir podatkov je spletna stran [kulinarika.net](https://www.kulinarika.net/recepti/seznam/?besede=&ImeRecepta=&crka=&Avtor=&as_values_sestavine=&kategorija=7&kategorija1=&priloznost=%25&priprava=%25&cas=0&slika=0&datum_kriterij=objava&datumi=vsi&datumod=&datumdo=&receptisplosno=Iskanje&sort=datum&nacin=desc).

## O projektu
Omejila sem se na kategorijo mesnih jedi, ki vsebuje pribli�no 1800 receptov. Od vsakega recepta sem uporabila naslednje podatke: ime jedi, avtor, vrsta, �as priprave, zahtevnost, �tevilo porcij in datum objave. Vsebina vseh receptov ni popolna, saj nekateri podatki manjkajo ali pa so zapisani nestrukturirano in bi jih bilo te�ko vklju�ili v analizo.
Ugotavljala sem porazdelitev �tevila receptov po letih, najpogostej�e vrste jedi, najaktivnej�e avtorje, povezave med zahtevnostjo, �tevilom porcij, �asom priprave in vrsto ter iz imena jedi poskusila napovedati vrsto.

## Vsebina repozitorija
Datoteka *p2.py* zbere podatke s spletne strani, jih uredi in vrne csv datoteko urejenih podatkov, ki jih uporabimo v analizi. Datoteka *Untitled.ipynb* vsebuje celotno analizo.