#!/usr/bin/env python3
"""Erzeugt eigenes XMLTV (30 Tage) fuer Kanaele ohne echtes EPG. Output: epg.xml.gz"""
import gzip, os, html
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

SP = "."
TZ = ZoneInfo("Europe/Berlin")
START = datetime.now(TZ).replace(hour=0, minute=0, second=0, microsecond=0)
DAYS = 30

# id -> (Anzeigename, Blockstunden, Titel, Beschreibung) | 3liga/event: Sonderlogik
CH = {}
for n in [1, 2, 5, 6, 7, 8]:
    CH[f"skyselect{n}.custom"] = (f"Sky Select {n}", 3, "Wunschkino – aktuelle Filme",
        "Sky Select: aktuelle Spielfilme auf Bestellung.")
for n, genre in [(24, "Horror"), (25, "Comedy"), (26, "Familie"), (27, "Animation"), (28, "Science-Fiction"), (29, "Drama")]:
    CH[f"skyselect{n}.custom"] = (f"Sky Select {n}", 3, f"Wunschkino: {genre}",
        f"Sky Select: {genre}-Filme auf Bestellung.")
for n in range(1, 8):
    q = "4K-" if n <= 3 else ""
    CH[f"maxselect{n}.custom"] = (f"Max Select {n}", 3, f"{q}Wunschkino (Max Select)",
        f"Max Select: aktuelle Spielfilme{' in 4K' if n<=3 else ''} auf Bestellung.")
CH["magentasport.custom"] = ("MagentaSport", 3, "Live-Sport auf MagentaSport",
    "3. Liga, Eishockey (PENNY DEL), Basketball (easyCredit BBL) und mehr – live und als Wiederholung.")
CH["daznf1.custom"] = ("DAZN F1", 3, "Motorsport-Events", "Event-Kanal: aktiv bei Formel-Rennen und Motorsport-Events.")
CH["daznnba.custom"] = ("DAZN NBA", 3, "NBA – Spiele & Highlights", "Live-Spiele, Wiederholungen und Highlights der NBA.")
CH["daznnfl.custom"] = ("DAZN NFL Network", 3, "NFL Network", "American Football: Live-Spiele, Analysen und Highlights.")
CH["daznmlb.custom"] = ("DAZN MLB", 3, "MLB – Baseball live", "Major League Baseball: Live-Spiele und Highlights.")
CH["daznlfc.custom"] = ("DAZN LFC TV", 3, "Liverpool FC TV", "Der Klub-Kanal des FC Liverpool: Spiele, Interviews, Archiv.")
CH["eurosport2event.custom"] = ("Eurosport 2 Event", 3, "Eurosport-Event-Kanal", "Aktiv bei besonderen Live-Übertragungen.")
CH["puls24.custom"] = ("PULS 24", 1, "PULS 24 Nachrichten", "Nachrichten, Talks und Dokus aus Österreich – rund um die Uhr.")
CH["terramaterwild.custom"] = ("Terra Mater Wild", 2, "Naturdokumentationen", "Terra Mater: Natur- und Tierdokumentationen in Spielfilmqualität.")
CH["skycinemafun.custom"] = ("Sky Cinema Fun", 2, "Komödien am Stück", "Sky Cinema Fun: Komödien rund um die Uhr.")
CH["skycinemahits.custom"] = ("Sky Cinema Hits", 2, "Film-Hits", "Sky Cinema Hits: die erfolgreichsten Filme der letzten Jahre.")
CH["skycinemaspecial.custom"] = ("Sky Cinema Special", 2, "Themen-Specials", "Sky Cinema Special: wechselnde Film-Themenschwerpunkte.")
CH["skycinema.custom"] = ("Sky Cinema", 2, "Spielfilm", "Sky Cinema: aktuelle Spielfilme.")
CH["filmgold.custom"] = ("Filmgold", 2, "Filmklassiker", "Filmgold: deutsche und internationale Filmklassiker.")
CH["festival.custom"] = ("Festival 4K", 2, "Konzerte & Festivals in 4K", "Festival: Konzerte und Musikfestivals in 4K.")
for n in range(2, 9):
    CH[f"liga3k{n}.custom"] = (f"3. Liga {n}", None, None, None)  # Sonderlogik

def ts(dt): return dt.strftime("%Y%m%d%H%M%S %z").replace(":", "")

out = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv generator-info-name="uhf-custom-epg">']
for cid, (name, *_1) in CH.items():
    out.append(f'  <channel id="{cid}"><display-name lang="de">{html.escape(name)}</display-name></channel>')

for cid, (name, hours, title, desc) in CH.items():
    if cid.startswith("liga3k"):
        for d in range(DAYS):
            day = START + timedelta(days=d)
            wd = day.weekday()  # 5=Sa, 6=So
            slots = []
            if wd == 5: slots = [(13, 18, "Live: 3. Liga – Samstagsspiele")]
            elif wd == 6: slots = [(12, 18, "Live: 3. Liga – Sonntagsspiele")]
            cursor = day
            for h1, h2, t in slots:
                a, b = day.replace(hour=h1), day.replace(hour=h2)
                if cursor < a:
                    out.append(f'  <programme start="{ts(cursor)}" stop="{ts(a)}" channel="{cid}"><title lang="de">Sendepause bis zum Spieltag</title></programme>')
                out.append(f'  <programme start="{ts(a)}" stop="{ts(b)}" channel="{cid}"><title lang="de">{html.escape(t)}</title><desc lang="de">Spieltagskanal – aktiv bei Live-Spielen der 3. Liga.</desc></programme>')
                cursor = b
            nxt = day + timedelta(days=1)
            if cursor < nxt:
                out.append(f'  <programme start="{ts(cursor)}" stop="{ts(nxt)}" channel="{cid}"><title lang="de">Sendepause bis zum Spieltag</title></programme>')
    else:
        t0 = START
        end = START + timedelta(days=DAYS)
        while t0 < end:
            t1 = t0 + timedelta(hours=hours)
            out.append(f'  <programme start="{ts(t0)}" stop="{ts(t1)}" channel="{cid}"><title lang="de">{html.escape(title)}</title><desc lang="de">{html.escape(desc)}</desc></programme>')
            t0 = t1
out.append("</tv>")

data = "\n".join(out).encode()
with gzip.open(f"{SP}/epg.xml.gz", "wb") as f: f.write(data)
print(f"epg.xml.gz erzeugt: {len(CH)} Kanaele, {DAYS} Tage")
