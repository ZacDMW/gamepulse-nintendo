"""GamePulse Intelligence — playful presentation, serious sourced data.

Independent educational dashboard; not affiliated with Nintendo.
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.database import connect, seed

ROOT = Path(__file__).resolve().parent
COLORS = {
    "Racing": "#e53d4d",
    "Platformer": "#4bbada",
    "RPG": "#9074df",
    "Simulation": "#45ad80",
    "Party": "#f4bb36",
    "Fighting": "#f4824c",
    "Action-adventure": "#5383d2",
}
CONSOLE_COLORS = {
    "Nintendo Switch 2": "#df2c3d",
    "Nintendo Switch": "#58bcd9",
    "Wii U": "#9a84e1",
    "Nintendo 3DS": "#efb838",
    "Wii": "#58bc8d",
    "Nintendo DS": "#ef8b65",
}

st.set_page_config(
    page_title="GamePulse • Nintendo Edition",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed",
)
theme = ROOT / "assets" / "theme.css"
st.markdown(f"<style>{theme.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Read validated snapshots from the local SQLite store."""
    with connect() as conn:
        seed(conn)
        dates = pd.read_sql_query(
            "SELECT as_of FROM snapshots ORDER BY as_of DESC", conn
        )["as_of"].tolist()
        consoles = pd.read_sql_query("SELECT * FROM consoles", conn)
        titles = pd.read_sql_query("SELECT * FROM titles", conn)
    return dates, consoles, titles


def section(icon, heading, subheading):
    st.markdown(
        f'<div class="gp-section"><span class="gp-section-icon">{icon}</span>'
        f'<div><div class="gp-section-title">{heading}</div>'
        f'<div class="gp-section-sub">{subheading}</div></div></div>',
        unsafe_allow_html=True,
    )


def stat(label, value, footnote, color):
    st.markdown(
        f'<div class="gp-stat gp-stat-{color}">'
        f'<div class="gp-stat-label">{label}</div>'
        f'<div class="gp-stat-value">{value}</div>'
        f'<div class="gp-stat-foot">{footnote}</div></div>',
        unsafe_allow_html=True,
    )


def style_chart(fig, height):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=15, r=40, t=15, b=30),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(family="Trebuchet MS, Arial, sans-serif", size=13, color="#243144"),
        hoverlabel=dict(bgcolor="#243144", font_color="#ffffff"),
        showlegend=False,
        xaxis=dict(title="Million units sold", gridcolor="#f0e8df", zeroline=False),
        yaxis=dict(title=None, showgrid=False, automargin=True),
        bargap=0.33,
    )
    return fig


st.markdown(
    '<div class="gp-brandline"><span class="gp-mark">✦</span>'
    '<div><div class="gp-wordmark">GAME<span> </span><em>PULSE</em></div>'
    '<div class="gp-subbrand">INTELLIGENCE · NINTENDO EDITION</div></div></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="gp-hero"><div class="gp-hero-content">'
    '<div class="gp-eyebrow">★ WELCOME TO THE DATA WORLD ★</div>'
    '<h1>Big numbers.<br>Big adventures.</h1>'
    '<p>Explore the stories behind console generations, fan-favorite games, '
    'and the numbers that power Nintendo’s universe.</p>'
    '<div class="gp-hero-tags"><span>🎮 Console sales</span>'
    '<span>🏆 Game rankings</span><span>✨ Genre insights</span>'
    '</div></div></div>',
    unsafe_allow_html=True,
)

dates, consoles, titles = load_data()
if not dates:
    st.error("No verified sales snapshot is available yet.")
    st.stop()

choose, badge = st.columns([2, 3])
with choose:
    selected_date = st.selectbox(
        "🗓️ Pick a reporting checkpoint",
        dates,
        format_func=lambda date: pd.Timestamp(date).strftime("%B %d, %Y"),
        help="Only dates with an imported, reviewed official Nintendo sales snapshot appear here.",
    )
with badge:
    st.markdown(
        '<div class="gp-note"><strong>📌 Official figures, not live sales.</strong> '
        'All values are cumulative, worldwide, publicly reported units as of the selected '
        'checkpoint. Updates are reviewed before publication.</div>',
        unsafe_allow_html=True,
    )

c = consoles.loc[consoles["as_of"].eq(selected_date)].copy()
t = titles.loc[titles["as_of"].eq(selected_date)].copy()
sw2_rows = c.loc[c["name"].eq("Nintendo Switch 2")]
if sw2_rows.empty:
    st.error("Nintendo Switch 2 data is missing from this snapshot.")
    st.stop()
sw2 = sw2_rows.iloc[0]

section("🎯", "Checkpoint unlocked!", "The headline stats from this reporting period")
metric1, metric2, metric3 = st.columns(3)
with metric1:
    stat("Switch 2 hardware", f'{sw2["hardware_m"]:,.2f}M', "Cumulative worldwide hardware units", "red")
with metric2:
    stat("Switch 2 software", f'{sw2["software_m"]:,.2f}M', "Cumulative worldwide software units", "blue")
with metric3:
    stat("Featured games", f"{len(t):,}", "Selected titles with published sales figures", "yellow")

overview, games, sources = st.tabs(
    ["🕹️ Console quest", "🏆 Games & genres", "📖 Data guide"]
)

with overview:
    section("🕹️", "The console quest", "How do different Nintendo systems stack up?")
    metric = st.radio(
        "Compare by",
        ["Hardware", "Software"],
        horizontal=True,
        key="console_metric",
    )
    value_col = "hardware_m" if metric == "Hardware" else "software_m"
    chart_data = c.sort_values(value_col, ascending=True)
    fig = px.bar(
        chart_data,
        x=value_col,
        y="name",
        orientation="h",
        color="name",
        color_discrete_map=CONSOLE_COLORS,
        text=value_col,
        labels={value_col: "Millions of units", "name": "System"},
        hover_data={"name": False, value_col: ":,.2f"},
    )
    fig.update_traces(
        texttemplate="%{x:,.2f}M",
        textposition="outside",
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>%{x:,.2f} million units<extra></extra>",
    )
    fig = style_chart(fig, 425)
    fig.update_xaxes(title=f"{metric} · millions of units", rangemode="tozero")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown(
        '<div class="gp-note"><strong>🧠 Analyst tip:</strong> '
        'These are lifetime-to-date totals, not matched launch-window sales. '
        'A newer console has had less time on the market, so these figures '
        'should not be read as a like-for-like launch performance ranking.</div>',
        unsafe_allow_html=True,
    )

with games:
    section("🏆", "The hall of fame", "Explore the games Nintendo has published sales figures for")
    available_platforms = sorted(t["platform"].unique().tolist())
    first = "Nintendo Switch 2" if "Nintendo Switch 2" in available_platforms else available_platforms[0]
    choice = st.selectbox(
        "🎮 Pick your platform",
        ["All featured platforms"] + available_platforms,
        index=(available_platforms.index(first) + 1),
        key="game_platform",
    )
    picked = t if choice == "All featured platforms" else t.loc[t["platform"].eq(choice)]
    selected = picked.sort_values("units_m", ascending=True).copy()
    selected["display_title"] = selected["title"].apply(
        lambda name: name if len(name) <= 38 else name[:35] + "…"
    )
    fig_games = px.bar(
        selected,
        x="units_m",
        y="display_title",
        orientation="h",
        color="genre",
        color_discrete_map=COLORS,
        text="units_m",
        hover_name="title",
        custom_data=["note", "platform"],
    )
    fig_games.update_traces(
        texttemplate="%{x:,.2f}M",
        textposition="outside",
        hovertemplate=(
            "<b>%{hovertext}</b><br>Reported sales: %{x:,.2f}M units"
            "<br>Platform: %{customdata[1]}"
            "<br>Note: %{customdata[0]}<extra></extra>"
        ),
    )
    fig_games = style_chart(fig_games, max(390, 48 * len(selected) + 100))
    st.plotly_chart(fig_games, use_container_width=True, config={"displayModeBar": False})

    section("✨", "Genre playground", "A snapshot of only the featured titles—not the entire market")
    st.markdown(
        '<div class="gp-note"><strong>⚠️ Sample, not market share:</strong> '
        'Genre totals below sum only the selected, published game figures. '
        'They are not overall Nintendo genre sales. Genres are assigned by '
        'this project; editions and bundled copies have special rules.</div>',
        unsafe_allow_html=True,
    )
    genre_data = (
        picked.groupby("genre", as_index=False)["units_m"]
        .sum()
        .sort_values("units_m", ascending=False)
    )
    donut, summary = st.columns([3, 2])
    with donut:
        genre_fig = px.pie(
            genre_data,
            names="genre",
            values="units_m",
            hole=0.62,
            color="genre",
            color_discrete_map=COLORS,
        )
        genre_fig.update_traces(
            textinfo="percent",
            textposition="outside",
            marker=dict(line=dict(color="white", width=3)),
            hovertemplate="<b>%{label}</b><br>Featured-title sum: %{value:.2f}M<extra></extra>",
        )
        genre_fig.update_layout(
            template="plotly_white",
            height=370,
            margin=dict(l=15, r=15, t=10, b=10),
            paper_bgcolor="white",
            font=dict(family="Trebuchet MS, Arial, sans-serif", color="#243144"),
            legend=dict(orientation="h", y=-0.14, x=0),
        )
        st.plotly_chart(genre_fig, use_container_width=True, config={"displayModeBar": False})
    with summary:
        st.markdown("**📊 Featured-title totals by genre**")
        st.dataframe(
            genre_data.rename(
                columns={"genre": "Genre", "units_m": "Reported units (M)"}
            ),
            hide_index=True,
            use_container_width=True,
        )
        st.caption("Some values cannot be combined into a complete market-wide total.")

with sources:
    section("📖", "The data guide", "Every reliable dashboard needs clear rules")
    st.markdown(
        """
**What the figures represent**

- Data comes from Nintendo's official investor-relations reports.
- Values represent **worldwide, cumulative reported unit sales** as of the chosen date—not real-time retail purchases.
- Hardware and software counts are different metrics; software units should not be interpreted as unique customers.
- The game list contains **selected leading reported titles**, not a complete Nintendo software catalog.
- The genre labels are assigned for this project and should not be presented as Nintendo's official genre taxonomy.

**Reporting caveats**

- Console generations have different release dates and therefore unequal observation windows.
- Editions, bundles, downloadable copies, and publishing territories may affect game-level figures.
- Pokémon Pokopia's reported figure excludes Japan under Nintendo's publishing scope.
- No U.S. state-level sales estimates have been inferred.

**Official source links**

- [Nintendo hardware and software sales](https://www.nintendo.co.jp/ir/en/finance/hard_soft/index.html)
- [Nintendo Switch 2 software sales](https://www.nintendo.co.jp/ir/en/finance/software/index.html)
- [Nintendo Switch software sales](https://www.nintendo.co.jp/ir/en/finance/software/switch.html)
        """
    )
    st.markdown("**🔎 Browse the imported game records**")
    st.dataframe(
        t[["title", "platform", "genre", "units_m", "note"]].rename(
            columns={
                "title": "Title",
                "platform": "Platform",
                "genre": "Genre",
                "units_m": "Units (M)",
                "note": "Reporting note",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )
    st.download_button(
        "⬇️ Export featured titles (CSV)",
        data=t.to_csv(index=False).encode("utf-8"),
        file_name=f"gamepulse_titles_{selected_date}.csv",
        mime="text/csv",
    )

st.markdown(
    '<div class="gp-foot"><strong>GamePulse Intelligence</strong> ✦ Built for '
    'curious players and careful analysts. Independent educational project; '
    'not affiliated with or endorsed by Nintendo. Nintendo and all game titles '
    'remain the property of their respective owners. <br>'
    'Next level: verified quarterly timelines, regional breakdowns, and '
    'transparent forecasting once enough observations exist.</div>',
    unsafe_allow_html=True,
)
