# MSRT — Smart Subtitles

A free desktop app — now for **Windows and macOS** — that transcribes and translates video subtitles with AI, powered by the Google Gemini API.

```
Video → ffmpeg (extract audio) → Google Gemini (transcribe + translate in one call) → SRT
```

## Features

**Video processing**
- Supports MP4, MOV, MKV, AVI, WEBM
- Drag & drop or browse for a file
- English video → English + Persian subtitles, or Persian video → Persian + English subtitles
- Long videos are automatically split into chunks before sending to the API — no manual splitting, no file-size limits to worry about
- A 16:9 video preview with play/pause and a seek bar appears as soon as you pick a file
- After processing, the layout switches to video on the left and the transcript/translation on the right, with the currently-spoken line **highlighted live** as the video plays (click any line to jump straight to it)
- Download the English and Persian SRT files separately, or copy the plain text (no timestamps)

**Subtitle formatting**
- Adjustable words-per-line (1–10) for how the SRT is chunked
- **Reapply** re-flows the already-generated subtitles instantly with a new words-per-line value — no re-processing, no extra API calls

**Translate an existing SRT**
- Translate a ready-made `.srt` file without needing the original video
- Both directions: English → Persian and Persian → English
- Original timing is preserved exactly

**History**
- Every processed video/SRT is saved automatically
- Reopen and review past results anytime
- Delete individual history items

**Settings**
- Save your Google Gemini API key
- Live daily token-usage meter with a manual refresh and automatic 24h reset
- Dark and light themes (independently designed, not just inverted)
- English and Persian interface, fully switchable at runtime

**Polish**
- Three-step guided onboarding for first-time users
- A Cancel button appears while a job is running
- Success confirmation banner after each run
- Native-feeling right-to-left Persian text that stays readable even when mixed with English words/numbers in the same line
- Clean, professional UI with the app's own custom offline icon set (no emoji)

## Platforms

| | Windows | macOS |
|---|---|---|
| Packaged as | `MSRT.exe` installer (Inno Setup) | `MSRT.app` + `.dmg` |
| Build script | `build_windows.py` | `build_macos.py` |
| Status | Built and tested locally | Built and smoke-tested automatically on a real macOS runner via GitHub Actions (`.github/workflows/build-macos.yml`) — see note below |

Same codebase, same AI logic, same data model — only the packaging differs per platform.

> **Note on the macOS build:** it is produced and verified by this repo's own GitHub Actions workflow on a hosted Apple Silicon runner (imports cleanly, builds `MSRT.app`, and launches it headlessly to confirm it actually starts), since development happens without local Mac hardware. Every push to `main` that touches app code re-runs it, and the resulting `.dmg` is published to the workflow's run page as a downloadable artifact — grab it from the **Actions** tab, or push a `vX.Y-macos` tag to also attach it to a GitHub Release.

## Tech stack

| | |
|---|---|
| Language | Python 3.11+ |
| UI | PyQt6 |
| AI (speech-to-text + translation) | Google Gemini API (`gemini-3.5-flash-lite`) |
| Packaging | PyInstaller (+ Inno Setup on Windows) |
| Platforms | Windows 10/11, macOS 12+ |

## Getting started (for users)

1. Download the latest build for your platform:
   - **Windows:** the installer from the [Releases](../../releases) page.
   - **macOS:** the `.dmg` from the latest successful run of the [`build-macos`](../../actions/workflows/build-macos.yml) workflow (or a tagged Release, once one exists).
2. Run it — ffmpeg is bundled, nothing else to install separately.
3. Get a free API key from [aistudio.google.com](https://aistudio.google.com) and paste it into MSRT's Settings page.
4. Drop in a video and go.

> On macOS, since the app is currently only ad-hoc signed, the first launch needs **right-click → Open** (not a double-click) to get past Gatekeeper's "unidentified developer" warning.

## Running from source (for developers)

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

On macOS, install ffmpeg first so `python main.py` runs without bundling it yourself:
```bash
brew install ffmpeg
```

## Building a release

**Windows:**
```bash
# 1. Place ffmpeg.exe and ffprobe.exe (static build, e.g. from gyan.dev) in resources/
pip install -r requirements.txt
python build_windows.py          # -> dist/MSRT.exe
# 2. Compile installer/setup.iss with Inno Setup 6 -> MSRT-Setup-*.exe
```

**macOS** (must run on a real Mac — PyInstaller doesn't cross-build):
```bash
# 1. Place ffmpeg/ffprobe (no extension, chmod +x) in resources/
#    e.g. brew install ffmpeg, then copy the binaries out of the Homebrew prefix
pip install -r requirements.txt
python build_macos.py            # -> dist/MSRT.app, dist/MSRT.dmg
```
No Mac available? Push to this repo (or trigger it manually from the **Actions** tab) and let `.github/workflows/build-macos.yml` build it on a hosted macOS runner instead.

## License

MIT — see [LICENSE](LICENSE).

---

# MSRT — زیرنویس هوشمند

یک برنامه‌ی دسکتاپ کاملاً رایگان — حالا هم برای **ویندوز و هم مک** — که با هوش مصنوعی، زیرنویس ویدیوها را رونویسی و ترجمه می‌کند، با استفاده از Google Gemini API.

```
ویدیو → ffmpeg (استخراج صدا) → Google Gemini (رونویسی + ترجمه در یک تماس) → SRT
```

## ویژگی‌ها

**پردازش ویدیو**
- پشتیبانی از MP4، MOV، MKV، AVI، WEBM
- Drag & drop یا انتخاب فایل
- ویدیوی انگلیسی ← زیرنویس انگلیسی + فارسی، یا ویدیوی فارسی ← زیرنویس فارسی + انگلیسی
- ویدیوهای طولانی خودکار به چند بخش تقسیم می‌شوند قبل از ارسال به API
- با انتخاب فایل، بلافاصله یک پیش‌نمایش ویدیو با نسبت ۱۶:۹ همراه با دکمه‌ی پخش و نوار پیشرفت نمایش داده می‌شود
- بعد از پردازش، چیدمان صفحه به ویدیو در سمت چپ و متن اصلی/ترجمه در سمت راست تغییر می‌کند؛ خطی که در حال گفته‌شدن است **به‌صورت زنده هایلایت** می‌شود (با کلیک روی هر خط می‌توانید مستقیم به همان لحظه از ویدیو بروید)
- دانلود جداگانه‌ی فایل‌های SRT انگلیسی و فارسی، یا کپی متن ساده (بدون زمان‌بندی)

**قالب‌بندی زیرنویس**
- تنظیم تعداد کلمه در هر خط (۱ تا ۱۰)
- دکمه‌ی **اعمال مجدد** زیرنویس ساخته‌شده را فوراً با تعداد کلمه‌ی جدید بازچینش می‌کند — بدون پردازش دوباره و بدون تماس اضافه با API

**ترجمه‌ی زیرنویس آماده**
- ترجمه‌ی یک فایل `.srt` آماده بدون نیاز به ویدیوی اصلی
- هر دو جهت: انگلیسی ← فارسی و فارسی ← انگلیسی
- حفظ کامل زمان‌بندی اصلی

**تاریخچه**
- ذخیره‌ی خودکار تمام پردازش‌های ویدیو/زیرنویس
- بازیابی و مشاهده‌ی مجدد نتایج قبلی در هر زمان
- حذف تک‌تک آیتم‌های تاریخچه

**تنظیمات**
- ذخیره‌ی کلید Google Gemini API
- نمایش زنده‌ی مصرف توکن روزانه با دکمه‌ی بروزرسانی دستی و ریست خودکار ۲۴ ساعته
- تم تیره و روشن (هرکدام جداگانه طراحی شده، نه صرفاً معکوسِ یکدیگر)
- رابط کاربری فارسی و انگلیسی، قابل‌تعویض در حین اجرا

**تجربه‌ی کاربری**
- راهنمای سه‌مرحله‌ای برای کاربران جدید
- دکمه‌ی «لغو» حین پردازش
- بنر تأیید موفقیت پس از هر پردازش
- متن فارسی راست‌به‌چپ طبیعی که حتی در ترکیب با کلمات/اعداد انگلیسی در یک خط، خوانا باقی می‌ماند
- طراحی تمیز و حرفه‌ای همراه با مجموعه آیکون‌های اختصاصی آفلاین (بدون ایموجی)

## پلتفرم‌ها

| | ویندوز | مک |
|---|---|---|
| بسته‌بندی | نصب‌کننده‌ی `MSRT.exe` (Inno Setup) | `MSRT.app` + `.dmg` |
| اسکریپت بیلد | `build_windows.py` | `build_macos.py` |
| وضعیت | ساخته و تست‌شده به‌صورت محلی | ساخته و تست‌شده به‌صورت خودکار روی یک رانر واقعی macOS از طریق GitHub Actions (`.github/workflows/build-macos.yml`) |

همان کد، همان منطق هوش مصنوعی، همان مدل داده — فقط بسته‌بندی بر اساس پلتفرم فرق می‌کند.

> **نکته درباره‌ی بیلد مک:** چون توسعه بدون سخت‌افزار مک انجام می‌شود، این بیلد توسط workflow گیت‌هاب‌اکشنز خودِ همین ریپو روی یک رانر واقعی Apple Silicon ساخته و تأیید می‌شود (ایمپورت کامل، ساخت `MSRT.app`، و اجرای واقعی و headless آن برای اطمینان از بالا آمدن درست برنامه). با هر پوش به شاخه‌ی `main` که فایل‌های برنامه را تغییر دهد دوباره اجرا می‌شود و فایل `.dmg` نهایی را به‌عنوان artifact قابل دانلود در صفحه‌ی اجرای workflow می‌گذارد — از تب **Actions** بگیرید، یا با پوش کردن یک تگ به شکل `vX.Y-macos` آن را به یک Release هم ضمیمه کنید.

## اطلاعات فنی

| مورد | جزئیات |
|---|---|
| زبان برنامه‌نویسی | Python 3.11+ |
| رابط کاربری | PyQt6 |
| هوش مصنوعی (رونویسی + ترجمه) | Google Gemini API (`gemini-3.5-flash-lite`) |
| بسته‌بندی | PyInstaller (+ Inno Setup برای ویندوز) |
| پلتفرم‌ها | Windows 10/11، macOS 12+ |

## شروع کار (برای کاربران)

۱. آخرین نسخه‌ی مناسب پلتفرم خود را دانلود کنید:
   - **ویندوز:** فایل نصب از صفحه‌ی [Releases](../../releases)
   - **مک:** فایل `.dmg` از آخرین اجرای موفق workflow [`build-macos`](../../actions/workflows/build-macos.yml) (یا یک Release تگ‌شده، هر زمان ساخته شود)
۲. اجرایش کنید — ffmpeg داخلش هست، نیازی به نصب جداگانه نیست.
۳. یک کلید رایگان از [aistudio.google.com](https://aistudio.google.com) بگیرید و در تنظیمات برنامه وارد کنید.
۴. یک ویدیو انتخاب کنید و شروع کنید.

> روی مک، چون برنامه فعلاً فقط ad-hoc امضا شده، برای اولین اجرا باید روی آیکون **راست‌کلیک → Open** کنید (نه دابل‌کلیک ساده) تا هشدار Gatekeeper رد شود.

## اجرا از سورس (برای توسعه‌دهندگان)

```bash
python -m venv .venv

# ویندوز
.venv\Scripts\activate

# مک / لینوکس
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

روی مک، قبلش ffmpeg را نصب کنید تا نیازی به باندل‌کردن دستی آن نباشد:
```bash
brew install ffmpeg
```

## ساخت نسخه‌ی نهایی

**ویندوز:**
```bash
# ۱. فایل‌های ffmpeg.exe و ffprobe.exe (نسخه‌ی static، مثلاً از gyan.dev) را در resources/ قرار دهید
pip install -r requirements.txt
python build_windows.py          # -> dist/MSRT.exe
# ۲. فایل installer/setup.iss را با Inno Setup 6 کامپایل کنید -> MSRT-Setup-*.exe
```

**مک** (باید روی یک مک واقعی اجرا شود — PyInstaller قابلیت cross-build ندارد):
```bash
# ۱. فایل‌های ffmpeg/ffprobe (بدون پسوند، chmod +x) را در resources/ قرار دهید
#    مثلاً brew install ffmpeg و سپس کپی باینری‌ها از پوشه‌ی Homebrew
pip install -r requirements.txt
python build_macos.py            # -> dist/MSRT.app، dist/MSRT.dmg
```
مک ندارید؟ به این ریپو پوش کنید (یا از تب **Actions** به‌صورت دستی اجرا کنید) و بگذارید `.github/workflows/build-macos.yml` آن را روی یک رانر واقعی مک بسازد.

## لایسنس

MIT — به فایل [LICENSE](LICENSE) مراجعه کنید.
