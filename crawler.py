import requests
import pandas as pd
import time

BASE_URL = "https://sirup.inaproc.id/sirup/datatablectr"
ID_KLDI = "D212"
PAGE_SIZE = 10000

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://sirup.inaproc.id/"
}

ENDPOINTS = {
    "Penyedia": "dataruppenyediakldi",
    "Swakelola": "datarupswakelolakldi",
    "PDS": "dataruppenyediaswakelolaallrekapkldi",
}

HEADER_PENYEDIA = [
    "Kode RUP",
    "Satuan Kerja",
    "Nama Paket",
    "Pagu",
    "Metode Pemilihan",
    "Sumber Dana",
    "Kode RUP",
    "Waktu Pemilihan"
]

HEADER_SWAKelola = [
    "Kode RUP",
    "Satuan Kerja",
    "Nama Paket",
    "Pagu",
    "Sumber Dana",
    "Kode RUP",
    "Waktu Pelaksanaan",
    "Status"
]

HEADER_PDS = [
    "Kode RUP",
    "Satuan Kerja",
    "Nama Paket",
    "Pagu",
    "Waktu",
    "Metode",
    "Sumber Dana"
]


def crawl(endpoint, label, tahun):

    print(f"\n📥 Ambil data: {label}")

    start = 0
    rows = []

    while True:

        params = {
            "idKldi": ID_KLDI,
            "tahun": tahun,
            "iDisplayStart": start,
            "iDisplayLength": PAGE_SIZE,
            "sEcho": 1
        }

        url = f"{BASE_URL}/{endpoint}"

        r = requests.get(url, headers=HEADERS, params=params)

        if r.status_code == 404:
            print("⚠️ Endpoint tidak tersedia")
            break

        if r.status_code != 200:
            print(f"⏹️ Stop crawl, status {r.status_code}")
            break

        data = r.json().get("aaData", [])

        if not data:
            print("✅ Data habis")
            break

        rows.extend(data)

        print(f"  ✔ Ambil {len(data)} data (start {start})")

        start += PAGE_SIZE

        time.sleep(0.4)

    return rows


def to_df(rows, label):

    if not rows:
        print(f"⚠️ {label} kosong")
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    print(f"📊 {label}: {df.shape[1]} kolom")

    if label == "Penyedia":
        df.columns = HEADER_PENYEDIA[:df.shape[1]]

    elif label == "Swakelola":
        df.columns = HEADER_SWAKelola[:df.shape[1]]

    elif label == "PDS":
        df.columns = HEADER_PDS[:df.shape[1]]

    return df


def generate_excel(tahun):

    dfs = {}

    for label, endpoint in ENDPOINTS.items():
        dfs[label] = to_df(crawl(endpoint, label, tahun), label)

    output = f"PAKET_RUP_KALSEL_{tahun}.xlsx"

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        for label, df in dfs.items():
            df.to_excel(writer, sheet_name=label, index=False)

    print(f"\n✅ SELESAI! File tersimpan: {output}")

    return output