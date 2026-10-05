# Contoh: Python — olah CSV dengan pandas

```python
import pandas as pd

desa = pd.read_csv('data/villages.csv', dtype=str)

# 1. semua kelurahan di DKI Jakarta (kode 31.*) beserta kode posnya
dki = desa[desa['code'].str.startswith('31.') & (desa['type'] == 'Kelurahan')]
print(dki[['code', 'name', 'postal_code']].head())

# 2. distribusi kode pos: berapa desa per kode pos
print(desa['postal_code'].value_counts().head(10))

# 3. gabung dengan kecamatan untuk alamat lengkap
kec = pd.read_csv('data/districts.csv', dtype=str)
kab = pd.read_csv('data/regencies.csv', dtype=str)

alamat = (desa.merge(kec, left_on='district_code', right_on='code', suffixes=('', '_kec'))
              .merge(kab, left_on='regency_code', right_on='code', suffixes=('', '_kab')))
print(alamat[['name', 'name_kec', 'name_kab', 'postal_code']].head(3))
```

Tanpa pandas, cukup `csv` bawaan Python:

```python
import csv

with open('data/villages.csv', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        if row['postal_code'] == '10110':
            print(row['code'], row['name'])
```
