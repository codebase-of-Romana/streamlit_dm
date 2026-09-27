"""
esign-System für alle Seiten der Bewerbungs-App.
================================================================
Wird von Über_mich.py und von pages/*.py importiert, damit Farben, Fonts
und Karten-Stile an einer Stelle gepflegt werden.
"""

import os           #für os.path.exists (Logo-Check in render_topbar)
import textwrap     #für Container
import streamlit as st

# ---------------------------------------------------------------------------
# FARBEN (dm-CI, Lila als Leitfarbe)
# ---------------------------------------------------------------------------
DM_BLAU = "#0C3D91"
DM_BLAU_DUNKEL = "#082A63"
DM_LILA = "#8B6FD6"
DM_LILA_DUNKEL = "#5B3FA0"
DM_LILA_HELL = "#F1EEFC"
DM_GOLD = "#C98500"
DM_TEXT = "#1F2430"
DM_GRAU = "#6B7280"


def html(block: str) -> None:
#rendert rohes HTML
    dedented = textwrap.dedent(block).strip("\n")
    stripped_lines = [line.lstrip() for line in dedented.splitlines()]
    st.markdown("\n".join(stripped_lines), unsafe_allow_html=True)


def section_title(kicker: str, title: str) -> None:
    html(f"""
    <div class="section-title">
        <span class="section-kicker">{kicker}</span>
        <h2>{title}</h2>
    </div>
    """)


def inject_base_css() -> None:
    """Einmal pro Seite ganz oben aufrufen."""
    html(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Manrope', 'Segoe UI', sans-serif;
        color: {DM_TEXT};
    }}

    .stApp {{
        background:
            radial-gradient(750px circle at 92% -10%, rgba(139,111,214,0.14), transparent 60%),
            radial-gradient(650px circle at -10% 100%, rgba(12,61,145,0.06), transparent 55%),
            #fbfaff;
        background-attachment: fixed;
    }}

    h1, h2, h3, h4 {{ font-family: 'Manrope', sans-serif; color: {DM_BLAU}; font-weight: 700; }}
    p, li {{ line-height: 1.65; color: {DM_TEXT}; }}

    /* ---- Seiten-Menü Sidebar (Über mich / Praxisbeispiel) ---- */
    [data-testid="stSidebarNavLink"] p {{
        font-size: 1.08rem !important;
        font-weight: 700 !important;
    }}

    /* ---- Haupt-Tabs (Über mich/Werdegang/Skills & Tools, Netzwerk/Nachfrageprognose/... ) ---- */
    [data-testid="stTab"] p {{
        font-size: 1.05rem !important;
        font-weight: 700 !important;
    }}

    /* ---- Top-Bar mit Logo ---- */
    .topbar {{ display:flex; align-items:center; gap:1.1rem; padding: 0.2rem 0 1.3rem 0; }}
    .dm-logo {{
        display:inline-flex; flex-direction:column; align-items:flex-start;
        background:#ffffff; border-radius:14px; padding:0.5rem 1rem 0.4rem;
        box-shadow: 0 10px 24px -12px rgba(30,20,70,0.35);
    }}
    .dm-logo .letters {{ font-size:1.5rem; font-weight:800; letter-spacing:-0.5px; color:{DM_BLAU}; line-height:1; }}
    .dm-logo .wave {{ width:36px; height:5px; margin-top:5px; border-radius:3px; background: linear-gradient(90deg, {DM_LILA}, {DM_BLAU}); }}
    .topbar .role-label {{ font-size:1.15rem; font-weight:600; color:{DM_TEXT}; }}

    /* ---- Hero ---- */
    .hero {{
        background: #ffffff;
        border-left: 4px solid {DM_BLAU};
        border-radius: 4px 20px 20px 4px;
        padding: 2.5rem 2.9rem 2rem 2.9rem;
        box-shadow: 0 20px 44px -30px rgba(30,20,70,0.4);
        container-type: inline-size;
    }}
    .hero .kicker {{ font-size:0.76rem; font-weight:700; letter-spacing:0.09em; text-transform:uppercase; color:{DM_LILA_DUNKEL}; margin-bottom:0.9rem; display:block; }}
    .hero h1 {{ font-size:2.2rem; font-weight:700; color:{DM_BLAU_DUNKEL}; margin:0 0 0.3rem 0; }}
    .hero .role {{ font-size:1.06rem; font-weight:500; color:{DM_TEXT}; margin-bottom:1.1rem; }}
    .hero .rule {{ width:46px; height:3px; background:{DM_LILA}; border-radius:2px; margin:0 0 1.1rem 0; }}

    .hero-facts {{ display:flex; flex-wrap:wrap; gap:0; margin-top:1.4rem; padding-top:1.15rem; border-top:1px solid #ECE9F9; }}
    .hero-facts .fact {{ flex:1 1 240px; padding:0 1.4rem; border-left:1px solid #ECE9F9; }}
    .hero-facts .fact:first-child {{ border-left:none; padding-left:0; }}
    .hero-facts .flabel {{ font-size:0.7rem; text-transform:uppercase; letter-spacing:0.05em; color:{DM_LILA_DUNKEL}; font-weight:700; }}
    .hero-facts .fvalue {{ font-size:0.92rem; font-weight:600; color:{DM_TEXT}; margin-top:0.28rem; }}

    /* ---- Schmale Karte: hero-facts stapeln einheitlich statt seitlich
       getrennt. Container-Query statt Viewport-Media-Query, weil die
       tatsächliche Breite dieser Karte nicht am Bildschirm hängt, sondern
       auch von Sidebar-Zustand und der Foto-Spalte daneben abhängt - beides
       ändert sich unabhängig vom Viewport. ---- */
    @container (max-width: 768px) {{
        .hero-facts {{ flex-direction:column; }}
        .hero-facts .fact {{ border-left:none; padding:0.9rem 0 0 0; border-top:1px solid #ECE9F9; }}
        .hero-facts .fact:first-child {{ padding-top:0; border-top:none; }}
    }}

    /* ---- Wellen-Platzhalter ---- */
    .wave-divider {{ margin: -0.6rem 0 2rem 0; line-height:0; }}
    .wave-divider svg {{ width:100%; height:100px; display:block; }}

    /* ---- Foto-Platzhalter ---- */
    .photo-slot {{
        background:#ffffff; border:1px solid #E9E6F5; border-radius:20px; height:100%; min-height:220px;
        display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center;
        color:{DM_GRAU}; padding:1rem; box-shadow: 0 16px 34px -26px rgba(30,20,70,0.32);
    }}
    .photo-slot.has-photo {{ padding:0; overflow:hidden; }}
    .photo-slot.has-photo img {{
        width:100%; height:100%; min-height:220px; object-fit:cover;
        border-radius:19px; display:block;
    }}

    /* ---- Abschnitts-Überschriften ---- */
    .section-title {{ margin: 0.4rem 0 1.6rem 0; }}
    .section-kicker {{ font-size:0.74rem; font-weight:700; letter-spacing:0.09em; text-transform:uppercase; color:{DM_LILA_DUNKEL}; }}
    .section-title h2 {{ font-size:1.9rem; font-weight:800; color:{DM_BLAU_DUNKEL}; margin:0.25rem 0 0 0; }}

    /* ---- Lead-Box ---- */
    .lead-box {{
        background: {DM_LILA_HELL};
        border-left: 4px solid {DM_LILA};
        border-radius: 4px 16px 16px 4px;
        padding: 1.5rem 1.8rem;
        margin-bottom: 1.6rem;
    }}
    .lead-box p {{ font-size:1rem; color:#33324a; margin:0; }}

    /* ---- Karten ---- */
    .card {{ border-radius:20px; padding:1.7rem 1.9rem; margin-bottom:1.3rem; box-shadow:0 16px 34px -24px rgba(30,20,70,0.35); border-top:5px solid var(--accent, {DM_LILA}); height:100%; }}
    .card h3 {{ margin-top:0; font-size:1.16rem; font-weight:700; }}
    .card p {{ font-size:0.96rem; color:#3a3f4e; }}
    .card-blue {{ --accent: {DM_BLAU}; background: linear-gradient(180deg, #F2F5FC 0%, #ffffff 55%); }}
    .card-lila {{ --accent: {DM_LILA}; background: linear-gradient(180deg, {DM_LILA_HELL} 0%, #ffffff 55%); }}

    /* ---- Kachel-/Metrik-Karten (für Praxisbeispiel-Seite) ---- */
    .metric-tile {{ background:#fff; border-radius:14px; padding:1rem 1.2rem; box-shadow:0 10px 22px -20px rgba(30,20,70,0.3); height:100%; border-top:3px solid var(--accent, {DM_LILA}); }}
    .metric-tile .m-label {{ font-size:0.72rem; text-transform:uppercase; letter-spacing:0.05em; color:{DM_LILA_DUNKEL}; font-weight:700; }}
    .metric-tile .m-value {{ font-size:1.5rem; font-weight:800; color:{DM_TEXT}; margin-top:0.25rem; }}
    .metric-tile .m-delta {{ font-size:0.8rem; color:{DM_GRAU}; margin-top:0.2rem; }}

    /* ---- Venn-Diagramm ---- */
    .venn-wrap {{
        background:#ffffff; border-radius:20px; padding:1.4rem;
        box-shadow:0 16px 34px -24px rgba(30,20,70,0.35);
        margin-bottom:1.4rem; display:flex; justify-content:center;
    }}
    .venn-stage {{ position:relative; width:100%; max-width:460px; aspect-ratio:520/400; }}
    .venn-stage svg {{ position:absolute; inset:0; width:100%; height:100%; display:block; }}
    .venn-label {{ position:absolute; font-weight:700; font-size:0.92rem; font-family:'Manrope', sans-serif; white-space:nowrap; }}
    .venn-label.werte {{ left:19%; top:15%; color:{DM_LILA_DUNKEL}; }}
    .venn-label.kultur {{ right:12%; top:15%; color:{DM_BLAU_DUNKEL}; }}
    .venn-label.rolle {{ left:50%; bottom:1%; transform:translateX(-50%); color:#7a5c00; }}

    /* ---- Werdegang: zentrierte Punkt-Timeline ---- */
    .timeline-track {{ position:relative; margin-left:8px; padding-left:2.4rem; border-left:3px solid #E4DEF7; }}
    .wg-item {{ position:relative; margin-bottom:1.5rem; }}
    .wg-item:last-child {{ margin-bottom:0; }}
    .wg-item::before {{
        content:""; position:absolute; left:calc(-2.4rem - 10.5px); top:1.6rem;
        width:18px; height:18px; border-radius:50%;
        background: var(--dot, {DM_LILA_DUNKEL});
        border:3px solid #fbfaff;
        box-shadow: 0 0 0 2px var(--dot, {DM_LILA_DUNKEL}), 0 4px 10px -2px var(--dot, {DM_LILA_DUNKEL});
    }}
    .wg-item.blau {{ --dot: {DM_BLAU}; }}
    .wg-item.lila {{ --dot: {DM_LILA_DUNKEL}; }}
    .wg-item.lila-hell {{ --dot: {DM_LILA}; }}
    .wg-card {{ background:#ffffff; border-radius:18px; padding:1.3rem 1.7rem; box-shadow:0 14px 30px -24px rgba(30,20,70,0.32); }}
    .wg-card h4 {{ margin:0 0 0.35rem 0; font-size:1.18rem; font-weight:700; color:{DM_LILA}; }}
    .wg-meta {{ display:flex; align-items:center; gap:0.55rem; flex-wrap:wrap; margin-bottom:0.7rem; }}
    .wg-meta .company {{ font-size:1.18rem; font-weight:700; color:{DM_BLAU_DUNKEL}; }}
    .wg-meta .wg-dot {{ color:#c9c4de; }}
    .wg-pill {{ background:{DM_LILA_HELL}; color:{DM_LILA_DUNKEL}; font-size:0.78rem; font-weight:700; padding:0.22rem 0.75rem; border-radius:8px; white-space:nowrap; }}
    .wg-card ul {{ margin:0.3rem 0 0.7rem 0; padding-left:1.15rem; }}
    .wg-card li {{ font-size:0.92rem; margin-bottom:0.32rem; color:#3a3f4e; }}
    .wg-tags .tag {{ display:inline-block; background:#F5F5FA; color:{DM_TEXT}; border:1px solid #E4E4EF; font-size:0.76rem; font-weight:500; padding:0.16rem 0.62rem; border-radius:7px; margin:0.12rem 0.25rem 0 0; }}
    @media (min-width: 900px) {{
        .wg-card ul {{ columns: 2; column-gap: 2.2rem; }}
        .wg-card li {{ break-inside: avoid; }}
    }}

    /* ---- Ausbildung ---- */
    .edu-card {{ background:#ffffff; border-radius:18px; padding:1.5rem 1.7rem; box-shadow:0 14px 30px -24px rgba(30,20,70,0.32); border-top:5px solid {DM_LILA}; height:100%; }}
    .edu-card .years-pill {{ display:inline-block; background:{DM_LILA_HELL}; color:{DM_LILA_DUNKEL}; font-weight:700; font-size:0.78rem; padding:0.24rem 0.75rem; border-radius:8px; margin-bottom:0.7rem; }}
    .edu-card .degree {{ font-weight:700; color:{DM_BLAU_DUNKEL}; font-size:1.1rem; }}
    .edu-card .inst {{ font-size:0.92rem; color:{DM_GRAU}; margin-top:0.35rem; }}

    /* ---- Skills / generische Tag-Karten ---- */
    .skillcard {{ background:#ffffff; border-radius:16px; padding:1.2rem 1.35rem; box-shadow:0 12px 26px -22px rgba(30,20,70,0.3); border-top:3px solid var(--accent, {DM_LILA}); }}
    .skillcard h4 {{ margin:0 0 0.7rem 0; font-size:0.96rem; font-weight:700; color:{DM_BLAU_DUNKEL}; }}
    .skillcard .tag {{ display:inline-block; background:#F5F5FA; border:1px solid #E4E4EF; color:{DM_TEXT}; padding:0.28rem 0.8rem; border-radius:8px; font-size:0.82rem; font-weight:500; margin:0 0.35rem 0.35rem 0; }}
    .skillcard .subgroup {{ font-size:0.7rem; text-transform:uppercase; letter-spacing:0.04em; color:{DM_GRAU}; font-weight:700; margin:0.7rem 0 0.4rem 0; }}
    /* Tooltip rein per CSS (attr(data-tooltip)) statt title="" - Streamlits
       HTML-Rendering entfernt das title-Attribut, data-* bleibt erhalten. */
    .tag.tag-tooltip {{ position:relative; cursor:help; border-bottom:1px dotted {DM_LILA_DUNKEL}; }}
    .tag.tag-tooltip::after {{
        content: attr(data-tooltip);
        position:absolute; left:50%; bottom:135%; transform:translateX(-50%);
        background:{DM_TEXT}; color:#fff; padding:0.55rem 0.75rem; border-radius:8px;
        font-size:0.78rem; font-weight:400; line-height:1.4; white-space:normal;
        width:max-content; max-width:260px; text-align:left;
        box-shadow:0 10px 24px -8px rgba(0,0,0,0.35);
        opacity:0; visibility:hidden; transition:opacity 0.15s ease;
        z-index:60; pointer-events:none;
    }}
    .tag.tag-tooltip::before {{
        content:""; position:absolute; left:50%; bottom:118%; transform:translateX(-50%);
        border:6px solid transparent; border-top-color:{DM_TEXT};
        opacity:0; visibility:hidden; transition:opacity 0.15s ease; z-index:60;
    }}
    .tag.tag-tooltip:hover::after, .tag.tag-tooltip:hover::before {{
        opacity:1; visibility:visible;
    }}

    /* ---- Radar-Chart (reines SVG + HTML-Overlay-Labels) ---- */
    .radar-wrap {{ background:#fff; border-radius:16px; padding:1.4rem; box-shadow:0 12px 26px -22px rgba(30,20,70,0.3); display:flex; justify-content:center; }}
    .radar-stage {{ position:relative; width:100%; max-width:380px; aspect-ratio:1/1; }}
    .radar-stage svg {{ position:absolute; inset:0; width:100%; height:100%; display:block; }}
    .radar-label {{ position:absolute; font-size:0.78rem; font-weight:600; color:{DM_TEXT}; text-align:center; white-space:nowrap; line-height:1.3; }}
    .radar-value {{ font-size:0.72rem; font-weight:700; color:{DM_LILA_DUNKEL}; }}

    /* ---- Schmale Bildschirme: "Stakeholder-Kommunikation" darf an der
       vorgesehenen Stelle (<wbr> im Label-Text) umbrechen, statt die Seite
       horizontal scrollbar zu machen. Andere, kürzere Labels bleiben unter
       100px ohnehin einzeilig. ---- */
    @media (max-width: 500px) {{
        .radar-label {{ white-space:normal; max-width:100px; }}
    }}

    /* ---- Footer: Kontakt & Download ---- */
    .footer-divider {{ border:none; border-top:1px solid #E9E6F5; margin:2.2rem 0 1.6rem 0; }}
    .contact-bar {{ display:flex; gap:0.8rem; flex-wrap:wrap; align-items:center; }}
    .contact-pill, .contact-pill:hover, .contact-pill:visited {{
        display:inline-flex; align-items:center; gap:0.55rem;
        background:#ffffff; border:1px solid #E4E4EF; border-radius:999px;
        padding:0.55rem 1.15rem; font-size:0.9rem; font-weight:600; color:#000000 !important;
        text-decoration:none !important; box-shadow:0 8px 18px -14px rgba(30,20,70,0.3);
    }}
    .contact-pill .badge {{
        display:inline-flex; align-items:center; justify-content:center;
        width:22px; height:22px; border-radius:50%; background:{DM_LILA_DUNKEL};
        color:white; font-size:0.66rem; font-weight:800;
    }}

    /* ---- Native Streamlit-Expander im Template-Look ---- */
    [data-testid="stExpander"] {{
        border: 1px solid #E9E6F5 !important;
        border-radius: 14px !important;
        background: #ffffff;
        box-shadow: 0 10px 22px -20px rgba(30,20,70,0.3);
        margin-bottom: 0.7rem;
        overflow: hidden;
    }}
    [data-testid="stExpander"] summary {{
        font-weight: 700 !important;
        font-size: 0.96rem !important;
        color: {DM_BLAU_DUNKEL} !important;
        padding: 0.2rem 0 !important;
    }}
    [data-testid="stExpander"] summary:hover {{ color: {DM_LILA_DUNKEL} !important; }}
    [data-testid="stExpanderDetails"] p {{ font-size: 0.92rem; color: #3a3f4e; }}

    /* Farbiger linker Rahmen je Narrativ-Expander (per st.container(key=...)) */
    .st-key-narrativ-0 [data-testid="stExpander"] {{ border-left: 4px solid {DM_BLAU} !important; }}
    .st-key-narrativ-1 [data-testid="stExpander"] {{ border-left: 4px solid {DM_LILA_DUNKEL} !important; }}
    .st-key-narrativ-2 [data-testid="stExpander"] {{ border-left: 4px solid {DM_LILA_DUNKEL} !important; }}
    .st-key-narrativ-3 [data-testid="stExpander"] {{ border-left: 4px solid {DM_BLAU} !important; }}

    /* ---- Link im Praxisbeispiel-Banner (st.info) ---- */
    [data-testid="stAlert"] a {{ color: {DM_LILA_DUNKEL} !important; font-weight:700; text-decoration:underline; }}
    [data-testid="stAlert"] a:hover {{ color: {DM_BLAU_DUNKEL} !important; }}

    /* ---- Scenario-Karten (Praxisbeispiel-Seite) ---- */
    .scenario-intro {{
        background:#ffffff; border-left:4px solid {DM_LILA}; border-radius:4px 16px 16px 4px;
        padding:1.2rem 1.5rem; margin-bottom:1.3rem; box-shadow:0 14px 30px -24px rgba(30,20,70,0.32);
    }}
    .scenario-intro .s-kicker {{ font-size:0.72rem; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; color:{DM_LILA_DUNKEL}; }}
    .scenario-intro p {{ margin:0.4rem 0 0; font-size:0.94rem; color:#3a3f4e; }}
    .data-note {{ font-size:0.78rem; color:{DM_GRAU}; font-style:italic; margin-top:0.4rem; }}
    </style>
    """)


def render_topbar(logo_path: str, label: str) -> None:
    """Logo-Kopfzeile - nutzt echtes Logo, falls unter logo_path vorhanden."""
    if os.path.exists(logo_path):
        col_logo, col_label = st.columns([1, 5])
        with col_logo:
            st.image(logo_path, width=90)
        with col_label:
            st.markdown(
                f"<div style='padding-top:0.85rem; font-size:1.15rem; font-weight:600; color:{DM_TEXT};'>"
                f"{label}</div>",
                unsafe_allow_html=True,
            )
    else:
        html(f"""
        <div class="topbar">
            <div class="dm-logo">
                <span class="letters">dm</span>
                <span class="wave"></span>
            </div>
            <span class="role-label">{label}</span>
        </div>
        """)
