"""
dm Bewerbungs-Dashboard - Seite 1: Über mich
=============================================
Autor: Romana
Zweck: Interaktive Bewerbung für die Position
       Data Analyst / Data Scientist - Supply Chain Data Analytics bei dm

Struktur des Gesamtprojekts:
    Über_mich.py                                   <- diese Datei = Startseite "Über mich"
    pages/1_Praxisbeispiel.py                      <- Praxisbeispiel mit 5 Szenarien
    styling.py                                     <- Design-System
    datasim.py                                     <- simulierte Supply-Chain-Daten für das Praxisbeispiel
    .streamlit/config.toml                         <- Farbschema (dm-CI, Lila als Leitfarbe)
"""

import base64      #für Foto
import mimetypes   #für Foto - Ermittlung des MIME-Typs
import re          #ladet regex für _parse_start_datum
import sqlite3
import pandas as pd
import math
from datetime import date   #für die Live Berechnung von den Werdegangs timestamps

import streamlit as st

from styling import (
    DM_BLAU, DM_BLAU_DUNKEL, DM_LILA, DM_LILA_DUNKEL, DM_LILA_HELL,
    DM_GOLD, DM_TEXT, DM_GRAU,
    html, section_title, inject_base_css, render_topbar,
)

_MONAT_NUM = {
    "jänner": 1, "januar": 1, "februar": 2, "märz": 3, "april": 4, "mai": 5,
    "juni": 6, "juli": 7, "august": 8, "september": 9, "oktober": 10,
    "november": 11, "dezember": 12,
}


def _parse_start_datum(zeit: str) -> "date | None":
    """Extrahiert das Startdatum aus einem Zeitraum-String wie 'August 2018 – März 2021'."""
    start = zeit.split("–")[0].strip()
    treffer = re.match(r"(\w+)\s+(\d{4})", start)
    if not treffer:
        return None
    monat = _MONAT_NUM.get(treffer.group(1).lower())
    if not monat:
        return None
    return date(int(treffer.group(2)), monat, 1)


def berufserfahrung_jahre(werdegang: list[dict]) -> int:
    """Ganze Jahre seit dem frühesten Startdatum im Werdegang — live berechnet
    statt hart gecoded. Abgerundet (>X Jahre heißt X volle Jahre sind um, nicht aufgerundet auf das laufende Jahr)."""
    start_daten = [d for e in werdegang if (d := _parse_start_datum(e["zeit"]))]
    if not start_daten:
        return 0
    fruehester = min(start_daten)
    heute = date.today()
    jahre = heute.year - fruehester.year - (
        (heute.month, heute.day) < (fruehester.month, fruehester.day)
    )
    return jahre

# ---------------------------------------------------------------------------
# SEITEN-KONFIGURATION
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Romana | Bewerbung Data Analyst/Scientist @dm",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="auto",
)


# ---------------------------------------------------------------------------
# STAMMDATEN 
# ---------------------------------------------------------------------------
NAME = "Romana"
ROLLE = "Data Analyst / Scientist"
GITHUB_URL = "https://github.com/codebase-of-Romana"

WERDEGANG_DATA = [
    dict(
        farbe="blau", titel="Business Data Analyst", firma="Tractive",
        zeit="März 2024 – Juli 2026",
        bullets=[
            "Baute die zentrale Datenbasis für Subscription- und CRM-Analysen auf und verantwortete deren laufende Pflege",
            "Beantwortete Fragestellungen zu Kundenabwanderung und Subscription-Verhalten mit SQL-Abfragen in Redshift, Ergebnisse in Dashboards via Tableau für Stakeholder aufbereitet",
            "Analysierte Performance-Abweichungen und leitete daraus konkrete Handlungsempfehlungen für Stakeholder ab",
            "Arbeitete als Schnittstelle zwischen Domain-Stakeholder, Product- und Backend-Team, um Datenanforderungen zu klären und Analysen & Dashboards zu erstellen",
            "Gestaltete gemeinsam mit dem Team die Datenstrategie (Data Dictionary, Semantic Layer, Data Engineering) und Reporting-Standards mit",
            "Setzte KI-Tools (ChatGPT, Claude) gezielt ein, um komplexe SQL-Queries & Python Scripte schneller zu entwickeln und zu optimieren",
            "Nutzte KI zur Identifikation von Mustern und Anomalien in großen Datensätzen",
        ],
        tags=["SQL", "Python", "Redshift", "Tableau", "dbt", "Airflow", "A/B-Testing"],
    ),
    dict(
        farbe="lila", titel="Data Analyst", firma="Blockpit AG",
        zeit="Oktober 2021 – Februar 2024",
        bullets=[
            "Rückkehr zu Blockpit — diesmal mit Fokus auf Datenanalyse statt Marketing",
            "Baute Data Abteilung mit auf und entwickelte Analysen und Dashboards mit SQL-Queries in Metabase und PowerBI",
            "Baute das laufende Reporting zu Abonnement-, Business- und Produktdaten für das Management auf",
            "Übernahme von Data Engineering Tasks und Aufbau von Data Pipelines ",
            "Trug mit einem internationalen Team zur Entwicklung und Umsetzung einer Blitzscaling-Strategie bei",
        ],
        tags=["SQL", "MySQL", "Reporting", "PowerBI", "Metabase", "GA"],
    ),
    dict(
        farbe="lila-hell", titel="Web Analyst", firma="Oberösterreichische Versicherung",
        zeit="April 2021 – September 2021",
        bullets=[
            "Richtete Matomo und Piwik Pro als Tracking-Grundlage für die Webanalyse ein",
            "Analysierte Conversion-Rates und Sales-Funnel-Daten, um Schwachstellen in der Customer Journey zu identifizieren",
            "Führte A/B-Tests durch und optimierte darauf aufbauend Landingpages zur Steigerung der Conversion-Rate",
            "Stellte die Einhaltung der Datenschutz-Vorgaben (DSGVO) bei allen Kampagnenaktivitäten sicher",
        ],
        tags=["Matomo", "Piwik Pro", "A/B-Testing"],
    ),
    dict(
        farbe="lila", titel="Online Marketing Manager / Web & Product Analyst", firma="Blockpit AG",
        zeit="August 2018 – März 2021",
        bullets=[
            "Verantwortete CRM, E-Mail-Marketing und Drip-Kampagnen entlang der gesamten Customer Journey",
            "Baute Mail-Automation-Funnels und Datenpipelines für HubSpot und Mailchimp auf, um Kampagnen automatisiert und datenbasiert auszusteuern",
            "Entwickelte eine Web- und App-Tracking-Strategie auf Basis der User Journey als Grundlage für alle nachgelagerten Analysen",
            "Richtete Event-Tracking mit Google Analytics und Tag Manager ein und stellte damit die Datengrundlage für Kampagnenauswertungen sicher",
            "Entwickelte Tracking- und Dashboard-Konzepte für CRM-, Content-, SEO-, Social-Media-, Magazin-, Paid-Ads-, Video-, Influencer- und Produktkampagnen, um datenbasierte Entscheidungen über alle Kanäle hinweg zu ermöglichen",
        ],
        tags=["GA", "Tag Manager", "Tracking", "HubSpot", "Mailchimp"],
    ),
]

AUSBILDUNG_DATA = [
    dict(jahre="2018 – 2020", degree="Master — Kommunikation, Wissen, Medien", inst="FH OÖ Campus Hagenberg"),
    dict(jahre="2015 – 2018", degree="Bachelor — Kommunikation, Wissen, Medien", inst="FH OÖ Campus Hagenberg"),
]

KOMPETENZ_MATRIX = [
    (
        "Datenanalyse",
        "Tiefgehende, explorative Analysen auf großen Datenmengen mit klaren Handlungsempfehlungen.",
        "Bei Blockpit und Tractive eigenverantwortlich für die explorative Analyse großer Datenmengen im Subscription-Kerngeschäft — inklusive Aufbau eines Semantic Layer mit dbt, damit Kennzahlen wie Umsatz in jedem Dashboard dasselbe bedeuten.",
    ),
    (
        "Toolentwicklung",
        "Innovative Anwendungen & Modelle zur Entscheidungsunterstützung gemeinsam mit der IT entwickeln.",
        "Enge Zusammenarbeit mit Product- und Backend-Team bei Tractive, um fachliche Fragestellungen in Datenmodelle und technische Anforderungen zu übersetzen.",
    ),
    (
        "Beratung & Projektunterstützung",
        "Fachliche Problemstellungen in technische Anforderungen übersetzen, Kolleg:innen beratend zur Seite stehen.",
        "Gemeinsam mit Stakeholdern Domain-Knowledge und Semantic Layer sowie Kennzahlen definiert, Datenmodelle und Dashboards gebaut und Self-Service Analytics für Fachbereiche ausgebaut.",
    ),
    (
        "Wissenstransfer",
        "Durch Dokumentation & interne Austauschformate Data Analytics im Unternehmen verankern.",
        "Aktiver Wissensaustausch mit Stakeholder über Domainwissen. Mitgestaltung von Datateam-Strategie und Reporting-Standards bei Tractive, Aufbau von Datenkatalog und Semantic Layer, damit Dashboards aktiv genutzt werden statt zu verstauben — mit durchgängiger Förderung von Self-Service Analytics.",
    ),
    (
        "Qualitätssicherung",
        "Qualität & Integrität von Daten und Use Cases überwachen und kontinuierlich optimieren.",
        "Durchgängiger Fokus auf Datenqualität bei Tractive: Testfälle direkt in SQL-Skripten und in den Airflow-ETL-Jobs stellen sicher, dass Stakeholder verlässlich korrekte Daten erhalten.",
    ),
    (
        "Logistik Know-How",
        "Fundierte Kenntnisse in Netzwerkplanung, Supply Chain Management und/oder Operations Research, idealerweise im Handels- und/oder Distributionsumfeld.",
        "Tractive vertreibt neben Abos auch physische GPS-Tracker — dadurch direkte Berührung mit Einkaufs- und Operationsdaten, die eng mit dem Subscription-Geschäft verzahnt sind.",
    ),
    (
        "Analytische Denkweise",
        "Schnelle Auffassungsgabe und Freude an komplexen analytischen Lösungsansätzen — Erkenntnisgewinn und Validierung stehen im Vordergrund.",
        "Ich löse Probleme am liebsten im direkten Austausch mit den Stakeholdern und Arbeitskolleg:innen. Mein Leitsatz dabei, von Jim Bergeson: 'Data will talk to you, if you're willing to listen.'",
    ),
    (
        "Eigenständigkeit und Weitblick",
        "Eigenverantwortliches, strukturiertes Arbeiten; klare Kommunikation zwischen zentralen Schnittstellen national und mit Länderkolleg:innen.",
        "Ich arbeite eigenständig und strukturiert, wirke aktiv an der Daten- und Unternehmensstrategie mit und bringe mich verlässlich in Projekte ein, die über das Tagesgeschäft hinausgehen. Seit über sechs Jahren ist Englisch bei Blockpit und Tractive meine Arbeitssprache in Wort und Schrift.",
    ),
]

# ---------------------------------------------------------------------------
# Skill-Abgleich 
# ---------------------------------------------------------------------------
_LUECKEN = {"Logistik Know-How", "Posit", "Snowflake", "Streamlit (Grundkenntnisse siehe dieses Projekt)"}

KOMPETENZ_ABGLEICH = [
    (titel, titel not in _LUECKEN) for titel, _, _ in KOMPETENZ_MATRIX
] + [
    ("Fundierte Ausbildung", True),
]

# Erfahrungstext je Kompetenzbereich
KOMPETENZ_ERFAHRUNG = {titel: erfahrung for titel, _, erfahrung in KOMPETENZ_MATRIX}
KOMPETENZ_ERFAHRUNG["Fundierte Ausbildung"] = (
    "Technisch ausgerichtetes Studium an einem IT-Campus (Bachelor & Master, "
    "FH Hagenberg) mit Datenbanken als Bachelor-Schwerpunkt."
)

SPRACH_PROGRAMM_SKILLS = [
    (s, s not in _LUECKEN)
    for s in ["Deutsch", "Englisch", "SQL", "Python" ]
]

# ---------------------------------------------------------------------------
# ATTACHEMENTS
# ---------------------------------------------------------------------------
LOGO_PATH = "assets/dm_logo.png"
PORTRAIT_PATH = "assets/portrait.jpg"

inject_base_css()

# ---------------------------------------------------------------------------
# "Kompakte Ansicht": responsive Design
# der komplette Inhalt wird in einem Container gestapelt und untereinander angeordnet.
# ---------------------------------------------------------------------------
if "kompakt" not in st.session_state:
    st.session_state["kompakt"] = False
KOMPAKT = st.session_state["kompakt"]


def split(*ratios, gap="large"):
    if KOMPAKT:
        c = st.container()
        return tuple(c for _ in ratios)
    return st.columns(list(ratios), gap=gap)


def split_n(n, gap="medium"):
    return split(*([1] * n), gap=gap)


def praxisbeispiel_banner() -> None:
    """Verweis auf das Praxisbeispiel - identisch am Ende jedes Tabs."""
    st.info(
        "Im linken Menü befindet sich der Punkt "
        "[**Praxisbeispiel**](/Praxisbeispiel): mit fünf Szenarien — "
        "Netzwerkkarte, Nachfrageprognose, Liefertreue, CO2-Fußabdruck "
        "und einer Semantic-Layer-Demo."
    )

# ---------------------------------------------------------------------------
# HERO
# ---------------------------------------------------------------------------
col_hero, col_photo = split(2.5, 1, gap="large")

_erfahrung_jahre = berufserfahrung_jahre(WERDEGANG_DATA)

with col_hero:
    html(f"""
    <div class="hero">
        <span class="kicker">Bewerbung · Supply Chain Data Analytics · Verteilerzentrum Enns</span>
        <h1>{NAME}</h1>
        <div class="role">{ROLLE}</div>
        <div class="rule"></div>
        <div class="hero-facts">
            <div class="fact"><div class="flabel">Berufserfahrung</div><div class="fvalue">&gt;6 Jahre in Data Analytics &amp; Business Intelligence</div></div>
            <div class="fact"><div class="flabel">Ausbildung</div><div class="fvalue">Bachelor &amp; Master an der FH Hagenberg</div></div>
            <div class="fact"><div class="flabel">Kernthemen</div><div class="fvalue">Subscription · CRM · Operations</div></div>
        </div>
    </div>
    """)

with col_photo:
    _foto_mime = mimetypes.guess_type(PORTRAIT_PATH)[0]
    with open(PORTRAIT_PATH, "rb") as _foto_datei:
        _foto_b64 = base64.b64encode(_foto_datei.read()).decode()
    html(f"""
    <div class="photo-slot has-photo">
        <img src="data:{_foto_mime};base64,{_foto_b64}" alt="Porträtfoto">
    </div>
    """)

# lila Wellen-Platzhalter
html(f"""
<div class="wave-divider">
    <svg viewBox="0 0 1440 100" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M0,55 C 220,100 460,20 720,45 C 980,70 1220,25 1440,55 L1440,100 L0,100 Z" fill="{DM_LILA_HELL}"></path>
        <path d="M0,40 C 260,80 500,5 760,35 C 1000,62 1240,15 1440,42 L1440,70 C 1240,45 1000,90 760,62 C 500,32 260,108 0,68 Z" fill="#E3DBF7" opacity="0.75"></path>
    </svg>
</div>
""")

# ---------------------------------------------------------------------------
# NAVIGATION
# ---------------------------------------------------------------------------
tab_ueber_mich, tab_werdegang, tab_skills = st.tabs(
    ["Über mich", "Werdegang", "Skills & Tools"]
)

# ---------------------------------------------------------------------------
# TAB: ÜBER MICH
# ---------------------------------------------------------------------------
with tab_ueber_mich:
    section_title("Persönlich", "Über mich")

    html("""
    <div class="lead-box">
        <p>
            Nach meinem technisch ausgerichteten Studium an der FH Hagenberg habe
            ich im Online Marketing begonnen und dort schnell meine
            Leidenschaft für Web-Analyse und Tracking entdeckt. Aus dem
            Bedürfnis heraus, den Erfolg von Marketingaktivitäten wirklich zu
            verstehen, bin ich nach und nach ins Reporting und schließlich
            vollständig in die Datenanalyse gewechselt. Sowohl bei Blockpit
            als auch bei Tractive war ich im Data Team für Subscription- und
            Produktdaten verantwortlich: habe Domainwissen aufgebaut, Projekte und KPIs gemeinsam mit
            Stakeholdern definiert, Daten bereinigt und aufbereitet sowie
            Datenmodelle und Dashboards gebaut, die als Entscheidungsgrundlage
            von Management und Stakeholder verwendet wurden.
        </p>
    </div>
    """)

    # Berufsstationen & Erfahrung
    kpi_cols = split_n(3, gap="medium")
    kpis = [
        ("Berufsstationen", str(len(WERDEGANG_DATA))),
        ("Berufserfahrung", f">{_erfahrung_jahre} Jahre"),
        ("Erfahrung als Data Analyst", ">6 Jahre"),
    ]
    for col, (label, value) in zip(kpi_cols, kpis):
        with col:
            html(f"""
            <div class="metric-tile" style="--accent:{DM_LILA};">
                <div class="m-label">{label}</div>
                <div class="m-value">{value}</div>
            </div>
            """)

    st.write("")


    NARRATIV = [
        ("Meine Stärken", "verlässlich, genau, direkt", "blau", (
            "Verlässlichkeit, Genauigkeit und eine klare, direkte Kommunikation "
            "prägen meine Arbeitsweise. Bevor ich eine Erkenntnis weitergebe, "
            "will ich verstanden haben, warum sich die Zahlen so verhalten, "
            "wie sie es tun — Domainwissen aufbauen, Daten zuvor zu validieren und zu verstehen sind die Grundlage für "
            "mich für jedes Reporting. Genauso wichtig ist mir, Daten so "
            "aufzubereiten, dass sie für andere nutzbar werden: angefangen "
            "bei klarer Semantic-Layer-Definition, über gezielte "
            "Unterstützung und Übergabe von Reportings und "
            "Self-Service-Lösungen an Stakeholder, bis hin zur Dokumentation "
            "der Datenmodelle für Arbeitskolleg:innen.\n\n"
        )),
        ("Das erwartet ihr von mir", "mitdenkend & teamorientiert", "lila", (
            "Ich bringe eine mitdenkende, teamorientierte Arbeitsweise mit und "
            "lerne gerne von erfahrenen Kolleg:innen, genauso wie ich mein "
            "Wissen weitergebe. Offenheit für fachliche und persönliche "
            "Weiterentwicklung sowie aufmerksames Zuhören und Aufbau eines Domainwissens gehören für mich zu "
            "einer guten Zusammenarbeit dazu. Ownership für meinen Zuständigkeitsbereich zu übernehmen ist für mich selbstverständlich. "
            ""
        )),
        ("Warum ich zu dm passe", "Mitarbeit im SCDA-Team", "lila", (
            "dm baut mit dem Team Supply Chain Data Analytics (SCDA) die "
            "analytische Grundlage für ein Logistiknetzwerk über 12 "
            "europäische Länder auf — genau hier möchte ich "
            "mitgestalten. Bei Tractive habe ich bereits an der Data-Strategie "
            "des Teams mitgewirkt, einen Semantic Layer mit eingeführt und "
            "mitgeholfen, dass sich das Data Team im Unternehmen stärker "
            "etabliert: weg von der reinen Ticket-Abarbeitung, hin zu "
            "Zeit um Auswertungen mit echtem Tiefgang zu erschaffen, die als Grundlage für "
            "Entscheidungen und Optimierungen dienen. "
            "Von Grund auf mitzudenken, aber auch "
            "Bestehendes zu überarbeiten und weiterzuentwickeln — suche ich "
            "auch bei dm. Als langjährige dm-Kundin reizt mich zusätzlich der "
            "Blick hinter die Kulissen: wie ein derart komplexes Logistik-Netzwerk "
            "transparent und steuerbar gemacht wird."
        )),
        ("Warum die Rolle zu meinen Zielen passt", "Team & Vielfalt", "blau", (
            "Bisher habe ich vor allem Daten zu Abo- und Kundenverhalten analysiert - "
            "am Supply Chain Management fasziniert mich besonders, dass hier die Datenanalyse "
            "auf reale, komplexe Entscheidungen trifft: Standortplanung, Transportrouten, "
            "Bestände. Jede Zahl hat sofort eine operative Konsequenz. "
            "Nach Jahren in Subscription- und Produktanalyse suche ich genau diese "
            "Herausforderung: ein neu aufgebautes Team, in dem ich von Anfang an mitgestalten kann, "
            "wie Logistikprozesse messbar und steuerbar werden — für ein Netzwerk, "
            "das über 12 Länder hinweg wirklich etwas bewegt."
        )),
    ]

    col_l, col_r = split(1, 1, gap="large")
    for idx, (col, (titel, hook, farbe, text)) in enumerate(zip((col_l, col_l, col_r, col_r), NARRATIV)):
        with col:
            with st.container(key=f"narrativ-{idx}"):
                # Zweizeiliges Label: Titel fett, Aufhänger darunter kursiv
                with st.expander(f"**{titel}**  \n*{hook}*"):
                    st.markdown(text)

    st.write("")
    st.markdown("#### Was dm für mich als Arbeitgeber attraktiv macht")

    col_venn, col_text = split(1, 1.3, gap="large")

    with col_venn:
        html(f"""
        <div class="venn-wrap" style="min-height:400px;">
            <div class="venn-stage">
                <svg viewBox="0 0 520 400" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Venn-Diagramm: Meine Werte, dm's Kultur und die Rolle überschneiden sich">
                    <circle cx="210" cy="168" r="122" fill="{DM_LILA}" fill-opacity="0.42" stroke="{DM_LILA_DUNKEL}" stroke-width="1.5"></circle>
                    <circle cx="310" cy="168" r="122" fill="{DM_BLAU}" fill-opacity="0.32" stroke="{DM_BLAU}" stroke-width="1.5"></circle>
                    <circle cx="260" cy="245" r="122" fill="{DM_GOLD}" fill-opacity="0.30" stroke="{DM_GOLD}" stroke-width="1.5"></circle>
                </svg>
                <div class="venn-label werte">Meine Werte</div>
                <div class="venn-label kultur">dm's Kultur</div>
                <div class="venn-label rolle">Die Rolle</div>
            </div>
        </div>
        """)

    with col_text:
        html("""
        <div class="lead-box" style="min-height:400px; display:flex; align-items:center;">
            <p>
                Was mich überzeugt, ist die Kombination aus
                <b>eigenverantwortlichem Arbeiten</b> und einer
                <b>dialogischen Unternehmenskultur</b>, in der Vertrauen vor
                Kontrolle steht — eingebettet in eine <b>Firmenkultur</b>, die
                Fehler als Teil des gemeinsamen Wachstums begreift statt sie zu
                sanktionieren. Dazu kommt ein <b>Onboarding</b>, das einem Zeit
                gibt, wirklich anzukommen, und die Gewissheit, mit dm einen
                <b>sicheren Arbeitgeber</b> zu wählen. Am meisten reizt mich
                aber die <b>innovative Entwicklungsumgebung</b> im neuen
                SCDA-Team — genau dort möchte ich mitwirken, dass Kolleg:innen
                data-driven Entscheidungen treffen können.
            </p>
        </div>
        """)

    st.write("")
    praxisbeispiel_banner()

# ---------------------------------------------------------------------------
# TAB: WERDEGANG
# ---------------------------------------------------------------------------
with tab_werdegang:
    section_title("Karriere", "Werdegang")

    st.markdown("##### Berufserfahrung im Detail")

    col_search, col_filter = split(2, 1, gap="medium")
    with col_search:
        suche = st.text_input(
            "Suche (z. B. SQL, Redshift, Marketing,...)",
            "", placeholder="Suchbegriff eingeben …",
        )
    with col_filter:
        alle_tags_sorted = sorted({t for e in WERDEGANG_DATA for t in e["tags"]})
        gewaehlte_tags = st.multiselect("Nach Tool filtern", alle_tags_sorted, placeholder="Toolliste öffnen")

    def _treffer(eintrag: dict) -> bool:
        haystack = " ".join(
            [eintrag["titel"], eintrag["firma"], *eintrag["bullets"], *eintrag["tags"]]
        ).lower()
        if suche and suche.lower() not in haystack:
            return False
        if gewaehlte_tags and not any(t in eintrag["tags"] for t in gewaehlte_tags):
            return False
        return True

    gefiltert = [e for e in WERDEGANG_DATA if _treffer(e)]

    if suche or gewaehlte_tags:
        st.caption(f"{len(gefiltert)} von {len(WERDEGANG_DATA)} Stationen zeigen einen Treffer.")

    if not gefiltert:
        st.info("Keine Station passt zu diesem Filter — probier einen anderen Begriff oder ein anderes Tool.")
    else:
        items_html = ""
        for e in gefiltert:
            bullets_html = "".join(f"<li>{b}</li>" for b in e["bullets"])
            tags_html = "".join(f'<span class="tag">{t}</span>' for t in e["tags"])
            items_html += f"""
            <div class="wg-item {e['farbe']}">
                <div class="wg-card">
                    <h4>{e['titel']}</h4>
                    <div class="wg-meta">
                        <span class="company">{e['firma']}</span>
                        <span class="wg-dot">·</span>
                        <span class="wg-pill">{e['zeit']}</span>
                    </div>
                    <ul>{bullets_html}</ul>
                    <div class="wg-tags">{tags_html}</div>
                </div>
            </div>
            """
        html(f"""<div class="timeline-track">{items_html}</div>""")

    st.write("")
    st.write("")
    st.markdown("##### Ausbildung")
    st.write("")

    col_e1, col_e2 = split(1, 1, gap="medium")
    for col, a in zip((col_e1, col_e2), AUSBILDUNG_DATA):
        with col:
            html(f"""
            <div class="edu-card">
                <div class="years-pill">{a['jahre']}</div>
                <div class="degree">{a['degree']}</div>
                <div class="inst">{a['inst']}</div>
            </div>
            """)

    st.write("")
    st.write("")
    praxisbeispiel_banner()

# ---------------------------------------------------------------------------
# TAB: SKILLS & TOOLS
# ---------------------------------------------------------------------------
with tab_skills:
    section_title("Werkzeuge", "Skills & Tools")

    st.markdown("#### Skill-Abgleich mit der Stellenanzeige")

    _covered = [t for t, ok in KOMPETENZ_ABGLEICH if ok]
    _gaps = [t for t, ok in KOMPETENZ_ABGLEICH if not ok]
    _quote = len(_covered) / len(KOMPETENZ_ABGLEICH) * 100

    col_pct, col_list = split(1, 2, gap="large")
    with col_pct:
        html(f"""
        <div class="metric-tile" style="--accent:{DM_LILA_DUNKEL}; height:auto;">
            <div class="m-label">Fachliche Abdeckung</div>
            <div class="m-value">{_quote:.0f}%</div>
            <div class="m-delta">{len(_covered)} von {len(KOMPETENZ_ABGLEICH)} Bereichen</div>
        </div>
        """)
    with col_list:
        _covered_html = "".join(
            f'<span class="tag tag-tooltip" data-tooltip="{KOMPETENZ_ERFAHRUNG.get(t, "").replace(chr(34), "&quot;")}">{t}</span>'
            for t in _covered
        )
        _gap_html = "".join(
            f'<span class="tag" style="opacity:0.55; border-style:dashed;">{t}</span>' for t in _gaps
        )
        html(f"""
        <div class="skillcard" style="--accent:{DM_LILA};">
            <h4>Fachliche Kompetenzbereiche</h4>
            {_covered_html}
            <div class="subgroup">Noch ausbaufähig</div>
            {_gap_html}
        </div>
        """)
        st.caption("Zum Hovern über einen Bereich: kurze Begründung als Tooltip.")

    st.write("")
    st.write("")
    st.markdown("#### Werkzeugkasten im Detail")

    row1 = split_n(3, gap="medium")
    with row1[0]:
        html("""
        <div class="skillcard" style="--accent:#0C3D91;">
            <h4>Datenanalyse & Modellierung</h4>
            <span class="tag">SQL</span>
            <span class="tag">Python</span>
            <div class="subgroup">Bibliotheken</div>
            <span class="tag">Pandas</span>
            <span class="tag">NumPy</span>
            <span class="tag">scikit-learn</span>
            <span class="tag">Matplotlib</span>
            <span class="tag">Seaborn</span>
            <div class="subgroup">Programme & Versionierung</div>
            <span class="tag">VS Code</span>
            <span class="tag">DBeaver</span>
            <span class="tag">Git</span>
        </div>
        """)
    with row1[1]:
        html("""
        <div class="skillcard" style="--accent:#8B6FD6;">
            <h4>Data Engineering & Orchestrierung</h4>
            <span class="tag">Redshift</span>
            <span class="tag">MongoDB</span>
            <span class="tag">MySQL</span>
            <span class="tag">BigQuery</span>
            <span class="tag">AWS S3 (Grundkenntnisse)</span>
            <span class="tag">dbt</span>
            <span class="tag">Airflow</span>
            <span class="tag">Adverity</span>
        </div>
        """)
    with row1[2]:
        html("""
        <div class="skillcard" style="--accent:#0C3D91;">
            <h4>BI & Visualisierung</h4>
            <span class="tag">Tableau</span>
            <span class="tag">Metabase</span>
            <span class="tag">Looker</span>
            <span class="tag">Power BI</span>
            <span class="tag">Excel</span>
            <span class="tag">Google Sheets</span>
        </div>
        """)

    st.write("")
    row2 = split_n(3, gap="medium")
    with row2[0]:       
        _sp_covered = [s for s, ok in SPRACH_PROGRAMM_SKILLS if ok]
        _sp_covered_html = "".join(f'<span class="tag">{s}</span>' for s in _sp_covered)
        html(f"""
        <div class="skillcard" style="--accent:#0C3D91;">
            <h4>Sprache & Programmierung</h4>
            {_sp_covered_html}
            <span class="tag">ChatGPT / Claude</span>
        </div>
        """)
    with row2[1]:
        html("""
        <div class="skillcard" style="--accent:#8B6FD6;">
            <h4>Arbeitsweise</h4>
            <span class="tag">Data Strategy</span>
            <span class="tag">Dashboard Design</span>
            <span class="tag">A/B-Testing</span>
            <span class="tag">Self Service Analytics</span>
            <span class="tag">Semantic Layer</span>
            <span class="tag tag-tooltip" data-tooltip="Bei OÖV aktiv umgesetzt: Sicherstellung der Datenschutz-Compliance bei allen Kampagnenaktivitäten. Und bei Tractive DSGVO Konzept für Speicherung/ Löschung von Daten für einen bestimmten Zeitpunkt/ Zweck.">DSGVO / Datenschutz</span>
        </div>
        """)
    with row2[2]:
        html("""
        <div class="skillcard" style="--accent:#0C3D91;">
            <h4>Projektmanagement & Kollaboration</h4>
            <span class="tag">Jira</span>
            <span class="tag">Bitbucket</span>
            <span class="tag">Confluence</span>
            <span class="tag">Slack</span>
            <span class="tag">Google Suite</span>
        </div>
        """)

    st.write("")

    # -----------------------------------------------------------------
    # Option 1: SQL Insights
    # -----------------------------------------------------------------
    st.write("")
    st.markdown("#### SQL live ausführen")
    st.caption(
        "Kleine In-Memory-Datenbank aus dem Werdegang mit sqlite3"
    )

    @st.cache_resource
    def _sql_demo_connection():
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        conn.execute("""
            CREATE TABLE stationen (
                reihenfolge INTEGER PRIMARY KEY,
                station TEXT,
                firma TEXT,
                zeitraum TEXT
            )
        """)
        conn.execute("CREATE TABLE einsatz (station TEXT, tool TEXT)")
        for idx, e in enumerate(WERDEGANG_DATA):
            conn.execute(
                "INSERT INTO stationen VALUES (?, ?, ?, ?)",
                (idx, e["titel"], e["firma"], e["zeit"]),
            )
            for t in e["tags"]:
                conn.execute("INSERT INTO einsatz VALUES (?, ?)", (e["titel"], t))
        conn.commit()
        return conn

    _conn = _sql_demo_connection()

 
    _SQL_PRESETS = {
        "JOIN — Tools je Station mit Zeitraum": (
            "SELECT s.firma, s.zeitraum, e.tool\n"
            "FROM einsatz e\n"
            "JOIN stationen s ON e.station = s.station\n"
            "ORDER BY s.reihenfolge, e.tool;"
        ),
        "SELF-JOIN — welche Tools habe ich firmenübergreifend mitgenommen?": (
            "SELECT e1.tool, s1.firma AS firma_a, s2.firma AS firma_b\n"
            "FROM einsatz e1\n"
            "JOIN einsatz e2\n"
            "  ON e1.tool = e2.tool AND e1.station < e2.station\n"
            "JOIN stationen s1 ON e1.station = s1.station\n"
            "JOIN stationen s2 ON e2.station = s2.station\n"
            "ORDER BY e1.tool;"
        ),
        "WINDOW FUNCTION — kumulierter Werkzeugkasten über die Karriere": (
            "SELECT s.reihenfolge, s.firma,\n"
            "       COUNT(e.tool) AS tools_diese_station,\n"
            "       SUM(COUNT(e.tool)) OVER (ORDER BY s.reihenfolge) AS kumulierte_tools\n"
            "FROM stationen s\n"
            "JOIN einsatz e ON e.station = s.station\n"
            "GROUP BY s.reihenfolge, s.firma\n"
            "ORDER BY s.reihenfolge;"
        ),
        "SUBQUERY — Tools, die bei Tractive neu dazukamen": (
            "SELECT tool\n"
            "FROM einsatz\n"
            "WHERE station = (SELECT station FROM stationen WHERE reihenfolge = 0)\n"
            "  AND tool NOT IN (\n"
            "      SELECT tool FROM einsatz e2\n"
            "      JOIN stationen s2 ON e2.station = s2.station\n"
            "      WHERE s2.reihenfolge > 0\n"
            "  );"
        ),
    }
    _sql_auswahl = st.selectbox("Abfrage wählen", list(_SQL_PRESETS.keys()))
    _sql = _SQL_PRESETS[_sql_auswahl]
    st.code(_sql, language="sql")
    _df_sql_result = pd.read_sql_query(_sql.rstrip(";"), _conn)
    st.dataframe(_df_sql_result, hide_index=True, width="stretch")

    # -----------------------------------------------------------------
    # Option 2: Selbsteinschätzung
    # -----------------------------------------------------------------
    st.write("")
    st.write("")
    st.markdown("#### Kompetenzprofil (Selbsteinschätzung)")
    st.caption("Eigene Einschätzung, zur Einordnung")

    _RADAR_ACHSEN = [
        ("SQL", 4),
        ("Dashboarding", 5),
        ("Stakeholder-<wbr>Kommunikation", 5),
        ("Data Modeling", 4),
        ("Python", 4),
    ]
    _RADAR_MAX = 5
    _n = len(_RADAR_ACHSEN)
    _cx, _cy, _r, _vb = 150, 150, 110, 300

    def _radar_punkt(i, anteil):
        winkel = math.radians(-90 + i * (360 / _n))
        return _cx + math.cos(winkel) * _r * anteil, _cy + math.sin(winkel) * _r * anteil

    _ring_svg = "".join(
        f'<circle cx="{_cx}" cy="{_cy}" r="{_r * f:.1f}" fill="none" stroke="#E9E6F5" stroke-width="1"></circle>'
        for f in (0.2, 0.4, 0.6, 0.8, 1.0)
    )

    _achsen_svg = ""
    _poly_pts = []
    _dots_svg = ""
    _label_html = ""
    for i, (name, wert) in enumerate(_RADAR_ACHSEN):
        x_end, y_end = _radar_punkt(i, 1.0)
        _achsen_svg += f'<line x1="{_cx}" y1="{_cy}" x2="{x_end:.1f}" y2="{y_end:.1f}" stroke="#E9E6F5" stroke-width="1"></line>'
        x_val, y_val = _radar_punkt(i, wert / _RADAR_MAX)
        _poly_pts.append(f"{x_val:.1f},{y_val:.1f}")
        _dots_svg += f'<circle cx="{x_val:.1f}" cy="{y_val:.1f}" r="4" fill="{DM_LILA_DUNKEL}"></circle>'

        left_pct, top_pct = x_end / _vb * 100, y_end / _vb * 100
        tx = "-50%" if 35 < left_pct < 65 else ("-100%" if left_pct <= 35 else "0%")
        ty = "-100%" if top_pct < 35 else ("0%" if top_pct > 65 else "-50%")
        _label_html += (
            f'<div class="radar-label" style="left:{left_pct:.1f}%; top:{top_pct:.1f}%; '
            f'transform:translate({tx}, {ty});">{name}<br><span class="radar-value">{wert}/{_RADAR_MAX}</span></div>'
        )

    _polygon_svg = (
        f'<polygon points="{" ".join(_poly_pts)}" fill="{DM_LILA}" '
        f'fill-opacity="0.35" stroke="{DM_LILA_DUNKEL}" stroke-width="2"></polygon>'
    )

    html(f"""
    <div class="radar-wrap">
        <div class="radar-stage">
            <svg viewBox="0 0 {_vb} {_vb}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Radar-Chart Kompetenzprofil">
                {_ring_svg}
                {_achsen_svg}
                {_polygon_svg}
                {_dots_svg}
            </svg>
            {_label_html}
        </div>
    </div>
    """)
    st.write("")
    praxisbeispiel_banner()

# ---------------------------------------------------------------------------
# FOOTER: Kontakt-Leiste, CV-Download & Kompakt-Toggle
# ---------------------------------------------------------------------------
st.write("")
html('<hr class="footer-divider">')

st.toggle(
    "Kompakte Ansicht",
    key="kompakt",
    help=(
        "Reduziert die Spaltenzahl auf der ganzen Seite auf eine Spalte — "
        "simuliert, wie sich das Layout auf einem schmalen Bildschirm verhält."
    ),
)

col_contact, col_download = split(2, 1, gap="large")

#with col_contact:
#    html(f"""
#    <div class="contact-bar">
#        <a href="{LINKEDIN_URL}" target="_blank" class="contact-pill">
#           <span class="badge">in</span> LinkedIn
#        </a>
#        <a href="{GITHUB_URL}" target="_blank" class="contact-pill">
#            <span class="badge">&lt;/&gt;</span> GitHub
#        </a>
#        <a href="mailto:{EMAIL_ADDRESS}" class="contact-pill">
#            <span class="badge">@</span> E-Mail
#        </a>
#   </div>
#    """)

