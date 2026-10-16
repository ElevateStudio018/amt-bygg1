# AMT Bygg – webbplats

Statisk webbplats för AMT Bygg (amtgroup.se). Ingen server eller databas krävs – alla filer kan laddas upp till valfritt webbhotell (Netlify, Vercel, GitHub Pages, Loopia, One.com m.fl.).

## Bygga

```bash
python3 src/build.py           # skriver sidorna till repots rot
python3 -m http.server 8000    # förhandsvisa på http://localhost:8000
```

Kräver Python 3 med Pillow (för bildmått). `python3 src/patterns.py` genererar om mönsterbiblioteket.

## Struktur

| Sökväg | Innehåll |
| --- | --- |
| `src/pages/*.html` | Sidornas innehåll (redigera här, inte i de byggda filerna) |
| `src/build.py` | Sidmall, meny, sidfot, klienter, partners, ramavtal och kontaktuppgifter |
| `src/patterns.py` | Materialmönster i loggans färger: träådring, fiskben, regelverk, tegel, snitt, rutnät |
| `assets/` | CSS, JS, typsnitt (lokalt hostade), bilder, logotyper, vCard |

Klienter, partners och försäkringsbolag läggs till i listorna `CLIENTS`, `PARTNERS` och `INSURERS` i `src/build.py` (logotyp i `assets/logos/<id>.png`).

## Formulär

Formulären öppnar idag ett förifyllt mejl till amtbygg@amtgroup.se. För att skicka direkt från sidan, sätt `FORM_ENDPOINT_CONTACT` och `FORM_ENDPOINT_DAMAGE` i `src/build.py` till t.ex. en Formspree-URL och bygg om.

## Omdirigering

Gamla adressen `/skadereparation` pekar vidare till `/anmal-skada/`.

## Typsnitt och bilder

Rubriker, meny och etiketter använder Montserrat (SIL Open Font License), som ligger närmast loggans geometriska bokstäver. Brödtext är Hanken Grotesk. Båda ligger lokalt i `assets/fonts/`.

Bilderna `goteborg-*` och `bygg-arbetsplats` kommer från Unsplash (fri att använda kommersiellt, ingen attribuering krävs):

| Fil | Fotograf |
| --- | --- |
| `goteborg-kranar`, `goteborg-hamn` | Dmitrii E. |
| `goteborg-eriksberg` | Jeet Datta |
| `bygg-arbetsplats` | Glenov Brankovic |

Startsidans film (`assets/video/hero-stad-*.mp4`, stillbild `assets/img/hero-stad-poster.jpg`) är Mixkit-klipp 4010 under Mixkit License (fri att använda kommersiellt). Den är komprimerad med ffmpeg (H.264, CRF 31, utan ljud): 1600 px för dator och 960 px för mobil.
