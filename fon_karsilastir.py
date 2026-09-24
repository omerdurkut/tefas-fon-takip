"""
TEFAS Fon Karşılaştırma Scripti (Faz 3)
==========================================
Amaç: Birden fazla fonu aynı anda çekip, aynı grafikte adil bir şekilde
      karşılaştırmak.

Kullanım:
    python fon_karsilastir.py

ÖNEMLİ FİKİR - NEDEN "ENDEKS BAZLI" KARŞILAŞTIRIYORUZ:
Bir fonun fiyatı 1.29 TL, başka birinin 47 TL olabilir - bu, ikisinden
hangisinin "daha iyi performans gösterdiğini" göstermez, sadece o fonun
birim fiyatının tarihsel olarak nasıl belirlendiğini gösterir. Adil
karşılaştırma için her fonun başlangıç fiyatını 100 kabul edip, oradan
itibaren % değişimi izliyoruz. Böylece "hangisi daha çok arttı" sorusuna
doğrudan cevap alıyoruz.
"""

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from tefas import Crawler

# --- 1. AYARLAR --------------------------------------------------
# Karşılaştırmak istediğin fon kodlarını buraya ekle.
# TEFAS'ta bir fonun sayfasına girip URL'deki kodu kopyalayabilirsin.
FON_KODLARI = ["AFA", "ICA", "YAY", "AOY"]
# AFA = Para Piyasası Fonu (düşük risk, sabit getiri mantığı)
# ICA = ICBC Turkey Portföy Altın Fonu (kıymetli maden)
# YAY = Yapı Kredi Portföy Yabancı Teknoloji Sektörü Hisse Senedi Fonu (yüksek risk/getiri potansiyeli)
# AOY = Ak Portföy Alternatif Enerji Yabancı Hisse Senedi Fonu (yenilenebilir enerji - First Solar, Vestas, Ørsted vb.)

BUGUN = datetime.now()
BASLANGIC = BUGUN - timedelta(days=90)  # son 90 gün
BASLANGIC_STR = BASLANGIC.strftime("%Y-%m-%d")
BITIS_STR = BUGUN.strftime("%Y-%m-%d")


def tek_fon_cek(kod: str) -> pd.DataFrame:
    """Tek bir fonun verisini çeker ve temizler."""
    tefas = Crawler()
    df = tefas.fetch(
        start=BASLANGIC_STR,
        end=BITIS_STR,
        name=kod,
        columns=["code", "date", "price"],
    )

    if df is None or df.empty:
        print(f"  UYARI: '{kod}' için veri bulunamadı, atlanıyor.")
        return None

    df = df.rename(columns={"code": "fon_kodu", "date": "tarih", "price": "fiyat"})
    df["tarih"] = pd.to_datetime(df["tarih"])
    df["fiyat"] = df["fiyat"].astype(float)
    df = df.sort_values("tarih").reset_index(drop=True)
    return df


def endekse_cevir(df: pd.DataFrame) -> pd.DataFrame:
    """Fiyat serisini, ilk günü 100 kabul ederek endekse çevirir."""
    ilk_fiyat = df["fiyat"].iloc[0]
    df["endeks"] = (df["fiyat"] / ilk_fiyat) * 100
    return df


def tum_fonlari_cek(kodlar: list[str]) -> dict[str, pd.DataFrame]:
    """Listedeki her fon için veri çeker, sözlük olarak döndürür."""
    sonuc = {}
    for kod in kodlar:
        print(f"{kod} çekiliyor...")
        df = tek_fon_cek(kod)
        if df is not None:
            sonuc[kod] = endekse_cevir(df)
    return sonuc


def karsilastirma_tablosu(veriler: dict[str, pd.DataFrame]):
    """Her fonun dönem getirisini basit bir tablo olarak yazdırır."""
    print(f"\n{'Fon':<8} {'Başlangıç':<12} {'Son':<12} {'Getiri (%)':<10}")
    print("-" * 44)
    for kod, df in veriler.items():
        ilk = df["fiyat"].iloc[0]
        son = df["fiyat"].iloc[-1]
        getiri = (son - ilk) / ilk * 100
        print(f"{kod:<8} {ilk:<12.4f} {son:<12.4f} {getiri:<10.2f}")


def karsilastirma_grafigi(veriler: dict[str, pd.DataFrame]):
    """Tüm fonları aynı grafikte, endeks bazlı olarak çizer."""
    plt.figure(figsize=(10, 5))
    for kod, df in veriler.items():
        plt.plot(df["tarih"], df["endeks"], label=kod, marker="o", markersize=2)

    plt.title(f"Fon Karşılaştırması (Başlangıç = 100) - Son {(BUGUN - BASLANGIC).days} Gün")
    plt.xlabel("Tarih")
    plt.ylabel("Endeks (Başlangıç = 100)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("fon_karsilastirma.png")
    print("\nGrafik 'fon_karsilastirma.png' olarak kaydedildi.")


if __name__ == "__main__":
    veriler = tum_fonlari_cek(FON_KODLARI)

    if not veriler:
        print("Hiçbir fon için veri çekilemedi.")
    else:
        karsilastirma_tablosu(veriler)
        karsilastirma_grafigi(veriler)
