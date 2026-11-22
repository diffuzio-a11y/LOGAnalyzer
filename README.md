# LOGAnalyzer – FCT Log Analysis

**Készítette:** Fekete Róbert

**Intézmény:** Dunaújvárosi Egyetem

**Szakirány:** Mérnökinformatikus

**Tantárgy:** Szkriptnyelvek

**Programozási nyelv:** Python

## A projekt bemutatása

A LOGAnalyzer egy Python nyelven, Tkinter grafikus felülettel készített alkalmazás, amely FCT (Functional Circuit Test) gyártási tesztlogfájlok feldolgozására és elemzésére szolgál.

A program célja, hogy a TXT-formátumú logfájlokból kimutassa a sikeres (OK) és sikertelen (NOK) tesztek számát, összesítse a hibakódokat, valamint meghatározza a három leggyakrabban előforduló hibát.

Az alkalmazás napi jelentések készítésére, korábbi elemzések visszakeresésére és kiválasztott időszakok hibastatisztikáinak összehasonlítására is alkalmas.

## Főbb funkciók

- TXT-logfájlok beolvasása és feldolgozása
- OK és NOK eredmények összesítése
- Hibakódok darabszámának meghatározása
- TOP 3 hibakód megjelenítése
- Hibamegnevezések betöltése CSV-fájlból
- Egyedi logfájlok megnyitása és tartalmuk megtekintése
- Napi elemzések kézi mentése JSON-formátumban
- Korábbi napi jelentések megnyitása
- Mentési előzmények táblázatos megjelenítése
- Időszakos TOP 3 elemzés kezdő és záró dátum alapján
- Grafikus felület és eseménykezelés

## Felhasznált Python-modulok

**os - Fájlok és mappák kezelésére, elérési utak összeállítására és ellenőrzésére szolgál.**

Példák: `os.listdir()`, `os.path.join()`, `os.path.isfile()`, `os.path.isdir()`, `os.makedirs()`.

**json - A program a JSON-formátumot a beállítások és napi elemzések tárolására használja.**

Három alkalmazott függvénye:

- `json.load()` – JSON-adatok beolvasása fájlból
- `json.dump()` – Python-adatok mentése JSON-fájlba
- `json.dumps()` – Python-adatok JSON-formátumú szöveggé alakítása

**fr_log_analyzer – saját modul**

A logfájlok feldolgozását, a hibakódok összesítését, a napi mentéseket és az időszakos elemzést végzi.

**További modulok:** `tkinter`, `csv`, `datetime`, `calendar`.

## Saját függvények

A saját modul fontosabb függvényei:

- `FR_logfajlok_keresese()` – TXT-fájlok keresése
- `FR_log_adatok_kinyerese()` – adatok kinyerése a logfájl tartalmából
- `FR_osszes_log_beolvasasa()` – logfájlok feldolgozása
- `FR_hibanevek_betoltese()` – hibamegnevezések betöltése
- `FR_napi_mentes()` – napi elemzés mentése
- `FR_mentesek_betoltese()` – korábbi mentések beolvasása
- `FR_idoszakos_top3()` – időszakos hibastatisztika készítése

## Saját osztály

**FR_LogElemzo**

Az osztály a feldolgozott logadatok alapján kiszámítja az OK/NOK darabszámokat, összesíti a hibakódokat és meghatározza a TOP 3 hibát.

Fontosabb metódusai:

- `FR_ok_darabszam()`
- `FR_nok_darabszam()`
- `FR_hibakodok_osszesitese()`
- `FR_top3_hiba()`

## A program indítása

1. A projekt megnyitása PyCharmban vagy más Python-fejlesztőkörnyezetben.
2. A `main.py` futtatása.
3. A „Logfájlok ellenőrzése” gombbal a TXT-logfájlokat tartalmazó mappa kiválasztása.
4. Az eredmények megtekintése a grafikus felületen.
5. Szükség esetén a napi elemzés mentése vagy korábbi jelentések megnyitása.

A program Python szabványos könyvtári modulokat használ, külön külső Python-csomag telepítése nem szükséges.

## Projektfájlok

- `main.py` – grafikus felület és eseménykezelés
- `fr_log_analyzer.py` – saját elemző modul és osztály
- `errors.csv` – hibakódok és megnevezések (a teszteléshez használt hibakódokat és azok megnevezéseit tartalmazó fájl).
- `LOGAnalyzer.png` – alkalmazásikon
- `settings.json` – legutóbb használt mappa beállítása
- `Napi_mentesek/` – a napi elemzések JSON-állományai

## Megjegyzés

Az időszakos TOP 3 számítás az egy naphoz tartozó több mentés közül a legutolsót veszi figyelembe, hogy ugyanazokat az eredményeket ne számolja többször.

A projekt egyetemi beadandó feladatként készült. Működését tesztlogfájlokkal ellenőriztem, azonban valós gyártási környezetben még nem került tesztelésre.