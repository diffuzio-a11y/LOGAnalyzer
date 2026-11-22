
import os
import csv
import json
from datetime import datetime, date


def FR_logfajlok_keresese(mappa):
    fajlok = []

    if os.path.isdir(mappa):
        for nev in os.listdir(mappa):
            utvonal = os.path.join(mappa, nev)

            if os.path.isfile(utvonal) and nev.lower().endswith(".txt"):
                fajlok.append(utvonal)

    return sorted(fajlok)


def FR_log_adatok_kinyerese(tartalom):
    adatok = {}

    for sor in tartalom.splitlines():
        if ":" in sor:
            kulcs, ertek = sor.split(":", 1)
            adatok[kulcs.strip()] = ertek.strip()

    return adatok


def FR_osszes_log_beolvasasa(mappa):
    osszes_adat = []

    for utvonal in FR_logfajlok_keresese(mappa):
        with open(utvonal, "r", encoding="utf-8-sig") as fajl:
            adatok = FR_log_adatok_kinyerese(fajl.read())
            osszes_adat.append(adatok)

    return osszes_adat


def FR_hibanevek_betoltese(fajlnev):
    hibanevek = {}

    with open(fajlnev, "r", encoding="utf-8-sig", newline="") as fajl:
        adatok = csv.DictReader(fajl)

        for adat in adatok:
            hibanevek[adat["hibakod"]] = adat["megnevezes"]

    return hibanevek


class FR_LogElemzo:
    def __init__(self, adatok):
        self.adatok = adatok

    def FR_ok_darabszam(self):
        darab = 0

        for adat in self.adatok:
            if adat.get("Result") == "OK":
                darab += 1

        return darab

    def FR_nok_darabszam(self):
        darab = 0

        for adat in self.adatok:
            if adat.get("Result") == "NOK":
                darab += 1

        return darab

    def FR_hibakodok_osszesitese(self):
        hibakodok = {}

        for adat in self.adatok:
            if adat.get("Result") == "NOK":
                kod = adat.get("ErrorCode", "")

                if kod != "":
                    if kod in hibakodok:
                        hibakodok[kod] += 1
                    else:
                        hibakodok[kod] = 1

        return hibakodok

    def FR_top3_hiba(self):
        hibakodok = self.FR_hibakodok_osszesitese()

        rendezett = sorted(
            hibakodok.items(),
            key=lambda adat: (-adat[1], adat[0])
        )

        return rendezett[:3]


def FR_napi_mentes(
    mappa,
    log_darab,
    ok_darab,
    nok_darab,
    hibakodok,
    hibanevek
):
    os.makedirs(mappa, exist_ok=True)

    most = datetime.now()
    datum = most.date().isoformat()
    idopont = most.isoformat(timespec="seconds")

    rendezett = sorted(
        hibakodok.items(),
        key=lambda adat: (-adat[1], adat[0])
    )

    top3 = []

    for kod, darab in rendezett[:3]:
        top3.append({
            "hibakod": kod,
            "darab": darab,
            "megnevezes": hibanevek.get(
                kod,
                "Ismeretlen hiba"
            )
        })

    adatok = {
        "datum": datum,
        "mentes_idopontja": idopont,
        "het": most.date().isocalendar().week,
        "logfajlok": log_darab,
        "OK": ok_darab,
        "NOK": nok_darab,
        "top3": top3,
        "osszes_hibakod": hibakodok
    }

    json_szoveg = json.dumps(
        adatok,
        ensure_ascii=False,
        indent=4
    )

    sorszam = 1

    while True:
        fajlnev = f"TOP3_{datum}_{sorszam:03d}.json"
        utvonal = os.path.join(mappa, fajlnev)

        try:
            with open(
                utvonal,
                "x",
                encoding="utf-8"
            ) as fajl:
                fajl.write(json_szoveg)

            return utvonal

        except FileExistsError:
            sorszam += 1


def FR_mentesek_betoltese(mappa):
    mentesek = []

    if not os.path.isdir(mappa):
        return mentesek

    for fajlnev in sorted(os.listdir(mappa)):
        if not fajlnev.lower().endswith(".json"):
            continue

        utvonal = os.path.join(mappa, fajlnev)

        if not os.path.isfile(utvonal):
            continue

        with open(
            utvonal,
            "r",
            encoding="utf-8"
        ) as fajl:
            adatok = json.load(fajl)

        date.fromisoformat(adatok["datum"])

        adatok["fajlnev"] = fajlnev
        mentesek.append(adatok)

    mentesek.sort(
        key=lambda adat: (
            adat["datum"],
            adat["fajlnev"]
        )
    )

    return mentesek


def FR_idoszakos_top3(mentesek, kezdet, veg):
    napi_mentesek = {}

    for mentes in mentesek:
        datum = mentes["datum"]

        if kezdet <= datum <= veg:
            napi_mentesek[datum] = mentes

    osszes_hibakod = {}

    for mentes in napi_mentesek.values():
        hibakodok = mentes["osszes_hibakod"]

        for kod, darab in hibakodok.items():
            if kod in osszes_hibakod:
                osszes_hibakod[kod] += darab
            else:
                osszes_hibakod[kod] = darab

    rendezett = sorted(
        osszes_hibakod.items(),
        key=lambda adat: (-adat[1], adat[0])
    )

    return rendezett[:3], len(napi_mentesek)
