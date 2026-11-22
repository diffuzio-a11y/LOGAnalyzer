
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import json
import calendar
from datetime import date

from fr_log_analyzer import (
    FR_logfajlok_keresese,
    FR_osszes_log_beolvasasa,
    FR_LogElemzo,
    FR_hibanevek_betoltese,
    FR_napi_mentes,
    FR_mentesek_betoltese,
    FR_idoszakos_top3
)

alapmappa = os.path.dirname(os.path.abspath(__file__))
beallitas_fajl = os.path.join(alapmappa, "settings.json")
csv_fajl = os.path.join(alapmappa, "errors.csv")
mentes_mappa = os.path.join(alapmappa, "Napi_mentesek")

sugo = None
aktualis_elemzes = None


def FR_mappa_betoltes():
    if os.path.isfile(beallitas_fajl):
        try:
            with open(beallitas_fajl, "r", encoding="utf-8") as fajl:
                adatok = json.load(fajl)
                mappa = adatok.get("mappa", "")

                if os.path.isdir(mappa):
                    return mappa
        except (OSError, ValueError, TypeError, AttributeError):
            pass

    return ""


def FR_mappa_mentes(mappa):
    try:
        with open(beallitas_fajl, "w", encoding="utf-8") as fajl:
            json.dump({"mappa": mappa}, fajl, indent=4)
    except OSError:
        messagebox.showwarning(
            "LOGAnalyzer",
            "A legutóbbi mappa beállítását nem sikerült menteni."
        )


def FR_hibanevek():
    try:
        return FR_hibanevek_betoltese(csv_fajl)
    except (OSError, UnicodeError, ValueError, KeyError):
        return {}


def FR_ellenorzes():
    global aktualis_elemzes

    mappa = filedialog.askdirectory(
        title="Logfájlokat tartalmazó mappa kiválasztása",
        initialdir=FR_mappa_betoltes() or os.path.expanduser("~")
    )

    if not mappa:
        return

    aktualis_elemzes = None
    mentes_gomb.config(state=tk.DISABLED)
    mentes_felirat.config(text="")

    fajlok = FR_logfajlok_keresese(mappa)

    if len(fajlok) == 0:
        messagebox.showwarning(
            "LOGAnalyzer",
            "A kiválasztott mappában nem találhatók TXT-logfájlok."
        )
        return

    try:
        adatok = FR_osszes_log_beolvasasa(mappa)
        hibanevek = FR_hibanevek_betoltese(csv_fajl)
    except (OSError, UnicodeError, ValueError, KeyError):
        messagebox.showerror(
            "LOGAnalyzer",
            "Nem sikerült beolvasni a logfájlokat vagy az errors.csv fájlt."
        )
        return

    elemzo = FR_LogElemzo(adatok)
    hibakodok = elemzo.FR_hibakodok_osszesitese()

    ok_darab = elemzo.FR_ok_darabszam()
    nok_darab = elemzo.FR_nok_darabszam()

    osszes_felirat.config(text=f"Logfájlok: {len(fajlok)} db")
    ok_felirat.config(text=f"OK: {ok_darab} db")
    nok_felirat.config(text=f"NOK: {nok_darab} db")

    hibakod_lista.delete("1.0", tk.END)
    hibakod_lista.insert(tk.END, "Hibakód       Darab\n\n")

    for kod, darab in sorted(hibakodok.items()):
        hibakod_lista.insert(tk.END, f"{kod:<14}{darab}\n")

    for sor in top3_lista.get_children():
        top3_lista.delete(sor)

    for hely, adat in enumerate(elemzo.FR_top3_hiba(), 1):
        kod = adat[0]
        darab = adat[1]
        nev = hibanevek.get(kod, "Ismeretlen hiba")

        top3_lista.insert(
            "",
            tk.END,
            values=(hely, kod, darab, nev)
        )

    aktualis_elemzes = {
        "mappa": mappa,
        "log_darab": len(fajlok),
        "ok_darab": ok_darab,
        "nok_darab": nok_darab,
        "hibakodok": hibakodok,
        "hibanevek": hibanevek
    }

    FR_mappa_mentes(mappa)

    mentes_gomb.config(state=tk.NORMAL)
    mentes_felirat.config(
        text="Az elemzés elkészült. Az eredmény még nincs elmentve."
    )


def FR_napi_mentes_gomb():
    if aktualis_elemzes is None:
        messagebox.showwarning(
            "LOGAnalyzer",
            "Először végezz el egy logfájl-ellenőrzést!"
        )
        return

    datum = date.today().isoformat()

    valasz = messagebox.askyesno(
        "Napi TOP 3 mentése",
        f"Elmented a jelenlegi elemzést?\n\n"
        f"Dátum: {datum}\n"
        f"Logfájlok: {aktualis_elemzes['log_darab']} db\n"
        f"OK: {aktualis_elemzes['ok_darab']} db\n"
        f"NOK: {aktualis_elemzes['nok_darab']} db\n\n"
        f"A korábbi mentések megmaradnak."
    )

    if not valasz:
        return

    try:
        utvonal = FR_napi_mentes(
            mentes_mappa,
            aktualis_elemzes["log_darab"],
            aktualis_elemzes["ok_darab"],
            aktualis_elemzes["nok_darab"],
            aktualis_elemzes["hibakodok"],
            aktualis_elemzes["hibanevek"]
        )
    except (OSError, ValueError, TypeError):
        messagebox.showerror(
            "LOGAnalyzer",
            "Nem sikerült elmenteni a napi elemzést."
        )
        return

    mentes_felirat.config(
        text=f"Utolsó mentés: {os.path.basename(utvonal)}"
    )

    messagebox.showinfo(
        "LOGAnalyzer",
        f"A napi elemzés sikeresen elmentve!\n\n"
        f"{os.path.basename(utvonal)}"
    )


def FR_beolvasas():
    fajlnev = filedialog.askopenfilename(
        title="Logfájl kiválasztása",
        initialdir=FR_mappa_betoltes() or os.path.expanduser("~"),
        filetypes=[("Logfájlok", "*.txt")]
    )

    if not fajlnev:
        return

    try:
        with open(fajlnev, "r", encoding="utf-8-sig") as fajl:
            tartalom = fajl.read()
    except (OSError, UnicodeError):
        messagebox.showerror(
            "LOGAnalyzer",
            "Nem sikerült beolvasni a kiválasztott logfájlt."
        )
        return

    FR_mappa_mentes(os.path.dirname(fajlnev))

    log_keret.config(
        text=f"Kiválasztott logfájl – {os.path.basename(fajlnev)}"
    )

    log_szoveg.delete("1.0", tk.END)
    log_szoveg.insert(tk.END, tartalom)


def FR_sugo(gomb, szoveg):
    def FR_megjelenites(esemeny):
        global sugo

        if sugo is not None:
            sugo.destroy()

        sugo = tk.Toplevel(gomb)
        sugo.overrideredirect(True)
        sugo.geometry(
            f"+{esemeny.x_root + 15}+{esemeny.y_root + 15}"
        )

        tk.Label(
            sugo,
            text=szoveg,
            bg="#ffffe0",
            relief="solid",
            borderwidth=1,
            padx=8,
            pady=5
        ).pack()

    def FR_elrejtes(esemeny):
        global sugo

        if sugo is not None:
            sugo.destroy()
            sugo = None

    gomb.bind("<Enter>", FR_megjelenites)
    gomb.bind("<Leave>", FR_elrejtes)


def FR_naptar(mezo):
    try:
        aktualis = date.fromisoformat(mezo.get())
    except ValueError:
        aktualis = date.today()

    szulo_ablak = mezo.winfo_toplevel()

    ablak_naptar = tk.Toplevel(szulo_ablak)
    ablak_naptar.title("Dátum kiválasztása")
    ablak_naptar.resizable(False, False)
    ablak_naptar.transient(szulo_ablak)
    ablak_naptar.grab_set()

    ev = tk.IntVar(value=aktualis.year)
    honap = tk.IntVar(value=aktualis.month)

    fejlec = tk.Frame(ablak_naptar)
    fejlec.pack(padx=12, pady=10)

    napok_keret = tk.Frame(ablak_naptar)
    napok_keret.pack(padx=12, pady=(0, 12))

    def FR_nap_valasztas(nap):
        kivalasztott = date(ev.get(), honap.get(), nap)
        mezo.delete(0, tk.END)
        mezo.insert(0, kivalasztott.isoformat())
        ablak_naptar.destroy()

    def FR_naptar_frissites():
        for elem in napok_keret.winfo_children():
            elem.destroy()

        fejlec_szoveg.config(
            text=f"{ev.get()}. {honap.get():02d}."
        )

        napnevek = ["H", "K", "Sz", "Cs", "P", "Sz", "V"]

        for oszlop, nev in enumerate(napnevek):
            tk.Label(
                napok_keret,
                text=nev,
                width=5,
                font=("Arial", 9, "bold")
            ).grid(row=0, column=oszlop)

        hetek = calendar.monthcalendar(ev.get(), honap.get())

        for sor, het in enumerate(hetek, 1):
            for oszlop, nap in enumerate(het):
                if nap != 0:
                    tk.Button(
                        napok_keret,
                        text=str(nap),
                        width=4,
                        command=lambda n=nap: FR_nap_valasztas(n)
                    ).grid(
                        row=sor,
                        column=oszlop,
                        padx=1,
                        pady=1
                    )

    def FR_honap_valtas(irany):
        uj_honap = honap.get() + irany
        uj_ev = ev.get()

        if uj_honap == 0:
            uj_honap = 12
            uj_ev -= 1

        if uj_honap == 13:
            uj_honap = 1
            uj_ev += 1

        if uj_ev < 1 or uj_ev > 9999:
            return

        honap.set(uj_honap)
        ev.set(uj_ev)
        FR_naptar_frissites()

    tk.Button(
        fejlec,
        text="<",
        width=4,
        command=lambda: FR_honap_valtas(-1)
    ).pack(side=tk.LEFT)

    fejlec_szoveg = tk.Label(
        fejlec,
        width=15,
        font=("Arial", 11, "bold")
    )
    fejlec_szoveg.pack(side=tk.LEFT, padx=5)

    tk.Button(
        fejlec,
        text=">",
        width=4,
        command=lambda: FR_honap_valtas(1)
    ).pack(side=tk.LEFT)

    FR_naptar_frissites()


def FR_mentes_reszletek(mentes):
    reszlet_ablak = tk.Toplevel(ablak)
    reszlet_ablak.title("LOGAnalyzer - Mentett elemzés")
    reszlet_ablak.geometry("750x600")
    reszlet_ablak.minsize(600, 450)

    tk.Label(
        reszlet_ablak,
        text="Mentett napi elemzés",
        font=("Arial", 17, "bold")
    ).pack(pady=15)

    informaciok = tk.Frame(reszlet_ablak)
    informaciok.pack(fill=tk.X, padx=20, pady=5)

    szoveg = (
        f"Dátum: {mentes['datum']}\n"
        f"Mentés időpontja: {mentes.get('mentes_idopontja', '')}\n"
        f"Fájlnév: {mentes['fajlnev']}\n"
        f"Logfájlok: {mentes.get('logfajlok', 0)} db\n"
        f"OK: {mentes.get('OK', 0)} db\n"
        f"NOK: {mentes.get('NOK', 0)} db"
    )

    tk.Label(
        informaciok,
        text=szoveg,
        justify=tk.LEFT,
        font=("Arial", 11)
    ).pack(anchor="w")

    tk.Label(
        reszlet_ablak,
        text="TOP 3 hibakód",
        font=("Arial", 12, "bold")
    ).pack(pady=(15, 5))

    top_keret = tk.Frame(reszlet_ablak)
    top_keret.pack(fill=tk.X, padx=20)

    top_tabla = ttk.Treeview(
        top_keret,
        columns=("hely", "kod", "darab", "nev"),
        show="headings",
        height=3
    )

    top_tabla.heading("hely", text="Hely", anchor="center")
    top_tabla.heading("kod", text="Hibakód", anchor="center")
    top_tabla.heading("darab", text="Darab", anchor="center")
    top_tabla.heading(
        "nev",
        text="Hiba megnevezése",
        anchor="center"
    )

    top_tabla.column(
        "hely", width=60, anchor="center", stretch=False
    )
    top_tabla.column(
        "kod", width=100, anchor="center", stretch=False
    )
    top_tabla.column(
        "darab", width=75, anchor="center", stretch=False
    )
    top_tabla.column(
        "nev", width=350, anchor="center", stretch=True
    )

    top_tabla.pack(fill=tk.X)

    for hely, adat in enumerate(mentes["top3"], 1):
        top_tabla.insert(
            "",
            tk.END,
            values=(
                hely,
                adat["hibakod"],
                adat["darab"],
                adat.get("megnevezes", "Ismeretlen hiba")
            )
        )

    tk.Label(
        reszlet_ablak,
        text="Összes hibakód",
        font=("Arial", 12, "bold")
    ).pack(pady=(15, 5))

    hibakod_keret = tk.Frame(reszlet_ablak)
    hibakod_keret.pack(
        fill=tk.BOTH,
        expand=True,
        padx=20,
        pady=(0, 15)
    )

    hibakod_tabla = ttk.Treeview(
        hibakod_keret,
        columns=("kod", "darab"),
        show="headings"
    )

    hibakod_tabla.heading("kod", text="Hibakód")
    hibakod_tabla.heading("darab", text="Darab")

    hibakod_tabla.column("kod", width=180, anchor="center")
    hibakod_tabla.column("darab", width=120, anchor="center")

    gorgeto = ttk.Scrollbar(
        hibakod_keret,
        orient=tk.VERTICAL,
        command=hibakod_tabla.yview
    )

    hibakod_tabla.configure(yscrollcommand=gorgeto.set)

    gorgeto.pack(side=tk.RIGHT, fill=tk.Y)
    hibakod_tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    for kod, darab in sorted(mentes["osszes_hibakod"].items()):
        hibakod_tabla.insert(
            "",
            tk.END,
            values=(kod, darab)
        )


def FR_elozmenyek():
    ablak_elozmeny = tk.Toplevel(ablak)
    ablak_elozmeny.title("LOGAnalyzer - Napi TOP 3 előzmények")
    ablak_elozmeny.geometry("950x600")
    ablak_elozmeny.minsize(750, 450)

    tk.Label(
        ablak_elozmeny,
        text="Napi TOP 3 hibák - Előzmények",
        font=("Arial", 16, "bold")
    ).pack(pady=15)

    keret = tk.Frame(ablak_elozmeny)
    keret.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

    tabla = ttk.Treeview(
        keret,
        columns=("het", "datum", "idopont", "hely", "kod", "darab"),
        show="headings",
        selectmode="browse"
    )

    stilus = ttk.Style()
    stilus.configure("Elvalasztott.Treeview", rowheight=25)
    tabla.configure(style="Elvalasztott.Treeview")
    tabla.tag_configure("elvalaszto", background="#E0E0E0")

    tabla.heading("het", text="Hét")
    tabla.heading("datum", text="Dátum")
    tabla.heading("idopont", text="Mentés ideje")
    tabla.heading("hely", text="Helyezés")
    tabla.heading("kod", text="Hibakód")
    tabla.heading("darab", text="Darab")

    tabla.column("het", width=65, anchor="center")
    tabla.column("datum", width=130, anchor="center")
    tabla.column("idopont", width=115, anchor="center")
    tabla.column("hely", width=100, anchor="center")
    tabla.column("kod", width=120, anchor="center")
    tabla.column("darab", width=90, anchor="center")

    gorgeto = ttk.Scrollbar(
        keret,
        orient=tk.VERTICAL,
        command=tabla.yview
    )

    tabla.configure(yscrollcommand=gorgeto.set)

    gorgeto.pack(side=tk.RIGHT, fill=tk.Y)
    tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    informacio = tk.Label(
        ablak_elozmeny,
        text="",
        font=("Arial", 10)
    )
    informacio.pack(pady=5)

    gomb_keret = tk.Frame(ablak_elozmeny)
    gomb_keret.pack(pady=10)

    sorok = {}

    def FR_elozmenyek_frissites():
        nonlocal sorok

        for sor in tabla.get_children():
            tabla.delete(sor)

        sorok = {}

        try:
            mentesek = FR_mentesek_betoltese(mentes_mappa)
        except (OSError, ValueError, KeyError, TypeError):
            messagebox.showerror(
                "LOGAnalyzer",
                "Nem sikerült betölteni a napi mentéseket."
            )
            return

        informacio.config(
            text=f"Mentett elemzések száma: {len(mentesek)}"
        )

        for sorszam, mentes in enumerate(mentesek):
            datum = mentes["datum"]
            het = date.fromisoformat(datum).isocalendar().week

            idopont = mentes.get("mentes_idopontja", "")

            if "T" in idopont:
                idopont = idopont.split("T", 1)[1]

            top3 = mentes["top3"]

            for index in range(3):
                if index < len(top3):
                    kod = top3[index]["hibakod"]
                    darab = top3[index]["darab"]
                else:
                    kod = ""
                    darab = ""

                if index == 0:
                    het_szoveg = str(het)
                    datum_szoveg = datum
                    ido_szoveg = idopont
                else:
                    het_szoveg = ""
                    datum_szoveg = ""
                    ido_szoveg = ""

                sor_id = tabla.insert(
                    "",
                    tk.END,
                    values=(
                        het_szoveg,
                        datum_szoveg,
                        ido_szoveg,
                        f"TOP {index + 1}",
                        kod,
                        darab
                    )
                )

                sorok[sor_id] = mentes

            if sorszam < len(mentesek) - 1:
                tabla.insert(
                    "",
                    tk.END,
                    values=("", "", "", "", "", ""),
                    tags=("elvalaszto",)
                )

    def FR_mentes_megnyitas():
        kivalasztott = tabla.selection()

        if not kivalasztott:
            messagebox.showwarning(
                "LOGAnalyzer",
                "Először jelölj ki egy mentett elemzést!"
            )
            return

        sor_id = kivalasztott[0]
        mentes = sorok.get(sor_id)

        if mentes is not None:
            FR_mentes_reszletek(mentes)
        else:
            messagebox.showwarning(
                "LOGAnalyzer",
                "A mentés egyik TOP 3 sorát jelöld ki!"
            )

    tk.Button(
        gomb_keret,
        text="Mentés megnyitása",
        command=FR_mentes_megnyitas,
        width=20
    ).pack(side=tk.LEFT, padx=8)

    tk.Button(
        gomb_keret,
        text="Lista frissítése",
        command=FR_elozmenyek_frissites,
        width=20
    ).pack(side=tk.LEFT, padx=8)

    tabla.bind(
        "<Double-1>",
        lambda esemeny: FR_mentes_megnyitas()
    )

    FR_elozmenyek_frissites()


def FR_idoszakos_ablak():
    ablak_idoszak = tk.Toplevel(ablak)
    ablak_idoszak.title("LOGAnalyzer - Időszakos TOP 3")
    ablak_idoszak.geometry("850x520")
    ablak_idoszak.minsize(650, 450)

    tk.Label(
        ablak_idoszak,
        text="Időszakos TOP 3 hibaelemzés",
        font=("Arial", 16, "bold")
    ).pack(pady=15)

    datum_keret = tk.Frame(ablak_idoszak)
    datum_keret.pack(pady=10)

    tk.Label(
        datum_keret,
        text="Kezdő dátum:"
    ).grid(row=0, column=0, padx=5)

    kezdo_mezo = tk.Entry(datum_keret, width=13)
    kezdo_mezo.grid(row=0, column=1, padx=5)
    kezdo_mezo.insert(
        0,
        date.today().replace(day=1).isoformat()
    )

    tk.Button(
        datum_keret,
        text="Naptár",
        command=lambda: FR_naptar(kezdo_mezo)
    ).grid(row=0, column=2, padx=5)

    tk.Label(
        datum_keret,
        text="Záró dátum:"
    ).grid(row=0, column=3, padx=5)

    zaro_mezo = tk.Entry(datum_keret, width=13)
    zaro_mezo.grid(row=0, column=4, padx=5)
    zaro_mezo.insert(0, date.today().isoformat())

    tk.Button(
        datum_keret,
        text="Naptár",
        command=lambda: FR_naptar(zaro_mezo)
    ).grid(row=0, column=5, padx=5)

    eredmeny_felirat = tk.Label(
        ablak_idoszak,
        text="Válaszd ki az időszakot!",
        font=("Arial", 11)
    )
    eredmeny_felirat.pack(pady=10)

    tabla_keret = tk.Frame(ablak_idoszak)
    tabla_keret.pack(
        fill=tk.BOTH,
        expand=True,
        padx=15,
        pady=10
    )

    tabla = ttk.Treeview(
        tabla_keret,
        columns=("hely", "kod", "darab", "nev"),
        show="headings",
        height=3
    )

    tabla.heading("hely", text="Helyezés", anchor="center")
    tabla.heading("kod", text="Hibakód", anchor="center")
    tabla.heading("darab", text="Darab", anchor="center")
    tabla.heading(
        "nev",
        text="Hiba megnevezése",
        anchor="center"
    )

    tabla.column(
        "hely", width=100, anchor="center", stretch=False
    )
    tabla.column(
        "kod", width=120, anchor="center", stretch=False
    )
    tabla.column(
        "darab", width=90, anchor="center", stretch=False
    )
    tabla.column(
        "nev", width=350, anchor="center", stretch=True
    )

    tabla.pack(fill=tk.BOTH, expand=True)

    def FR_idoszakos_szamitas():
        try:
            kezdet = date.fromisoformat(kezdo_mezo.get().strip())
            veg = date.fromisoformat(zaro_mezo.get().strip())
        except ValueError:
            messagebox.showwarning(
                "LOGAnalyzer",
                "A dátum formátuma ÉÉÉÉ-HH-NN legyen!"
            )
            return

        if kezdet > veg:
            messagebox.showwarning(
                "LOGAnalyzer",
                "A kezdő dátum nem lehet későbbi a záró dátumnál."
            )
            return

        try:
            mentesek = FR_mentesek_betoltese(mentes_mappa)

            eredmeny, napok = FR_idoszakos_top3(
                mentesek,
                kezdet.isoformat(),
                veg.isoformat()
            )
        except (OSError, ValueError, KeyError, TypeError):
            messagebox.showerror(
                "LOGAnalyzer",
                "Nem sikerült elkészíteni az időszakos elemzést."
            )
            return

        for sor in tabla.get_children():
            tabla.delete(sor)

        hibanevek = FR_hibanevek()

        for hely, adat in enumerate(eredmeny, 1):
            kod = adat[0]
            darab = adat[1]
            nev = hibanevek.get(kod, "Ismeretlen hiba")

            tabla.insert(
                "",
                tk.END,
                values=(f"TOP {hely}", kod, darab, nev)
            )

        eredmeny_felirat.config(
            text=f"Időszak: {kezdet} - {veg} | "
                 f"Figyelembe vett napok: {napok}"
        )

        if napok == 0:
            messagebox.showinfo(
                "LOGAnalyzer",
                "A kiválasztott időszakban nincs mentett elemzés."
            )

    tk.Button(
        ablak_idoszak,
        text="TOP 3 kiszámítása",
        command=FR_idoszakos_szamitas,
        width=22
    ).pack(pady=10)

ablak = tk.Tk()

ikon_fajl = os.path.join(alapmappa, "LOGAnalyzer.png")
ikon = tk.PhotoImage(file=ikon_fajl)
ablak.iconphoto(True, ikon)

ablak.title("LOGAnalyzer - FCT Log Analysis")
ablak.geometry("1100x700")
ablak.minsize(950, 550)

tk.Label(
    ablak,
    text="LOGAnalyzer",
    font=("Arial", 22, "bold")
).pack(pady=15)

gombok = tk.Frame(ablak)
gombok.pack(pady=10)

ellenorzes_gomb = tk.Button(
    gombok,
    text="Logfájlok ellenőrzése",
    command=FR_ellenorzes
)
ellenorzes_gomb.pack(side=tk.LEFT, padx=5)

beolvasas_gomb = tk.Button(
    gombok,
    text="Logfájl beolvasása",
    command=FR_beolvasas
)
beolvasas_gomb.pack(side=tk.LEFT, padx=5)

mentes_gomb = tk.Button(
    gombok,
    text="Napi TOP 3 mentése",
    command=FR_napi_mentes_gomb,
    state=tk.DISABLED
)
mentes_gomb.pack(side=tk.LEFT, padx=5)

elozmenyek_gomb = tk.Button(
    gombok,
    text="Napi TOP 3 előzmények",
    command=FR_elozmenyek
)
elozmenyek_gomb.pack(side=tk.LEFT, padx=5)

idoszakos_gomb = tk.Button(
    gombok,
    text="Időszakos TOP 3",
    command=FR_idoszakos_ablak
)
idoszakos_gomb.pack(side=tk.LEFT, padx=5)

FR_sugo(
    ellenorzes_gomb,
    "Adja meg a logfájlokat tartalmazó mappát."
)
FR_sugo(
    beolvasas_gomb,
    "Adja meg az elemezni kívánt logfájlt."
)
FR_sugo(
    mentes_gomb,
    "A jelenlegi TOP 3 elemzés mentése."
)
FR_sugo(
    elozmenyek_gomb,
    "Korábbi napi TOP 3 elemzések megtekintése."
)
FR_sugo(
    idoszakos_gomb,
    "TOP 3 hibák összesítése kiválasztott időszakra."
)

eredmeny_keret = tk.Frame(ablak)
eredmeny_keret.pack(pady=10)

osszes_felirat = tk.Label(
    eredmeny_keret,
    text="Logfájlok: 0 db",
    font=("Arial", 12, "bold")
)
osszes_felirat.pack(side=tk.LEFT, padx=10)

ok_felirat = tk.Label(
    eredmeny_keret,
    text="OK: 0 db",
    font=("Arial", 12, "bold"),
    fg="#006400"
)
ok_felirat.pack(side=tk.LEFT, padx=10)

nok_felirat = tk.Label(
    eredmeny_keret,
    text="NOK: 0 db",
    font=("Arial", 12, "bold"),
    fg="#FF0000"
)
nok_felirat.pack(side=tk.LEFT, padx=10)

mentes_felirat = tk.Label(
    ablak,
    text="",
    font=("Arial", 9)
)
mentes_felirat.pack()

tartalom = tk.Frame(ablak)
tartalom.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

bal = tk.LabelFrame(
    tartalom,
    text="Összes hibakód",
    font=("Arial", 11, "bold"),
    width=300
)
bal.pack(side=tk.LEFT, fill=tk.Y, padx=5)
bal.pack_propagate(False)

jobb = tk.Frame(tartalom)
jobb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

hibakod_lista = tk.Text(
    bal,
    font=("Consolas", 11)
)
hibakod_lista.pack(
    fill=tk.BOTH,
    expand=True,
    padx=10,
    pady=10
)

top3_keret = tk.LabelFrame(
    jobb,
    text="TOP 3 hibakód",
    font=("Arial", 11, "bold")
)
top3_keret.pack(fill=tk.X, pady=(0, 10))

top3_lista = ttk.Treeview(
    top3_keret,
    columns=("hely", "kod", "darab", "nev"),
    show="headings",
    height=3
)

top3_lista.heading("hely", text="Hely", anchor="center")
top3_lista.heading("kod", text="Hibakód", anchor="center")
top3_lista.heading("darab", text="Darab", anchor="center")
top3_lista.heading(
    "nev",
    text="Hiba megnevezése",
    anchor="center"
)

top3_lista.column(
    "hely", width=55, minwidth=45,
    anchor="center", stretch=False
)
top3_lista.column(
    "kod", width=90, minwidth=75,
    anchor="center", stretch=False
)
top3_lista.column(
    "darab", width=75, minwidth=65,
    anchor="center", stretch=False
)
top3_lista.column(
    "nev", width=350, minwidth=180,
    anchor="center", stretch=True
)

top3_lista.pack(fill=tk.X, padx=10, pady=(10, 0))

top3_gorgeto = ttk.Scrollbar(
    top3_keret,
    orient=tk.HORIZONTAL,
    command=top3_lista.xview
)
top3_gorgeto.pack(fill=tk.X, padx=10, pady=(0, 5))
top3_lista.configure(xscrollcommand=top3_gorgeto.set)

log_keret = tk.LabelFrame(
    jobb,
    text="Kiválasztott logfájl",
    font=("Arial", 11, "bold")
)
log_keret.pack(fill=tk.BOTH, expand=True)

log_szoveg = tk.Text(
    log_keret,
    font=("Consolas", 11)
)
log_szoveg.pack(
    fill=tk.BOTH,
    expand=True,
    padx=10,
    pady=10
)

ablak.mainloop()
