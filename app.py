import sys, os, re, json, tempfile, subprocess, datetime, webbrowser
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QTextEdit, QTabWidget,
    QProgressBar, QFrame, QStackedWidget, QLineEdit, QMessageBox,
    QSlider, QScrollArea, QDialog, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings, QTimer, QSize
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QBrush, QPen, QLinearGradient, QIcon

from groq import Groq

# ═══════════════════════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════════════════════
def resource_path(rel):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)

def data_path(filename):
    base = os.path.dirname(sys.executable) if getattr(sys,'frozen',False) else os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, filename)

def find_ffmpeg(name):
    if getattr(sys, 'frozen', False): return resource_path(name)
    return name

FFMPEG       = find_ffmpeg("ffmpeg")
FFPROBE      = find_ffmpeg("ffprobe")
HISTORY_FILE = data_path("history.json")

# ═══════════════════════════════════════════════════════════════════════════════
# THEME
# ═══════════════════════════════════════════════════════════════════════════════
DARK  = dict(bg="#09090F",surface="#0F0F1A",card="#1A1A28",border="rgba(255,255,255,0.07)",
             accent="#6366F1",accent2="#818CF8",text="#F1F1F3",muted="#6B6B80",
             sub="#C8C8D8",success="#34D399",scrollbar="#2A2A3A",danger="#F87171")
LIGHT = dict(bg="#F2F2F7",surface="#E8E8ED",card="#FFFFFF",border="rgba(0,0,0,0.09)",
             accent="#5856D6",accent2="#007AFF",text="#1C1C1E",muted="#8E8E93",
             sub="#3C3C43",success="#34C759",scrollbar="#C7C7CC",danger="#EF4444")
CT   = DARK
LANG = "fa"

UI = {
"fa": dict(
    process="پردازش ویدیو", srt_page="ترجمه SRT", history="تاریخچه",
    settings="تنظیمات", about="درباره",
    drop_hint="ویدیوت رو اینجا بنداز\nیا دکمه «انتخاب فایل» رو بزن\n\nMP4 · MOV · MKV · AVI · WEBM\n\n⚠️ به دلیل تحریم‌ها قبل از پردازش از فیلترشکن استفاده کن",
    srt_drop_hint="فایل SRT رو اینجا بنداز\nیا دکمه «انتخاب فایل» رو بزن\n\n.srt",
    browse="📂   انتخاب فایل ویدیو", srt_browse="📂   انتخاب فایل SRT",
    copy="کپی متن", copied="✓ کپی شد", new_video="ویدیو جدید", new_srt="SRT جدید",
    dl_srt="⬇   دانلود SRT انگلیسی", dl_srt_fa="⬇   دانلود SRT فارسی",
    refresh="🔄  اعمال مجدد", tok_refresh="🔄  بروزرسانی",
    tab_en="📝 متن انگلیسی", tab_fa="🌐 ترجمه فارسی", tab_srt="📄 SRT", tab_srt_fa="🌐 SRT فارسی",
    save="ذخیره", saved="✓ ذخیره شد",
    words_label="کلمه در هر خط:", words_hint="۱ = هر کلمه جداگانه  ·  ۱۰ = بدون تغییر",
    lang_select="زبان ویدیو:", lang_en="انگلیسی", lang_fa_vid="فارسی",
    groq_key="Groq API Key", groq_hint="رایگانه — از console.groq.com بگیرش",
    theme_label="تم برنامه", dark_btn="🌑  دارک", light_btn="☀️  روشن",
    lang_label="زبان برنامه",
    usage_label="مصرف توکن امروز (تخمینی)", tok_refresh_hint="برای بروزرسانی دکمه بزن",
    no_key="API Key نداری", no_key_msg="اول از تنظیمات Groq API Key رو وارد کن.",
    err_title="خطا", info_title="اطلاعات",
    sentences="جمله", no_history="هنوز زیرنویسی ساخته نشده.",
    history_open="باز کردن", history_delete="حذف",
    step1="استخراج صدا از ویدیو…", step2="تشخیص متن — Groq Whisper Large v3…",
    step3="ترجمه — Groq LLaMA 3.3 70B…", step4="✅  زیرنویس با موفقیت ساخته شد!",
    srt_step="ترجمه SRT…", srt_done="✅  SRT فارسی آماده شد!",
    saved_srt="فایل SRT ذخیره شد:\n",
    whisper_tok="Whisper", llm_tok="LLM", ver="v1.1  —  رایگان",
    # onboarding
    ob_title1="به MSRT خوش آمدید 👋",
    ob_body1="MSRT زیرنویس ویدیوهای شما رو با هوش مصنوعی استخراج و به فارسی ترجمه می‌کنه.\n\nقبل از شروع، به یک API Key رایگان از Groq نیاز داری.",
    ob_get_key="🔑  دریافت API Key رایگان",
    ob_title2="API Key رو وارد کن",
    ob_body2="بعد از ثبت‌نام در Groq، API Key رو کپی کن و:\n\n۱. از منوی راست روی ⚙️ تنظیمات کلیک کن\n۲. کلید رو در بخش «Groq API Key» وارد کن\n۳. دکمه ذخیره رو بزن",
    ob_title3="آماده‌ای! 🎉",
    ob_body3="حالا ویدیوت رو به صفحه «پردازش ویدیو» بنداز یا از دکمه «انتخاب فایل» استفاده کن.\n\n⚠️ به دلیل تحریم‌ها، قبل از پردازش حتماً از فیلترشکن استفاده کن.",
    ob_next="بعدی ←", ob_done="شروع کن!",
    ob_skip="رد کردن",
),
"en": dict(
    process="Process Video", srt_page="Translate SRT", history="History",
    settings="Settings", about="About",
    drop_hint="Drop your video here\nor click «Browse File»\n\nMP4 · MOV · MKV · AVI · WEBM\n\n⚠️ Due to sanctions, use a VPN before processing",
    srt_drop_hint="Drop your SRT file here\nor click «Browse File»\n\n.srt",
    browse="📂   Browse Video File", srt_browse="📂   Browse SRT File",
    copy="Copy Text", copied="✓ Copied", new_video="New Video", new_srt="New SRT",
    dl_srt="⬇   Download English SRT", dl_srt_fa="⬇   Download Persian SRT",
    refresh="🔄  Re-apply", tok_refresh="🔄  Refresh",
    tab_en="📝 English Text", tab_fa="🌐 Persian Translation", tab_srt="📄 SRT", tab_srt_fa="🌐 Persian SRT",
    save="Save", saved="✓ Saved",
    words_label="Words per line:", words_hint="1 = one word  ·  10 = no change",
    lang_select="Video language:", lang_en="English", lang_fa_vid="Persian",
    groq_key="Groq API Key", groq_hint="Free — get it from console.groq.com",
    theme_label="App Theme", dark_btn="🌑  Dark", light_btn="☀️  Light",
    lang_label="App Language",
    usage_label="Today's token usage (estimated)", tok_refresh_hint="Click to refresh",
    no_key="No API Key", no_key_msg="Add your Groq API Key in Settings first.",
    err_title="Error", info_title="Info",
    sentences="sentences", no_history="No subtitles generated yet.",
    history_open="Open", history_delete="Delete",
    step1="Extracting audio…", step2="Transcribing — Groq Whisper Large v3…",
    step3="Translating — Groq LLaMA 3.3 70B…", step4="✅  Subtitle created successfully!",
    srt_step="Translating SRT…", srt_done="✅  Persian SRT ready!",
    saved_srt="SRT file saved:\n",
    whisper_tok="Whisper", llm_tok="LLM", ver="v1.1  —  Free",
    ob_title1="Welcome to MSRT 👋",
    ob_body1="MSRT extracts subtitles from your videos using AI and translates them to Persian.\n\nFirst, you need a free API Key from Groq.",
    ob_get_key="🔑  Get Free API Key",
    ob_title2="Enter Your API Key",
    ob_body2="After signing up at Groq, copy your API Key and:\n\n1. Click ⚙️ Settings in the right menu\n2. Paste your key in the «Groq API Key» field\n3. Click Save",
    ob_title3="You're Ready! 🎉",
    ob_body3="Now drop your video into the «Process Video» page or use the Browse button.\n\n⚠️ Due to sanctions, use a VPN before processing.",
    ob_next="Next →", ob_done="Let's go!",
    ob_skip="Skip",
)}

def T(k): return UI[LANG].get(k,k)
def t(k): return CT[k]

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def fmt_ts(sec):
    ms=int((sec%1)*1000); s=int(sec)%60; m=int(sec//60)%60; h=int(sec//3600)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def chunk_segments(segments, wpl):
    if wpl >= 10: return segments
    result=[]
    for seg in segments:
        words=seg["text"].split(); fa_words=seg.get("fa","").split(); n=len(words)
        if n<=wpl: result.append(seg); continue
        dur=seg["end"]-seg["start"]
        for i in range(0,n,wpl):
            ws=words[i:i+wpl]; fs=fa_words[i:i+wpl] if fa_words else []
            result.append({"start":seg["start"]+(i/n)*dur,"end":seg["start"]+(min(i+wpl,n)/n)*dur,
                           "text":" ".join(ws),"fa":" ".join(fs)})
    return result

def to_srt(segs, fa=False):
    return "\n".join(f"{i}\n{fmt_ts(s['start'])} --> {fmt_ts(s['end'])}\n"
                     f"{s.get('fa',s['text']) if fa else s['text']}\n"
                     for i,s in enumerate(segs,1))

def to_text(segs, lang):
    return "\n".join(f"[{fmt_ts(s['start'])}]  {s.get('fa',s['text']) if lang=='fa' else s['text']}"
                     for s in segs)

def parse_srt(text):
    segs=[]
    for block in re.split(r'\n\s*\n', text.strip()):
        lines=block.strip().split('\n')
        if len(lines)<3: continue
        m=re.match(r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})',lines[1])
        if not m: continue
        def ts2s(ts):
            h,r=ts.split(':',1); mm,r2=r.split(':',1); s,ms=r2.split(',')
            return int(h)*3600+int(mm)*60+int(s)+int(ms)/1000
        segs.append({"start":ts2s(m.group(1)),"end":ts2s(m.group(2)),"text":" ".join(lines[2:]).strip(),"fa":""})
    return segs

GROQ_DAILY={"whisper":28800,"llm":500000}

def estimate_tokens(segs):
    if not segs: return 0,0
    dur=segs[-1]["end"]-segs[0]["start"]
    words=sum(len(s["text"].split()) for s in segs)
    return int(dur*7), int(words*2.5)

def load_history():
    try:
        with open(HISTORY_FILE,encoding="utf-8") as f: return json.load(f)
    except: return []

def save_history(recs):
    try:
        with open(HISTORY_FILE,"w",encoding="utf-8") as f: json.dump(recs,f,ensure_ascii=False,indent=2)
    except Exception as e: print(f"History save error: {e}")

def add_history(fname,segs,wh,llm):
    recs=load_history()
    recs.insert(0,{"date":datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                   "filename":fname,"sentences":len(segs),"wh_tok":wh,"llm_tok":llm,"segments":segs})
    save_history(recs[:50])

def today_usage():
    today=datetime.datetime.now().strftime("%Y-%m-%d")
    wh=llm=0
    for r in load_history():
        if r.get("date","").startswith(today): wh+=r.get("wh_tok",0); llm+=r.get("llm_tok",0)
    return wh,llm

# ═══════════════════════════════════════════════════════════════════════════════
# WORKERS
# ═══════════════════════════════════════════════════════════════════════════════
def translate_batches(client, segments, src_lang="en"):
    """Translate segments. If src_lang='fa', translate FA→EN. Otherwise EN→FA."""
    for i in range(0,len(segments),60):
        batch=segments[i:i+60]
        numbered="\n".join(f"[{j}] {s['text']}" for j,s in enumerate(batch))
        if src_lang=="fa":
            prompt=("You are a professional translator. Translate each numbered Persian (Farsi) line to natural English.\n"
                    "Rules:\n- Output ONLY the translated lines\n- Keep numbering [0],[1],...\n"
                    "- No explanation or extra text\n\n"+numbered)
        else:
            prompt=("You are a professional Persian translator. Translate each numbered English line to fluent, natural Persian (Farsi).\n"
                    "Important: Use correct Persian grammar and natural everyday language. Avoid word-for-word translation.\n"
                    "Rules:\n- Output ONLY the translated lines\n- Keep numbering [0],[1],...\n"
                    "- No explanation or extra text\n\n"+numbered)
        resp=client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":"You are an expert translator. Output only translations, nothing else."},
                      {"role":"user","content":prompt}],
            temperature=0.1, max_tokens=4096)
        fa_map={}
        for line in resp.choices[0].message.content.strip().split("\n"):
            m=re.match(r"\[(\d+)\]\s*(.*)",line.strip())
            if m: fa_map[int(m.group(1))]=m.group(2).strip()
        for j,seg in enumerate(batch): seg["fa"]=fa_map.get(j,"")
    return segments

class VideoWorker(QThread):
    progress=pyqtSignal(int,str); finished=pyqtSignal(list,int,int); error=pyqtSignal(str)
    def __init__(self,video_path,groq_key,wpl,vid_lang="en"):
        super().__init__()
        self.video_path=video_path; self.groq_key=groq_key
        self.wpl=wpl; self.vid_lang=vid_lang
    def run(self):
        try:
            client=Groq(api_key=self.groq_key)
            self.progress.emit(1,T("step1"))
            tmp=tempfile.mkdtemp(); audio=os.path.join(tmp,"audio.mp3")
            r=subprocess.run([FFMPEG,"-y","-i",self.video_path,"-vn","-ar","16000","-ac","1",
                              "-c:a","libmp3lame","-q:a","2",audio],capture_output=True,text=True)
            if r.returncode!=0: self.error.emit(f"ffmpeg error:\n{r.stderr[-300:]}"); return
            self.progress.emit(2,T("step2"))
            size_mb=os.path.getsize(audio)/1024/1024
            segs=[]
            if size_mb<=24: segs=self._transcribe(client,audio)
            else:
                for chunk,offset in self._split(audio,tmp): segs.extend(self._transcribe(client,chunk,offset))
            if not segs: self.error.emit("No speech detected."); return
            self.progress.emit(3,T("step3"))
            # For Persian videos: transcribe in FA, translate to EN, keep FA as translation
            if self.vid_lang=="fa":
                segs=translate_batches(client,segs,src_lang="fa")
                # swap: text=EN translation, fa=original Persian
                for seg in segs:
                    orig=seg["text"]; seg["text"]=seg["fa"]; seg["fa"]=orig
            else:
                segs=translate_batches(client,segs,src_lang="en")
            if self.wpl<10: segs=chunk_segments(segs,self.wpl)
            wh,llm=estimate_tokens(segs)
            self.progress.emit(4,T("step4"))
            self.finished.emit(segs,wh,llm)
        except Exception as e:
            err=str(e)
            if "401" in err or "invalid_api_key" in err.lower(): self.error.emit("Invalid API Key. Check Settings.")
            elif "429" in err or "rate_limit" in err.lower(): self.error.emit("Groq daily limit reached. Try tomorrow.")
            else: self.error.emit(err)
    def _transcribe(self,client,path,offset=0.0):
        with open(path,"rb") as f:
            resp=client.audio.transcriptions.create(
                file=(Path(path).name,f),model="whisper-large-v3",
                response_format="verbose_json",language=self.vid_lang)
        result=[]
        for s in resp.segments:
            if isinstance(s,dict): st,en,tx=s.get("start",0),s.get("end",0),s.get("text","").strip()
            else: st,en,tx=s.start,s.end,s.text.strip()
            if tx: result.append({"start":st+offset,"end":en+offset,"text":tx,"fa":""})
        return result
    def _split(self,audio,tmp,mins=10):
        probe=subprocess.run([FFPROBE,"-v","error","-show_entries","format=duration",
                              "-of","default=noprint_wrappers=1:nokey=1",audio],capture_output=True,text=True)
        total=float(probe.stdout.strip() or "0"); secs=mins*60; chunks=[]; start=0; idx=0
        while start<total:
            out=os.path.join(tmp,f"c{idx}.mp3")
            subprocess.run([FFMPEG,"-y","-i",audio,"-ss",str(start),"-t",str(secs),"-c","copy",out],capture_output=True)
            chunks.append((out,start)); start+=secs; idx+=1
        return chunks

class SrtWorker(QThread):
    progress=pyqtSignal(int,str); finished=pyqtSignal(list); error=pyqtSignal(str)
    def __init__(self,segs,groq_key):
        super().__init__(); self.segs=segs; self.groq_key=groq_key
    def run(self):
        try:
            client=Groq(api_key=self.groq_key)
            self.progress.emit(1,T("srt_step"))
            self.segs=translate_batches(client,self.segs,src_lang="en")
            self.progress.emit(2,T("srt_done"))
            self.finished.emit(self.segs)
        except Exception as e: self.error.emit(str(e))

# ═══════════════════════════════════════════════════════════════════════════════
# UI HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
EXTS_VID=(".mp4",".mov",".mkv",".avi",".webm"); EXTS_SRT=(".srt",)

class DropZone(QLabel):
    file_dropped=pyqtSignal(str)
    def __init__(self,exts):
        super().__init__(); self.exts=exts; self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter); self.setMinimumHeight(160); self._hint=""; self.restyle()
    def set_hint(self,h): self._hint=h; self.restyle()
    def restyle(self,hover=False):
        b=t("accent") if hover else t("border"); bg="rgba(99,102,241,0.07)" if hover else t("card"); c=t("accent2") if hover else t("muted")
        self.setStyleSheet(f"QLabel{{border:2px dashed {b};border-radius:14px;color:{c};background:{bg};font-size:12px;padding:22px;}}")
        icon="📄" if ".srt" in self.exts else "🎞️"
        self.setText(f"{icon}\n\n{self._hint}")
    def dragEnterEvent(self,e):
        if e.mimeData().hasUrls() and e.mimeData().urls()[0].toLocalFile().lower().endswith(self.exts):
            e.acceptProposedAction(); self.restyle(True)
        else: e.ignore()
    def dragLeaveEvent(self,e): self.restyle()
    def dropEvent(self,e):
        self.restyle(); path=e.mimeData().urls()[0].toLocalFile()
        if path.lower().endswith(self.exts): e.acceptProposedAction(); self.file_dropped.emit(path)

def mk(label,primary=False,danger=False,h=40,w=None):
    b=QPushButton(label); b.setFixedHeight(h)
    if w: b.setFixedWidth(w)
    b.setCursor(Qt.CursorShape.PointingHandCursor); _sb(b,primary,danger); return b

def _sb(b,primary=False,danger=False):
    if primary:
        b.setStyleSheet(f"QPushButton{{background:{t('accent')};color:white;border-radius:9px;font-size:13px;font-weight:600;border:none;padding:0 18px;}}QPushButton:hover{{background:{t('accent2')}}}")
    elif danger:
        b.setStyleSheet(f"QPushButton{{background:transparent;color:{t('danger')};border:1px solid {t('danger')};border-radius:7px;font-size:12px;padding:0 12px;}}QPushButton:hover{{background:{t('danger')};color:white;}}")
    else:
        b.setStyleSheet(f"QPushButton{{background:{t('surface')};color:{t('sub')};border:1px solid {t('border')};border-radius:9px;font-size:13px;font-weight:500;padding:0 14px;}}QPushButton:hover{{background:{t('card')};color:{t('text')};border-color:{t('accent')}}}")

def txte():
    w=QTextEdit(); w.setReadOnly(True)
    w.setStyleSheet(f"background:transparent;border:none;color:{t('sub')};font-family:'Cascadia Code','Consolas',monospace;font-size:12px;padding:14px;")
    return w

def tab_style():
    return (f"QTabWidget::pane{{border:none;background:{t('card')};}}QTabBar::tab{{background:transparent;color:{t('muted')};"
            f"padding:10px 20px;font-size:13px;border-bottom:2px solid transparent;}}QTabBar::tab:selected{{color:{t('text')};"
            f"border-bottom:2px solid {t('accent')};}}QTabBar::tab:hover{{color:{t('sub')}}}")

class SuccessBanner(QFrame):
    def __init__(self,msg):
        super().__init__()
        self.setStyleSheet(f"QFrame{{background:rgba(52,211,153,0.12);border:1px solid rgba(52,211,153,0.3);border-radius:10px;}}")
        lay=QHBoxLayout(self); lay.setContentsMargins(16,12,16,12); lay.setSpacing(10)
        icon=QLabel("✅"); icon.setStyleSheet("font-size:20px;border:none;background:transparent;")
        lbl=QLabel(msg); lbl.setStyleSheet(f"color:{t('success')};font-size:13px;font-weight:600;border:none;background:transparent;")
        lay.addWidget(icon); lay.addWidget(lbl); lay.addStretch()

# ─── Rounded logo label ───────────────────────────────────────────────────────
class RoundedLogo(QLabel):
    def __init__(self,path,size=44):
        super().__init__(); self._size=size; self.setFixedSize(size,size)
        px=QPixmap(path).scaled(size,size,Qt.AspectRatioMode.KeepAspectRatioByExpanding,Qt.TransformationMode.SmoothTransformation)
        # crop to circle with rounded corners
        rounded=QPixmap(size,size); rounded.fill(Qt.GlobalColor.transparent)
        p=QPainter(rounded); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        from PyQt6.QtGui import QPainterPath
        path_obj=QPainterPath(); path_obj.addRoundedRect(0,0,size,size,10,10)
        p.setClipPath(path_obj); p.drawPixmap(0,0,px); p.end()
        self.setPixmap(rounded)

# ═══════════════════════════════════════════════════════════════════════════════
# ONBOARDING DIALOG
# ═══════════════════════════════════════════════════════════════════════════════
class OnboardingDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("MSRT")
        self.setFixedSize(480,340)
        self.setWindowFlags(Qt.WindowType.Dialog|Qt.WindowType.FramelessWindowHint)
        self._page=0; self._build()

    def _build(self):
        self.setStyleSheet(f"QDialog{{background:{t('card')};border-radius:16px;border:1px solid {t('border')}}}")
        lay=QVBoxLayout(self); lay.setContentsMargins(36,36,36,28); lay.setSpacing(0)
        # logo
        logo_path=resource_path("icon_256.png")
        if os.path.exists(logo_path):
            logo=RoundedLogo(logo_path,52)
            logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lay.addWidget(logo,alignment=Qt.AlignmentFlag.AlignCenter)
        lay.addSpacing(16)
        self.title_lbl=QLabel(); self.title_lbl.setFont(QFont("Segoe UI",16,QFont.Weight.Bold))
        self.title_lbl.setStyleSheet(f"color:{t('text')}"); self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.title_lbl)
        lay.addSpacing(14)
        self.body_lbl=QLabel(); self.body_lbl.setWordWrap(True)
        self.body_lbl.setStyleSheet(f"color:{t('sub')};font-size:13px;line-height:1.6")
        self.body_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.body_lbl)
        lay.addSpacing(10)
        self.link_btn=QPushButton(); self.link_btn.setFixedHeight(38)
        self.link_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.link_btn.setStyleSheet(f"QPushButton{{background:transparent;color:{t('accent2')};border:1px solid {t('accent2')};border-radius:8px;font-size:12px;}}QPushButton:hover{{background:rgba(99,102,241,0.08)}}")
        self.link_btn.clicked.connect(lambda:webbrowser.open("https://console.groq.com"))
        lay.addWidget(self.link_btn)
        lay.addStretch()
        # buttons row
        brow=QHBoxLayout(); brow.setSpacing(10)
        self.skip_btn=QPushButton(T("ob_skip")); self.skip_btn.setFixedHeight(36)
        self.skip_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.skip_btn.setStyleSheet(f"QPushButton{{background:transparent;color:{t('muted')};border:none;font-size:12px;}}QPushButton:hover{{color:{t('text')}}}")
        self.skip_btn.clicked.connect(self.accept)
        self.next_btn=QPushButton(); self.next_btn.setFixedHeight(38); self.next_btn.setFixedWidth(120)
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.setStyleSheet(f"QPushButton{{background:{t('accent')};color:white;border-radius:9px;font-size:13px;font-weight:600;border:none;}}QPushButton:hover{{background:{t('accent2')}}}")
        self.next_btn.clicked.connect(self._next)
        # dots
        self.dots=[QLabel("●") for _ in range(3)]
        dot_row=QHBoxLayout(); dot_row.setSpacing(6)
        for d in self.dots: dot_row.addWidget(d)
        brow.addWidget(self.skip_btn); brow.addStretch(); brow.addLayout(dot_row); brow.addStretch(); brow.addWidget(self.next_btn)
        lay.addLayout(brow)
        self._refresh()

    def _refresh(self):
        pages=[("ob_title1","ob_body1",True),("ob_title2","ob_body2",False),("ob_title3","ob_body3",False)]
        title_k,body_k,show_link=pages[self._page]
        self.title_lbl.setText(T(title_k)); self.body_lbl.setText(T(body_k))
        self.link_btn.setText(T("ob_get_key")); self.link_btn.setVisible(show_link)
        self.next_btn.setText(T("ob_done") if self._page==2 else T("ob_next"))
        for i,d in enumerate(self.dots):
            d.setStyleSheet(f"color:{t('accent') if i==self._page else t('border')};font-size:10px")

    def _next(self):
        if self._page<2: self._page+=1; self._refresh()
        else: self.accept()

# ═══════════════════════════════════════════════════════════════════════════════
# PROCESS PAGE
# ═══════════════════════════════════════════════════════════════════════════════
class ProcessPage(QWidget):
    history_updated=pyqtSignal()
    def __init__(self,get_key,get_wpl):
        super().__init__(); self.get_key=get_key; self.get_wpl=get_wpl
        self.segments=[]; self.raw_segments=[]; self._fname=""; self._build()

    def _build(self):
        self.lay=QVBoxLayout(self); self.lay.setContentsMargins(28,24,28,24); self.lay.setSpacing(14)
        # header
        hdr=QHBoxLayout()
        self.ttl=QLabel(); self.ttl.setFont(QFont("Segoe UI",17,QFont.Weight.Bold))
        self.bdg=QLabel("Groq Whisper Large v3  ·  LLaMA 3.3 70B")
        hdr.addWidget(self.ttl); hdr.addStretch(); hdr.addWidget(self.bdg); self.lay.addLayout(hdr)
        # controls row: language + words per line
        ctrl=QHBoxLayout(); ctrl.setSpacing(16)
        # language selector
        lang_lbl=QLabel(); lang_lbl.setObjectName("lang_lbl")
        self.vid_lang_combo=QComboBox(); self.vid_lang_combo.setFixedHeight(34); self.vid_lang_combo.setFixedWidth(110)
        self.vid_lang_combo.setStyleSheet(f"QComboBox{{background:{t('card')};color:{t('text')};border:1px solid {t('border')};border-radius:8px;padding:0 10px;font-size:12px;}}QComboBox::drop-down{{border:none;}}QComboBox QAbstractItemView{{background:{t('card')};color:{t('text')};border:1px solid {t('border')}}}")
        ctrl.addWidget(lang_lbl); ctrl.addWidget(self.vid_lang_combo)
        ctrl.addSpacing(20)
        # words slider
        words_lbl=QLabel(); words_lbl.setObjectName("words_lbl")
        self.wsl=QSlider(Qt.Orientation.Horizontal); self.wsl.setRange(1,10)
        self.wsl.setValue(int(QSettings("MSRT","App").value("wpl",10)))
        self.wsl.setInvertedAppearance(False); self.wsl.setFixedWidth(120)
        self.wsl.setStyleSheet(f"QSlider::groove:horizontal{{height:5px;background:{t('surface')};border-radius:3px;}}QSlider::handle:horizontal{{width:16px;height:16px;margin:-5px 0;background:{t('accent')};border-radius:8px;}}QSlider::sub-page:horizontal{{background:{t('accent')};border-radius:3px;}}")
        self.wval=QLabel(str(self.wsl.value())); self.wval.setFixedWidth(22)
        self.wval.setStyleSheet(f"color:{t('accent')};font-size:13px;font-weight:700")
        self.wsl.valueChanged.connect(lambda v:(self.wval.setText(str(v)),QSettings("MSRT","App").setValue("wpl",v)))
        ctrl.addWidget(words_lbl); ctrl.addWidget(self.wsl); ctrl.addWidget(self.wval)
        ctrl.addStretch()
        self.lay.addLayout(ctrl)
        # drop zone
        self.dz=DropZone(EXTS_VID); self.dz.file_dropped.connect(self.on_file); self.lay.addWidget(self.dz)
        self.bbtn=mk(""); self.bbtn.clicked.connect(self.browse); self.lay.addWidget(self.bbtn)
        # progress
        self.pfrm=QFrame(); self.pfrm.hide()
        pfl=QVBoxLayout(self.pfrm); pfl.setContentsMargins(20,16,20,16); pfl.setSpacing(10)
        self.plbl=QLabel(); self.plbl.setFont(QFont("Segoe UI",12))
        self.pbar=QProgressBar(); self.pbar.setRange(0,4); self.pbar.setValue(0); self.pbar.setTextVisible(False); self.pbar.setFixedHeight(6)
        pfl.addWidget(self.plbl); pfl.addWidget(self.pbar); self.lay.addWidget(self.pfrm)
        self.banner=None
        # result
        self.rfrm=QFrame(); self.rfrm.hide()
        rfl=QVBoxLayout(self.rfrm); rfl.setContentsMargins(0,0,0,0); rfl.setSpacing(0)
        self.tabs=QTabWidget()
        self.en=txte(); self.fa=txte(); self.sr=txte()
        self.tabs.addTab(self.en,""); self.tabs.addTab(self.fa,""); self.tabs.addTab(self.sr,"")
        rfl.addWidget(self.tabs)
        brow=QHBoxLayout(); brow.setContentsMargins(14,10,14,14); brow.setSpacing(8)
        self.clbl=QLabel()
        self.rfbtn=mk("",h=36); self.rfbtn.clicked.connect(self.do_refresh)
        self.cpbtn=mk("",h=36); self.cpbtn.clicked.connect(self.copy)
        self.nwbtn=mk("",h=36); self.nwbtn.clicked.connect(self.reset)
        self.dlbtn=mk("",primary=True,h=36); self.dlbtn.clicked.connect(self.dl)
        brow.addWidget(self.clbl); brow.addStretch()
        brow.addWidget(self.rfbtn); brow.addWidget(self.cpbtn); brow.addWidget(self.nwbtn); brow.addWidget(self.dlbtn)
        rfl.addLayout(brow); self.lay.addWidget(self.rfrm); self.lay.addStretch()
        self.apply_theme()

    def apply_theme(self):
        self.ttl.setText(T("process")); self.ttl.setStyleSheet(f"color:{t('text')}")
        self.bdg.setStyleSheet(f"color:{t('muted')};font-size:11px;background:{t('card')};border-radius:10px;padding:4px 10px")
        # language combo
        lang_lbl=self.findChild(QLabel,"lang_lbl")
        if lang_lbl: lang_lbl.setText(T("lang_select")); lang_lbl.setStyleSheet(f"color:{t('muted')};font-size:12px")
        self.vid_lang_combo.clear()
        self.vid_lang_combo.addItem(T("lang_en"),"en")
        self.vid_lang_combo.addItem(T("lang_fa_vid"),"fa")
        self.vid_lang_combo.setStyleSheet(f"QComboBox{{background:{t('card')};color:{t('text')};border:1px solid {t('border')};border-radius:8px;padding:0 10px;font-size:12px;}}QComboBox::drop-down{{border:none;}}QComboBox QAbstractItemView{{background:{t('card')};color:{t('text')};border:1px solid {t('border')}}}")
        words_lbl=self.findChild(QLabel,"words_lbl")
        if words_lbl: words_lbl.setText(T("words_label")); words_lbl.setStyleSheet(f"color:{t('muted')};font-size:12px")
        self.wsl.setStyleSheet(f"QSlider::groove:horizontal{{height:5px;background:{t('surface')};border-radius:3px;}}QSlider::handle:horizontal{{width:16px;height:16px;margin:-5px 0;background:{t('accent')};border-radius:8px;}}QSlider::sub-page:horizontal{{background:{t('accent')};border-radius:3px;}}")
        self.wval.setStyleSheet(f"color:{t('accent')};font-size:13px;font-weight:700")
        self.bbtn.setText(T("browse")); _sb(self.bbtn)
        self.pfrm.setStyleSheet(f"background:{t('card')};border-radius:12px")
        self.plbl.setStyleSheet(f"color:{t('sub')};font-size:13px")
        self.pbar.setStyleSheet(f"QProgressBar{{background:{t('surface')};border-radius:3px;}}QProgressBar::chunk{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {t('accent')},stop:1 {t('accent2')});border-radius:3px;}}")
        self.rfrm.setStyleSheet(f"background:{t('card')};border-radius:12px")
        self.tabs.setStyleSheet(tab_style())
        self.tabs.setTabText(0,T("tab_en")); self.tabs.setTabText(1,T("tab_fa")); self.tabs.setTabText(2,T("tab_srt"))
        ts=f"background:transparent;border:none;color:{t('sub')};font-family:'Cascadia Code','Consolas',monospace;font-size:12px;padding:14px;"
        for w in [self.en,self.fa,self.sr]: w.setStyleSheet(ts)
        self.clbl.setStyleSheet(f"color:{t('muted')};font-size:11px")
        self.rfbtn.setText(T("refresh")); _sb(self.rfbtn)
        self.cpbtn.setText(T("copy")); _sb(self.cpbtn)
        self.nwbtn.setText(T("new_video")); _sb(self.nwbtn)
        self.dlbtn.setText(T("dl_srt")); _sb(self.dlbtn,primary=True)
        self.dz.set_hint(T("drop_hint"))

    def browse(self):
        p,_=QFileDialog.getOpenFileName(self,"","","Video (*.mp4 *.mov *.mkv *.avi *.webm)")
        if p: self.on_file(p)

    def on_file(self,path):
        key=self.get_key()
        if not key: QMessageBox.warning(self,T("no_key"),T("no_key_msg")); return
        self._fname=os.path.basename(path)
        vid_lang=self.vid_lang_combo.currentData() or "en"
        self.dz.hide(); self.bbtn.hide(); self.rfrm.hide()
        if self.banner:
            self.lay.removeWidget(self.banner); self.banner.deleteLater(); self.banner=None
        self.pfrm.show(); self.pbar.setValue(0); self.plbl.setText(T("step1"))
        self.worker=VideoWorker(path,key,self.wsl.value(),vid_lang)
        self.worker.progress.connect(lambda s,m:(self.pbar.setValue(s),self.plbl.setText(m)))
        self.worker.finished.connect(self.on_done); self.worker.error.connect(self.on_err); self.worker.start()

    def on_done(self,segs,wh,llm):
        self.raw_segments=segs; self.pfrm.hide()
        if self.banner:
            self.lay.removeWidget(self.banner); self.banner.deleteLater()
        self.banner=SuccessBanner(T("step4"))
        self.lay.insertWidget(self.lay.indexOf(self.rfrm),self.banner)
        self._show(segs); add_history(self._fname,segs,wh,llm); self.history_updated.emit()

    def _show(self,segs):
        self.segments=segs; self.rfrm.show()
        self.en.setPlainText(to_text(segs,"en")); self.fa.setPlainText(to_text(segs,"fa")); self.sr.setPlainText(to_srt(segs))
        self.clbl.setText(f"{len(segs)} {T('sentences')}")

    def do_refresh(self):
        if not self.raw_segments: return
        segs=chunk_segments(self.raw_segments,self.wsl.value()); self._show(segs)

    def on_err(self,msg):
        self.pfrm.hide(); self.dz.show(); self.bbtn.show(); QMessageBox.critical(self,T("err_title"),msg)

    def copy(self):
        w=self.tabs.currentWidget()
        if isinstance(w,QTextEdit):
            QApplication.clipboard().setText(w.toPlainText()); self.cpbtn.setText(T("copied"))
            QTimer.singleShot(1500,lambda:self.cpbtn.setText(T("copy")))

    def dl(self):
        if not self.segments: return
        p,_=QFileDialog.getSaveFileName(self,"","subtitle_en.srt","SRT (*.srt)")
        if p:
            with open(p,"w",encoding="utf-8") as f: f.write(to_srt(self.segments))
            QMessageBox.information(self,T("info_title"),T("saved_srt")+p)

    def reset(self):
        self.segments=[]; self.raw_segments=[]; self.rfrm.hide(); self.dz.show(); self.bbtn.show()
        if self.banner: self.lay.removeWidget(self.banner); self.banner.deleteLater(); self.banner=None
        self.en.clear(); self.fa.clear(); self.sr.clear()

    def load_segments(self,segs):
        self.raw_segments=segs; self._show(segs); self.dz.hide(); self.bbtn.hide(); self.pfrm.hide()

# ═══════════════════════════════════════════════════════════════════════════════
# SRT PAGE
# ═══════════════════════════════════════════════════════════════════════════════
class SrtPage(QWidget):
    def __init__(self,get_key):
        super().__init__(); self.get_key=get_key; self.segs=[]; self.banner=None; self._build()
    def _build(self):
        self.lay=QVBoxLayout(self); self.lay.setContentsMargins(28,24,28,24); self.lay.setSpacing(14)
        self.ttl=QLabel(); self.ttl.setFont(QFont("Segoe UI",17,QFont.Weight.Bold)); self.lay.addWidget(self.ttl)
        self.dz=DropZone(EXTS_SRT); self.dz.file_dropped.connect(self.on_file); self.lay.addWidget(self.dz)
        self.bbtn=mk(""); self.bbtn.clicked.connect(self.browse); self.lay.addWidget(self.bbtn)
        self.pfrm=QFrame(); self.pfrm.hide()
        pfl=QVBoxLayout(self.pfrm); pfl.setContentsMargins(20,16,20,16); pfl.setSpacing(10)
        self.plbl=QLabel(); self.plbl.setFont(QFont("Segoe UI",12))
        self.pbar=QProgressBar(); self.pbar.setRange(0,2); self.pbar.setValue(0); self.pbar.setTextVisible(False); self.pbar.setFixedHeight(6)
        pfl.addWidget(self.plbl); pfl.addWidget(self.pbar); self.lay.addWidget(self.pfrm)
        self.rfrm=QFrame(); self.rfrm.hide()
        rfl=QVBoxLayout(self.rfrm); rfl.setContentsMargins(0,0,0,0); rfl.setSpacing(0)
        self.tabs=QTabWidget(); self.fa_txt=txte(); self.tabs.addTab(self.fa_txt,""); rfl.addWidget(self.tabs)
        brow=QHBoxLayout(); brow.setContentsMargins(14,10,14,14); brow.setSpacing(8)
        self.nwbtn=mk("",h=36); self.nwbtn.clicked.connect(self.reset)
        self.dlbtn=mk("",primary=True,h=36); self.dlbtn.clicked.connect(self.dl)
        brow.addStretch(); brow.addWidget(self.nwbtn); brow.addWidget(self.dlbtn)
        rfl.addLayout(brow); self.lay.addWidget(self.rfrm); self.lay.addStretch()
        self.apply_theme()
    def apply_theme(self):
        self.ttl.setText(T("srt_page")); self.ttl.setStyleSheet(f"color:{t('text')}")
        self.bbtn.setText(T("srt_browse")); _sb(self.bbtn)
        self.pfrm.setStyleSheet(f"background:{t('card')};border-radius:12px")
        self.plbl.setStyleSheet(f"color:{t('sub')};font-size:13px")
        self.pbar.setStyleSheet(f"QProgressBar{{background:{t('surface')};border-radius:3px;}}QProgressBar::chunk{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {t('accent')},stop:1 {t('accent2')});border-radius:3px;}}")
        self.rfrm.setStyleSheet(f"background:{t('card')};border-radius:12px")
        self.tabs.setStyleSheet(tab_style()); self.tabs.setTabText(0,T("tab_srt_fa"))
        self.fa_txt.setStyleSheet(f"background:transparent;border:none;color:{t('sub')};font-family:'Cascadia Code','Consolas',monospace;font-size:12px;padding:14px;")
        self.nwbtn.setText(T("new_srt")); _sb(self.nwbtn)
        self.dlbtn.setText(T("dl_srt_fa")); _sb(self.dlbtn,primary=True)
        self.dz.set_hint(T("srt_drop_hint"))
    def browse(self):
        p,_=QFileDialog.getOpenFileName(self,"","","SRT (*.srt)")
        if p: self.on_file(p)
    def on_file(self,path):
        key=self.get_key()
        if not key: QMessageBox.warning(self,T("no_key"),T("no_key_msg")); return
        with open(path,encoding="utf-8",errors="ignore") as f: content=f.read()
        segs=parse_srt(content)
        if not segs: QMessageBox.warning(self,T("err_title"),"Could not parse SRT."); return
        self.dz.hide(); self.bbtn.hide(); self.rfrm.hide()
        if self.banner: self.lay.removeWidget(self.banner); self.banner.deleteLater(); self.banner=None
        self.pfrm.show(); self.pbar.setValue(0)
        self.worker=SrtWorker(segs,key)
        self.worker.progress.connect(lambda s,m:(self.pbar.setValue(s),self.plbl.setText(m)))
        self.worker.finished.connect(self.on_done); self.worker.error.connect(self.on_err); self.worker.start()
    def on_done(self,segs):
        self.segs=segs; self.pfrm.hide()
        if self.banner: self.lay.removeWidget(self.banner); self.banner.deleteLater()
        self.banner=SuccessBanner(T("srt_done"))
        self.lay.insertWidget(self.lay.indexOf(self.rfrm),self.banner)
        self.rfrm.show(); self.fa_txt.setPlainText(to_srt(segs,fa=True))
    def on_err(self,msg):
        self.pfrm.hide(); self.dz.show(); self.bbtn.show(); QMessageBox.critical(self,T("err_title"),msg)
    def dl(self):
        if not self.segs: return
        p,_=QFileDialog.getSaveFileName(self,"","subtitle_fa.srt","SRT (*.srt)")
        if p:
            with open(p,"w",encoding="utf-8") as f: f.write(to_srt(self.segs,fa=True))
            QMessageBox.information(self,T("info_title"),T("saved_srt")+p)
    def reset(self):
        self.segs=[]; self.rfrm.hide(); self.dz.show(); self.bbtn.show(); self.fa_txt.clear()
        if self.banner: self.lay.removeWidget(self.banner); self.banner.deleteLater(); self.banner=None

# ═══════════════════════════════════════════════════════════════════════════════
# HISTORY PAGE
# ═══════════════════════════════════════════════════════════════════════════════
class HistoryPage(QWidget):
    open_segments=pyqtSignal(list)
    def __init__(self):
        super().__init__(); self.lay=QVBoxLayout(self); self.lay.setContentsMargins(28,24,28,24); self.lay.setSpacing(16); self._build()
    def _build(self):
        while self.lay.count():
            it=self.lay.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        ttl=QLabel(T("history")); ttl.setFont(QFont("Segoe UI",17,QFont.Weight.Bold)); ttl.setStyleSheet(f"color:{t('text')}"); self.lay.addWidget(ttl)
        recs=load_history()
        if not recs:
            lbl=QLabel(T("no_history")); lbl.setStyleSheet(f"color:{t('muted')};font-size:13px"); self.lay.addWidget(lbl); self.lay.addStretch(); return
        scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("QScrollArea{border:none;background:transparent}")
        inner=QWidget(); inner.setStyleSheet("background:transparent"); ilay=QVBoxLayout(inner); ilay.setSpacing(10); ilay.setContentsMargins(0,0,8,0)
        for i,rec in enumerate(recs):
            card=QFrame(); card.setStyleSheet(f"QFrame{{background:{t('card')};border-radius:12px;border:1px solid {t('border')}}}")
            cl=QHBoxLayout(card); cl.setContentsMargins(16,14,16,14); cl.setSpacing(12)
            info=QVBoxLayout(); info.setSpacing(4)
            fn=QLabel(f"🎬  {rec.get('filename','—')}"); fn.setStyleSheet(f"color:{t('text')};font-size:13px;font-weight:600")
            dt=QLabel(f"{rec.get('date','')}  ·  {rec.get('sentences',0)} {T('sentences')}  ·  ~{rec.get('wh_tok',0)+rec.get('llm_tok',0):,} tokens")
            dt.setStyleSheet(f"color:{t('muted')};font-size:11px")
            info.addWidget(fn); info.addWidget(dt)
            ob=mk(T("history_open"),h=34); segs=rec.get("segments",[])
            ob.clicked.connect(lambda _,s=segs:self.open_segments.emit(s))
            db=mk(T("history_delete"),danger=True,h=34); db.clicked.connect(lambda _,idx=i:self._del(idx))
            cl.addLayout(info); cl.addStretch(); cl.addWidget(ob); cl.addWidget(db); ilay.addWidget(card)
        ilay.addStretch(); scroll.setWidget(inner); self.lay.addWidget(scroll)
    def _del(self,idx): recs=load_history(); recs.pop(idx); save_history(recs); self._build()
    def refresh(self): self._build()
    def apply_theme(self): self._build()

# ═══════════════════════════════════════════════════════════════════════════════
# SETTINGS PAGE
# ═══════════════════════════════════════════════════════════════════════════════
class SettingsPage(QWidget):
    theme_changed=pyqtSignal(); lang_changed=pyqtSignal()
    def __init__(self):
        super().__init__(); self.cfg=QSettings("MSRT","App")
        self.lay=QVBoxLayout(self); self.lay.setContentsMargins(0,0,0,0); self._build()
    def _build(self):
        while self.lay.count():
            it=self.lay.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("QScrollArea{border:none;background:transparent}")
        w=QWidget(); w.setStyleSheet("background:transparent"); sl=QVBoxLayout(w); sl.setContentsMargins(28,24,28,28); sl.setSpacing(18)
        def H(txt,sz=13,bold=False):
            l=QLabel(txt); l.setFont(QFont("Segoe UI",sz,QFont.Weight.Bold if bold else QFont.Weight.Normal))
            l.setStyleSheet(f"color:{t('text')}"); l.setWordWrap(True); return l
        def hint(txt):
            l=QLabel(txt); l.setWordWrap(True); l.setStyleSheet(f"color:{t('muted')};font-size:12px"); return l
        def div():
            f=QFrame(); f.setFrameShape(QFrame.Shape.HLine); f.setStyleSheet(f"color:{t('border')}"); return f
        sl.addWidget(H(T("settings"),18,True))
        # API Key
        sl.addWidget(H("🔑  "+T("groq_key"),13,True)); sl.addWidget(hint(T("groq_hint")))
        self.key_in=QLineEdit(); self.key_in.setPlaceholderText("gsk_...")
        self.key_in.setEchoMode(QLineEdit.EchoMode.Password); self.key_in.setText(self.cfg.value("groq_key",""))
        self.key_in.setFixedHeight(44)
        self.key_in.setStyleSheet(f"QLineEdit{{background:{t('card')};border:1px solid {t('border')};border-radius:9px;color:{t('text')};padding:0 14px;font-size:13px;}}QLineEdit:focus{{border-color:{t('accent')}}}")
        sl.addWidget(self.key_in)
        sb=mk(T("save"),primary=True,h=42); sb.clicked.connect(self._save); sl.addWidget(sb)
        self.slbl=QLabel(""); self.slbl.setStyleSheet(f"color:{t('success')};font-size:12px"); sl.addWidget(self.slbl)
        sl.addWidget(div())
        # Token usage + refresh button
        tok_hdr=QHBoxLayout()
        tok_hdr.addWidget(H("📊  "+T("usage_label"),13,True))
        tok_hdr.addStretch()
        rfbtn=mk(T("tok_refresh"),h=32,w=110); rfbtn.clicked.connect(self._build); tok_hdr.addWidget(rfbtn)
        sl.addLayout(tok_hdr)
        wh,llm=today_usage()
        for label,used,total in [(T("whisper_tok"),wh,GROQ_DAILY["whisper"]),(T("llm_tok"),llm,GROQ_DAILY["llm"])]:
            pct=min(int(used/total*100),100) if total>0 else 0
            rl=QLabel(f"{label}: {used:,} / {total:,}  ({pct}%)"); rl.setStyleSheet(f"color:{t('sub')};font-size:12px"); sl.addWidget(rl)
            bar=QProgressBar(); bar.setRange(0,100); bar.setValue(pct); bar.setTextVisible(False); bar.setFixedHeight(6)
            col=t("danger") if pct>80 else t("accent")
            bar.setStyleSheet(f"QProgressBar{{background:{t('surface')};border-radius:3px;}}QProgressBar::chunk{{background:{col};border-radius:3px;}}"); sl.addWidget(bar)
        sl.addWidget(div())
        # Theme
        sl.addWidget(H("🎨  "+T("theme_label"),13,True))
        trow=QHBoxLayout(); trow.setSpacing(8)
        self.dbtn=mk(T("dark_btn"),h=38,w=110); self.lbtn=mk(T("light_btn"),h=38,w=110)
        self.dbtn.clicked.connect(lambda:self._theme("dark")); self.lbtn.clicked.connect(lambda:self._theme("light"))
        self._rtheme(); trow.addWidget(self.dbtn); trow.addWidget(self.lbtn); trow.addStretch(); sl.addLayout(trow); sl.addWidget(div())
        # Language
        sl.addWidget(H("🌐  "+T("lang_label"),13,True))
        lrow=QHBoxLayout(); lrow.setSpacing(8)
        self.fabtn=mk("🇮🇷  فارسی",h=38,w=130); self.enbtn=mk("🇺🇸  English",h=38,w=130)
        self.fabtn.clicked.connect(lambda:self._lang("fa")); self.enbtn.clicked.connect(lambda:self._lang("en"))
        self._rlang(); lrow.addWidget(self.fabtn); lrow.addWidget(self.enbtn); lrow.addStretch(); sl.addLayout(lrow)
        sl.addStretch(); scroll.setWidget(w); self.lay.addWidget(scroll)
    def _rtheme(self):
        is_dark=CT is DARK
        for btn,active in [(self.dbtn,is_dark),(self.lbtn,not is_dark)]:
            if active: btn.setStyleSheet(f"QPushButton{{background:{t('accent')};color:white;border-radius:8px;font-size:12px;font-weight:600;border:none;}}")
            else: btn.setStyleSheet(f"QPushButton{{background:{t('card')};color:{t('muted')};border-radius:8px;font-size:12px;border:1px solid {t('border')};}}QPushButton:hover{{color:{t('text')}}}")
    def _rlang(self):
        is_fa=LANG=="fa"
        for btn,active in [(self.fabtn,is_fa),(self.enbtn,not is_fa)]:
            if active: btn.setStyleSheet(f"QPushButton{{background:{t('accent')};color:white;border-radius:8px;font-size:12px;font-weight:600;border:none;}}")
            else: btn.setStyleSheet(f"QPushButton{{background:{t('card')};color:{t('muted')};border-radius:8px;font-size:12px;border:1px solid {t('border')};}}QPushButton:hover{{color:{t('text')}}}")
    def _theme(self,mode):
        global CT; CT=DARK if mode=="dark" else LIGHT; self.cfg.setValue("theme",mode); self.theme_changed.emit()
    def _lang(self,lang):
        global LANG; LANG=lang; self.cfg.setValue("lang",lang); self.lang_changed.emit()
    def _save(self): self.cfg.setValue("groq_key",self.key_in.text().strip()); self.slbl.setText(T("saved"))
    def get_key(self): return self.cfg.value("groq_key","")
    def get_wpl(self): return int(self.cfg.value("wpl",10))
    def apply_theme(self): self._build()

# ═══════════════════════════════════════════════════════════════════════════════
# ABOUT PAGE
# ═══════════════════════════════════════════════════════════════════════════════
class AboutPage(QWidget):
    def __init__(self):
        super().__init__(); self.lay=QVBoxLayout(self); self.lay.setContentsMargins(28,24,28,24); self.lay.setSpacing(20); self._build()
    def _build(self):
        while self.lay.count():
            it=self.lay.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        logo_path=resource_path("icon_256.png")
        if os.path.exists(logo_path):
            logo=RoundedLogo(logo_path,72)
            self.lay.addWidget(logo,alignment=Qt.AlignmentFlag.AlignCenter)
        name=QLabel("MSRT"); name.setFont(QFont("Segoe UI",22,QFont.Weight.Bold))
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if CT is DARK: name.setStyleSheet("color:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #FFFFFF,stop:1 #C8C8D8);font-size:22px;font-weight:700;")
        else: name.setStyleSheet("color:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #5856D6,stop:1 #818CF8);font-size:22px;font-weight:700;")
        self.lay.addWidget(name)
        ver=QLabel("v1.1"); ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver.setStyleSheet(f"color:{t('muted')};font-size:13px"); self.lay.addWidget(ver)
        desc=QLabel("زیرنویس هوشمند با Groq AI\nSmart Subtitle with Groq AI")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter); desc.setWordWrap(True)
        desc.setStyleSheet(f"color:{t('sub')};font-size:13px"); self.lay.addWidget(desc)
        # GitHub card
        card=QFrame()
        card.setStyleSheet(f"QFrame{{background:{t('card')};border-radius:14px;border:1px solid {t('border')}}}")
        cl=QVBoxLayout(card); cl.setContentsMargins(24,20,24,20); cl.setSpacing(12)
        gh_lbl=QLabel("🐙  github.com/mahzoonmmd/Msrt-sub")
        gh_lbl.setStyleSheet(f"color:{t('text')};font-size:13px;font-weight:600")
        gh_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter); cl.addWidget(gh_lbl)
        btnrow=QHBoxLayout(); btnrow.setSpacing(10)
        star_btn=mk("⭐  Star",h=38); star_btn.clicked.connect(lambda:webbrowser.open("https://github.com/mahzoonmmd/Msrt-sub/stargazers"))
        follow_btn=mk("👤  Follow",h=38); follow_btn.clicked.connect(lambda:webbrowser.open("https://github.com/mahzoonmmd"))
        repo_btn=mk("📂  Repository",primary=True,h=38); repo_btn.clicked.connect(lambda:webbrowser.open("https://github.com/mahzoonmmd/Msrt-sub"))
        btnrow.addStretch(); btnrow.addWidget(star_btn); btnrow.addWidget(follow_btn); btnrow.addWidget(repo_btn); btnrow.addStretch()
        cl.addLayout(btnrow)
        support=QLabel("اگه MSRT برات مفید بوده، با یه ⭐ Star و Follow حمایت کن!")
        support.setAlignment(Qt.AlignmentFlag.AlignCenter); support.setWordWrap(True)
        support.setStyleSheet(f"color:{t('muted')};font-size:12px"); cl.addWidget(support)
        self.lay.addWidget(card)
        self.lay.addStretch()
    def apply_theme(self): self._build()

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ═══════════════════════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("MSRT")
        self.setMinimumSize(920,680); self.resize(1080,740)
        icon_path=resource_path("icon.ico")
        if os.path.exists(icon_path): self.setWindowIcon(QIcon(icon_path))
        cfg=QSettings("MSRT","App")
        global CT,LANG
        CT=LIGHT if cfg.value("theme","dark")=="light" else DARK
        LANG=cfg.value("lang","fa"); self._build()
        # show onboarding on first run
        if not cfg.value("onboarded",False):
            QTimer.singleShot(300,self._show_onboarding)

    def _show_onboarding(self):
        dlg=OnboardingDialog(self); dlg.exec()
        QSettings("MSRT","App").setValue("onboarded",True)

    def _build(self):
        cw=QWidget(); self.setCentralWidget(cw)
        root=QHBoxLayout(cw); root.setContentsMargins(0,0,0,0); root.setSpacing(0)
        self.sp=SettingsPage(); self.hp=HistoryPage()
        self.pp=ProcessPage(self.sp.get_key,self.sp.get_wpl)
        self.srtp=SrtPage(self.sp.get_key)
        self.ab=AboutPage()
        self.sp.theme_changed.connect(self.retheme); self.sp.lang_changed.connect(self.relang)
        self.pp.history_updated.connect(lambda:self.hp.refresh())
        self.hp.open_segments.connect(lambda s:(self.pp.load_segments(s),self._nav(0)))
        self.stack=QStackedWidget()
        self.stack.addWidget(self.pp)   # 0
        self.stack.addWidget(self.srtp) # 1
        self.stack.addWidget(self.hp)   # 2
        self.stack.addWidget(self.sp)   # 3
        self.stack.addWidget(self.ab)   # 4
        # Sidebar RIGHT
        self.sb=QFrame(); self.sb.setFixedWidth(210)
        sl=QVBoxLayout(self.sb); sl.setContentsMargins(14,20,14,20); sl.setSpacing(4)
        # Logo
        self.logo_img=QLabel(); self.logo_img.setFixedSize(44,44); self.logo_img.setScaledContents(False)
        logo_px_path=resource_path("icon_256.png")
        if os.path.exists(logo_px_path):
            px=QPixmap(logo_px_path).scaled(44,44,Qt.AspectRatioMode.KeepAspectRatioByExpanding,Qt.TransformationMode.SmoothTransformation)
            rounded=QPixmap(44,44); rounded.fill(Qt.GlobalColor.transparent)
            p=QPainter(rounded); p.setRenderHint(QPainter.RenderHint.Antialiasing)
            from PyQt6.QtGui import QPainterPath
            pp2=QPainterPath(); pp2.addRoundedRect(0,0,44,44,10,10)
            p.setClipPath(pp2); p.drawPixmap(0,0,px); p.end()
            self.logo_img.setPixmap(rounded)
        logo_row=QHBoxLayout(); logo_row.setSpacing(10); logo_row.setContentsMargins(6,0,6,16)
        logo_row.addWidget(self.logo_img)
        self.brand_lbl=QLabel("MSRT"); self.brand_lbl.setFont(QFont("Segoe UI",17,QFont.Weight.Bold))
        logo_row.addWidget(self.brand_lbl); logo_row.addStretch()
        sl.addLayout(logo_row)
        self._nav_data=[("✦","process"),("📄","srt_page"),("📂","history"),("⚙️","settings"),("ℹ️","about")]
        self.navs=[]
        for icon,key in self._nav_data:
            b=QPushButton(f"  {icon}   {T(key)}"); b.setCheckable(True); b.setFixedHeight(40)
            b.setCursor(Qt.CursorShape.PointingHandCursor); b.setFont(QFont("Segoe UI",12))
            self.navs.append(b); sl.addWidget(b)
        for i,b in enumerate(self.navs): b.clicked.connect(lambda _,x=i:self._nav(x))
        sl.addStretch()
        self.vl=QLabel(T("ver")); self.vl.setContentsMargins(6,0,6,0); sl.addWidget(self.vl)
        root.addWidget(self.stack); root.addWidget(self.sb)
        self._nav(0); self.retheme()

    def _nav(self,idx):
        self.stack.setCurrentIndex(idx)
        if idx==2: self.hp.refresh()
        nb=f"QPushButton{{background:transparent;color:{t('muted')};border-radius:8px;text-align:left;padding:0 12px;border:none;}}QPushButton:hover{{background:{t('card')};color:{t('sub')};}}QPushButton:checked{{background:rgba(99,102,241,0.15);color:{t('accent2')};font-weight:600;}}"
        for i,b in enumerate(self.navs): b.setChecked(i==idx); b.setStyleSheet(nb)

    def retheme(self):
        self.centralWidget().setStyleSheet(f"background:{t('bg')}")
        self.setStyleSheet(f"QMainWindow{{background:{t('bg')};}}QScrollBar:vertical{{background:{t('surface')};width:6px;border-radius:3px;}}QScrollBar::handle:vertical{{background:{t('scrollbar')};border-radius:3px;min-height:20px;}}QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0;}}")
        self.sb.setStyleSheet(f"QFrame{{background:{t('surface')};border-left:1px solid {t('border')}}}")
        self.vl.setStyleSheet(f"color:{t('muted')};font-size:10px")
        if CT is DARK: self.brand_lbl.setStyleSheet("color:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #FFFFFF,stop:1 #C8C8D8);font-size:18px;font-weight:700;")
        else: self.brand_lbl.setStyleSheet("color:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #5856D6,stop:1 #818CF8);font-size:18px;font-weight:700;")
        self._nav(self.stack.currentIndex())
        for pg in [self.pp,self.srtp,self.hp,self.sp,self.ab]: pg.apply_theme()

    def relang(self):
        for b,(_,key) in zip(self.navs,self._nav_data):
            icon=b.text().strip().split()[0]; b.setText(f"  {icon}   {T(key)}")
        self.vl.setText(T("ver")); self.retheme()

if __name__=="__main__":
    app=QApplication(sys.argv)
    app.setFont(QFont("Segoe UI",11))
    win=MainWindow(); win.show()
    sys.exit(app.exec())
