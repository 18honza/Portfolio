"""Design system for the dashboard — ported from the Claude Design mockup
(Portfolio Command Center.dc.html): Geist/Geist Mono type, near-black canvas,
hairline cards, muted grays with green/red P&L accents.
"""
import plotly.express as px
import plotly.io as pio
import streamlit as st

# palette lifted from the design file
BG = "#08090A"
BG_SIDEBAR = "#0B0C0E"
CARD_BG = "rgba(255,255,255,0.015)"
BORDER = "rgba(255,255,255,0.07)"
BORDER_SOFT = "rgba(255,255,255,0.06)"
TEXT = "#EDEDEE"
TEXT_BRIGHT = "#F2F2F3"
MUTED = "#8A8F98"
FAINT = "#6B6F78"
GREEN = "#4DB88A"
RED = "#E06C75"
BLUE = "#5E8BD6"
GOLD = "#C6A15B"
PURPLE = "#B57EDC"
PALETTE = [BLUE, GREEN, GOLD, PURPLE, RED, MUTED, "#5A606B"]

_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap');

html, body, .stApp, [data-testid="stAppViewContainer"] {{
    background: {BG} !important;
    font-family: 'Geist', -apple-system, sans-serif;
    color: {TEXT};
}}
.block-container {{ padding-top: 2.4rem; max-width: 1360px; }}

h1, h2, h3 {{ font-family: 'Geist', sans-serif !important; letter-spacing: -0.02em; color: {TEXT_BRIGHT}; }}
h2 {{ font-size: 1.25rem !important; font-weight: 600 !important; }}
h3 {{ font-size: 1.05rem !important; font-weight: 600 !important; }}

/* ---- brand header ---- */
.pcc-brand {{ display: flex; align-items: center; gap: 14px; }}
.pcc-dot {{
    width: 10px; height: 10px; border-radius: 50%; background: {GREEN};
    box-shadow: 0 0 12px rgba(77,184,138,0.8); flex: 0 0 auto;
}}
.pcc-title {{ font-family: 'Geist', sans-serif; font-size: 26px; font-weight: 600; letter-spacing: -0.02em; color: {TEXT_BRIGHT}; line-height: 1.15; }}
.pcc-sub {{ font-family: 'Geist Mono', monospace; font-size: 10.5px; letter-spacing: 0.09em; text-transform: uppercase; color: {FAINT}; margin-top: 5px; }}

/* ---- sidebar ---- */
[data-testid="stSidebar"] {{ background: {BG_SIDEBAR}; border-right: 1px solid {BORDER_SOFT}; }}
[data-testid="stSidebar"] hr {{ border-color: {BORDER_SOFT}; }}

/* ---- widget labels: tiny mono uppercase, like the design ---- */
[data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"] {{
    font-family: 'Geist Mono', monospace !important;
    font-size: 10.5px !important;
    letter-spacing: 0.07em; text-transform: uppercase; color: {FAINT} !important;
}}

/* ---- metric cards ---- */
[data-testid="stMetric"] {{
    background: {CARD_BG}; border: 1px solid {BORDER};
    border-radius: 14px; padding: 16px 18px;
}}
[data-testid="stMetricLabel"] p {{
    font-family: 'Geist Mono', monospace !important; font-size: 10.5px !important;
    letter-spacing: 0.07em; text-transform: uppercase; color: {FAINT} !important;
}}
[data-testid="stMetricValue"] {{
    font-family: 'Geist Mono', monospace !important; font-size: 20px !important;
    font-weight: 500; color: {TEXT_BRIGHT};
}}
[data-testid="stMetricDelta"] {{ font-family: 'Geist Mono', monospace !important; font-size: 12px !important; }}

/* ---- tabs ---- */
.stTabs [data-baseweb="tab-list"] {{
    gap: 26px; background: transparent;
    border-bottom: 1px solid {BORDER};
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important; color: {MUTED};
    font-family: 'Geist', sans-serif; font-size: 13.5px; font-weight: 500;
    padding: 2px 2px 12px 2px;
}}
.stTabs [data-baseweb="tab"]:hover {{ color: {TEXT}; }}
.stTabs [aria-selected="true"] {{ color: {TEXT_BRIGHT} !important; }}
.stTabs [data-baseweb="tab-highlight"] {{ background-color: {TEXT_BRIGHT}; height: 1px; }}
.stTabs [data-baseweb="tab-border"] {{ background: {BORDER}; }}

/* ---- buttons ---- */
.stButton > button, [data-testid="stFormSubmitButton"] > button {{
    border-radius: 8px; border: 1px solid rgba(255,255,255,0.12);
    background: rgba(255,255,255,0.03); color: {TEXT};
    font-family: 'Geist', sans-serif; font-size: 13px; font-weight: 500;
}}
.stButton > button:hover {{ border-color: rgba(255,255,255,0.25); background: rgba(255,255,255,0.06); color: {TEXT_BRIGHT}; }}

/* ---- inputs ---- */
[data-baseweb="input"], [data-baseweb="base-input"] {{
    background: rgba(255,255,255,0.03) !important; border-radius: 8px;
}}
[data-baseweb="input"] input, [data-baseweb="select"] div {{
    font-family: 'Geist Mono', monospace !important; font-size: 13px !important;
}}
[data-baseweb="select"] > div {{ background: rgba(255,255,255,0.03) !important; border-radius: 8px; }}

/* ---- cards: bordered containers & expanders ---- */
[data-testid="stVerticalBlockBorderWrapper"] > div {{ border-radius: 14px; }}
[data-testid="stVerticalBlockBorderWrapper"] {{
    border-radius: 14px;
}}
div[data-testid="stVerticalBlockBorderWrapper"]:has(> div) {{
    background: {CARD_BG};
}}
[data-testid="stExpander"] {{
    background: {CARD_BG}; border: 1px solid {BORDER} !important; border-radius: 14px !important;
}}
[data-testid="stExpander"] summary {{ font-family: 'Geist', sans-serif; font-size: 13.5px; font-weight: 500; }}
[data-testid="stExpander"] summary:hover {{ color: {TEXT_BRIGHT}; }}

/* ---- alerts -> design-tinted chips ---- */
div[data-testid="stAlert"] {{ border-radius: 10px; }}
div[data-testid="stAlert"]:has([data-testid="stAlertContentError"]) {{
    background: rgba(224,108,117,0.10); border: 1px solid rgba(224,108,117,0.35);
}}
div[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) {{
    background: rgba(198,161,91,0.10); border: 1px solid rgba(198,161,91,0.35);
}}
div[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) {{
    background: rgba(77,184,138,0.10); border: 1px solid rgba(77,184,138,0.30);
}}
div[data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) {{
    background: rgba(94,139,214,0.10); border: 1px solid rgba(94,139,214,0.30);
}}
div[data-testid="stAlert"] p {{ font-size: 13px; line-height: 1.55; }}
[data-testid="stAlertContentError"] {{ color: #ff8a80; }}
[data-testid="stAlertContentWarning"] {{ color: {GOLD}; }}
[data-testid="stAlertContentSuccess"] {{ color: {GREEN}; }}
[data-testid="stAlertContentInfo"] {{ color: {BLUE}; }}

/* ---- dataframes ---- */
[data-testid="stDataFrame"] {{
    border: 1px solid {BORDER}; border-radius: 12px; overflow: hidden;
}}

/* ---- radio as quiet segmented text ---- */
[data-testid="stSidebar"] [role="radiogroup"] label p {{ font-family: 'Geist', sans-serif; font-size: 13px; }}

/* ---- markdown blockquote (market context) ---- */
blockquote {{
    border-left: 2px solid {BLUE} !important; background: rgba(94,139,214,0.06);
    border-radius: 0 10px 10px 0; padding: 10px 14px !important;
}}
blockquote p {{ color: {MUTED} !important; font-size: 13.5px; }}
</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def brand_header() -> None:
    st.markdown(
        """
        <div class="pcc-brand">
          <div class="pcc-dot"></div>
          <div>
            <div class="pcc-title">Portfolio Command Center</div>
            <div class="pcc-sub">Trading212 · CZK · MPT + Johnny's framework · recommendations only</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_fig(fig, height: int | None = None):
    """Apply the design's chart language to a plotly figure."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Geist Mono, monospace", size=11, color=MUTED),
        colorway=PALETTE,
        legend=dict(font=dict(size=11, color=MUTED)),
        margin=dict(t=42, b=10, l=6, r=6),
    )
    fig.update_xaxes(gridcolor=BORDER_SOFT, zerolinecolor=BORDER, linecolor=BORDER)
    fig.update_yaxes(gridcolor=BORDER_SOFT, zerolinecolor=BORDER, linecolor=BORDER)
    if fig.layout.title and fig.layout.title.text:
        fig.update_layout(title_font=dict(family="Geist, sans-serif", size=13, color=TEXT))
    if height:
        fig.update_layout(height=height)
    return fig


def use_design_defaults() -> None:
    px.defaults.color_discrete_sequence = PALETTE
    pio.templates.default = "plotly_dark"
