"""
Simulationsdaten für das Supply-Chain-Praxisbeispiel
=======================================================
"""

from __future__ import annotations

import math
from datetime import date, timedelta

import numpy as np
import pandas as pd

RNG_SEED = 42

# ---------------------------------------------------------------------------
# Stammdaten: Hub + 12 Länder der Ländergruppe (real: dm Österreich + die
# 11 Verbundenen Länder Bosnien-Herzegowina, Bulgarien, Kroatien, Italien,
# Nordmazedonien, Rumänien, Serbien, Slowakei, Slowenien, Tschechien, Ungarn).
# Koordinaten = grobe Näherung (Hauptstadt bzw. Enns fuer den Hub), nur zur
# Illustration auf der Karte - keine echten Distributionsrouten.
# ---------------------------------------------------------------------------
HUB = {"ort": "Verteilzentrum Enns", "lat": 48.2167, "lon": 14.4667}

# Reale Filialzahlen je Land (Quelle: https://www.dm.at/unternehmen/zahlen-und-fakten/unternehmenszahlen,
# Stand Geschäftsjahr 2024/25 - letztlich auf dm's eigenem Geschäftsbericht
# basierend). Wird als Gewichtung für Kartengröße/Liniendicke und als
# Sampling-Wahrscheinlichkeit für die simulierten Sendungen verwendet -
# eine reale Kennzahl statt einer frei erfundenen "Gewicht"-Spalte.
# https://content.services.dmtech.com/rootpage-dm-shop-de-at/resource/blob/219560/52f5ee02fc60b2c44d5a5967539af036/unternehmenszahlen-download-data.pdf
FILIALEN_JE_LAND = {
    "Österreich": 381,
    "Tschechien": 261,
    "Ungarn": 258,
    "Kroatien": 180,
    "Slowakei": 162,
    "Slowenien": 98,
    "Serbien": 136,
    "Rumänien": 167,
    "Bulgarien": 118,
    "Bosnien-Herzegowina": 94,
    "Nordmazedonien": 24,
    "Italien": 92,
}
FILIALEN_QUELLE = (
    "https://www.dm.at/unternehmen/zahlen-und-fakten/unternehmenszahlen (dm Presseinformation Geschäftsjahr 2024/25"
)

# EU-Mitgliedschaft je Land - real, relevant für Zoll-/Grenzrisiko bei der
# Liefertreue-Simulation (Serbien, Bosnien-Herzegowina, Nordmazedonien sind KEINE EU-Mitglieder, Waren queren dort eine Zollgrenze).
EU_MITGLIED = {
    "Österreich", "Tschechien", "Ungarn", "Kroatien", "Slowakei",
    "Slowenien", "Rumänien", "Bulgarien", "Italien",
}

# Koordinaten bleiben Landeshauptstädte als grobe geografische Anker für die
# Kartendarstellung (echte dm-Verteilzentren je Land sind öffentlich nicht 
# dokumentiert - Ausnahme: Enns/AT und Páty/HU, siehe real_intermodal_beispiel()).
_KOORDINATEN = {
    "Österreich": (48.2082, 16.3738),
    "Tschechien": (50.0755, 14.4378),
    "Ungarn": (47.4979, 19.0402),
    "Kroatien": (45.8150, 15.9819),
    "Slowakei": (48.1486, 17.1077),
    "Slowenien": (46.0569, 14.5058),
    "Serbien": (44.7866, 20.4489),
    "Rumänien": (44.4268, 26.1025),
    "Bulgarien": (42.6977, 23.3219),
    "Bosnien-Herzegowina": (43.8563, 18.4131),
    "Nordmazedonien": (41.9981, 21.4254),
    "Italien": (45.4642, 9.1900),
}

_MAX_FILIALEN = max(FILIALEN_JE_LAND.values())

COUNTRIES = [
    dict(
        land=land,
        lat=lat,
        lon=lon,
        filialen=FILIALEN_JE_LAND[land],
        gewicht=round(FILIALEN_JE_LAND[land] / _MAX_FILIALEN, 3),
        eu_mitglied=land in EU_MITGLIED,
    )
    for land, (lat, lon) in _KOORDINATEN.items()
]

KATEGORIEN = [
    "Babypflege", "Kosmetik", "Sonnenschutz", "Tiernahrung", "Drogeriebedarf",
    "Erkältungs- & Grippemittel", "Allergie & Heuschnupfen", "Weihnachtsartikel",
]
SPEDITEURE = ["Post AT", "DPD", "GLS", "Interne Flotte"]

# Grobe, oeffentlich dokumentierte Richtwerte fuer CO2 pro Tonnenkilometer
# (aggregierte Literaturwerte, keine dm-spezifische Messung):
CO2_FAKTOR_G_PRO_TKM = {
    "LKW (Diesel)": 62,
    "LKW (klein, Nahverkehr)": 90,
    "Bahn (Güterzug)": 22,
}


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Luftlinien-Distanz in km (Haversine-Formel)."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def countries_with_distance() -> pd.DataFrame:
    """Länder-Stammdaten inkl. Distanz zum Hub Enns (für Karte C und CO2 D)."""
    rows = []
    for c in COUNTRIES:
        dist = haversine_km(HUB["lat"], HUB["lon"], c["lat"], c["lon"])
        rows.append({**c, "distanz_km": round(dist)})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# A) Nachfrage-/Absatzdaten für die Prognose
# ---------------------------------------------------------------------------
def generate_sales_data(seed: int = RNG_SEED, days: int = 730) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    start = date.today() - timedelta(days=days)
    dates = pd.date_range(start, periods=days, freq="D")

    rows = []
    for kategorie in KATEGORIEN:
        basis = rng.uniform(90, 220)
        jahres_amplitude = rng.uniform(0.15, 0.4)
        phase = rng.uniform(0, 2 * np.pi)
        wochentag_muster = rng.uniform(0.88, 1.18, size=7)
        trend_pro_tag = rng.uniform(0.0001, 0.00035)

        for i, d in enumerate(dates):
            saison = 1 + jahres_amplitude * np.sin(2 * np.pi * d.dayofyear / 365 + phase)
            if kategorie == "Sonnenschutz" and d.month in (5, 6, 7, 8):
                saison *= 1.7
            if kategorie == "Kosmetik" and d.month == 12:
                saison *= 1.5
            if kategorie == "Babypflege":
                saison *= 1.0  # ganzjährig stabil, kaum Saisonalität
            if kategorie == "Erkältungs- & Grippemittel" and d.month in (11, 12, 1, 2):
                saison *= 2.1  # ausgeprägte Wintersaison
            if kategorie == "Allergie & Heuschnupfen" and d.month in (3, 4, 5, 6):
                saison *= 1.9  # Pollensaison Frühjahr
            if kategorie == "Weihnachtsartikel" and d.month in (11, 12):
                saison *= 3.2 if d.month == 12 else 1.6  # sehr scharfe Spitze
            wochentag = wochentag_muster[d.weekday()]
            trend = 1 + trend_pro_tag * i
            rauschen = rng.normal(1.0, 0.09)
            wert = max(0.0, basis * saison * wochentag * trend * rauschen)
            rows.append((d, kategorie, round(wert, 1)))

    return pd.DataFrame(rows, columns=["datum", "kategorie", "absatz"])


def build_forecast_features(df_kat: pd.DataFrame) -> pd.DataFrame:
    """Feature-Engineering für ein Kategorie-Subset."""
    out = df_kat.copy().sort_values("datum").reset_index(drop=True)
    out["wochentag"] = out["datum"].dt.weekday
    out["monat"] = out["datum"].dt.month
    doy = out["datum"].dt.dayofyear
    out["saison_sin"] = np.sin(2 * np.pi * doy / 365)
    out["saison_cos"] = np.cos(2 * np.pi * doy / 365)
    out["lag_7"] = out["absatz"].shift(7)
    out["lag_14"] = out["absatz"].shift(14)
    out["rollmean_7"] = out["absatz"].shift(1).rolling(7).mean()
    return out.dropna().reset_index(drop=True)


def train_demand_model(df: pd.DataFrame, kategorie: str, test_tage: int = 60):
    """
    Trainiert ein einfaches RandomForest-Regressionsmodell je Kategorie.
    Zeitbasierter Split (letzte `test_tage` = Testset).
    Gibt (df_volle_historie_mit_vorhersage, kpis, feature_importance) zurück.
    """
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_absolute_error

    df_kat = df[df["kategorie"] == kategorie]
    feat = build_forecast_features(df_kat)

    feature_cols = ["wochentag", "monat", "saison_sin", "saison_cos", "lag_7", "lag_14", "rollmean_7"]
    split_idx = len(feat) - test_tage
    train, test = feat.iloc[:split_idx], feat.iloc[split_idx:]

    model = RandomForestRegressor(n_estimators=200, max_depth=8, random_state=RNG_SEED)
    model.fit(train[feature_cols], train["absatz"])

    pred = model.predict(test[feature_cols])
    fehler = test["absatz"] - pred

    mae = mean_absolute_error(test["absatz"], pred)
    mape = float(np.mean(np.abs(fehler / test["absatz"].replace(0, np.nan))) * 100)
    # WMAPE: gewichteter Fehler über die Gesamtmenge statt Durchschnitt der
    # Einzel-Prozentfehler - robuster bei Tagen mit sehr niedrigem Absatz und
    # in Handel/Forecasting die gebräuchlichere Variante als klassischer MAPE.
    wmape = float(np.sum(np.abs(fehler)) / np.sum(test["absatz"]) * 100)
    # Bias: vorzeichenbehafteter Fehler - zeigt, ob das Modell systematisch
    # über- (negativ) oder unterschätzt (positiv). Für Supply Chain wichtig,
    # weil Überbestand und Stockout unterschiedlich teure Fehler sind.
    bias = float(fehler.mean())
    kpis = dict(mae=mae, mape=mape, wmape=wmape, bias=bias)

    # Volle Historie (inkl. Trainingszeitraum) fürs Chart zurückgeben, damit
    # die Seite echte Kalendermonate zeigen kann statt nur ein 60-Tage-Fenster.
    result = feat[["datum", "absatz"]].copy()
    result["vorhersage"] = np.nan
    result.loc[test.index, "vorhersage"] = pred
    result["im_testzeitraum"] = result.index.isin(test.index)

    importances = pd.Series(model.feature_importances_, index=feature_cols).sort_values(ascending=False)

    return result, kpis, importances


# ---------------------------------------------------------------------------
# B) Sendungen / Liefertreue
# ---------------------------------------------------------------------------
SHIPMENTS_SEED = 6


def generate_shipments_data(seed: int = SHIPMENTS_SEED, n: int = 4000) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    laender_df = countries_with_distance()
    gewichte = laender_df["gewicht"].to_numpy()
    gewichte = gewichte / gewichte.sum()

    carrier_faktor = {"Post AT": 0.85, "DPD": 1.0, "GLS": 1.15, "Interne Flotte": 0.6}

    rows = []
    start = date.today() - timedelta(days=365)
    for i in range(n):
        land_row = laender_df.iloc[rng.choice(len(laender_df), p=gewichte)]
        carrier = rng.choice(SPEDITEURE)
        versand_datum = start + timedelta(days=int(rng.integers(0, 365)))
        quartal = (versand_datum.month - 1) // 3 + 1

        basis_risiko = 0.05 + (land_row["distanz_km"] / 2500) * 0.18
        saison_faktor = 1.35 if quartal == 4 else (1.1 if quartal == 2 else 1.0)
        # Nicht-EU-Länder (Serbien, Bosnien-Herzegowina, Nordmazedonien) queren
        # eine Zollgrenze - realistischer zusätzlicher Verzögerungsfaktor,
        # nicht nur "weiter weg = später".
        zoll_faktor = 1.25 if not land_row["eu_mitglied"] else 1.0
        risiko = min(0.55, basis_risiko * carrier_faktor[carrier] * saison_faktor * zoll_faktor)
        verspaetet = rng.random() < risiko
        verzug_tage = 0
        if verspaetet:
            verzug_tage = int(rng.integers(1, 5))
            if not land_row["eu_mitglied"]:
                verzug_tage += int(rng.integers(0, 2))  # Zollabfertigung kann zusätzlich verzögern

        rows.append({
            "sendung_id": i + 1,
            "land": land_row["land"],
            "distanz_km": land_row["distanz_km"],
            "eu_mitglied": bool(land_row["eu_mitglied"]),
            "spediteur": carrier,
            "versand_datum": versand_datum,
            "quartal": f"Q{quartal}",
            "verspaetet": verspaetet,
            "verzug_tage": verzug_tage,
        })

    return pd.DataFrame(rows)


def on_time_rate(df: pd.DataFrame, group_col: str | None = None) -> pd.DataFrame:
    """
    EINE zentrale Kennzahlen-Definition ('Semantic Layer'-Gedanke):
    On-Time-Rate = Anteil nicht verspäteter Sendungen.
    Wird sowohl gruppiert (nach Land/Spediteur) als auch ungruppiert genutzt,
    damit die Kennzahl garantiert überall gleich berechnet wird.
    """
    if group_col is None:
        rate = (~df["verspaetet"]).mean() * 100
        return pd.DataFrame({"on_time_rate": [round(rate, 1)]})

    grouped = df.groupby(group_col)["verspaetet"].apply(lambda s: round((~s).mean() * 100, 1))
    return grouped.reset_index(name="on_time_rate").sort_values("on_time_rate", ascending=False)


# ---------------------------------------------------------------------------
# D) CO2-Fußabdruck der Transportrouten
# ---------------------------------------------------------------------------
def real_intermodal_beispiel() -> dict:
    """
    Reales Beispiel (keine Simulation!): dm hat 2024 angekündigt, Lieferungen
    von Großhändler:innen aus Belgien, Deutschland, Frankreich und Schweden zu
    den Verteilzentren Enns (AT) und Páty (HU, dm Marken-Verteilzentrum)
    schrittweise auf die Schiene zu verlagern (Partner: LKW Walter,
    kombinierter Verkehr - nur Vor-/Nachlauf per LKW).
    Quelle: retailreport.at/dm-verlagert-logistik-auf-die-schiene (7.6.2024),
    logistik-express.com (dieselbe Meldung).
    """
    herkunftslaender = ["Belgien", "Deutschland", "Frankreich", "Schweden"]
    ziel_verteilzentren = ["Enns (AT)", "Páty (HU) – dm Marken-Verteilzentrum"]
    co2_einsparung_ab_2026_t = 700
    einsparung_pct_range = (60, 80)
    lieferanten_enns = 14
    lieferanten_paty = 13
    partner = "LKW Walter (kombinierter Schienen-/Straßenverkehr)"

    # Sanity-Check mit den eigenen (Literatur-)Emissionsfaktoren: bei einem
    # angenommenen Split von 90% Schiene / 10% LKW-Vor-/Nachlauf, wie es
    # "Großteil Schiene, nur Vor-/Nachlauf LKW" beschreibt. Die einzelnen
    # Rechenschritte werden mit zurückgegeben, damit die Seite sie transparent
    # zeigen kann statt nur das fertige Ergebnis.
    lkw_faktor = CO2_FAKTOR_G_PRO_TKM["LKW (Diesel)"]
    bahn_faktor = CO2_FAKTOR_G_PRO_TKM["Bahn (Güterzug)"]
    schiene_anteil = 0.9
    blend_faktor = schiene_anteil * bahn_faktor + (1 - schiene_anteil) * lkw_faktor
    eigene_einsparung_pct = round((1 - blend_faktor / lkw_faktor) * 100)

    return dict(
        herkunftslaender=herkunftslaender,
        ziel_verteilzentren=ziel_verteilzentren,
        co2_einsparung_ab_2026_t=co2_einsparung_ab_2026_t,
        einsparung_pct_range=einsparung_pct_range,
        lieferanten_enns=lieferanten_enns,
        lieferanten_paty=lieferanten_paty,
        partner=partner,
        schiene_anteil_angenommen=schiene_anteil,
        lkw_faktor=lkw_faktor,
        bahn_faktor=bahn_faktor,
        blend_faktor=round(blend_faktor, 1),
        eigene_einsparung_pct=eigene_einsparung_pct,
        quelle="retailreport.at/dm-verlagert-logistik-auf-die-schiene (7.6.2024)",
    )


# Konkrete, benannte Beispielstrecke statt eines Durchschnitts über 12 Länder
# mit frei gewürfeltem Ladungsgewicht je Land. Ziel: eine reale Filiale:
# dm in Futurum Brno, Vídeňská 100, 619 00 Brno-jih.
# Koordinaten: eine exakte Straßen-Geokodierung war über die verfügbaren
# Geocoding-Dienste nicht erreichbar (robots.txt-Sperren) - verwendet wird
# daher die reale, mit Quelle belegte Koordinate des Stadtteils, in dem die
# Adresse liegt (Přízřenice/Brno-jih, Postleitzahl 619 00 passt zur Adresse).
# Quelle: en.wikipedia.org/wiki/Přízřenice.
BEISPIEL_ZIEL = dict(
    ort="Brno-jih – Futurum (Vídeňská 100, 619 00)",
    lat=49.14417,
    lon=16.62250,
    koordinaten_quelle="en.wikipedia.org/wiki/Přízřenice",
)


def generate_co2_beispielroute(ladung_t: float = 10.0) -> pd.DataFrame:
    """CO2-Ausstoß nach Fahrzeugtyp für EINE konkrete, reale Strecke:
    Verteilzentrum Enns -> Brno-jih (Futurum). Distanz = Haversine-Luftlinie
    zwischen den beiden realen Koordinaten (keine echte Straßen-/Schienenroute,
    aber kein Zufallswert). Ladung ist eine ausgewiesene Annahme (10 Tonnen,
    typische Ladung für einen regionalen Verteil-LKW), keine Messung."""
    dist = haversine_km(HUB["lat"], HUB["lon"], BEISPIEL_ZIEL["lat"], BEISPIEL_ZIEL["lon"])
    rows = []
    for fahrzeug, faktor in CO2_FAKTOR_G_PRO_TKM.items():
        co2_kg = (dist * ladung_t * faktor) / 1000
        rows.append({
            "ziel": BEISPIEL_ZIEL["ort"],
            "fahrzeug": fahrzeug,
            "distanz_km": round(dist),
            "ladung_t": ladung_t,
            "co2_kg": round(co2_kg, 1),
        })
    return pd.DataFrame(rows)


# Reale Verladepunkte für die Kartendarstellung der Beispielstrecke: kein
# Straßen-/Schienenverlauf (der ist nicht öffentlich als Geodaten verfügbar),
# aber reale, mit Quelle belegte Orte statt einer erfundenen Route.
TERMINAL_ENNS = dict(
    ort="Container Terminal Enns/Ennshafen",
    lat=48.2327,
    lon=14.5078,
    quelle="de.wikipedia.org/wiki/Ennshafen",
)
TERMINAL_BRNO = dict(
    ort="Terminal Brno (ČD Cargo, Horní Heršpice)",
    lat=49.16500,
    lon=16.61333,
    quelle="en.wikipedia.org/wiki/Horní_Heršpice",
)


def generate_co2_routenpunkte() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Punkte + Teilstrecken für die Kartendarstellung: Terminal Enns/Ennshafen
    -> Terminal Brno (Bahn-Hauptlauf) -> Futurum-Filiale (kurzer LKW-Nachlauf
    innerhalb Brnos, da beide Terminal-Standorte im selben Stadtteil liegen).
    Alle drei Koordinaten sind reale, mit Quelle belegte Orte (siehe oben und
    BEISPIEL_ZIEL); die Strecken selbst sind Luftlinien, keine Bahn-/Straßen-
    geometrie."""
    punkte = pd.DataFrame([
        {"ort": TERMINAL_ENNS["ort"], "lat": TERMINAL_ENNS["lat"], "lon": TERMINAL_ENNS["lon"], "rolle": "Start"},
        {"ort": TERMINAL_BRNO["ort"], "lat": TERMINAL_BRNO["lat"], "lon": TERMINAL_BRNO["lon"], "rolle": "Umschlag"},
        {"ort": BEISPIEL_ZIEL["ort"], "lat": BEISPIEL_ZIEL["lat"], "lon": BEISPIEL_ZIEL["lon"], "rolle": "Ziel"},
    ])

    bahn_km = haversine_km(TERMINAL_ENNS["lat"], TERMINAL_ENNS["lon"], TERMINAL_BRNO["lat"], TERMINAL_BRNO["lon"])
    lkw_km = haversine_km(TERMINAL_BRNO["lat"], TERMINAL_BRNO["lon"], BEISPIEL_ZIEL["lat"], BEISPIEL_ZIEL["lon"])
    strecken = pd.DataFrame([
        {
            "etappe": "Bahn: Terminal Enns/Ennshafen → Terminal Brno",
            "von_lat": TERMINAL_ENNS["lat"], "von_lon": TERMINAL_ENNS["lon"],
            "bis_lat": TERMINAL_BRNO["lat"], "bis_lon": TERMINAL_BRNO["lon"],
            "distanz_km": round(bahn_km),
        },
        {
            "etappe": "LKW-Nachlauf: Terminal Brno → Futurum-Filiale",
            "von_lat": TERMINAL_BRNO["lat"], "von_lon": TERMINAL_BRNO["lon"],
            "bis_lat": BEISPIEL_ZIEL["lat"], "bis_lon": BEISPIEL_ZIEL["lon"],
            "distanz_km": round(lkw_km),
        },
    ])
    return punkte, strecken
