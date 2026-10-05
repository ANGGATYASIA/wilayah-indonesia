# Contoh: Laravel — seeder wilayah

Impor CSV ke tabel `wilayah` sekali jalan, lalu relasinya tinggal pakai
`code` bertitik (mis. `11.01.01.2001`).

## 1. Migration

```php
// database/migrations/xxxx_create_wilayah_table.php
Schema::create('wilayah', function (Blueprint $table) {
    $table->string('code', 16)->primary();   // '11.01.01.2001'
    $table->string('name');
    $table->enum('level', ['provinsi', 'kabupaten', 'kecamatan', 'desa']);
    $table->string('type')->nullable();      // Kabupaten/Kota, Desa/Kelurahan
    $table->string('postal_code', 5)->nullable();
    $table->string('parent_code', 16)->nullable()->index();
});
```

## 2. Seeder

Taruh keempat CSV dari folder `data/` ke `database/seeders/csv/`,
lalu:

```php
// database/seeders/WilayahSeeder.php
namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class WilayahSeeder extends Seeder
{
    public function run(): void
    {
        $files = [
            'provinsi'  => ['provinces.csv',  fn($r) => [null, null]],
            'kabupaten' => ['regencies.csv',  fn($r) => [$r['type'], $r['province_code']]],
            'kecamatan' => ['districts.csv',  fn($r) => [null, $r['regency_code']]],
            'desa'      => ['villages.csv',   fn($r) => [$r['type'], $r['district_code']]],
        ];

        foreach ($files as $level => [$file, $map]) {
            $path = database_path("seeders/csv/{$file}");
            $rows = array_map('str_getcsv', file($path));
            $head = array_shift($rows);

            $batch = [];
            foreach ($rows as $row) {
                $r = array_combine($head, $row);
                [$type, $parent] = $map($r);
                $batch[] = [
                    'code'        => $r['code'],
                    'name'        => $r['name'],
                    'level'       => $level,
                    'type'        => $type,
                    'postal_code' => $r['postal_code'] ?? null,
                    'parent_code' => $parent,
                ];
                if (count($batch) === 1000) {
                    DB::table('wilayah')->upsert($batch, 'code');
                    $batch = [];
                }
            }
            if ($batch) DB::table('wilayah')->upsert($batch, 'code');
        }
    }
}
```

Jalankan: `php artisan db:seed --class=WilayahSeeder`

## 3. Contoh query

```php
// dropdown kabupaten di Jawa Barat (32)
$kabupaten = DB::table('wilayah')->where('parent_code', '32')->get();

// cari desa dari kode pos
$desa = DB::table('wilayah')
    ->where('level', 'desa')
    ->where('postal_code', '10110')
    ->get();
```
