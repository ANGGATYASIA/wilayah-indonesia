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

Taruh CSV dari folder `data/` ke `database/seeders/csv/`
(`provinces.csv` dan `regencies.csv` langsung, sisanya per wilayah —
`districts/*.csv` dan `villages/*.csv`), lalu:

```php
// database/seeders/WilayahSeeder.php
namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;

class WilayahSeeder extends Seeder
{
    public function run(): void
    {
        $levels = [
            'provinsi'  => ['pattern' => 'provinces.csv',    'map' => fn($r) => [null, null]],
            'kabupaten' => ['pattern' => 'regencies.csv',    'map' => fn($r) => [$r['type'], $r['province_code']]],
            'kecamatan' => ['pattern' => 'districts/*.csv', 'map' => fn($r) => [null, $r['regency_code']]],
            'desa'      => ['pattern' => 'villages/*.csv',  'map' => fn($r) => [$r['type'], $r['district_code']]],
        ];

        foreach ($levels as $level => ['pattern' => $pattern, 'map' => $map]) {
            foreach (glob(database_path("seeders/csv/{$pattern}")) as $path) {
                $this->seedFile($path, $level, $map);
            }
        }
    }

    private function seedFile(string $path, string $level, callable $map): void
    {
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
