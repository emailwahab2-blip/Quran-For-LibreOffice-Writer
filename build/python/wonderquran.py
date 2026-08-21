# -*- coding: utf-8 -*-
# Wonder Quran — LibreOffice add-in: sisip ayat Al-Qur'an + terjemah (Kemenag),
# dengan mode pilih-nomor & cari-ayat. Data offline dibundel di extension.
# Pengembang: Abdul Wahab Ahmad — https://www.facebook.com/emailwahab
import json
import os
import re
import uno
import unohelper
from com.sun.star.frame import XDispatchProvider, XDispatch
from com.sun.star.lang import XServiceInfo, XInitialization
from com.sun.star.awt import XActionListener, XItemListener

IMPL_NAME = "com.wahab.wonderquran.Handler"
PKG_ID = "com.wahab.wonderquran"
PROTO = "com.wahab.wonderquran:"

# konstanta UNO
from com.sun.star.text.ControlCharacter import PARAGRAPH_BREAK
RL_TB = 1   # com.sun.star.text.WritingMode2.RL_TB
LR_TB = 0
PA_LEFT = 0
PA_RIGHT = 1
PA_BLOCK = 2
PA_CENTER = 3

ARABIC_INDIC = "٠١٢٣٤٥٦٧٨٩"
QURAN_FONT = "LPMQ Isep Misbah"     # dibundel di extension
QURAN_FONT_FALLBACK = "KFGQPC Uthman Taha Naskh"
TAFSIR_FONT = "Amiri"               # dibundel di extension (untuk prosa tafsir)
BASMALAH = "بِسْمِ اللّٰهِ الرَّحْمٰنِ الرَّحِيْمِ"

# Tafsir Al-Qurthubi (Arab) — DITANAM offline di extension
# (data/tafsir/qurtubi/<surah>.json, per-ayah {ayah,text}).
TAFSIR_DIR = "qurtubi"
TAFSIR_NAME = "Al-Qurthubi"

# jarak antar-blok (satuan 1/100 mm)
GAP_AYAT = 250      # spasi di atas tiap ayat (pisah dari terjemah sebelumnya)
GAP_ID = 60         # spasi di bawah terjemah
GAP_TAF_LBL = 150   # spasi di atas label tafsir
GAP_TAF = 90        # spasi di bawah tiap paragraf tafsir

_DATA = {"surah": None, "flat": None}
_TAFSIR_MEM = {}    # surah -> {ayah: text}
_BASE = {"path": None}   # path root extension (disimpan saat _load)


# ---------------------------------------------------------------- util data
def _pkg_path(ctx):
    pip = ctx.getByName(
        "/singletons/com.sun.star.deployment.PackageInformationProvider")
    url = pip.getPackageLocation(PKG_ID)
    return unohelper.fileUrlToSystemPath(url)


def _load(ctx):
    if _DATA["surah"] is not None:
        return _DATA["surah"]
    base = _pkg_path(ctx)
    _BASE["path"] = base
    with open(os.path.join(base, "data", "quran_kemenag.json"),
              "r", encoding="utf-8") as f:
        d = json.load(f)
    _DATA["surah"] = d["surah"]
    return _DATA["surah"]


def _flat(ctx):
    if _DATA["flat"] is not None:
        return _DATA["flat"]
    flat = []
    for s in _load(ctx):
        for a in s["ayat"]:
            flat.append({
                "sn": s["nomor"], "nama": s["namaLatin"],
                "n": a["n"], "ar": a["ar"], "id": a["id"],
                "arn": _norm_ar(a["ar"]), "idn": a["id"].lower(),
            })
    _DATA["flat"] = flat
    return flat


def _to_arabic(n):
    return "".join(ARABIC_INDIC[int(c)] for c in str(n))


# normalisasi Arab (abaikan harakat/tasykil) — port ArabicNormalizer WonderOffice
_STRIP = set()
for a, b in [(0x0610, 0x061A), (0x064B, 0x065F), (0x06D6, 0x06ED)]:
    _STRIP.update(range(a, b + 1))
_STRIP.update([0x0670, 0x0640])  # dagger alif + tatwil
_MAP = {'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ٱ': 'ا',
        'ى': 'ي', 'ؤ': 'و', 'ئ': 'ي', 'ة': 'ه'}


def _norm_ar(s):
    out = []
    for ch in s:
        c = ord(ch)
        if c in _STRIP:
            continue
        out.append(_MAP.get(ch, ch))
    return "".join(out)


def _is_arabic(s):
    return any(0x0600 <= ord(c) <= 0x06FF for c in s)


def _search(ctx, query, limit=200):
    q = query.strip()
    if not q:
        return []
    res = []
    if _is_arabic(q):
        nq = _norm_ar(q)
        for e in _flat(ctx):
            if nq in e["arn"]:
                res.append(e)
                if len(res) >= limit:
                    break
    else:
        lq = q.lower()
        for e in _flat(ctx):
            if lq in e["idn"]:
                res.append(e)
                if len(res) >= limit:
                    break
    return res


# ---------------------------------------------------------------- tafsir
def _clean_tafsir(t):
    if not t:
        return ""
    t = re.sub(r"\[\[.*?\]\]", "", t, flags=re.S)   # aparat editorial ganda
    lines = [ln for ln in t.split("\n")
             if not re.match(r"^[\s*_.\-—–=~]+$", ln)]  # buang pemisah hias
    t = "\n".join(lines)
    t = re.sub(r"\n{3,}", "\n\n", t).strip()
    return t


def _load_tafsir_surah(surah):
    """{ayah:int -> text:str} untuk satu surah, dari bundel offline."""
    if surah in _TAFSIR_MEM:
        return _TAFSIR_MEM[surah]
    path = os.path.join(_BASE["path"] or "", "data", "tafsir",
                        TAFSIR_DIR, "%d.json" % surah)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    m = {}
    for it in data:
        try:
            m[int(it["ayah"])] = it.get("text", "")
        except Exception:
            pass
    _TAFSIR_MEM[surah] = m
    return m


def _linespacing(pct):
    ls = uno.createUnoStruct("com.sun.star.style.LineSpacing")
    ls.Mode = 0        # PROP (proporsional)
    ls.Height = pct
    return ls


# ------------------------------------------------------------ penyisipan doc
def _insert(model, surah, start, end, opt_ar, opt_id, opt_ref, opt_taf):
    text = model.getText()
    ctrl = model.getCurrentController()
    vc = ctrl.getViewCursor()
    cur = text.createTextCursorByRange(vc.getStart())

    def line(s, arabic=False, center=False, space_before=0, space_after=0,
             font=None, size=20.0, bold=False):
        cur.ParaAdjust = PA_CENTER if center else (PA_BLOCK if arabic else PA_LEFT)
        cur.WritingMode = RL_TB if arabic else LR_TB
        cur.ParaTopMargin = space_before
        cur.ParaBottomMargin = space_after
        if arabic:
            cur.CharFontNameComplex = font or QURAN_FONT
            cur.CharHeightComplex = size
            cur.CharWeightComplex = 100.0  # NORMAL
            cur.ParaLineSpacing = _linespacing(120)  # cegah tumpang tindih
        else:
            cur.CharHeight = 11.0 if bold else 12.0
            cur.CharWeight = 150.0 if bold else 100.0  # BOLD / NORMAL
            cur.ParaLineSpacing = _linespacing(100)
        text.insertString(cur, s, False)
        text.insertControlCharacter(cur, PARAGRAPH_BREAK, False)

    nama = surah["namaLatin"]
    snum = surah["nomor"]
    ayat = {a["n"]: a for a in surah["ayat"]}

    tmap = {}
    taf_err = None
    if opt_taf:
        try:
            tmap = _load_tafsir_surah(snum)
        except Exception as e:
            taf_err = str(e)

    if opt_ar and start == 1 and snum not in (1, 9):
        line(BASMALAH, arabic=True, center=True, space_after=GAP_ID)

    for n in range(start, end + 1):
        a = ayat.get(n)
        if not a:
            continue
        if opt_ar:
            line(a["ar"] + " ۝" + _to_arabic(n), arabic=True,
                 space_before=GAP_AYAT)
        if opt_id:
            if opt_ref:
                line("%s (QS. %s: %d)" % (a["id"], nama, n),
                     space_after=GAP_ID)
            else:
                line("%d. %s" % (n, a["id"]), space_after=GAP_ID)
        if opt_taf and not taf_err:
            txt = _clean_tafsir(tmap.get(n, ""))
            if txt:
                line("Tafsir %s — ayat %d:" % (TAFSIR_NAME, n), bold=True,
                     space_before=GAP_TAF_LBL, space_after=40)
                for para in txt.split("\n\n"):
                    para = para.strip()
                    if para:
                        line(para, arabic=True, font=TAFSIR_FONT, size=14.0,
                             space_after=GAP_TAF)

    if opt_taf and taf_err:
        line("(Tafsir %s gagal diunduh: %s)" % (TAFSIR_NAME, taf_err))

    if opt_id and not opt_ref:
        line("(QS. %s: %d-%d)" % (nama, start, end), center=True)

    # kembalikan paragraf lanjutan ke normal (LTR kiri)
    cur.ParaAdjust = PA_LEFT
    cur.WritingMode = LR_TB


# ----------------------------------------------------------------- listener
class _Btn(unohelper.Base, XActionListener):
    def __init__(self, cb):
        self.cb = cb

    def actionPerformed(self, ev):
        self.cb()

    def disposing(self, ev):
        pass


class _Sel(unohelper.Base, XItemListener):
    def __init__(self, cb):
        self.cb = cb

    def itemStateChanged(self, ev):
        self.cb()

    def disposing(self, ev):
        pass


# -------------------------------------------------------------- dialog utama
class Dialog:
    def __init__(self, ctx, smgr, model):
        self.ctx = ctx
        self.smgr = smgr
        self.model = model
        self.surahs = _load(ctx)
        self.results = []
        self.action = None

    def _create(self, service):
        return self.smgr.createInstanceWithContext(service, self.ctx)

    def run(self):
        dlg = self._create("com.sun.star.awt.UnoControlDialog")
        dmodel = self._create("com.sun.star.awt.UnoControlDialogModel")
        dmodel.Width = 260
        dmodel.Height = 264
        dmodel.Title = "Sisip Ayat Al-Qur'an"
        dlg.setModel(dmodel)

        def add(name, service, props):
            m = dmodel.createInstance(
                "com.sun.star.awt.UnoControl%sModel" % service)
            for k, v in props.items():
                setattr(m, k, v)
            dmodel.insertByName(name, m)
            return m

        add("lblS", "FixedText", dict(PositionX=6, PositionY=6, Width=60,
            Height=10, Label="Surah:"))
        surah_items = tuple("%d. %s" % (s["nomor"], s["namaLatin"])
                            for s in self.surahs)
        lstS = add("lstS", "ListBox", dict(PositionX=6, PositionY=17,
            Width=248, Height=12, Dropdown=True, StringItemList=surah_items))
        lstS.SelectedItems = (0,)

        add("lblA", "FixedText", dict(PositionX=6, PositionY=34, Width=60,
            Height=10, Label="Ayat awal:"))
        edA = add("edA", "Edit", dict(PositionX=66, PositionY=32, Width=40,
            Height=12, Text=""))
        add("lblB", "FixedText", dict(PositionX=120, PositionY=34, Width=40,
            Height=10, Label="akhir:"))
        edB = add("edB", "Edit", dict(PositionX=160, PositionY=32, Width=40,
            Height=12, Text=""))
        cbFull = add("cbFull", "CheckBox", dict(PositionX=6, PositionY=48,
            Width=200, Height=10, Label="Satu surah penuh", State=0))

        add("lblQ", "FixedText", dict(PositionX=6, PositionY=64, Width=250,
            Height=10, Label="— atau cari ayat (kata Arab / arti Indonesia) —"))
        edQ = add("edQ", "Edit", dict(PositionX=6, PositionY=76, Width=190,
            Height=12, Text=""))
        add("btnFind", "Button", dict(PositionX=200, PositionY=76, Width=54,
            Height=12, Label="Cari"))
        lstR = add("lstR", "ListBox", dict(PositionX=6, PositionY=92,
            Width=248, Height=90, Dropdown=False))

        cbAr = add("cbAr", "CheckBox", dict(PositionX=6, PositionY=188,
            Width=70, Height=10, Label="Teks Arab", State=1))
        cbId = add("cbId", "CheckBox", dict(PositionX=82, PositionY=188,
            Width=80, Height=10, Label="Terjemah", State=1))
        cbRef = add("cbRef", "CheckBox", dict(PositionX=168, PositionY=188,
            Width=86, Height=10, Label="Info surah:ayat", State=1))
        cbTaf = add("cbTaf", "CheckBox", dict(PositionX=6, PositionY=202,
            Width=248, Height=10,
            Label="+ Tafsir Al-Qurthubi (Arab, offline)",
            State=0))

        add("btnIns", "Button", dict(PositionX=104, PositionY=224, Width=70,
            Height=16, Label="Sisipkan", DefaultButton=True))
        add("btnCancel", "Button", dict(PositionX=180, PositionY=224,
            Width=70, Height=16, Label="Batal"))

        dlg.setVisible(False)
        toolkit = self._create("com.sun.star.awt.Toolkit")
        dlg.createPeer(toolkit, None)

        cS = dlg.getControl("lstS")
        cA = dlg.getControl("edA")
        cB = dlg.getControl("edB")
        cQ = dlg.getControl("edQ")
        cR = dlg.getControl("lstR")

        def do_find():
            q = cQ.getModel().Text
            self.results = _search(self.ctx, q)
            arabic = _is_arabic(q)   # cari Arab → tampilkan ayat; else terjemah
            items = []
            for e in self.results:
                snip = e["ar"] if arabic else e["id"]
                if len(snip) > 60:
                    snip = snip[:60] + "…"
                items.append("QS. %s:%d — %s" % (e["nama"], e["n"], snip))
            m = cR.getModel()
            if not items:
                if (q or "").strip() == "":
                    m.StringItemList = ()               # kotak cari kosong
                else:
                    m.StringItemList = ("(Tidak ada hasil)",)  # bukan macet
            else:
                m.StringItemList = tuple(items)

        def on_pick():
            sel = cR.getSelectedItemPos()
            if sel < 0 or sel >= len(self.results):
                return
            e = self.results[sel]
            cS.getModel().SelectedItems = (e["sn"] - 1,)
            cA.getModel().Text = str(e["n"])
            cB.getModel().Text = str(e["n"])
            cbFull_c = dlg.getControl("cbFull")
            cbFull_c.getModel().State = 0

        def do_insert():
            self.action = "insert"
            dlg.endExecute()

        def do_cancel():
            self.action = None
            dlg.endExecute()

        dlg.getControl("btnFind").addActionListener(_Btn(do_find))
        dlg.getControl("btnIns").addActionListener(_Btn(do_insert))
        dlg.getControl("btnCancel").addActionListener(_Btn(do_cancel))
        cR.addItemListener(_Sel(on_pick))

        dlg.setVisible(True)
        dlg.execute()

        if self.action != "insert":
            dlg.dispose()
            return

        # baca state
        sidx = cS.getSelectedItemPos()
        if sidx < 0:
            sidx = 0
        surah = self.surahs[sidx]
        full = dlg.getControl("cbFull").getModel().State == 1
        opt_ar = dlg.getControl("cbAr").getModel().State == 1
        opt_id = dlg.getControl("cbId").getModel().State == 1
        opt_ref = dlg.getControl("cbRef").getModel().State == 1
        opt_taf = dlg.getControl("cbTaf").getModel().State == 1

        def _int(s, default):
            s = (s or "").strip()
            try:
                return int(s)
            except ValueError:
                return default

        jml = surah["jumlahAyat"]
        if full:
            start, end = 1, jml
        else:
            start = _int(cA.getModel().Text, 1)
            end = _int(cB.getModel().Text, start)
        start = max(1, min(start, jml))
        end = max(start, min(end, jml))

        dlg.dispose()

        if not (opt_ar or opt_id or opt_taf):
            return
        _insert(self.model, surah, start, end, opt_ar, opt_id, opt_ref,
                opt_taf)


# -------------------------------------------------------- ProtocolHandler
class WonderQuranHandler(unohelper.Base, XServiceInfo, XDispatchProvider,
                         XDispatch, XInitialization):
    def __init__(self, ctx):
        self.ctx = ctx
        self.smgr = ctx.getServiceManager()
        self.frame = None

    # XInitialization
    def initialize(self, args):
        if args:
            self.frame = args[0]

    # XServiceInfo
    def getImplementationName(self):
        return IMPL_NAME

    def supportsService(self, name):
        return name == "com.sun.star.frame.ProtocolHandler"

    def getSupportedServiceNames(self):
        return ("com.sun.star.frame.ProtocolHandler",)

    # XDispatchProvider
    def queryDispatch(self, url, target, flags):
        if url.Protocol == PROTO:
            return self
        return None

    def queryDispatches(self, requests):
        return tuple(self.queryDispatch(r.FeatureURL, r.FrameName,
                     r.SearchFlags) for r in requests)

    # XDispatch
    def dispatch(self, url, args):
        if url.Protocol != PROTO:
            return
        if url.Path != "insert":
            return
        try:
            model = self.frame.getController().getModel()
        except Exception:
            return
        try:
            Dialog(self.ctx, self.smgr, model).run()
        except Exception as e:
            self._msg(str(e))

    def addStatusListener(self, listener, url):
        pass

    def removeStatusListener(self, listener, url):
        pass

    def _msg(self, txt):
        try:
            tk = self.smgr.createInstanceWithContext(
                "com.sun.star.awt.Toolkit", self.ctx)
            from com.sun.star.awt.MessageBoxType import ERRORBOX
            box = tk.createMessageBox(
                None, ERRORBOX, 1, "Wonder Quran", txt)
            box.execute()
        except Exception:
            pass


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(
    WonderQuranHandler, IMPL_NAME,
    ("com.sun.star.frame.ProtocolHandler",))
