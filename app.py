import streamlit as st
import pandas as pd

# ==========================================
# MATEMATICKÉ JADRO (Nezmenené)
# ==========================================
def simuluj_investovanie_profesional(
        vklad_suma, periodicita, rocny_vynos_p, ter_p,
        spravca_p, vstupny_poplatok_p, transakcny_poplatok_p,
        poplatok_spolocnosti_p, roky
):
    celkovo_dni = roky * 365
    nastavenia_periodicity = {'tyzdenne': 52, 'mesacne': 12, 'rocne': 1}
    pocet_vkladov_za_rok = nastavenia_periodicity[periodicita]
    celkovy_pocet_vkladov = pocet_vkladov_za_rok * roky

    dni_vkladov = set()
    for i in range(celkovy_pocet_vkladov):
        den_vkladu = int(i * (365 / pocet_vkladov_za_rok)) + 1
        dni_vkladov.add(den_vkladu)

    cielova_suma = vklad_suma * celkovy_pocet_vkladov
    vstupny_poplatok_celkovo = cielova_suma * (vstupny_poplatok_p / 100)

    cisty_rocny_vynos = rocny_vynos_p - ter_p
    cisty_denny_rast = (1 + cisty_rocny_vynos / 100) ** (1 / 365)

    hodnota_uctu = 0.0
    celkovo_vlozene = 0.0
    celkovo_zaplatene_transakcne = 0.0
    rocna_historia = []

    for den in range(1, celkovo_dni + 1):
        aktualny_rok = ((den - 1) // 365) + 1
        peniaze_na_investovanie = 0.0

        if den in dni_vkladov:
            peniaze_na_investovanie += vklad_suma
            celkovo_vlozene += vklad_suma

        if peniaze_na_investovanie > 0 and transakcny_poplatok_p > 0:
            tx_fee = peniaze_na_investovanie * (transakcny_poplatok_p / 100)
            celkovo_zaplatene_transakcne += tx_fee
            peniaze_na_investovanie -= tx_fee

        hodnota_uctu += peniaze_na_investovanie
        hodnota_uctu *= cisty_denny_rast

        if spravca_p > 0:
            aktualna_sadzba_spravcu = 0.5 if hodnota_uctu >= 500000 else spravca_p
            denny_poplatok_spravcu = (1 + aktualna_sadzba_spravcu / 100) ** (1 / 365) - 1
            hodnota_uctu -= (hodnota_uctu * denny_poplatok_spravcu)

        if poplatok_spolocnosti_p > 0 and (den % 365 in [91, 182, 273, 0]):
            stvrtrocna_sadzba = (1 + poplatok_spolocnosti_p / 100) ** (1 / 4) - 1
            hodnota_uctu -= (hodnota_uctu * stvrtrocna_sadzba)

        if den % 365 == 0:
            rocna_historia.append((aktualny_rok, round(celkovo_vlozene, 2), round(hodnota_uctu, 2)))

    return (round(celkovo_vlozene, 2), round(hodnota_uctu, 2),
            round(vstupny_poplatok_celkovo, 2), round(celkovo_zaplatene_transakcne, 2), rocna_historia)

# ==========================================
# INTERAKTÍVNE UI (Streamlit)
# ==========================================
st.set_page_config(page_title="Investičná Kalkulačka", layout="wide")

st.title("📈 Interaktívna Investičná Kalkulačka")
st.markdown("Porovnanie nákladov sprostredkovateľa verzus samostatné investovanie cez brokera s nulovými poplatkami.")

# --- VSTUPNÉ PARAMETRE (Umiestnené dole pod grafom pomocou kontajnerov) ---
st.write("---")
st.subheader("⚙️ Nastavenie parametrov")

col1, col2, col3 = st.columns(3)

with col1:
    vklad_suma = st.number_input("Pravidelný vklad (€)", min_value=10.0, value=100.0, step=10.0)
    periodicita = st.selectbox("Periodicita", options=["mesacne", "tyzdenne", "rocne"])
    roky = st.slider("Dĺžka investovania (roky)", min_value=1, max_value=50, value=40)

with col2:
    rocny_vynos_p = st.number_input("Očakávaný ročný výnos trhu (%)", value=8.0, step=0.5)
    ter_p = st.number_input("TER fondu (%)", value=0.2048, step=0.0001, format="%.4f")

with col3:
    st.markdown("**Poplatky sprostredkovateľa:**")
    spravca_p = st.number_input("Ročný poplatok Prosight (%)", value=1.0, step=0.1)
    vstupny_poplatok_p = st.number_input("Vstupný poplatok z cieľovej sumy (%)", value=3.0, step=0.5)
    poplatok_spolocnosti_p = st.number_input("Poplatok správcovskej spoločnosti (eic) (%)", value=0.2, step=0.1)

# --- SPRACOVANIE DÁT ---
# 1. Sprostredkovateľ
vlozene_1, vysledok_1, fee_vstup_1, fee_tx_1, hist_1 = simuluj_investovanie_profesional(
    vklad_suma, periodicita, rocny_vynos_p, ter_p, spravca_p, vstupny_poplatok_p, 0.2, poplatok_spolocnosti_p, roky
)

# 2. Samostatný investor
vlozene_2, vysledok_2, fee_vstup_2, fee_tx_2, hist_2 = simuluj_investovanie_profesional(
    vklad_suma, periodicita, rocny_vynos_p, ter_p, 0.0, 0.0, 0.0, 0.0, roky
)

# Príprava dát do tabuľky pre interaktívny graf
df1 = pd.DataFrame(hist_1, columns=['Rok', 'Vložené spolu', 'S poplatkami'])
df2 = pd.DataFrame(hist_2, columns=['Rok', 'Vložené spolu 2', 'Čisté ETF (0%)'])

# Spojenie do jednej tabuľky
df_graf = pd.merge(df1, df2[['Rok', 'Čisté ETF (0%)']], on='Rok')
df_graf.set_index('Rok', inplace=True)

# --- VYKRESLENIE GRAFU ---
st.write("---")
st.subheader("📊 Vývoj majetku v čase")
# Vykreslenie interaktívneho čiarového grafu z 3 stĺpcov
st.line_chart(df_graf[['Vložené spolu', 'S poplatkami', 'Čisté ETF (0%)']], height=400)

# --- VÝPOČTY PRE FINÁLNY REPORT ---
rozdiel_zostatkov = vysledok_2 - vysledok_1
celkova_strata = rozdiel_zostatkov + fee_vstup_1
denny_naklad = celkova_strata / (roky * 365)
poplatok_odpredaj_1 = vysledok_1 * 0.002
cisty_vysledok_po_odpredaji_1 = vysledok_1 - poplatok_odpredaj_1

# --- FINÁLNE VÝSLEDKY A ČÍSLA ---
st.write("---")
st.subheader("💰 Finančný sumár")

col_res1, col_res2, col_res3 = st.columns(3)

col_res1.metric(label="Konečný zostatok (Čisté ETF)", value=f"{vysledok_2:,.2f} €".replace(",", " "))
col_res2.metric(label="Konečný zostatok (Sprostredkovateľ)", value=f"{vysledok_1:,.2f} €".replace(",", " "))
col_res3.metric(label="CELKOVÁ STRATA (Rozdiel + Poplatky)", value=f"- {celkova_strata:,.2f} €".replace(",", " "), delta_color="inverse")

st.markdown("### Detail poplatkov a strát (Stratégia so sprostredkovateľom)")
st.text(f"""
Jednorazový vstupný poplatok (zaplatený pomimo):       {fee_vstup_1:,.2f} €
Celkové transakčné poplatky pri nákupe (0.2%):         {fee_tx_1:,.2f} €
Strata na samotnom zostatku (ušlý zisk + poplatky):    {rozdiel_zostatkov:,.2f} €
-------------------------------------------------------------------------
Priemerný denný náklad na sprostredkovateľa:           {denny_naklad:,.2f} € / deň
-------------------------------------------------------------------------
Poplatok za finálny odpredaj majetku (0.2%):           {poplatok_odpredaj_1:,.2f} €
Čistá vyplatená suma po záverečnom odpredaji:          {cisty_vysledok_po_odpredaji_1:,.2f} €
""")