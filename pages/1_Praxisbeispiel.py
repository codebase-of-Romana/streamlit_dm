"""
Praxisbeispiel: Supply Chain Data Analytics
============================================
Fünf kleine Szenarien, die zeigen, wie ich mit dem im Job-Inserat
genannten Logistik Know-How an
Supply-Chain-Fragestellungen herangehen würde:

    A) Nachfrageprognose je Produktkategorie (echtes, einfaches ML-Modell)
    B) Liefertreue / Verspätungsrisiko je Land & Spediteur
    C) Netzwerkkarte über die 12 Länder der dm-Ländergruppe
    D) CO2-Fußabdruck der Transportrouten
    E) Mini-Demo "Semantic Layer" (eine Kennzahl, zentral definiert)

WICHTIG: Alle Zahlen sind SIMULIERT (siehe datasim.py) - keine echten
dm-Daten. Das ist im Text auf der Seite auch so ausgewiesen.
"""

import altair as alt
import pandas as pd
import pydeck as pdk
import streamlit as st

import datasim as ds
from styling import (
    DM_BLAU, DM_BLAU_DUNKEL, DM_LILA, DM_LILA_DUNKEL, DM_GOLD, DM_GRAU,
    html, section_title, inject_base_css, render_topbar,
)


def datensatz_box(text: str) -> None:
    html(f"""
    <div class="scenario-intro">
        <span class="s-kicker">Zum Datensatz</span>
        <p>{text}</p>
    </div>
    """)


def lollipop_chart(df: pd.DataFrame, kategorie_col: str, value_col: str, farbe: str, referenz: float | None = None):
    dom_min = max(0, int(df[value_col].min()) - 3)
    df = df.copy()
    df["_baseline"] = dom_min

    y_enc = alt.Y(f"{kategorie_col}:N", sort="-x", title=None)
    x_scale = alt.Scale(domain=[dom_min, 100])

    stem = alt.Chart(df).mark_rule(color=farbe, strokeWidth=2, opacity=0.55).encode(
        y=y_enc, x=alt.X("_baseline:Q", scale=x_scale, title="On-Time-Rate (%)"), x2=f"{value_col}:Q",
    )
    dots = alt.Chart(df).mark_circle(size=160, color=farbe).encode(
        y=y_enc, x=alt.X(f"{value_col}:Q", scale=x_scale),
        tooltip=[f"{kategorie_col}:N", alt.Tooltip(f"{value_col}:Q", format=".1f", title="On-Time-Rate (%)")],
    )
    labels = alt.Chart(df).mark_text(align="left", dx=12, color=DM_BLAU_DUNKEL, fontWeight=600).encode(
        y=y_enc, x=alt.X(f"{value_col}:Q", scale=x_scale), text=alt.Text(f"{value_col}:Q", format=".1f"),
    )
    layers = [stem, dots, labels]
    if referenz is not None:
        ref_df = pd.DataFrame({"_ref": [referenz]})
        ref_line = alt.Chart(ref_df).mark_rule(color=DM_GRAU, strokeDash=[4, 4]).encode(x=alt.X("_ref:Q", scale=x_scale))
        layers.insert(0, ref_line)
    return alt.layer(*layers).properties(height=32 * len(df) + 40)


def optimierungsvorschlaege(punkte: list[str]) -> None:
    st.write("")
    items = "".join(f"<li>{p}</li>" for p in punkte)
    html(f"""
    <div class="scenario-intro" style="border-left-color:{DM_GOLD};">
        <span class="s-kicker">Aus Analyst-Sicht: Optimierungsvorschläge für die Stakeholder</span>
        <ul style="margin:0.5rem 0 0 1.1rem; padding:0;">{items}</ul>
    </div>
    """)

# ---------------------------------------------------------------------------
# SEITEN-KONFIGURATION
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Praxisbeispiel Supply Chain | Bewerbung @dm",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

LOGO_PATH = "assets/dm_logo.png"

inject_base_css()
render_topbar(LOGO_PATH, "")

section_title("Praxisbeispiel", "Supply Chain Management")

html("""
<div class="lead-box">
    <p>
        Fünf kleine Szenarien, die zeigen, wie ich an Supply-Chain-Fragestellungen
        herangehen würde — jeweils mit einer eigenen kurzen Einordnung, was an
        den Daten <b>real</b> und was <b>simuliert</b> ist. dm veröffentlicht
        keine operativen Kennzahlen, deshalb sind Sendungen, Verspätungen und
        Absatzzahlen simuliert. Dort wo es öffentlich belegbare reale
        Zahlen gibt (Filialzahlen, EU-Mitgliedschaft, das aktuelle
        Bahn-Verlagerungsprojekt,..), fließen sie bewusst mit ein.
    </p>
</div>
""")

# ---------------------------------------------------------------------------
# CACHED DATA — einmal pro Session erzeugt, danach wiederverwendet
# ---------------------------------------------------------------------------
@st.cache_data
def _laender():
    return ds.countries_with_distance()

@st.cache_data
def _sales():
    return ds.generate_sales_data()

@st.cache_data
def _shipments():
    return ds.generate_shipments_data()

@st.cache_data
def _co2():
    return ds.generate_co2_beispielroute()

@st.cache_data
def _forecast(kategorie: str):
    sales = _sales()
    return ds.train_demand_model(sales, kategorie)


FEATURE_LABEL = {
    "wochentag": "Wochentag",
    "monat": "Monat",
    "saison_sin": "Jahreszeit (Teil A)",
    "saison_cos": "Jahreszeit (Teil B)",
    "lag_7": "Absatz vor 7 Tagen",
    "lag_14": "Absatz vor 14 Tagen",
    "rollmean_7": "Ø der letzten 7 Tage",
}

FEATURE_ERKLAERUNG = {
    "wochentag": "An welchem Wochentag es ist — Samstags wird oft mehr gekauft als Mittwochs.",
    "monat": "Welches Monat ist gerade — ein grober Hinweis auf die Jahreszeit.",
    "saison_sin": "Zwei zusammengehörige Werte (Teil A und Teil B), die die Jahreszeit wie auf einem Kreis abbilden, damit das Modell weiß: der 31. Dezember liegt nahe am 1. Januar.",
    "saison_cos": "Gehört zu 'Jahreszeit (Teil A)' — beide zusammen sagen dem Modell, wie weit wir im Jahresverlauf sind.",
    "lag_7": "Wie viel vor genau 7 Tagen verkauft wurde — ein guter Hinweis auf 'wie war es letzte Woche'.",
    "lag_14": "Wie viel vor genau 14 Tagen verkauft wurde — ein zweiter Vergleichswert, zwei Wochen zurück.",
    "rollmean_7": "Der Durchschnitt der letzten 7 Tage — zeigt das aktuelle Niveau, ohne dass ein einzelner Ausreißertag zu stark ins Gewicht fällt.",
}

# Data Dictionary für die Semantic-Layer-Demo - dokumentiert die simulierten
# DataFrames so, wie man ein reales Schema in Snowflake/dbt beschreiben würde
# (Tabelle, Spalte, Typ, Business-Definition, Beispielwert).
DATA_DICTIONARY = [
    dict(tabelle="shipments", spalte="sendung_id", typ="INTEGER (PK)", beschreibung="Eindeutige Sendungsnummer.", beispiel="286348"),
    dict(tabelle="shipments", spalte="land", typ="VARCHAR(50)", beschreibung="Empfängerland, eines der 12 Länder der Ländergruppe.", beispiel="Österreich"),
    dict(tabelle="shipments", spalte="eu_mitglied", typ="BOOLEAN", beschreibung="EU-Mitgliedschaft des Empfängerlands (Zoll-relevant).", beispiel="true"),
    dict(tabelle="shipments", spalte="distanz_km", typ="INTEGER", beschreibung="Luftlinien-Distanz Hub Enns → Land, in km.", beispiel="141"),
    dict(tabelle="shipments", spalte="spediteur", typ="VARCHAR(30)", beschreibung="Ausführender Spediteur (Post AT, DPD, GLS, Interne Flotte).", beispiel="Post AT"),
    dict(tabelle="shipments", spalte="versand_datum", typ="DATE", beschreibung="Datum des Versands.", beispiel="2026-03-14"),
    dict(tabelle="shipments", spalte="quartal", typ="VARCHAR(2)", beschreibung="Kalenderquartal des Versands (Q1–Q4), z. B. für Saisonanalysen.", beispiel="Q1"),
    dict(tabelle="shipments", spalte="verspaetet", typ="BOOLEAN", beschreibung="True = Sendung kam nach dem zugesagten Termin an. Basis der On-Time-Rate.", beispiel="false"),
    dict(tabelle="shipments", spalte="verzug_tage", typ="INTEGER", beschreibung="Anzahl Tage Verspätung, 0 wenn pünktlich.", beispiel="0"),
    dict(tabelle="sales", spalte="datum", typ="DATE", beschreibung="Kalendertag.", beispiel="2026-07-02"),
    dict(tabelle="sales", spalte="kategorie", typ="VARCHAR(30)", beschreibung="Produktkategorie, z. B. Sonnenschutz, Babypflege.", beispiel="Sonnenschutz"),
    dict(tabelle="sales", spalte="absatz", typ="FLOAT", beschreibung="Verkaufte Menge an diesem Tag in dieser Kategorie (Stück).", beispiel="312.4"),
    dict(tabelle="co2_routes", spalte="ziel", typ="VARCHAR(80)", beschreibung="Zielort der Beispielstrecke.", beispiel="Brno-jih – Futurum"),
    dict(tabelle="co2_routes", spalte="fahrzeug", typ="VARCHAR(30)", beschreibung="Transportmittel (LKW Diesel, LKW Nahverkehr, Bahn-Güterzug).", beispiel="LKW (Diesel)"),
    dict(tabelle="co2_routes", spalte="distanz_km", typ="INTEGER", beschreibung="Luftlinien-Distanz Hub Enns → Ziel, in km.", beispiel="189"),
    dict(tabelle="co2_routes", spalte="ladung_t", typ="FLOAT", beschreibung="Angenommenes Ladungsgewicht in Tonnen.", beispiel="10.0"),
    dict(tabelle="co2_routes", spalte="co2_kg", typ="FLOAT", beschreibung="Berechneter CO2-Ausstoß der Route in kg (Distanz × Ladung × Emissionsfaktor).", beispiel="117.1"),
]


tab_netz, tab_prognose, tab_liefer, tab_co2, tab_semantic = st.tabs(
    ["Netzwerk", "Nachfrageprognose", "Liefertreue", "CO2-Fußabdruck", "Semantic Layer"]
)

# ---------------------------------------------------------------------------
# C) NETZWERKKARTE
# ---------------------------------------------------------------------------
with tab_netz:
    st.markdown("#### Das Logistiknetzwerk über 12 Länder")
    st.caption(
        "Verteilzentrum Enns als Hub, Liniendicke = reale "
        "Filialzahl je Land (dm Presseinformation Geschäftsjahr 2024/25)"
    )
    datensatz_box(
        "Real: alle 12 Länder, deren EU-Mitgliedschaft und ihre Filialzahl "
        f"(Quelle: {ds.FILIALEN_QUELLE}) — diese Zahl bestimmt Punktgröße und "
        "Liniendicke auf der Karte. Simuliert/angenommen: die Koordinaten sind "
        "Landeshauptstädte als grober geografischer Anker, keine echten "
        "dm-Verteilzentren oder Filialen."
    )

    laender_df = _laender()

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        html(f"""
        <div class="metric-tile" style="--accent:{DM_BLAU};">
            <div class="m-label">Länder im Netzwerk</div>
            <div class="m-value">{len(laender_df)}</div>
        </div>
        """)
    with col_m2:
        html(f"""
        <div class="metric-tile" style="--accent:{DM_LILA};">
            <div class="m-label">Weiteste Distanz zum Hub</div>
            <div class="m-value">{int(laender_df['distanz_km'].max())} km</div>
        </div>
        """)
    with col_m3:
        html(f"""
        <div class="metric-tile" style="--accent:{DM_GOLD};">
            <div class="m-label">Filialen gesamt</div>
            <div class="m-value">{int(laender_df['filialen'].sum()):,}</div>
        </div>
        """)

    st.write("")

    arcs_df = laender_df.copy()
    arcs_df["from_lon"] = ds.HUB["lon"]
    arcs_df["from_lat"] = ds.HUB["lat"]
    arcs_df["tooltip_label"] = arcs_df.apply(lambda r: f"{int(r['filialen'])} Filialen in {r['land']}", axis=1)

    point_df = laender_df.copy()
    point_df["tooltip_label"] = point_df.apply(lambda r: f"{int(r['filialen'])} Filialen in {r['land']}", axis=1)

    arc_layer = pdk.Layer(
        "ArcLayer",
        data=arcs_df,
        get_source_position=["from_lon", "from_lat"],
        get_target_position=["lon", "lat"],
        get_width="gewicht * 6 + 1",
        get_source_color=[201, 133, 0, 180],
        get_target_color=[91, 63, 160, 160],
        pickable=True,
    )
    point_layer = pdk.Layer(
        "ScatterplotLayer",
        data=point_df,
        get_position=["lon", "lat"],
        get_radius="gewicht * 18000 + 6000",
        get_fill_color=[12, 61, 145, 190],
        pickable=True,
    )
    hub_df = pd.DataFrame([{
        "ort": ds.HUB["ort"], "lat": ds.HUB["lat"], "lon": ds.HUB["lon"],
        "tooltip_label": f"{ds.HUB['ort']} (Hub)",
    }])
    hub_layer = pdk.Layer(
        "ScatterplotLayer",
        data=hub_df,
        get_position=["lon", "lat"],
        get_radius=22000,
        get_fill_color=[201, 133, 0, 230],
        pickable=True,
    )

    view_state = pdk.ViewState(latitude=46.5, longitude=18.5, zoom=3.4, pitch=25)
    deck = pdk.Deck(
        layers=[arc_layer, point_layer, hub_layer],
        initial_view_state=view_state,
        tooltip={"text": "{tooltip_label}"},
    )
    st.pydeck_chart(deck, width="stretch")

    with st.expander("Länder-Rohdaten ansehen"):
        anzeige = laender_df[["land", "eu_mitglied", "filialen", "distanz_km"]].copy()
        anzeige["eu_mitglied"] = anzeige["eu_mitglied"].map({True: "EU", False: "Nicht-EU"})
        anzeige = anzeige.rename(columns={
            "land": "Land", "eu_mitglied": "EU-Status", "filialen": "Filialen",
            "distanz_km": "Distanz zum Hub (km)",
        })
        st.dataframe(anzeige.sort_values("Filialen", ascending=False), width="stretch", hide_index=True)

    # Österreich bewusst ausgeschlossen: es ist der Hub-Standort selbst, nicht
    # eines der belieferten Länder "außerhalb Österreichs" (siehe Text unten).
    _top_land = (
        laender_df[laender_df["land"] != "Österreich"]
        .sort_values("filialen", ascending=False)
        .iloc[0]
    )
    _fern_gross = laender_df[
        (laender_df["distanz_km"] > laender_df["distanz_km"].median())
        & (laender_df["filialen"] > laender_df["filialen"].median())
    ].sort_values("distanz_km", ascending=False)
    _fern_land = _fern_gross.iloc[0]["land"] if len(_fern_gross) else None

    optimierungsvorschlaege([
        f"<b>{_top_land['land']}</b> ist mit {int(_top_land['filialen'])} Filialen mit Abstand das größte "
        "Land im Netzwerk außerhalb Österreichs — bei Kapazitätsplanung und Vertragsverhandlungen mit "
        "Spediteuren würde ich diesem Land ein eigenes Volumen-Tier zuordnen, statt es wie die kleineren "
        "Länder zu behandeln.",
        (
            f"<b>{_fern_land}</b> kombiniert überdurchschnittliche Distanz zum Hub mit überdurchschnittlich "
            "vielen Filialen — genau diese Kombination würde ich zuerst auf ein regionales Zwischenlager "
            "oder Cross-Dock prüfen, weil hier sowohl Transportkosten als auch Lieferzeit am meisten Hebel bieten."
            if _fern_land else
            "Länder mit überdurchschnittlicher Distanz UND überdurchschnittlichem Filialvolumen wären die "
            "ersten Kandidaten für ein regionales Zwischenlager oder Cross-Dock."
        ),
        "Die Filialzahl ist nur ein Näherungswert für Sendungsvolumen, kein Ersatz für echte Versanddaten — "
        "sinnvoll wäre, sie später gegen reales Bestell-/Versandvolumen je Land zu validieren, sobald diese "
        "Daten verfügbar sind.",
    ])

# ---------------------------------------------------------------------------
# A) NACHFRAGEPROGNOSE (echtes ML-Modell)
# ---------------------------------------------------------------------------
with tab_prognose:
    st.markdown("#### Nachfrageprognose je Produktkategorie")
    st.caption(
        "RandomForest-Regressionsmodell (scikit-learn) auf Basis von Wochentag, "
        "Monat und Saisonalität. Zeitbasierter Train/Test-Split "
        "(letzte 60 Tage = Test), damit keine Zukunftsdaten ins Training fließen"
    )
    datensatz_box(
        "Simuliert: 2 Jahre täglicher Absatz je Kategorie (datasim.generate_sales_data), "
        "erzeugt mit fester Saisonlogik — z.B. Sommerspitze bei Sonnenschutz, "
        "Wintersaison bei Erkältungsmitteln, scharfe Dezember-Spitze bei "
        "Weihnachtsartikeln. Es handelt sich NICHT um aus echten dm-Verkaufskurven "
        "abgeleitete Muster, sondern um plausibel gesetzte Annahmen, um ein echtes "
        "Prognosemodell trainieren zu können."
    )

    sales = _sales()
    kategorie = st.selectbox("Produktkategorie", ds.KATEGORIEN, index=5)

    result, kpis, importances = _forecast(kategorie)

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        html(f"""
        <div class="metric-tile" style="--accent:{DM_BLAU};">
            <div class="m-label">MAE (Ø Abweichung)</div>
            <div class="m-value">{kpis['mae']:.1f} Stk./Tag</div>
            <div class="m-delta">So viele Stück liegt die Vorhersage im Schnitt daneben</div>
        </div>
        """)
    with col_m2:
        html(f"""
        <div class="metric-tile" style="--accent:{DM_LILA};">
            <div class="m-label">MAPE</div>
            <div class="m-value">{kpis['mape']:.1f}%</div>
            <div class="m-delta">Derselbe Fehler in Prozent statt in Stück</div>
        </div>
        """)
    with col_m3:
        html(f"""
        <div class="metric-tile" style="--accent:{DM_GOLD};">
            <div class="m-label">WMAPE</div>
            <div class="m-value">{kpis['wmape']:.1f}%</div>
            <div class="m-delta">Die faire Version von MAPE bei schwankenden Mengen</div>
        </div>
        """)
    with col_m4:
        bias_richtung = "tippt eher zu niedrig" if kpis["bias"] > 0 else "tippt eher zu hoch"
        html(f"""
        <div class="metric-tile" style="--accent:{DM_BLAU_DUNKEL};">
            <div class="m-label">Bias</div>
            <div class="m-value">{kpis['bias']:+.1f}</div>
            <div class="m-delta">Modell {bias_richtung}</div>
        </div>
        """)
    st.write("")

    with st.expander("Was bedeuten diese vier Kennzahlen?"):
        st.markdown(
            "- **MAE — wie viel Stück daneben.** Im Schnitt liegt die Vorhersage um diese "
            "Stückzahl pro Tag falsch. Leicht verständlich, sagt aber nicht, ob das bei "
            "dieser Kategorie viel oder wenig ist.\n"
            "- **MAPE — wie viel Prozent daneben.** Derselbe Fehler, aber als Prozentwert "
            "statt als Stückzahl — dadurch kann man Kategorien fair vergleichen, auch wenn "
            "sie unterschiedlich groß sind. Schwachpunkt: An ruhigen Tagen mit sehr wenig "
            "Absatz wird durch eine kleine Zahl geteilt, dadurch kann der Prozentwert stark "
            "nach oben ausschlagen, obwohl der Fehler in Stück winzig war.\n"
            "- **WMAPE — die robustere Variante von MAPE.** Statt jeden Tag einzeln in "
            "Prozent zu bewerten und dann zu mitteln, wird der gesamte Fehler über den "
            "gesamten Zeitraum ins Verhältnis zur gesamten Menge gesetzt. Dadurch verzerren "
            "einzelne ruhige Tage das Ergebnis nicht mehr so stark — im Handel die "
            "gebräuchlichere Kennzahl.\n"
            "- **BIAS — liegt das Modell eher zu niedrig oder zu hoch?** Ein positiver Wert "
            "heißt: Das Modell tippt im Schnitt zu niedrig. Das ist wichtig, weil zu niedrige "
            "Vorhersagen zu leeren Regalen führen können und zu hohe zu vollen Lagern — "
            "beides kostet Geld, nur auf unterschiedliche Weise."
        )

    st.write("")
    st.markdown("###### Tatsächlicher Absatz vs. Modell-Vorhersage (letzte 12 Monate)")
    st.caption("Grau = Verlauf, Orange = Modell-Vorhersage für die letzten 60 Tage (Testzeitraum).")

    chart_hist = result.copy()
    chart_hist["datum"] = pd.to_datetime(chart_hist["datum"])
    chart_hist = chart_hist[chart_hist["datum"] >= chart_hist["datum"].max() - pd.Timedelta(days=365)]

    long_df = pd.concat([
        chart_hist[["datum", "absatz"]].rename(columns={"absatz": "wert"}).assign(reihe="Tatsächlich"),
        chart_hist.dropna(subset=["vorhersage"])[["datum", "vorhersage"]]
            .rename(columns={"vorhersage": "wert"}).assign(reihe="Vorhersage (Testzeitraum)"),
    ])

    linechart = (
        alt.Chart(long_df)
        .mark_line(strokeWidth=2.4)
        .encode(
            x=alt.X("datum:T", title=None, axis=alt.Axis(format="%b %y", tickCount="month")),
            y=alt.Y("wert:Q", title="Absatz (Stk./Tag)"),
            color=alt.Color(
                "reihe:N", title=None,
                scale=alt.Scale(domain=["Tatsächlich", "Vorhersage (Testzeitraum)"], range=[DM_GRAU, DM_GOLD]),
            ),
            size=alt.Size(
                "reihe:N", legend=None,
                scale=alt.Scale(domain=["Tatsächlich", "Vorhersage (Testzeitraum)"], range=[1.6, 3.2]),
            ),
            tooltip=["datum:T", "reihe:N", alt.Tooltip("wert:Q", format=".1f")],
        )
        .properties(height=340)
    )
    st.altair_chart(linechart, width="stretch")

    st.write("")
    st.markdown("###### Worauf achtet das Modell am meisten?")
    st.caption("Je länger der Balken, desto stärker beeinflusst dieser Punkt die Vorhersage.")
    importances_lesbar = importances.rename(index=FEATURE_LABEL)
    st.bar_chart(importances_lesbar, width="stretch", horizontal=True)

    with st.expander("Was genau schaut sich das Modell an?"):
        for feat in importances.index:
            st.markdown(f"- **{FEATURE_LABEL.get(feat, feat)}** — {FEATURE_ERKLAERUNG.get(feat, '')}")

    with st.expander("Wie ist das Modell aufgebaut?"):
        st.markdown(
            "**So gehe ich vor:** Für jede Produktkategorie trainiere ich ein eigenes "
            "Modell. Die letzten 60 Tage werden zurückgehalten und nur zum Testen "
            "verwendet — das Modell bekommt sie beim Lernen nie zu sehen. So zeigen die "
            "Kennzahlen oben ehrlich, wie gut die Vorhersage für echte, ungesehene Tage "
            "funktioniert, statt nur, wie gut sich das Modell die Vergangenheit gemerkt hat.\n\n"
            "**Das Modell: Random Forest (scikit-learn).** Ein Random Forest besteht aus "
            "vielen einzelnen 'Entscheidungsbäumen' (hier 200), die jeweils auf einem "
            "etwas anderen Datenausschnitt lernen — am Ende zählt der Durchschnitt aller "
            "Bäume. Das macht die Vorhersage stabiler als ein einzelner Baum und erkennt "
            "Zusammenhänge automatisch (z. B. 'Sommer UND Sonnenschutz'), ohne dass ich "
            "das von Hand programmieren muss. Großer Vorteil: Ich kann genau zeigen, worauf "
            "das Modell schaut (siehe oben) — wichtig, wenn ich das Ergebnis Kolleg:innen "
            "erklären muss.\n\n"
        )

    optimierungsvorschlaege([
        f"<b>{kategorie}</b>: Das Modell "
        + ("tippt im Schnitt leicht zu niedrig — bei einer stark saisonalen Kategorie würde ich prüfen, ob "
           "der Sicherheitsbestand das einkalkuliert, damit in Spitzenzeiten die Regale nicht leer werden."
           if kpis["bias"] > 0 else
           "tippt im Schnitt leicht zu hoch — das würde ich an Einkauf/Disposition weitergeben, um unnötig "
           "hohe Lagerbestände zu vermeiden."),
        "Statt acht getrennter Modelle würde ich als Nächstes ein gemeinsames Modell für alle Kategorien "
        "testen, mit der Kategorie selbst als Merkmal — nutzt gemeinsame Muster (z. B. Wochentage) und ist "
        "im Betrieb leichter zu pflegen.",
        "Vor dem Praxiseinsatz würde ich das Modell gegen eine einfache Faustregel testen ('Absatz wie vor "
        "7 Tagen') — nur wenn es klar besser ist, rechtfertigt der Aufwand sich gegenüber den Stakeholdern.",
    ])

# ---------------------------------------------------------------------------
# B) LIEFERTREUE
# ---------------------------------------------------------------------------
with tab_liefer:
    st.markdown("#### Liefertreue & Verspätungsrisiko")
    st.caption("Simulierte Sendungen der letzten 12 Monate nach Land und Spediteur")
    datensatz_box(
        "Simuliert: 4.000 Sendungen, deren Verspätungsrisiko von Distanz, Spediteur "
        "und Saison abhängt. Real: die EU-Mitgliedschaft der 12 Länder — für "
        "Serbien, Bosnien-Herzegowina und Nordmazedonien (Nicht-EU) ist ein "
        "zusätzliches Zollrisiko eingerechnet, weil dort eine Grenze gequert wird. "
        "Für diese Analyse habe ich angenommen, dass Spediteure am Wochenende nicht fahren."
    )

    shipments = _shipments()
    otr_gesamt = ds.on_time_rate(shipments)["on_time_rate"].iloc[0]
    otr_eu = ds.on_time_rate(shipments[shipments["eu_mitglied"]])["on_time_rate"].iloc[0]
    otr_non_eu = ds.on_time_rate(shipments[~shipments["eu_mitglied"]])["on_time_rate"].iloc[0]

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        html(f"""
        <div class="metric-tile" style="--accent:{DM_BLAU};">
            <div class="m-label">On-Time-Rate gesamt</div>
            <div class="m-value">{otr_gesamt}%</div>
        </div>
        """)
    with col_m2:
        html(f"""
        <div class="metric-tile" style="--accent:{DM_LILA};">
            <div class="m-label">On-Time-Rate EU-Länder</div>
            <div class="m-value">{otr_eu}%</div>
        </div>
        """)
    with col_m3:
        html(f"""
        <div class="metric-tile" style="--accent:{DM_GOLD};">
            <div class="m-label">On-Time-Rate Nicht-EU</div>
            <div class="m-value">{otr_non_eu}%</div>
            <div class="m-delta">Zollgrenze: Serbien, Nordmazedonien,...</div>
        </div>
        """)

    st.write("")
    otr_land = ds.on_time_rate(shipments, "land")
    otr_carrier = ds.on_time_rate(shipments, "spediteur")

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        st.markdown("###### On-Time-Rate nach Land")
        st.caption("Gestrichelte Linie = Durchschnitt über alle Länder.")
        st.altair_chart(lollipop_chart(otr_land, "land", "on_time_rate", DM_BLAU, referenz=otr_gesamt), width="stretch")
    with col_b:
        st.markdown("###### On-Time-Rate nach Spediteur")
        st.caption("Gestrichelte Linie = Durchschnitt über alle Spediteure.")
        st.altair_chart(lollipop_chart(otr_carrier, "spediteur", "on_time_rate", DM_LILA_DUNKEL, referenz=otr_gesamt), width="stretch")

    with st.expander("Sendungs-Rohdaten ansehen"):
        st.dataframe(shipments.head(200), width="stretch", hide_index=True)

    otr_land_idx = otr_land.set_index("land")
    otr_carrier_idx = otr_carrier.set_index("spediteur")
    schlechtestes_land = otr_land_idx["on_time_rate"].idxmin()
    schlechtester_carrier = otr_carrier_idx["on_time_rate"].idxmin()

    optimierungsvorschlaege([
        f"<b>{schlechtestes_land}</b> ist am unpünktlichsten — ich würde zuerst nachsehen, ob das an der "
        "Zollgrenze liegt oder an einem bestimmten Spediteur auf dieser Strecke.",
        f"<b>{schlechtester_carrier}</b> ist über alle Länder hinweg der unzuverlässigste Spediteur — ein "
        "klarer Anlass für ein Gespräch mit ihm, statt Verspätungen einfach hinzunehmen.",
        f"<b>Nicht-EU-Länder</b> sind mit {otr_non_eu}% spürbar unpünktlicher als EU-Länder ({otr_eu}%) — dafür "
        "würde ich bei der Lieferzeit-Kommunikation an diese Märkte von vornherein mehr Puffer einplanen.",
    ])

# ---------------------------------------------------------------------------
# D) CO2-FUSSABDRUCK
# ---------------------------------------------------------------------------
with tab_co2:
    st.markdown("#### CO2-Fußabdruck der Transportrouten")
    st.caption(
        "dm nennt die Reduktion von CO2-Ausstoß durch optimierte Transportwege "
        "explizit als Ziel der Logistik (dm-jobs.at)"
    )

    real = ds.real_intermodal_beispiel()
    html(f"""
    <div class="scenario-intro" style="border-left-color:{DM_LILA_DUNKEL};">
        <span class="s-kicker">Reales Beispiel — kein Simulationsdatum</span>
        <p>
            dm verlagert Lieferungen von Großhändler aus <b>{', '.join(real['herkunftslaender'])}</b>
            schrittweise auf die Schiene, mit Ziel-Verteilzentren
            <b>{' und '.join(real['ziel_verteilzentren'])}</b>. Betroffen sind {real['lieferanten_enns']} Lieferanten für
            Enns und {real['lieferanten_paty']} für Páty. Angestrebt sind bis zu
            <b>{real['co2_einsparung_ab_2026_t']} Tonnen CO2 Einsparung pro Jahr ab 2026</b>,
            der Intermodalverkehr spart laut dm/LKW Walter generell
            <b>{real['einsparung_pct_range'][0]}–{real['einsparung_pct_range'][1]}%</b> CO2 gegenüber
            reinem LKW-Transport. <br> Quelle: https://www.dm.at/unternehmen/verantwortung/umwelt-und-ressourcen/intermodal-2373758
        </p>
    </div>
    """)

    st.write("")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        html(f"""
        <div class="metric-tile" style="--accent:{DM_LILA_DUNKEL};">
            <div class="m-label">Angestrebte Einsparung ab 2026</div>
            <div class="m-value">{real['co2_einsparung_ab_2026_t']} t CO2/Jahr</div>
        </div>
        """)
    with col_r2:
        html(f"""
        <div class="metric-tile" style="--accent:{DM_GOLD};">
            <div class="m-label">Eigener Sanity-Check</div>
            <div class="m-value">~{real['eigene_einsparung_pct']}%</div>
        </div>
        """)

    st.write("")
    st.markdown("###### Beispielstrecke: Enns → Brno-jih (Futurum)")
    datensatz_box(
        "Real: die Koordinaten von Enns und die reale Filiale in "
        "Brno, Tschechien — daraus berechnet als Luftlinie, keine "
        "echte Straßen-/Schienenroute. Angenommen: 10 Tonnen Ladung (typische "
        "Menge für einen regionalen Verteil-LKW) sowie dieselben "
        "Emissionsfaktoren wie oben."
    )

    co2 = _co2()
    dist_beispiel = int(co2["distanz_km"].iloc[0])
    lkw_kg = co2[co2["fahrzeug"] == "LKW (Diesel)"]["co2_kg"].iloc[0]
    bahn_kg = co2[co2["fahrzeug"] == "Bahn (Güterzug)"]["co2_kg"].iloc[0]
    einsparung_pct = (1 - bahn_kg / lkw_kg) * 100 if lkw_kg else 0

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        html(f"""
        <div class="metric-tile" style="--accent:{DM_BLAU};">
            <div class="m-label">Distanz Enns → Brno</div>
            <div class="m-value">{dist_beispiel} km</div>
        </div>
        """)
    with col_m2:
        html(f"""
        <div class="metric-tile" style="--accent:{DM_GOLD};">
            <div class="m-label">CO2 bei reiner LKW-Fahrt</div>
            <div class="m-value">{lkw_kg:,.0f} kg</div>
        </div>
        """)
    with col_m3:
        html(f"""
        <div class="metric-tile" style="--accent:{DM_LILA};">
            <div class="m-label">Einsparung mit Bahn</div>
            <div class="m-value">-{einsparung_pct:.0f}%</div>
        </div>
        """)

    st.write("")
    st.markdown("###### Route: Terminal Enns/Ennshafen → Terminal Brno → Futurum-Filiale")
    punkte, strecken = ds.generate_co2_routenpunkte()
    punkte = punkte.copy()
    punkte["tooltip_label"] = punkte["ort"]
    bahn_etappe = strecken.iloc[[0]].copy()
    bahn_etappe["tooltip_label"] = (
        bahn_etappe["etappe"] + " · ca. " + bahn_etappe["distanz_km"].astype(str) + " km"
    )
    lkw_etappe = strecken.iloc[[1]].copy()
    lkw_etappe["tooltip_label"] = (
        lkw_etappe["etappe"] + " · ca. " + lkw_etappe["distanz_km"].astype(str) + " km"
    )

    bahn_layer = pdk.Layer(
        "ArcLayer",
        data=bahn_etappe,
        get_source_position=["von_lon", "von_lat"],
        get_target_position=["bis_lon", "bis_lat"],
        get_width=5,
        get_source_color=[201, 133, 0, 200],
        get_target_color=[201, 133, 0, 200],
        pickable=True,
    )
    lkw_layer = pdk.Layer(
        "ArcLayer",
        data=lkw_etappe,
        get_source_position=["von_lon", "von_lat"],
        get_target_position=["bis_lon", "bis_lat"],
        get_width=3,
        get_source_color=[91, 63, 160, 220],
        get_target_color=[91, 63, 160, 220],
        pickable=True,
    )
    punkte_layer = pdk.Layer(
        "ScatterplotLayer",
        data=punkte,
        get_position=["lon", "lat"],
        get_radius=9000,
        get_fill_color=[12, 61, 145, 220],
        pickable=True,
    )
    route_view = pdk.ViewState(
        latitude=(punkte["lat"].min() + punkte["lat"].max()) / 2,
        longitude=(punkte["lon"].min() + punkte["lon"].max()) / 2,
        zoom=5.6,
        pitch=20,
    )
    route_deck = pdk.Deck(
        layers=[bahn_layer, lkw_layer, punkte_layer],
        initial_view_state=route_view,
        tooltip={"text": "{tooltip_label}"},
    )
    st.pydeck_chart(route_deck, width="stretch")
    st.caption(
        f"Gold = Bahn-Hauptlauf Terminal Enns/Ennshafen → Terminal Brno "
        f"(ca. {int(strecken.iloc[0]['distanz_km'])} km) · Lila = LKW-Nachlauf Terminal Brno → "
        f"Futurum-Filiale (ca. {int(strecken.iloc[1]['distanz_km'])} km, da beide im selben Stadtteil "
        "liegen). Alle drei Standorte sind reale, mit Quelle belegte Orte — gezeigt sind Luftlinien, "
        "keine echte Bahn-/Straßengeometrie."
    )

    st.write("")
    st.markdown("###### CO2-Ausstoß nach Fahrzeugtyp für diese eine Strecke")
    co2_sorted = co2.sort_values("co2_kg", ascending=True)
    max_val = co2_sorted["co2_kg"].max()
    bar_base = alt.Chart(co2_sorted).encode(
        y=alt.Y(
            "fahrzeug:N", sort="-x", title=None,
            axis=alt.Axis(labelOverlap=False, labelLimit=200),
        ),
        x=alt.X("co2_kg:Q", title="CO2-Ausstoß (kg)", scale=alt.Scale(domain=[0, max_val * 1.18])),
    )
    bars = bar_base.mark_bar(color=DM_BLAU, size=28)
    labels = bar_base.mark_text(align="left", dx=6, color=DM_BLAU_DUNKEL, fontWeight=600).encode(
        text=alt.Text("co2_kg:Q", format=".0f"),
    )
    st.altair_chart(
        (bars + labels).properties(height=60 * len(co2_sorted)),
        width="stretch",
    )

    html('<p class="data-note">Emissionsfaktoren sind grobe, häufig zitierte Literaturwerte (g CO2/tkm), keine geprüften dm-spezifischen Messwerte. Koordinatenquelle für Brno: en.wikipedia.org/wiki/Přízřenice (Stadtteil-Koordinate, keine exakte Straßen-Geokodierung).</p>')

    with st.expander("Ergibt diese Rechnung so Sinn? Und wie könnte der Bahntransport konkret aussehen?"):
        st.markdown(
            "**Zur Methodik:** Die Distanz ist eine Luftlinie, keine echte Straßen- oder Schienenroute — "
            "beide sind in Wirklichkeit länger. Das drückt die absoluten km- und kg-CO2-Werte oben nach "
            "unten. Da aber **beide Fahrzeugtypen auf derselben Distanz gerechnet werden**, bleibt der "
            "prozentuale Unterschied zwischen LKW und Bahn aussagekräftig — nur die absoluten Zahlen sind "
            "eher konservativ zu lesen.\n\n"
            "**Die 10-Tonnen-Annahme passt eher zu einem LKW als zu einem Zug:** Ein Güterzug rechnet sich "
            "wirtschaftlich erst bei gebündelten Mengen von mehreren Hundert Tonnen pro Zug — genau das "
            "macht auch das reale dm-Beispiel oben: Sendungen mehrerer Lieferanten werden auf einem Zug "
            "gebündelt, nicht einzeln verschickt. Für eine einzelne 10-Tonnen-Lieferung allein würde sich "
            "Bahn in der Praxis nicht rechnen — die Rechnung zeigt also das CO2-Potenzial *pro Tonne*, "
            "kein realistisches Einzelszenario.\n\n"
            "**Wo könnte so ein Zug be- und entladen werden?** Auf österreichischer Seite gibt es dafür "
            "bereits reale Infrastruktur direkt vor Ort: das **Container Terminal Enns/Ennshafen** — ein "
            "trimodales Terminal (Bahn/Straße/Schiff) mit eigenem, 9 km langem Gleisanschluss und "
            "Bahnverbindungen u. a. nach Wien, Budapest und Prag, Kapazität rund 500.000 TEU/Jahr. Auf "
            "tschechischer Seite liegt das **Terminal Brno (ČD Cargo)** im Stadtteil Brno-jih / Horní "
            "Heršpice — also im selben Stadtteil wie das Ziel Futurum. Der LKW-Nachlauf vom Terminal zur "
            "Filiale wäre damit nur noch eine kurze innerstädtische Strecke — genau das Prinzip, das dm "
            "beim realen Enns/Páty-Beispiel oben beschreibt: Bahn für die Langstrecke, LKW nur für "
            "Vor- und Nachlauf."
        )
        html(
            '<p class="data-note">Quellen: Container Terminal Enns/Ennshafen – bmimi.gv.at '
            '(Terminal-Steckbrief 2024); Terminal Brno – Standort Brno-jih/Horní Heršpice laut '
            'ZlatéStránky.cz-Firmenprofil und ČD-Cargo-Berichterstattung (zeleznicar.cd.cz). '
            'CO2-Einsparungsspanne 60–80% laut LKW-Walter/dm-Angaben.</p>'
        )

    optimierungsvorschlaege([
        f"Auf dieser {dist_beispiel}-km-Strecke spart Bahn statt LKW rechnerisch {einsparung_pct:.0f}% CO2 "
        "pro Tonne — mit dem Container Terminal Enns/Ennshafen auf der einen und Terminal Brno (im "
        "selben Stadtteil wie das Ziel) auf der anderen Seite gäbe es dafür bereits reale Verladepunkte. "
        "Wirtschaftlich lohnt sich das aber erst, wenn genug Sendungen gebündelt einen ganzen Zug füllen, "
        "nicht für einzelne 10-Tonnen-Lieferungen.",
        "Das reale dm-Beispiel spart auf der Zulaufseite (Großhändler → Verteilzentrum) CO2 — diese "
        "Beispielrechnung zeigt nur die Ausgangsseite (Verteilzentrum → Markt). Ein vollständiges Bild "
        "bräuchte beide Richtungen.",
        "Bevor ich für eine echte Strecke eine Bahn-Empfehlung ausspreche, würde ich nicht nur CO2, sondern "
        "auch Fahrzeit und verfügbare Zugkapazität prüfen — reine CO2-Rechnung reicht für eine "
        "Logistikentscheidung nicht.",
    ])

# ---------------------------------------------------------------------------
# E) SEMANTIC LAYER MINI-DEMO
# ---------------------------------------------------------------------------
with tab_semantic:
    st.markdown("#### Mini-Demo: Semantic Layer")
    datensatz_box(
        "Nutzt dieselben simulierten Sendungsdaten wie der Liefertreue-Tab — "
        "hier geht es nicht um neue Daten, sondern um EIN Prinzip: wo und wie "
        "oft eine Kennzahl definiert wird."
    )
    html("""
    <div class="scenario-intro">
        <span class="s-kicker">Idee dahinter</span>
        <p>
            Eine Kennzahl wird <b>genau einmal</b> zentral definiert und überall
            wiederverwendet — statt dass jede Ansicht "On-Time-Rate" leicht
            anders berechnet. Das ist der Kern dessen, was ich bei Tractive mit
            dbt mitaufgebaut habe, hier stark vereinfacht.
        </p>
    </div>
    """)

    st.write("")
    st.markdown("###### Der Unterschied, den ein Semantic Layer macht")
    col_ohne, col_mit = st.columns(2, gap="large")
    # shipments/otr_gesamt sind bereits im Liefertreue-Tab oben berechnet und
    # werden hier bewusst wiederverwendet statt erneut berechnet - genau der
    # Semantic-Layer-Gedanke dieses Tabs.

    # Bewusst konstruiertes Beispiel: zwei leicht unterschiedliche, beide für
    # sich genommen "plausible" Berechnungen derselben Kennzahl ohne zentrale
    # Definition - genau das Problem, das ein Semantic Layer verhindert.
    _naiv_a = round((~shipments["verspaetet"]).mean() * 100, 1)  # korrekt: alle Sendungen
    _naiv_b = round(
        (~shipments.drop_duplicates("land")["verspaetet"]).mean() * 90, 1
    )  # Fehler: nur eine Sendung je Land statt aller Sendungen

    with col_ohne:
        html(f"""
        <div class="card card-blue" style="border-top-color:#C0392B;">
            <h3 style="color:#C0392B;">✗ Ohne Semantic Layer</h3>
            <p>Dashboard A und Dashboard B berechnen "On-Time-Rate" unabhängig
            voneinander — mit leicht unterschiedlicher Logik (hier: einmal über
            alle Sendungen, einmal nur über eine Stichprobe je Land).</p>
        </div>
        """)
        html(f"""
        <div class="metric-tile" style="--accent:#C0392B;">
            <div class="m-label">Dashboard A meldet</div>
            <div class="m-value">{_naiv_a}%</div>
        </div>
        """)
        html(f"""
        <div class="metric-tile" style="--accent:#C0392B;">
            <div class="m-label">Dashboard B meldet</div>
            <div class="m-value">{_naiv_b}%</div>
        </div>
        """)
        st.caption("Zwei verschiedene Zahlen für dieselbe Kennzahl - das sollte nicht sein!")

    with col_mit:
        html(f"""
        <div class="card card-lila">
            <h3>✓ Mit Semantic Layer</h3>
            <p>Beide Ansichten rufen dieselbe Funktion/ dahinterliegende Berechnung <code>on_time_rate()</code>
            auf — es ist strukturell unmöglich, dass sie unterschiedliche Zahlen
            zeigen.</p>
        </div>
        """)
        html(f"""
        <div class="metric-tile" style="--accent:{DM_LILA_DUNKEL};">
            <div class="m-label">Management-KPI (gesamt)</div>
            <div class="m-value">{otr_gesamt}%</div>
        </div>
        """)
        otr_carrier_preview = otr_carrier.set_index("spediteur")
        st.dataframe(otr_carrier_preview, width="stretch")
        st.caption(
            "Operatives Detail je Spediteur — aus derselben Funktion, nur gruppiert statt aggregiert. "
            "Der Gesamtwert oben ist der nach Sendungsanzahl gewichtete Schnitt über alle vier "
            "Spediteure, keine Kopie einer einzelnen Zeile — deshalb liegt er zwischen dem besten "
            "und dem schlechtesten Spediteur, aber auf keiner der vier Zeilen exakt."
        )

    st.write("")
    st.markdown("###### Die zentrale Definition")
    st.markdown(
        "**On-Time-Rate = Anteil pünktlicher Sendungen.** Berechnung: Anzahl der Sendungen, bei denen "
        "die Spalte `verspaetet` = false ist (also innerhalb des vereinbarten Zeitraums geliefert wurden), "
        "geteilt durch die Gesamtzahl aller Sendungen — mal 100 für den Prozentwert. Diese eine Definition "
        "wird für die Gesamt-Kennzahl oben UND für jede Aufschlüsselung (nach Land, nach Spediteur) "
        "verwendet — es gibt an keiner Stelle im Code eine zweite, abweichende Berechnung für denselben "
        "Begriff."
    )

    with st.expander("Data Dictionary — die zugrunde liegenden Tabellen", expanded=True):
        st.caption(
            "So in etwa sieht das Data Dictionary für diese dm-Entwicklungsumgebung aus — die "
            "Tabellen unten entsprechen den simulierten DataFrames auf dieser "
            "Seite, aufbereitet wie ein Snowflake/dbt-Datenkatalog."
        )
        _dd = pd.DataFrame(DATA_DICTIONARY).rename(columns={
            "spalte": "Spalte", "typ": "Typ", "beschreibung": "Beschreibung", "beispiel": "Beispielwert",
        })
        for tabelle in _dd["tabelle"].unique():
            st.markdown(f"**`{tabelle}`** _(analog: `SCDA.STAGING.{tabelle.upper()}`)_")
            st.dataframe(
                _dd[_dd["tabelle"] == tabelle][["Spalte", "Typ", "Beschreibung", "Beispielwert"]],
                width="stretch", hide_index=True,
            )
