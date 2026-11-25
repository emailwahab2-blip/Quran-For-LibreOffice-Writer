# Materi Unggah — extensions.libreoffice.org

Berkas ini berisi teks siap salin-tempel untuk form "Add Extension" di
https://extensions.libreoffice.org/admin (login lewat akun TDF di
https://user.documentfoundation.org). Situs baru (tdf.extensionuploadcenter)
memakai **Bahasa Inggris sebagai bahasa default** — isi English dulu, simpan,
lalu tambah realm "id" untuk terjemahan Indonesia.

Berkas rilis: `Quran-For-LibreOffice-Writer.oxt` (v1.0.0, ~12,6 MB).

---

## 1. Title
Quran For LibreOffice Writer

## 2. Short summary / tagline
Insert Qur'an verses (Arabic + Indonesian translation) and Tafsir al-Qurtubi into Writer — fully offline.

## 3. Description (English — bahasa default)

Quran For LibreOffice Writer inserts Qur'an verses — Arabic text together with the Indonesian Ministry of Religious Affairs (Kemenag 2019) translation — directly into your Writer document, similar to Kemenag's "Qur'an in Word" add-in but for LibreOffice and fully offline.

Features:
- Insert verse + translation alternately (each Arabic verse followed by its translation).
- Two ways to pick: choose a surah + verse range (or a whole surah), or search by Arabic word (harakat-insensitive) or by the Indonesian meaning.
- Automatic Basmalah when starting from verse 1 (except Al-Fatihah and At-Taubah).
- End-of-verse mark ۝ with Arabic-Indic numerals and a `(QS. Name: n)` reference label.
- Optional Tafsir al-Qurtubi (Arabic) — bundled offline, no download needed.
- Clean Arabic rendering: LPMQ Isep Misbah mushaf font (verses) and Amiri (tafsir), RTL with justified alignment.
- Everything is offline — no internet connection required.

Usage: menu **Al-Qur'an ▸ Sisip Ayat…** opens one dialog to choose surah/verse range or search, tick the elements you want (Arabic, translation, reference, Tafsir), then Insert at the cursor.

Data & credits: Arabic text & translation — Kemenag RI 2019 (via equran.id). Tafsir al-Qurtubi — spa5k/tafsir_api dataset. Fonts — LPMQ Isep Misbah (Kemenag) & Amiri (SIL OFL). Code license: MIT.

Developer: Abdul Wahab Ahmad — https://www.facebook.com/emailwahab

## 4. Description (Indonesia — realm "id")

Quran For LibreOffice Writer menyisipkan ayat Al-Qur'an — teks Arab beserta terjemah Kemenag RI 2019 — langsung ke dokumen Writer, mirip add-in "Qur'an in Word" Kemenag tetapi untuk LibreOffice dan sepenuhnya offline.

Fitur:
- Sisip ayat + terjemah selang-seling (tiap ayat Arab langsung diikuti terjemahnya).
- Dua cara memilih: pilih surah + rentang ayat (atau satu surah penuh), atau cari kata Arab (abaikan harakat) / lewat arti Indonesia.
- Basmalah otomatis saat mulai dari ayat 1 (kecuali Al-Fatihah & At-Taubah).
- Penanda akhir ayat ۝ dengan angka Arab-Hindi, dan label rujukan `(QS. Nama: n)`.
- Tafsir Al-Qurthubi (Arab) opsional — ditanam offline, tanpa perlu unduh.
- Teks Arab dirender rapi: font mushaf LPMQ Isep Misbah (ayat) & Amiri (tafsir), RTL rata kanan-kiri.
- Semua data offline — tak butuh koneksi internet.

Pemakaian: menu **Al-Qur'an ▸ Sisip Ayat…** membuka satu dialog untuk memilih surah/rentang ayat atau mencari, centang elemen (Arab, terjemah, rujukan, Tafsir), lalu Sisipkan pada posisi kursor.

Pengembang: Abdul Wahab Ahmad — https://www.facebook.com/emailwahab

## 5. Category / Tags
Kategori: **Writer**. Tag saran: `writer`, `quran`, `arabic`, `islam`, `religion`, `indonesian`, `kemenag`, `offline`, `rtl`, `tafsir`

## 6. Compatibility (versi LibreOffice)
- Diuji di LibreOffice 7.4.
- Karena murni konfigurasi + skrip Python UNO (tanpa kompilasi native), disarankan isi rentang lebar: **4.1 – 25.x** (min 4.1). Aman diklaim minimal 5.0.

## 7. License
- Kode: **MIT** (GNU-compatible; pilihan "MIT/X11" di dropdown lisensi situs).
- Data & font mengikuti sumber masing-masing (Kemenag; SIL OFL utk Amiri).

## 8. Tautan
- Homepage / Source: https://github.com/emailwahab2-blip/Quran-For-LibreOffice-Writer
- Release file: Quran-For-LibreOffice-Writer.oxt

## 9. Icon / Screenshot
- Ikon extension: `build/icons/icon.png` (42×42 — kecil, boleh diunggah tapi sebaiknya buat logo ≥256×256 utk kartu situs).
- Screenshot: BELUM ADA. Sangat disarankan lampirkan 1–2 tangkapan layar (menu "Al-Qur'an" + dialog + hasil sisip) agar entri menarik. Bisa saya bantu ambil bila Antum buka LibreOffice.

---

### Catatan sebelum submit
- Situs pindah dari Plone lama ke sistem baru; kalau nama ini pernah terindeks dari instans lama, JANGAN buat duplikat — klaim via email hostmaster@documentfoundation.org.
- Setelah submit → menunggu **moderasi** TDF sebelum tampil publik.
