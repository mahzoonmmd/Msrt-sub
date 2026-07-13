<div align="center">
  <img src="icon_256.png" width="120" alt="MSRT Logo"><br><br>
  <h1>MSRT — زیرنویس هوشمند</h1>
  <p><b>برنامه دسکتاپ ویندوز برای استخراج و ترجمه زیرنویس ویدیو</b></p>
  <p><i>Smart Windows desktop app for video subtitle extraction & Persian translation</i></p>
  <br>
  <img src="https://img.shields.io/badge/version-1.0-6366F1?style=flat-square">
  <img src="https://img.shields.io/badge/platform-Windows-0078D4?style=flat-square&logo=windows">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/API-Groq%20Free-34D399?style=flat-square">
  <img src="https://img.shields.io/badge/license-MIT-22C55E?style=flat-square">
</div>

---

<div dir="rtl">

## 🇮🇷 راهنمای فارسی

### ✨ قابلیت‌ها

| قابلیت | توضیح |
|--------|-------|
| 🎬 پردازش ویدیو | ویدیو بنداز، زیرنویس انگلیسی دقیق بگیر |
| 🌐 ترجمه فارسی | ترجمه هوشمند با Groq LLaMA 3.3 70B |
| 📄 ترجمه SRT | فایل SRT انگلیسی بده، فارسی بگیر (تایمینگ دست‌نخورده) |
| ✂️ کنترل کلمه | از ۱ تا ۱۰ کلمه در هر خط زیرنویس |
| 🔄 اعمال مجدد | بدون پردازش دوباره، تعداد کلمات رو تغییر بده |
| 📂 تاریخچه | تمام زیرنویس‌های قبلی ذخیره و قابل بازیابی |
| 🎨 تم | دارک / روشن قابل تغییر |
| 🇮🇷 🇺🇸 دوزبانه | رابط کاربری فارسی و انگلیسی |
| 📊 مصرف توکن | نمایش مصرف روزانه با ریست خودکار ۲۴ ساعته |

### 🚀 نصب و استفاده (کاربر عادی)

۱. فایل `MSRT_Setup_v1.0.exe` رو از بخش [Releases](../../releases) دانلود کن
۲. نصب کن و اجرا کن
۳. از [console.groq.com](https://console.groq.com) یه **API Key رایگان** بگیر
۴. توی تنظیمات برنامه وارد کن
۵. ویدیوت رو بنداز و زیرنویس بگیر ✅

> ⚠️ **به دلیل تحریم‌ها، قبل از پردازش حتماً از فیلترشکن استفاده کن**

### ⚙️ محدودیت حجم فایل صوتی

MSRT صدای ویدیو رو استخراج می‌کنه و به Groq Whisper میفرسته. Groq یه محدودیت **۲۵ مگابایت** برای هر فایل داره:

- **ویدیوهای کوتاه (زیر ~۴۵ دقیقه):** مستقیم پردازش میشن ✅
- **ویدیوهای بلند (بالای ~۴۵ دقیقه):** برنامه به صورت خودکار صدا رو به بخش‌های ۱۰ دقیقه‌ای تقسیم می‌کنه و جداگانه پردازش می‌کنه — برای این کار **ffprobe** هم باید داخل برنامه باشه

> 💡 نسخه‌ای که دانلود می‌کنی هر دو فایل ffmpeg و ffprobe رو داخل خودش داره و نیاز به نصب جداگانه نیست.

### 🛠️ نصب برای توسعه‌دهنده

**پیش‌نیازها:**
- Python 3.11+
- [ffmpeg + ffprobe](https://www.gyan.dev/ffmpeg/builds/) (اضافه شده به PATH)

```bash
git clone https://github.com/mahzoonmmd/Msrt-sub.git
cd Msrt-sub
pip install -r requirements.txt
python app.py
```

### 📦 ساخت فایل نصب

```bash
# ffmpeg.exe و ffprobe.exe رو کنار app.py بذار، بعد:
build.bat
# بعد از ساخت EXE، با Inno Setup فایل installer.iss رو Compile کن
```

### 💙 حمایت از پروژه

اگه MSRT برات مفید بوده، با یه ⭐ Star و Follow کمک کن این پروژه رشد کنه و بهتر بشه!

[![Star](https://img.shields.io/github/stars/mahzoonmmd/Msrt-sub?style=social)](https://github.com/mahzoonmmd/Msrt-sub/stargazers)
[![Follow](https://img.shields.io/github/followers/mahzoonmmd?style=social)](https://github.com/mahzoonmmd)

</div>

---

## 🇺🇸 English Guide

### ✨ Features

| Feature | Description |
|---------|-------------|
| 🎬 Video Processing | Drop a video, get accurate English subtitles |
| 🌐 Persian Translation | AI-powered translation via Groq LLaMA 3.3 70B |
| 📄 SRT Translation | Input English SRT → Output Persian SRT (timings preserved) |
| ✂️ Word Control | 1–10 words per subtitle line |
| 🔄 Re-apply | Change word count without reprocessing |
| 📂 History | All past subtitles saved and reopenable |
| 🎨 Theme | Dark / Light mode |
| 🇮🇷 🇺🇸 Bilingual | Persian and English UI |
| 📊 Token Usage | Daily usage display with automatic 24h reset |

### 🚀 Installation (End User)

1. Download `MSRT_Setup_v1.0.exe` from [Releases](../../releases)
2. Install and launch
3. Get a **free API Key** from [console.groq.com](https://console.groq.com)
4. Enter it in Settings
5. Drop your video and get subtitles ✅

> ⚠️ **Due to sanctions, use a VPN before processing**

### ⚙️ File Size & Long Videos

MSRT extracts audio from your video and sends it to Groq Whisper. Groq has a **25 MB limit** per file:

- **Short videos (under ~45 min):** Processed directly ✅
- **Long videos (over ~45 min):** MSRT automatically splits the audio into 10-minute chunks and processes them sequentially — this requires **ffprobe** to be bundled inside the app

> 💡 The downloadable release includes both ffmpeg and ffprobe — no separate installation needed.

### 🛠️ Developer Setup

**Requirements:**
- Python 3.11+
- [ffmpeg + ffprobe](https://www.gyan.dev/ffmpeg/builds/) (added to PATH)

```bash
git clone https://github.com/mahzoonmmd/Msrt-sub.git
cd Msrt-sub
pip install -r requirements.txt
python app.py
```

### 💙 Support the Project

If MSRT has been useful to you, a ⭐ Star and a Follow go a long way in helping this project grow!

[![Star](https://img.shields.io/github/stars/mahzoonmmd/Msrt-sub?style=social)](https://github.com/mahzoonmmd/Msrt-sub/stargazers)
[![Follow](https://img.shields.io/github/followers/mahzoonmmd?style=social)](https://github.com/mahzoonmmd)

---

## 🏗️ Architecture

```
Video → ffmpeg (audio extraction)
           ↓
    Groq Whisper Large v3 (speech recognition)
    [auto-split if audio > 25MB using ffprobe]
           ↓
    Groq LLaMA 3.3 70B (Persian translation)
           ↓
    Output: SRT + English text + Persian translation
```

## 🔑 API

| Service | Usage | Free Limit |
|---------|-------|-----------|
| [Groq](https://console.groq.com) | Speech-to-text + Translation | 14,400 sec audio/day |

## 📁 Project Structure

```
Msrt-sub/
├── app.py            # Main application
├── icon.ico          # Windows icon
├── icon_256.png      # App logo
├── requirements.txt  # Python dependencies
├── build.bat         # Build EXE script
├── installer.iss     # Inno Setup installer script
└── .gitignore
```

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

## 📄 License

[MIT](LICENSE) — Free for personal and commercial use
