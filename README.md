# Quran For LibreOffice Writer

Add-in (extension `.oxt`) untuk **LibreOffice Writer** yang menyisipkan **ayat Al-Qur'an (teks Arab) beserta terjemah Kemenag 2019** langsung ke dokumen — mirip add-in *"Qur'an in Word"* Kemenag, tetapi untuk LibreOffice dan sepenuhnya **offline**.

> Insert Qur'an verses (Arabic + Indonesian translation) and Tafsir al-Qurtubi into your LibreOffice Writer document — fully offline.

## ✨ Fitur

- **Sisip ayat + terjemah** selang-seling (tiap ayat Arab langsung diikuti terjemahnya).
- **Dua cara memilih:**
  - Pilih **surah** + **rentang ayat** (atau satu surah penuh).
  - **Cari ayat** dengan kata **Arab** (mengabaikan harakat) *atau* lewat **arti Indonesia** — hasil pencarian menyesuaikan jenis query.
- **Basmalah otomatis** saat mulai dari ayat 1 (kecuali Al-Fatihah & At-Taubah).
- Penanda akhir ayat ۝ dengan angka Arab-Hindi, dan label rujukan `(QS. Nama: n)`.
- **Tafsir Al-Qurthubi (Arab)** opsional — **ditanam offline**, tanpa perlu unduh.
- Teks Arab dirender rapi: font mushaf **LPMQ Isep Misbah** (ayat) & **Amiri** (tafsir), arah **RTL** + rata kanan-kiri, jarak antar-baris nyaman.
- Semua data **offline** — tak butuh koneksi internet.

## 📦 Pasang

1. Unduh berkas **`Quran-For-LibreOffice-Writer.oxt`** dari repo ini.
2. Buka LibreOffice → **Tools ▸ Extension Manager… ▸ Add…**, pilih berkas `.oxt` tersebut.
3. **Tutup LibreOffice sepenuhnya lalu buka kembali.**
4. Buka Writer → menu **Al-Qur'an ▸ Sisip Ayat…**

## 🖱️ Pakai

Menu **Al-Qur'an → Sisip Ayat…** membuka satu dialog:

- **Surah** + **Ayat awal/akhir**, atau centang **Satu surah penuh**.
- Atau kotak **cari ayat** (ketik kata Arab / arti Indonesia) → pilih hasil.
- Centang elemen: **Teks Arab**, **Terjemah**, **Info surah:ayat**, dan **+ Tafsir Al-Qurthubi**.
- **Sisipkan** → konten masuk pada posisi kursor.

## 🛠️ Bangun dari sumber

Extension ini murni konfigurasi + skrip Python (UNO); tak perlu kompilasi. Untuk membungkus ulang `.oxt`:

```bash
cd build
zip -r -X ../Quran-For-LibreOffice-Writer.oxt . -x '*.DS_Store'
# atau, tanpa 'zip':
python3 -c "import zipfile,os;z=zipfile.ZipFile('../Quran-For-LibreOffice-Writer.oxt','w',zipfile.ZIP_DEFLATED);[z.write(os.path.join(r,f),os.path.relpath(os.path.join(r,f),'.')) for r,_,fs in os.walk('.') for f in fs];z.close()"
```

Pasang lewat CLI: `unopkg add -f Quran-For-LibreOffice-Writer.oxt`

### Struktur

```
build/
  description.xml, META-INF/manifest.xml   # metadata extension
  Addons.xcu                               # menu "Al-Qur'an"
  ProtocolHandler.xcu                      # handler perintah
  python/wonderquran.py                    # komponen UNO: dialog + logika sisip
  data/quran_kemenag.json                  # 114 surah, teks Arab + terjemah
  data/tafsir/qurtubi/<1..114>.json        # Tafsir Al-Qurthubi (Arab)
  fonts/lpmq.ttf, fonts/amiri.ttf          # font Arab (dibundel)
```

## 📚 Sumber data & kredit

- **Teks Arab & terjemah:** Kemenag RI 2019 (via [equran.id](https://equran.id)).
- **Tafsir Al-Qurthubi (Arab):** dataset [spa5k/tafsir_api](https://github.com/spa5k/tafsir_api).
- **Font:** LPMQ Isep Misbah (Kemenag) & [Amiri](https://github.com/aliftype/amiri) (SIL OFL).

## 👤 Pengembang

**Abdul Wahab Ahmad** — <https://www.facebook.com/emailwahab>

## 📄 Lisensi

Kode: MIT (lihat `LICENSE`). Data & font mengikuti lisensi masing-masing sumber di atas.
