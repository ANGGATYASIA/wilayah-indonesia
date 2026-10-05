#!/usr/bin/env python3
"""Build script untuk repo wilayah-indonesia.

Membaca:
  source/wilayah.sql          (cahyadsn/wilayah, Kepmendagri 300.2.2-2430/2025, MIT)
  source/kodepos_parsed.csv   (mrayhanfadil/kodepos-id, nomor.net, MIT)

Menghasilkan:
  api/       JSON statis siap diakses via CDN (jsDelivr)
  data/      CSV per level
"""
import csv, json, os, re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'source')

def parse_wilayah():
    sql = open(os.path.join(SRC, 'wilayah.sql'), encoding='utf-8').read()
    rows = re.findall(r"\('([\d.]+)','((?:[^']|'')*)'\)", sql)
    out = []
    for kode, nama in rows:
        out.append((kode, nama.replace("''", "'").strip()))
    return out

def parse_kodepos():
    m = {}
    with open(os.path.join(SRC, 'kodepos_parsed.csv'), encoding='utf-8') as f:
        for r in csv.DictReader(f):
            kode = r['kode_wilayah'].strip()
            if not kode or kode in m:
                continue
            m[kode] = {
                'postal_code': r['kode_pos'].strip() or None,
                'dt2': r['dt2'].strip(),  # Kabupaten / Kota
                'is_kelurahan': r['is_kelurahan'].strip() == '1',
            }
    return m

def main():
    rows = parse_wilayah()
    kp = parse_kodepos()

    provinces, regencies, districts, villages = {}, {}, {}, {}
    reg_type = {}  # regency code -> Kabupaten/Kota
    for kode, nama in rows:
        parts = kode.split('.')
        if len(parts) == 1:
            provinces[kode] = nama
        elif len(parts) == 2:
            regencies[kode] = nama
        elif len(parts) == 3:
            districts[kode] = nama
        elif len(parts) == 4:
            villages[kode] = nama

    # tipe kabupaten/kota dari data kode pos
    for kode, v in kp.items():
        p = kode.split('.')
        if len(p) == 4 and v['dt2']:
            reg_type['.'.join(p[:2])] = v['dt2']

    missing_type = 0
    for kode in regencies:
        if kode not in reg_type:
            missing_type += 1
            reg_type[kode] = 'Kota' if int(kode.split('.')[1]) >= 71 else 'Kabupaten'

    # bangun struktur
    prov_list = [{'code': c, 'name': provinces[c]} for c in sorted(provinces)]
    reg_by_prov = defaultdict(list)
    for c in sorted(regencies):
        prov = c.split('.')[0]
        reg_by_prov[prov].append({'code': c, 'name': regencies[c],
                                 'type': reg_type[c], 'province_code': prov})
    dis_by_prov = defaultdict(list)
    for c in sorted(districts):
        p = c.split('.')
        dis_by_prov[p[0]].append({'code': c, 'name': districts[c],
                                 'regency_code': '.'.join(p[:2])})
    vil_by_reg = defaultdict(list)
    matched_pos = 0
    for c in sorted(villages):
        p = c.split('.')
        info = kp.get(c)
        if info and info['postal_code']:
            matched_pos += 1
            vtype = 'Kelurahan' if info['is_kelurahan'] else 'Desa'
            pos = info['postal_code']
        else:
            vtype = 'Kelurahan' if p[3].startswith('1') else 'Desa'
            pos = None
        vil_by_reg['.'.join(p[:2])].append({
            'code': c, 'name': villages[c], 'type': vtype,
            'postal_code': pos, 'district_code': '.'.join(p[:3]),
        })

    api = os.path.join(ROOT, 'api')
    os.makedirs(os.path.join(api, 'regencies'), exist_ok=True)
    os.makedirs(os.path.join(api, 'districts'), exist_ok=True)
    os.makedirs(os.path.join(api, 'villages'), exist_ok=True)

    def w(path, obj):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, separators=(',', ':'))

    w(os.path.join(api, 'provinces.json'), prov_list)
    for prov, lst in reg_by_prov.items():
        w(os.path.join(api, 'regencies', prov + '.json'), lst)
    for prov, lst in dis_by_prov.items():
        w(os.path.join(api, 'districts', prov + '.json'), lst)
    for reg, lst in vil_by_reg.items():
        w(os.path.join(api, 'villages', reg + '.json'), lst)
    w(os.path.join(api, 'index.json'), {
        'name': 'wilayah-indonesia',
        'description': 'Data wilayah administratif Indonesia: provinsi, kabupaten/kota, kecamatan, desa/kelurahan + kode pos.',
        'version': '2025.1',
        'source': 'Kepmendagri No. 300.2.2-2430 Tahun 2025; kode pos dari nomor.net',
        'counts': {'provinces': len(provinces), 'regencies': len(regencies),
                   'districts': len(districts), 'villages': len(villages)},
        'villages_with_postal_code': matched_pos,
    })

    data = os.path.join(ROOT, 'data')
    os.makedirs(data, exist_ok=True)

    def wcsv(path, header, rows):
        with open(path, 'w', encoding='utf-8', newline='') as f:
            wr = csv.writer(f)
            wr.writerow(header)
            wr.writerows(rows)

    wcsv(os.path.join(data, 'provinces.csv'), ['code', 'name'],
         [(c, provinces[c]) for c in sorted(provinces)])
    wcsv(os.path.join(data, 'regencies.csv'), ['code', 'name', 'type', 'province_code'],
         [(c, regencies[c], reg_type[c], c.split('.')[0]) for c in sorted(regencies)])
    wcsv(os.path.join(data, 'districts.csv'), ['code', 'name', 'regency_code'],
         [(c, districts[c], '.'.join(c.split('.')[:2])) for c in sorted(districts)])
    vrows = []
    for c in sorted(villages):
        p = c.split('.')
        info = kp.get(c)
        if info and info['postal_code']:
            vtype = 'Kelurahan' if info['is_kelurahan'] else 'Desa'
            pos = info['postal_code']
        else:
            vtype = 'Kelurahan' if p[3].startswith('1') else 'Desa'
            pos = ''
        vrows.append((c, villages[c], vtype, pos, '.'.join(p[:3])))
    wcsv(os.path.join(data, 'villages.csv'), ['code', 'name', 'type', 'postal_code', 'district_code'], vrows)

    print('provinsi:', len(provinces))
    print('kab/kota:', len(regencies), '(tipe dari data kodepos; fallback heuristik:', missing_type, ')')
    print('kecamatan:', len(districts))
    print('desa/kelurahan:', len(villages))
    print('desa ber-kode-pos:', matched_pos, f'({matched_pos/len(villages)*100:.1f}%)')
    print('contoh provinsi:', [p['name'] for p in prov_list if p['code'] in ('93', '94', '95', '96')])

if __name__ == '__main__':
    main()
