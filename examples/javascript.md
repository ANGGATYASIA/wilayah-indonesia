# Contoh: JavaScript — dropdown bertingkat

Form alamat klasik: provinsi -> kabupaten/kota -> kecamatan -> desa/kelurahan.
Demo live-nya ada di [`demo.html`](../demo.html).

```html
<select id="provinsi"></select>
<select id="kabupaten"></select>
<select id="kecamatan"></select>
<select id="desa"></select>

<script>
const BASE = 'https://cdn.jsdelivr.net/gh/ANGGATYASIA/wilayah-indonesia@main/api';
const $ = id => document.getElementById(id);

async function get(url) {
  const r = await fetch(url);
  return r.json();
}

function isi(select, items, label) {
  select.innerHTML = `<option value="">${label}</option>` +
    items.map(i => `<option value="${i.code}">${i.name}</option>`).join('');
}

// 1. provinsi
isi($('provinsi'), await get(`${BASE}/provinces.json`), 'Pilih provinsi');

$('provinsi').addEventListener('change', async e => {
  const prov = e.target.value;
  $('kabupaten').innerHTML = '<option>Memuat...</option>';
  const regs = await get(`${BASE}/regencies/${prov}.json`);
  isi($('kabupaten'), regs, 'Pilih kabupaten/kota');
  $('kecamatan').innerHTML = '<option value="">Pilih kecamatan</option>';
  $('desa').innerHTML = '<option value="">Pilih desa/kelurahan</option>';
});

// 2. kecamatan (file per provinsi, saring per kabupaten)
$('kabupaten').addEventListener('change', async e => {
  const kab = e.target.value;              // mis. '11.01'
  const prov = kab.split('.')[0];
  const all = await get(`${BASE}/districts/${prov}.json`);
  isi($('kecamatan'), all.filter(d => d.regency_code === kab), 'Pilih kecamatan');
  $('desa').innerHTML = '<option value="">Pilih desa/kelurahan</option>';
});

// 3. desa/kelurahan + kode pos (file per kabupaten)
$('kecamatan').addEventListener('change', async e => {
  const kec = e.target.value;              // mis. '11.01.01'
  const kab = kec.split('.').slice(0, 2).join('.');
  const all = await get(`${BASE}/villages/${kab}.json`);
  const list = all.filter(v => v.district_code === kec);
  $('desa').innerHTML = '<option value="">Pilih desa/kelurahan</option>' +
    list.map(v => `<option value="${v.code}">${v.name} — ${v.postal_code || '-'}</option>`).join('');
});
</script>
```
