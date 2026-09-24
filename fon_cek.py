"""
TEFAS Fon Veri Çekme - Başlangıç Scripti (v2)
==========================================
Amaç: Tek bir fonun geçmiş fiyat verisini çekip pandas DataFrame'e
      çevirmek ve basit bir grafik çizmek.

Kullanım:
    pip install tefas-crawler   (henüz kurmadıysan)
    python fon_cek.py

NEDEN DEĞİŞTİ: İlk versiyon TEFAS'ın eski, dokümante olmayan
BindHistoryInfo uç noktasını doğrudan çağırıyordu. TEFAS 2026'da bu
uç noktayı tamamen kapattı (404 hatası aldığın buydu). Kendi isteğimizi
her seferinde yeniden reverse-engineer etmek yerine, bu değişikliği
takip eden ve bakımı yapılan bir topluluk kütüphanesi (tefas-crawler)
kullanmak çok daha sağlam bir yaklaşım - gerçek projelerde üçüncü parti
API'lerle çalışırken sık karşılaşacağın bir durum bu.
"""

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from tefas import Crawler

# --- 1. AYARLAR --------------------------------------------------
# Örnek fon kodu: AFA = bir para piyasası fonu örneği.
# Gerçek kodu tefas.gov.tr'de fonun sayfasından (URL'deki kod) alabilirsin.
FON_KODU = "AFA"

BUGUN = datetime.now()
BASLANGIC = BUGUN - timedelta(days=90)  # son 90 gün

BASLANGIC_STR = BASLANGIC.strftime("%Y-%m-%d")
BITIS_STR = BUGUN.strftime("%Y-%m-%d")


def veri_cek() -> pd.DataFrame:
    """tefas-crawler kütüphanesi ile fon geçmiş verisini çeker."""
    tefas = Crawler()
    df = tefas.fetch(
        start=BASLANGIC_STR,
        end=BITIS_STR,
        name=FON_KODU,
        columns=["code", "date", "price"],
    )

    if df is None or df.empty:
        raise ValueError(
            f"Veri bulunamadı. Fon kodu '{FON_KODU}' doğru mu, "
            f"tarih aralığında işlem var mı kontrol et."
        )

    return df


def temizle(df: pd.DataFrame) -> pd.DataFrame:
    """Sütun isimlerini sadeleştirir ve tarihe göre sıralar."""
    df = df.rename(columns={
        "code": "fon_kodu",
        "date": "tarih",
        "price": "fiyat",
    })
    df["tarih"] = pd.to_datetime(df["tarih"])
    df["fiyat"] = df["fiyat"].astype(float)
    df = df.sort_values("tarih").reset_index(drop=True)
    return df


def grafik_ciz(df: pd.DataFrame):
    """Fiyat serisini basit bir çizgi grafikte gösterir."""
    plt.figure(figsize=(10, 5))
    plt.plot(df["tarih"], df["fiyat"], marker="o", markersize=3)
    plt.title(f"{FON_KODU} - Son {(BUGUN - BASLANGIC).days} Günlük Fiyat Hareketi")
    plt.xlabel("Tarih")
    plt.ylabel("Fiyat (TL)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("fon_grafik.png")
    print("Grafik 'fon_grafik.png' olarak kaydedildi.")


if __name__ == "__main__":
    print(f"{FON_KODU} için {BASLANGIC_STR} - {BITIS_STR} arası veri çekiliyor...")
    ham_veri = veri_cek()
    df = temizle(ham_veri)

    print(f"\n{len(df)} satır veri çekildi. İlk 5 satır:")
    print(df[["tarih", "fon_kodu", "fiyat"]].head())

    print(f"\nSon fiyat: {df['fiyat'].iloc[-1]:.4f} TL")
    ilk = df["fiyat"].iloc[0]
    son = df["fiyat"].iloc[-1]
    getiri = (son - ilk) / ilk * 100
    print(f"Dönem getirisi: %{getiri:.2f}")

    grafik_ciz(df)
