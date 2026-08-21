# Bekal Port ke Microsoft Word (PC)

Panduan untuk membuat versi **Microsoft Word desktop** dari ekstensi ini
("Quran For LibreOffice Writer"). Versi asli adalah ekstensi LibreOffice Writer
(`.oxt` Python/UNO) — lihat `build/python/wonderquran.py`. Dokumen ini merangkum
apa yang perlu dibawa saat mengerjakan ulang di Claude Code pada PC (yang bisa
menguji langsung di Word).

> **Beda dengan add-in AI:** ini **100% offline** — tidak ada panggilan jaringan.
> Semua data (ayat + terjemah + tafsir) dibundel. Tantangan utamanya bukan logika,
> tapi **membawa data besar & font** ke lingkungan Word.

---

## 1. Jalur yang direkomendasikan: **VBA add-in (`.dotm`)**

Padanan terdekat dengan versi UNO. Object model Word penuh, RTL matang, distribusi
satu file `.dotm` di `%APPDATA%\Microsoft\Word\STARTUP\` → tab Ribbon muncul otomatis.

Alternatif (jangan dulu): Office.js/taskpane (RTL & data lokal besar ribet),
VSTO C# (berat). Untuk data offline besar, VBA + file data di folder tetap paling
praktis.

---

## 2. Fitur & menu (harus identik dengan versi LibreOffice)

Tab/menu **"Al-Qur'an"** → perintah **"Sisip Ayat…"** membuka dialog (UserForm):

- Dropdown **surah** (1–114, `namaLatin`).
- **Ayat awal** & **akhir**, atau centang **"Satu surah penuh"**.
- Kotak **cari ayat**: kata **Arab** (abaikan harakat) → cuplikan ayat; kata
  **Latin** → cuplikan terjemah. Daftar hasil; pilih hasil → isi otomatis surah+ayat.
- Centang: **Teks Arab**, **Terjemah**, **Info surah:ayat**, **+ Tafsir Al-Qurthubi**.
- Tombol **Sisipkan** / **Batal**.

### Aturan penyisipan (selang-seling; WAJIB sama — lihat `_insert` di kode asli)

- Bila mulai ayat 1 & surah bukan 1/9 → sisip **Basmalah** (rata tengah).
- Per ayat: **teks Arab** + spasi + `۝` + **nomor ayat Arab-Hindi** (mis. `۝٥`).
- **Terjemah**: `"<terjemah> (QS. <Nama>: <n>)"` bila Info dicentang, else `"<n>. <terjemah>"`.
- Bila **Tafsir** dicentang: label **bold** `"Tafsir Al-Qurthubi — ayat n:"` lalu
  paragraf tafsir Arab (font Amiri 14pt, RTL).
- Ada margin/spasi antar-blok agar tak tumpang tindih (lihat konstanta `GAP_*`) +
  line-spacing proporsional 120% pada paragraf Arab.

### Format teks Arab

Font mushaf **LPMQ Isep Misbah** (fallback `KFGQPC Uthman Taha Naskh`), ukuran 20pt,
**complex-script**, arah **RTL**, paragraf **justify**. Tafsir pakai **Amiri** 14pt.

---

## 3. Data & aset yang harus dibawa (INTI kesulitan port)

Ada di repo ini, di `build/`:
- `data/quran_kemenag.json` (~2,6MB) — 114 surah, tiap ayat `{n, ar, id}`.
- `data/tafsir/qurtubi/<surah>.json` (1..114) — per-ayah `{ayah, text}`; total ~74MB
  mentah (di `.oxt` terkompres DEFLATE jadi ~12,6MB).
- `fonts/lpmq.ttf`, `fonts/amiri.ttf`.

**Strategi di Word:**
- `.dotm` **tidak** cocok meng-embed 74MB. Distribusikan sebagai **installer/zip**:
  `.dotm` + folder `data\` diletakkan di lokasi tetap, mis.
  `%APPDATA%\QuranForWord\data\...`. VBA baca file dari situ (path via `Environ("APPDATA")`).
- `quran_kemenag.json` (2,6MB) → muat sekali, cache di memori (Dictionary).
- Tafsir → baca **per-surah on-demand** dari file (persis pola `_load_tafsir_surah`).
- **Font tidak ter-install otomatis** oleh `.dotm`. Sertakan `lpmq.ttf` + `amiri.ttf`
  dan minta user meng-install (klik-kanan → Install), atau embed font ke dokumen.

---

## 4. Fungsi util yang harus di-port (ada di `build/python/wonderquran.py`)

- `_to_arabic(n)` — angka Latin → Arab-Hindi (`٠١٢…`).
- `_norm_ar(s)` — normalisasi Arab untuk pencarian: buang harakat/tasykil/tatwil
  (rentang U+0610–061A, 064B–065F, 06D6–06ED, 0670, 0640) + peta `أإآٱ→ا`, `ى→ي`,
  `ؤ→و`, `ئ→ي`, `ة→ه`. **Port persis** agar hasil cari sama.
- `_is_arabic(s)`, `_search(query)` — deteksi query Arab vs Latin lalu cari di
  `ar` (dinormalisasi) atau `id` (lowercase).
- `_clean_tafsir(t)` — buang aparat editorial `[[...]]` + baris pemisah hias.

Di VBA: normalisasi karakter pakai `AscW`/`ChrW` untuk rentang Unicode. Pencarian
substring biasa (`InStr`) setelah normalisasi.

---

## 5. Padanan properti: LibreOffice UNO → Word VBA

| Tujuan | UNO | Word VBA |
|---|---|---|
| **Font Arab (complex)** | `CharFontNameComplex` | `Range.Font.NameBi` |
| **Ukuran Arab (complex)** | `CharHeightComplex` | `Range.Font.SizeBi` |
| **Bold Arab** | `CharWeightComplex` | `Range.Font.BoldBi` |
| Bold teks biasa (label tafsir) | `CharWeight` 150/100 | `Range.Font.Bold` True/False |
| Arah RTL | `WritingMode = RL_TB(1)` | `ParagraphFormat.ReadingOrder = wdReadingOrderRtl` |
| Arah LTR | `WritingMode = LR_TB(0)` | `... = wdReadingOrderLtr` |
| Justify | `ParaAdjust = 2` | `ParagraphFormat.Alignment = wdAlignParagraphJustify` |
| Rata tengah (Basmalah) | `ParaAdjust = 3` | `wdAlignParagraphCenter` |
| Margin atas/bawah paragraf | `ParaTopMargin`/`ParaBottomMargin` (1/100 mm) | `ParagraphFormat.SpaceBefore`/`SpaceAfter` (poin) |
| Line spacing proporsional | `ParaLineSpacing` struct PROP | `ParagraphFormat.LineSpacingRule = wdLineSpaceMultiple` + `.LineSpacing` |
| Bahasa Arab (spell) | — | `Range.LanguageIDOther = wdArabic` |
| Sisip paragraf baru | `insertControlCharacter(PARAGRAPH_BREAK)` | `Range.InsertParagraphAfter` / `Selection.TypeParagraph` |
| Titik sisip | `ViewCursor.getStart()` | `Selection.Range` |

**Catatan:** properti berakhiran **Bi** (Bidirectional/complex script) = padanan
persis `*Complex` di UNO. Untuk teks Arab set pasangan Bi-nya.

---

## 6. Dialog (UserForm) — padanan kontrol

Dropdown surah (ComboBox), Edit ayat (TextBox), CheckBox penuh/Arab/Terjemah/Info/
Tafsir, TextBox cari + tombol Cari, ListBox hasil, tombol Sisipkan/Batal. Perilaku
"pilih hasil → isi surah+ayat" = event `ListBox_Click`.

---

## 7. Uji di Word (HARUS di PC)

- Muat 114 surah / 6236 ayat; cari Arab (abai harakat) & arti; hasil benar.
- Sisip selang-seling: Basmalah, `۝` + angka Arab-Hindi, label ref, tafsir.
- Arab RTL + font LPMQ (install dulu), tafsir Amiri, tak mojibake, tak tumpang tindih.
- Tafsir per-surah terbaca dari folder data.

---

## Referensi silang

Kode sumber lengkap di repo ini (`build/`). `build/python/wonderquran.py` adalah
sumber kebenaran perilaku — samakan format & fungsi util dengannya.
