"""GamePulse Intelligence: Nintendo-first business intelligence portfolio."""
import pandas as pd
import plotly.express as px
import streamlit as st
from src.database import connect, seed

st.set_page_config(page_title='GamePulse | Nintendo Intelligence', page_icon='🎮', layout='wide')
st.markdown('''<style>div[data-testid="stMetric"]{border:1px solid #354155;padding:17px;border-radius:12px} .stApp{background:#101723}</style>''', unsafe_allow_html=True)
st.title('🎮 GamePulse Intelligence')
st.caption('Nintendo Edition · Public investor-relations data · Educational portfolio (not affiliated with Nintendo)')


@st.cache_data
def load():
    with connect() as conn:
        seed(conn)
        dates = pd.read_sql_query('SELECT as_of FROM snapshots ORDER BY as_of DESC', conn)['as_of'].tolist()
        consoles = pd.read_sql_query('SELECT * FROM consoles ORDER BY as_of', conn)
        titles = pd.read_sql_query('SELECT * FROM titles ORDER BY as_of', conn)
    return dates, consoles, titles


dates, consoles, titles = load()
date = st.selectbox('Official reporting date', dates)
st.info(f'Figures are **worldwide life-to-date units as of {date}**, not live point-of-sale data. Updated only when Nintendo releases validated figures.')
c = consoles[consoles.as_of.eq(date)].copy()
t = titles[titles.as_of.eq(date)].copy()
sw2 = c[c.name.eq('Nintendo Switch 2')].iloc[0]
a,b,d = st.columns(3)
a.metric('Switch 2 hardware', f'{sw2.hardware_m:,.2f}M units')
b.metric('Switch 2 software', f'{sw2.software_m:,.2f}M units')
d.metric('Reported featured titles', f'{len(t):,}')

st.subheader('Console generations')
metric = st.radio('Measure', ['Hardware', 'Software'], horizontal=True)
col = 'hardware_m' if metric == 'Hardware' else 'software_m'
fig = px.bar(c.sort_values(col), x=col, y='name', orientation='h', labels={col:'Millions of units','name':'Console'}, text=col, template='plotly_dark')
fig.update_layout(height=410, margin=dict(t=10,b=25,l=0,r=15), paper_bgcolor='#101723',plot_bgcolor='#101723')
st.plotly_chart(fig, use_container_width=True)

st.subheader('Top-selling reported titles')
platforms = ['All platforms'] + sorted(t.platform.unique().tolist())
selected = st.selectbox('Platform', platforms)
filtered = t if selected == 'All platforms' else t[t.platform.eq(selected)]
fig2 = px.bar(filtered.sort_values('units_m'), x='units_m', y='title', orientation='h', color='genre',
              labels={'units_m':'Reported millions of units','title':'Game'},template='plotly_dark',hover_data=['note'])
fig2.update_layout(height=max(360,42*len(filtered)), margin=dict(t=10,b=25,l=0,r=5), paper_bgcolor='#101723', plot_bgcolor='#101723')
st.plotly_chart(fig2, use_container_width=True)

st.subheader('Genre mix among the reported titles')
st.warning('This is a descriptive view of selected top-selling titles, NOT the genre distribution of all games sold. Genre classifications are editorial labels; editions and bundled copies have special reporting rules.')
g = filtered.groupby('genre',as_index=False)['units_m'].sum().sort_values('units_m',ascending=False)
st.dataframe(g.rename(columns={'units_m':'Selected-title total (millions)'}),hide_index=True,use_container_width=True)
with st.expander('Inspect source records and caveats'):
    st.dataframe(filtered[['title','platform','genre','units_m','note']],hide_index=True,use_container_width=True)
    st.markdown('Official sources: [Nintendo hardware/software](https://www.nintendo.co.jp/ir/en/finance/hard_soft/index.html) · [Switch 2 titles](https://www.nintendo.co.jp/ir/en/finance/software/index.html) · [Switch titles](https://www.nintendo.co.jp/ir/en/finance/software/switch.html)')
    st.markdown('**Methodology:** Publicly disclosed company sell-in figures, millions of units, cumulative at the date stated. Avoid summing editions as if they represent distinct consumers. Pokémon Pokopia has a partial geographic publishing scope. No state-level or nationwide retail sell-through is inferred.')

st.caption('Roadmap: quarterly ingestion + verified regional financial statements + backtested forecasting once enough chronological observations exist.')
