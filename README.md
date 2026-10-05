# Wilayah Indonesia

Data wilayah administratif Indonesia lengkap: **38 provinsi, 514 kabupaten/kota,
7.285 kecamatan, 83.762 desa/kelurahan** — 97,8% desa sudah terpetakan ke kode pos.
Tersedia sebagai JSON statis (tinggal `fetch`, tanpa server) dan CSV.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Data: Kepmendagri 2025](https://img.shields.io/badge/Data-Kepmendagri%202025-blue)](#sumber-data)

## Pakai langsung tanpa install

Semua file JSON bisa diakses lewat CDN jsDelivr langsung dari repo ini.
Ganti `ANGGATYASIA` dengan username GitHub kamu kalau fork.

```text
https://cdn.jsdelivr.net/gh/ANGGATYASIA/wilayah-indonesia@main/api/provinces.json
https://cdn.jsdelivr.net/gh/ANGGATYASIA/wilayah-indonesia@main/api/regencies/11.json
https://cdn.jsdelivr.net/gh/ANGGATYASIA/wilayah-indonesia@main/api/districts/11.json
https://cdn.jsdelivr.net/gh/ANGGATYASIA/wilayah-indonesia@main/api/villages/11.01.json
https://cdn.jsdelivr.net/gh/ANGGATYASIA/wilayah-indonesia@main/api/index.json
```

Contoh JavaScript:

```js
const BASE = 'https://cdn.jsdelivr.net/gh/ANGGATYASIA/wilayah-indonesia@main/api';

// daftar provinsi
const provinces = await (await fetch(`${BASE}/provinces.json`)).json();

// kabupaten/kota di Aceh (kode 11)
const regencies = await (await fetch(`${BASE}/regencies/11.json`)).json();

// kecamatan per provinsi (dikelompokkan per provinsi agar file tetap kecil)
const districts = await (await fetch(`${BASE}/districts/11.json`)).json();

// desa/kelurahan per kabupaten (lengkap dengan kode pos)
const villages = await (await fetch(`${BASE}/villages/11.01.json`)).json();
// -> [{ code: '11.01.01.2001', name: 'Keude Bakongan', type: 'Desa',
//      postal_code: '23773', district_code: '11.01.01' }, ...]
```

Contoh cascading dropdown siap pakai ada di [`demo.html`](demo.html).

## Struktur data

Kode wilayah memakai format Kemendagri bertitik, mis. `11.01.01.2001`
(provinsi.kabupaten.kecamatan.desa).

| File | Isi |
|---|---|
| `api/provinces.json` | 38 provinsi |
| `api/regencies/{kode_prov}.json` | kabupaten/kota per provinsi (`type`: Kabupaten/Kota) |
| `api/districts/{kode_prov}.json` | kecamatan per provinsi (`regency_code` untuk relasi) |
| `api/villages/{kode_kab}.json` | desa/kelurahan per kabupaten (`type`: Desa/Kelurahan, `postal_code`, `district_code`) |
| `api/index.json` | meta: versi, jumlah data, sumber |

Satu desa/kelurahan:

```json
{
  "code": "31.71.01.1001",
  "name": "Gambir",
  "type": "Kelurahan",
  "postal_code": "10110",
  "district_code": "31.71.01"
}
```

`postal_code` bernilai `null` untuk sebagian kecil desa (terutama wilayah
pemekaran terbaru yang belum terpetakan).

## File CSV

Untuk diimpor ke database atau diolah dengan pandas/spreadsheet:

| File | Kolom |
|---|---|
| `data/provinces.csv` | code, name |
| `data/regencies.csv` | code, name, type, province_code |
| `data/districts.csv` | code, name, regency_code |
| `data/villages.csv` | code, name, type, postal_code, district_code |

Contoh seeder Laravel dan skrip Python ada di folder [`examples/`](examples/).

## Sumber data

- Struktur wilayah: **Kepmendagri No. 300.2.2-2430 Tahun 2025**,
  via [cahyadsn/wilayah](https://github.com/cahyadsn/wilayah) (MIT).
- Kode pos: scrape [nomor.net](https://www.nomor.net),
  via [mrayhanfadil/kodepos-id](https://github.com/mrayhanfadil/kodepos-id) (MIT),
  83.712 desa/kelurahan.
- Detail vintage, kecocokan data, dan cara memperbarui: [`SUMBER-DATA.md`](SUMBER-DATA.md).

## Regenerasi

Seluruh file `api/` dan `data/` dihasilkan oleh [`scripts/build.py`](scripts/build.py)
dari file mentah di `source/`. Kalau ada pemekaran wilayah baru, taruh file
sumber terbaru di `source/` lalu jalankan:

```bash
python3 scripts/build.py
```

## Lisensi

MIT — lihat [`LICENSE`](LICENSE). Data bersumber dari dokumen publik
pemerintah dan dataset MIT yang disebut di atas.
