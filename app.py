"""
TEFAS Fon Takip - İnteraktif Dashboard (Faz 6)
==========================================
Amaç: Önceki scriptlerdeki mantığı (fon çekme, endekse çevirme,
      karşılaştırma) tarayıcıda çalışan tıklanabilir bir arayüze taşımak.

Kullanım:
    pip install streamlit
    streamlit run app.py

Bu komut otomatik olarak tarayıcında bir sekme açar (genelde
http://localhost:8501). Kapatmak için terminalde Ctrl+C.
"""

import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from tefas import Crawler

# --- SAYFA AYARLARI ------------------------------------------------
st.set_page_config(page_title="TEFAS Fon Takip", layout="wide")
st.title("📊 TEFAS Fon Karşılaştırma")
st.caption("Fon seç, tarih aralığını ayarla, karşılaştır.")

# --- BİLİNEN FON ÖRNEKLERİ (istediğin kadar ekleyebilirsin) --------
ORNEK_FONLAR = {
    "AFA - Para Piyasası": "AFA",
    "ICA - Altın (ICBC)": "ICA",
    "YAY - Yabancı Teknoloji": "YAY",
    "AOY - Yenilenebilir Enerji": "AOY",
}


@st.cache_data(ttl=3600)  # aynı veriyi 1 saat boyunca tekrar tekrar TEFAS'tan çekme
def tek_fon_cek(kod: str, baslangic: str, bitis: str):
    """Tek bir fonun verisini çeker ve temizler. Sonucu önbelleğe alır."""
    tefas = Crawler()
    df = tefas.fetch(
        start=baslangic,
        end=bitis,
        name=kod,
        columns=["code", "date", "price"],
    )
    if df is None or df.empty:
        return None

    df = df.rename(columns={"code": "fon_kodu", "date": "tarih", "price": "fiyat"})
    df["tarih"] = pd.to_datetime(df["tarih"])
    df["fiyat"] = df["fiyat"].astype(float)
    df = df.sort_values("tarih").reset_index(drop=True)
    df["endeks"] = (df["fiyat"] / df["fiyat"].iloc[0]) * 100
    return df


# --- SOL PANEL: KONTROLLER -----------------------------------------
with st.sidebar:
    st.header("Ayarlar")

    secilenler = st.multiselect(
        "Karşılaştırılacak fonlar",
        options=list(ORNEK_FONLAR.keys()),
        default=list(ORNEK_FONLAR.keys()),
    )

    ek_kod = st.text_input("Başka bir fon kodu eklemek istersen buraya yaz (örn: TCD)")

    gun_sayisi = st.slider("Kaç günlük veri?", min_value=30, max_value=365, value=90, step=30)

    calistir = st.button("Verileri Çek ve Karşılaştır", type="primary")

# --- ANA PANEL: SONUÇLAR --------------------------------------------
if calistir:
    kodlar = [ORNEK_FONLAR[isim] for isim in secilenler]
    if ek_kod.strip():
        kodlar.append(ek_kod.strip().upper())

    if not kodlar:
        st.warning("En az bir fon seçmelisin.")
    else:
        bugun = datetime.now()
        baslangic = bugun - timedelta(days=gun_sayisi)
        baslangic_str = baslangic.strftime("%Y-%m-%d")
        bitis_str = bugun.strftime("%Y-%m-%d")

        veriler = {}
        with st.spinner("TEFAS'tan veri çekiliyor..."):
            for kod in kodlar:
                df = tek_fon_cek(kod, baslangic_str, bitis_str)
                if df is not None:
                    veriler[kod] = df
                else:
                    st.warning(f"'{kod}' için veri bulunamadı, atlandı.")

        if not veriler:
            st.error("Hiçbir fon için veri çekilemedi.")
        else:
            # --- Getiri tablosu ---
            st.subheader("Dönem Getirileri")
            tablo_satirlari = []
            for kod, df in veriler.items():
                ilk = df["fiyat"].iloc[0]
                son = df["fiyat"].iloc[-1]
                getiri = (son - ilk) / ilk * 100
                tablo_satirlari.append({
                    "Fon": kod,
                    "Başlangıç Fiyatı": round(ilk, 4),
                    "Son Fiyat": round(son, 4),
                    "Getiri (%)": round(getiri, 2),
                })
            tablo_df = pd.DataFrame(tablo_satirlari).sort_values("Getiri (%)", ascending=False)
            st.dataframe(tablo_df, use_container_width=True, hide_index=True)

            # --- Karşılaştırma grafiği ---
            st.subheader(f"Endeks Bazlı Karşılaştırma (Başlangıç = 100, son {gun_sayisi} gün)")
            grafik_df = pd.DataFrame({
                kod: df.set_index("tarih")["endeks"] for kod, df in veriler.items()
            })
            st.line_chart(grafik_df)

else:
    st.info("Soldan fon seçip 'Verileri Çek ve Karşılaştır' butonuna bas.")
