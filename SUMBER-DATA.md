# Sumber Data

Catatan asal-usul data repo ini: vintage, kecocokan antar sumber, dan cara
memperbarui saat ada pemekaran wilayah.

## 1. Struktur wilayah administratif

- **Sumber mentah:** `source/wilayah.sql` dari
  [cahyadsn/wilayah](https://github.com/cahyadsn/wilayah) (lisensi MIT).
- **Vintage:** Kepmendagri No. 300.2.2-2430 Tahun 2025 (diperbarui 13 Feb 2026
  di repo sumber).
- **Cakupan:** 38 provinsi, 514 kabupaten/kota, 7.285 kecamatan,
  83.762 desa/kelurahan.
- Sudah mencakup 4 provinsi pemekaran Papua: Papua Selatan (93),
  Papua Tengah (94), Papua Pegunungan (95), Papua Barat Daya (96).

## 2. Kode pos

- **Sumber mentah:** `source/kodepos_parsed.csv` dari
  [mrayhanfadil/kodepos-id](https://github.com/mrayhanfadil/kodepos-id)
  (lisensi MIT), yang di-scrape dari [nomor.net](https://www.nomor.net)
  pada 21 Agustus 2026.
- **Cakupan:** 83.712 desa/kelurahan.
- **Vintage kode:** berbasis Kepmendagri 2022, sehingga ada selisih kecil
  dengan struktur 2025 (pemekaran baru).

## 3. Penggabungan

`scripts/build.py` memakai struktur 2025 sebagai acuan nama dan hierarki,
lalu menempelkan kode pos dengan mencocokkan kode wilayah bertitik
(mis. `11.01.01.2001`).

- **Kecocokan:** 81.935 dari 83.762 desa (97,8%) mendapat kode pos.
  Sisanya `postal_code: null` — kebanyakan desa di wilayah pemekaran
  terbaru (terutama Papua Barat Daya) yang belum ada di data 2022.
- **Tipe kabupaten/kota:** diambil dari kolom `dt2` data kode pos.
  Untuk 6 kabupaten/kota di Papua Barat Daya yang tidak ada di data 2022,
  dipakai heuristik kode >= 71 = Kota (hasilnya benar: 96.71 Kota Sorong,
  sisanya kabupaten).
- **Tipe desa/kelurahan:** dari flag `is_kelurahan` data kode pos; kalau
  tidak ada, dari awalan kode (1xxx = Kelurahan, 2xxx = Desa).
- Nama dibersihkan dari spasi berlebih di ujung (5 baris di data mentah).

## 4. Memperbarui data

1. Unduh `wilayah.sql` terbaru dari cahyadsn/wilayah ke `source/`
   (timpa file lama).
2. Kalau ada dump kode pos yang lebih baru, timpa
   `source/kodepos_parsed.csv` (kolom yang dipakai: `kode_wilayah`,
   `kode_pos`, `dt2`, `is_kelurahan`).
3. Jalankan `python3 scripts/build.py`.
4. Cek angka di `api/index.json`, commit hasilnya.

Jangan mengedit file di `api/` atau `data/` manual — semuanya hasil generate.
