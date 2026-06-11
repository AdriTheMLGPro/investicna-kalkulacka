import streamlit as st
import pandas as pd

def simuluj_investovanie_profesional(
        vklad_suma,
        periodicita,
        rocny_vynos_p,
        ter_p,
        spravca_p,
        vstupny_poplatok_p,
        transakcny_poplatok_p,
        poplatok_spolocnosti_p,
        roky,
        typ_investicie
):
    celkovo_dni = roky * 365

    dni_vkladov = set()

    # Jednorazová investícia
    if typ_investicie == "Jednorazová investícia":
        celkovy_pocet_vkladov = 1
        dni_vkladov.add(1)

    # Pravidelná investícia
    else:
        nastavenia_periodicity = {
            'tyzdenne': 52,
            'mesacne': 12,
            'rocne': 1
        }

        pocet_vkladov_za_rok = nastavenia_periodicity[periodicita]
        celkovy_pocet_vkladov = pocet_vkladov_za_rok * roky

        for i in range(celkovy_pocet_vkladov):
            den_vkladu = int(i * (365 / pocet_vkladov_za_rok)) + 1
            dni_vkladov.add(den_vkladu)

    cielova_suma = (
        vklad_suma * celkovy_pocet_vkladov
        if typ_investicie == "Pravidelná investícia"
        else vklad_suma
    )

    vstupny_poplatok_celkovo = (
            cielova_suma *
            (vstupny_poplatok_p / 100)
    )

    cisty_rocny_vynos = (
            rocny_vynos_p - ter_p
    )

    cisty_denny_rast = (
        (1 + cisty_rocny_vynos / 100) ** (1 / 365)
        if cisty_rocny_vynos > 0
        else 1.0
    )

    hodnota_uctu = 0.0
    celkovo_vlozene = 0.0
    celkovo_zaplatene_transakcne = 0.0
    celkovo_zaplatene_fx = 0.0
    rocna_historia = []

    for den in range(1, celkovo_dni + 1):

        aktualny_rok = (
                ((den - 1) // 365) + 1
        )

        peniaze_na_investovanie = 0.0

        # Vklad
        if den in dni_vkladov:
            peniaze_na_investovanie += vklad_suma
            celkovo_vlozene += vklad_suma

        # Poplatky iba pri maklérovi
        if peniaze_na_investovanie > 0:

            # Transaction fee
            if transakcny_poplatok_p > 0:
                tx_fee = (
                        peniaze_na_investovanie *
                        (transakcny_poplatok_p / 100)
                )

                celkovo_zaplatene_transakcne += tx_fee
                peniaze_na_investovanie -= tx_fee

                # FX fee
                fx_fee = (
                        peniaze_na_investovanie *
                        0.66 *
                        (0.2 / 100)
                )

                celkovo_zaplatene_fx += fx_fee
                peniaze_na_investovanie -= fx_fee

        # Zainvestovanie
        hodnota_uctu += peniaze_na_investovanie
        hodnota_uctu *= cisty_denny_rast

        # Poplatok správcu
        if spravca_p > 0:

            if hodnota_uctu < 50000:
                aktualna_sadzba_spravcu = spravca_p

            elif 50000 <= hodnota_uctu < 100000:
                aktualna_sadzba_spravcu = 0.75

            elif 100000 <= hodnota_uctu < 200000:
                aktualna_sadzba_spravcu = 0.70

            elif 200000 <= hodnota_uctu < 300000:
                aktualna_sadzba_spravcu = 0.65

            elif 300000 <= hodnota_uctu < 400000:
                aktualna_sadzba_spravcu = 0.60

            elif 400000 <= hodnota_uctu < 500000:
                aktualna_sadzba_spravcu = 0.55

            else:
                aktualna_sadzba_spravcu = 0.50

            denny_poplatok_spravcu = (
                    (1 + aktualna_sadzba_spravcu / 100)
                    ** (1 / 365) - 1
            )

            hodnota_uctu -= (
                    hodnota_uctu *
                    denny_poplatok_spravcu
            )

        # Poplatok správcovskej spoločnosti
        # 0.24% p.a. strhávané mesačne
        if (
                poplatok_spolocnosti_p > 0
                and den % 30 == 0
        ):
            mesacna_sadzba = (
                    (1 + poplatok_spolocnosti_p / 100)
                    ** (1 / 12) - 1
            )

            hodnota_uctu -= (
                    hodnota_uctu *
                    mesacna_sadzba
            )

        # Ročná história
        if den % 365 == 0:
            rocna_historia.append(
                (
                    aktualny_rok,
                    round(celkovo_vlozene, 2),
                    round(hodnota_uctu, 2)
                )
            )

    return (
        round(celkovo_vlozene, 2),
        round(hodnota_uctu, 2),
        round(vstupny_poplatok_celkovo, 2),
        round(celkovo_zaplatene_transakcne, 2),
        round(celkovo_zaplatene_fx, 2),
        rocna_historia
    )

st.set_page_config(
    page_title="Investičná Kalkulačka",
    page_icon="📈",
    layout="wide"
)

hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""

st.markdown(
    hide_st_style,
    unsafe_allow_html=True
)

st.title(
    "📈 Profesionálna Investičná Kalkulačka"
)

st.markdown(
    "Porovnanie pridanej hodnoty makléra "
    "(vedenie, disciplína, správa) "
    "verzus investovanie na vlastnú päsť."
)

st.write("---")

typ_investicie = st.radio(
    "**Spôsob investovania:**",
    [
        "Pravidelná investícia",
        "Jednorazová investícia"
    ],
    index=0,
    horizontal=True
)

scenar = st.radio(
    "**Vyberte úroveň skúseností klienta "
    "(scenár pre prezentáciu):**",
    options=[
        "Neskúsený investor "
        "(Bežný človek bez vedenia – "
        "robí emočné chyby, stráca -3% p.a.)",

        "Profesionálny / Skúsený investor "
        "(Dokáže sám plne replikovať trh "
        "s 0% chybovosťou)"
    ],
    index=0
)

st.write("---")

st.subheader(
    "⚙️ Nastavenie parametrov"
)

col1, col2, col3 = st.columns(3)

with col1:

    vklad_suma = st.number_input(
        (
            "Pravidelný vklad (€)"
            if typ_investicie ==
               "Pravidelná investícia"
            else "Jednorazový vklad (€)"
        ),
        min_value=10.0,
        value=(
            100.0
            if typ_investicie ==
               "Pravidelná investícia"
            else 10000.0
        ),
        step=10.0
    )

    periodicita = (
        st.selectbox(
            "Periodicita vkladov",
            options=[
                "mesacne",
                "tyzdenne",
                "rocne"
            ]
        )
        if typ_investicie ==
           "Pravidelná investícia"
        else "rocne"
    )

    roky = st.slider(
        "Dĺžka investovania (roky)",
        min_value=1,
        max_value=50,
        value=40
    )

with col2:

    rocny_vynos_p = st.number_input(
        "Očakávaný ročný výnos trhu (%)",
        value=8.0,
        step=0.5
    )

    ter_p = st.number_input(
        "TER fondu (%)",
        value=0.2048,
        step=0.0001,
        format="%.4f"
    )

with col3:

    st.markdown(
        "**Poplatky správcu & "
        "Sprostredkovateľa:**"
    )

    spravca_p = st.number_input(
        "Základný ročný poplatok "
        "správcu (%)",
        value=1.0,
        step=0.1
    )

    vstupny_poplatok_p = st.number_input(
        "Vstupný poplatok "
        "z cieľovej sumy (%)",
        value=1.0,
        step=0.5
    )

    poplatok_spolocnosti_p = (
        st.number_input(
            "Poplatok správcovskej "
            "spoločnosti (%)",
            value=0.24,
            step=0.01
        )
    )

if "Neskúsený investor" in scenar:

    vynos_makler = rocny_vynos_p
    vynos_broker = rocny_vynos_p - 3.0

    st.info(
        f"💡 **Prezentačný modus:** "
        f"Maklér udržiava disciplínu "
        f"klienta na plnom výnose trhu "
        f"({vynos_makler}%). "

        f"Samostatný investor na vlastnú "
        f"päsť kvôli chybám v časovaní "
        f"a emóciám dosahuje výnos iba "
        f"{vynos_broker}%."
    )

else:

    vynos_makler = rocny_vynos_p
    vynos_broker = rocny_vynos_p

    st.success(
        f"📈 **Profesionálny modus:** "
        f"Obe strategie dosahujú plný "
        f"trhový výnos "
        f"{rocny_vynos_p}%. "

        f"Graf ukazuje čistý vplyv "
        f"poplatkových štruktúr."
    )

vlozene_1, vysledok_1, fee_vstup_1, fee_tx_1, fee_fx_1, hist_1 = (
    simuluj_investovanie_profesional(
        vklad_suma,
        periodicita,
        vynos_makler,
        ter_p,
        spravca_p,
        vstupny_poplatok_p,
        0.2,
        poplatok_spolocnosti_p,
        roky,
        typ_investicie
    )
)

vlozene_2, vysledok_2, fee_vstup_2, fee_tx_2, fee_fx_2, hist_2 = (
    simuluj_investovanie_profesional(
        vklad_suma,
        periodicita,
        vynos_broker,
        ter_p,
        0.0,
        0.0,
        0.0,
        0.0,
        roky,
        typ_investicie
    )
)

df1 = pd.DataFrame(
    hist_1,
    columns=[
        'Rok',
        'Vložené spolu',
        'S maklérom (S poplatkami)'
    ]
)

df2 = pd.DataFrame(
    hist_2,
    columns=[
        'Rok',
        'Vložené spolu 2',
        'Na vlastnú päsť '
        '(0% poplatky)'
    ]
)

df_graf = pd.merge(
    df1,
    df2[
        [
            'Rok',
            'Na vlastnú päsť '
            '(0% poplatky)'
        ]
    ],
    on='Rok'
)

df_graf.set_index(
    'Rok',
    inplace=True
)

st.write("---")

st.subheader(
    "📊 Vývoj majetku v čase"
)

st.line_chart(
    df_graf[
        [
            'Vložené spolu',
            'S maklérom (S poplatkami)',
            'Na vlastnú päsť '
            '(0% poplatky)'
        ]
    ],
    height=450
)

poplatok_odpredaj_1 = (
        vysledok_1 * 0.002
)

cisty_vysledok_po_odpredaji_1 = (
        vysledok_1 -
        poplatok_odpredaj_1
)

st.write("---")

st.subheader(
    "💰 Finančný sumár"
)

col_res1, col_res2, col_res3 = (
    st.columns(3)
)

col_res1.metric(
    label="Konečný stav s Maklérom",
    value=f"{vysledok_1:,.2f} €"
    .replace(",", " ")
)

col_res2.metric(
    label="Konečný stav "
          "na vlastnú päsť",
    value=f"{vysledok_2:,.2f} €"
    .replace(",", " ")
)

if vysledok_1 > vysledok_2:

    cisty_zisk_z_maklera = (
            vysledok_1 -
            vysledok_2
    )

    col_res3.metric(
        label="PRIDANÁ HODNOTA "
              "MAKLÉRA",
        value=f"+ "
              f"{cisty_zisk_z_maklera:,.2f} €"
        .replace(",", " "),
        delta="Maklér zarobil "
              "klientovi viac"
    )

else:

    cisty_rozdiel_poplatkov = (
            vysledok_2 -
            vysledok_1
    )

    celkova_strata_s_poplatkami = (
            cisty_rozdiel_poplatkov +
            fee_vstup_1
    )

    col_res3.metric(
        label="Rozdiel v prospech "
              "čistého ETF",

        value=f"- "
              f"{celkova_strata_s_poplatkami:,.2f} €"
        .replace(",", " "),

        delta_color="inverse",
        delta="Čisté ETF "
              "bez poplatkov vedie"
    )

st.markdown(
    "### 📋 Detailný rozbor stratégie"
)

col_info1, col_info2 = st.columns(2)

with col_info1:

    st.markdown(
        "**Prehľad vkladov "
        "a poplatkov:**"
    )

    st.text(
        f"""Celkovo vložený kapitál (vlastné vklady):   {vlozene_1:,.2f} €
-----------------------------------------------------------------
Vstupný poplatok (vypočítaný pomimo):        {fee_vstup_1:,.2f} €
Transakčné poplatky pri nákupoch (0.2%):       {fee_tx_1:,.2f} €
FX poplatky pri konverzii (66% × 0.2%):        {fee_fx_1:,.2f} €
Poplatok za finálny odpredaj majetku (0.2%):    {poplatok_odpredaj_1:,.2f} €
-----------------------------------------------------------------
Čistá vyplatená suma klientovi na ruku:         {cisty_vysledok_po_odpredaji_1:,.2f} €"""
    )

with col_info2:

    st.markdown(
        "**Zhodnotenie "
        "pre prezentáciu:**"
    )

    if "Neskúsený investor" in scenar:

        st.markdown(
            f"""
🔴 **Sám sebe nepriateľom:** 
Ak by si tento klient riešil
investovanie sám, kvôli chybám
v správaní a emóciám by skončil
s majetkom
**{vysledok_2:,.2f} €**.

🟢 **Sila odborného poradenstva:** 
S maklérom má síce poplatky
(ktoré sa s rastom majetku
automaticky znižujú až na 0,5%),
ale vďaka stopercentnej disciplíne
a plnému výnosu odchádza
s majetkom
**{vysledok_1:,.2f} €**.

🔥 **Výsledok:** 
Služba makléra priniesla klientovi
čistý majetok vyšší o
**{(vysledok_1 - vysledok_2):,.2f} €**,
čím poplatky kompletne stratili
na váhe a premenili sa na najlepšiu
investíciu do disciplíny.
"""
        )

    else:

        rozdiel_zostatkov = (
                vysledok_2 -
                vysledok_1
        )

        celkova_strata = (
                rozdiel_zostatkov +
                fee_vstup_1
        )

        denny_naklad = (
                celkova_strata /
                (roky * 365)
        )

        st.markdown(
            f"""
💼 **Pre skúseného profesionála:** 
Tento scenár potvrdzuje,
že pokiaľ je investor
dokonale disciplinovaný
a nedopúšťa sa chýb,
poplatková štruktúra
vrátane klesajúcej škály
ho v priebehu
{roky} rokov stojí
**{celkova_strata:,.2f} €**
na ušlom zisku a poplatkoch.

⏱️ **Denný náklad:** 
Poplatky a ušlý zisk
predstavujú priemerný náklad
**{denny_naklad:,.2f} € / deň**
za kompletnú správu
portfólia.
"""
        )
