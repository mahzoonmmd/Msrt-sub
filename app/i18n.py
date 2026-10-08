"""
i18n.py
-------
Minimal, dependency-free translation table for the UI (fa/en).
Usage: from app.i18n import t; t("home.title", lang)
"""
from __future__ import annotations

STRINGS = {
    "app.title": {"fa": "MSRT — زیرنویس هوشمند", "en": "MSRT — Smart Subtitles"},

    # Sidebar
    "nav.process": {"fa": "پردازش ویدیو", "en": "Process Video"},
    "nav.srt": {"fa": "ترجمه زیرنویس", "en": "Translate SRT"},
    "nav.history": {"fa": "تاریخچه", "en": "History"},
    "nav.settings": {"fa": "تنظیمات", "en": "Settings"},
    "nav.about": {"fa": "درباره برنامه", "en": "About"},

    # Process page
    "process.drop_title": {"fa": "ویدیوی خود را رها کنید", "en": "Drop your video here"},
    "process.drop_subtitle": {"fa": "یا برای انتخاب فایل کلیک کنید — MP4, MOV, MKV, AVI, WEBM",
                               "en": "or click to browse — MP4, MOV, MKV, AVI, WEBM"},
    "process.selected": {"fa": "فایل انتخاب‌شده:", "en": "Selected file:"},
    "process.source_lang": {"fa": "زبان ویدیو", "en": "Source language"},
    "process.lang_en": {"fa": "انگلیسی", "en": "English"},
    "process.lang_fa": {"fa": "فارسی", "en": "Persian"},
    "process.start": {"fa": "شروع پردازش", "en": "Start Processing"},
    "process.cancel": {"fa": "لغو", "en": "Cancel"},
    "process.tab_original": {"fa": "متن اصلی", "en": "Original"},
    "process.tab_translation": {"fa": "ترجمه", "en": "Translation"},
    "process.words_per_line": {"fa": "تعداد کلمه در هر خط", "en": "Words per line"},
    "process.reapply": {"fa": "اعمال مجدد", "en": "Reapply"},
    "process.download_en": {"fa": "دانلود SRT انگلیسی", "en": "Download English SRT"},
    "process.download_fa": {"fa": "دانلود SRT فارسی", "en": "Download Persian SRT"},
    "process.copy_plain": {"fa": "کپی متن", "en": "Copy text"},
    "process.remove_video": {"fa": "حذف ویدیو", "en": "Remove video"},
    "process.reapplied": {"fa": "تنظیمات زیرنویس بروزرسانی شد ✓", "en": "Subtitle settings updated ✓"},
    "process.no_result_yet": {"fa": "ابتدا یک ویدیو پردازش کنید", "en": "Process a video first"},
    "process.copied": {"fa": "متن کپی شد", "en": "Copied to clipboard"},
    "process.success": {"fa": "پردازش با موفقیت انجام شد ✓", "en": "Processing completed successfully ✓"},
    "process.no_api_key": {"fa": "ابتدا کلید Gemini API را در تنظیمات وارد کنید",
                            "en": "Please set your Gemini API key in Settings first"},
    "process.no_file": {"fa": "ابتدا یک ویدیو انتخاب کنید", "en": "Please choose a video first"},
    "process.info_tooltip": {"fa": "نمایش راهنمای شروع کار", "en": "Show the getting-started guide"},
    "process.step_audio": {"fa": "در حال استخراج صدا…", "en": "Extracting audio…"},
    "process.step_split": {"fa": "در حال تقسیم فایل صوتی…", "en": "Splitting audio into chunks…"},
    "process.step_transcribe": {"fa": "در حال تبدیل گفتار به متن…", "en": "Transcribing speech…"},
    "process.step_translate": {"fa": "در حال ترجمه…", "en": "Translating…"},
    "process.step_build_srt": {"fa": "در حال ساخت فایل SRT…", "en": "Building SRT…"},
    "process.error": {"fa": "خطا در پردازش:", "en": "Processing error:"},

    # SRT translate page
    "srt.title": {"fa": "ترجمه فایل SRT آماده", "en": "Translate an existing SRT"},
    "srt.drop_title": {"fa": "فایل SRT را رها کنید", "en": "Drop your .srt file here"},
    "srt.drop_subtitle": {"fa": "یا برای انتخاب فایل کلیک کنید", "en": "or click to browse"},
    "srt.direction": {"fa": "جهت ترجمه", "en": "Direction"},
    "srt.dir_en_fa": {"fa": "انگلیسی ← فارسی", "en": "English → Persian"},
    "srt.dir_fa_en": {"fa": "فارسی ← انگلیسی", "en": "Persian → English"},
    "srt.start": {"fa": "شروع ترجمه", "en": "Start Translation"},
    "srt.download": {"fa": "دانلود SRT ترجمه‌شده", "en": "Download translated SRT"},
    "srt.remove_file": {"fa": "حذف زیرنویس", "en": "Remove subtitle"},

    # History
    "history.empty": {"fa": "هنوز پردازشی ثبت نشده است.", "en": "No processed items yet."},
    "history.open": {"fa": "مشاهده", "en": "View"},
    "history.delete": {"fa": "حذف", "en": "Delete"},
    "history.confirm_delete": {"fa": "این مورد از تاریخچه حذف شود؟", "en": "Remove this item from history?"},

    # Settings
    "settings.api_key": {"fa": "کلید Gemini API", "en": "Gemini API Key"},
    "settings.section_api": {"fa": "هوش مصنوعی", "en": "AI / API"},
    "settings.section_usage": {"fa": "مصرف", "en": "Usage"},
    "settings.section_appearance": {"fa": "ظاهر برنامه", "en": "Appearance"},
    "settings.section_language": {"fa": "زبان", "en": "Language"},
    "settings.api_key_helper": {
        "fa": "برای رونویسی و ترجمه لازم است. یک کلید رایگان از aistudio.google.com بگیرید.",
        "en": "Required for transcription and translation. Get a free key from aistudio.google.com.",
    },
    "settings.api_key_placeholder": {"fa": "کلید API خود را اینجا وارد کنید",
                                      "en": "Paste your API key here"},
    "settings.save": {"fa": "ذخیره", "en": "Save"},
    "settings.saved": {"fa": "تنظیمات ذخیره شد", "en": "Settings saved"},
    "settings.usage": {"fa": "مصرف توکن امروز", "en": "Today's token usage"},
    "settings.refresh": {"fa": "بروزرسانی", "en": "Refresh"},
    "settings.usage_reset": {"fa": "ریست تا", "en": "Resets in"},
    "settings.theme": {"fa": "پوسته", "en": "Theme"},
    "settings.theme_dark": {"fa": "تیره", "en": "Dark"},
    "settings.theme_light": {"fa": "روشن", "en": "Light"},
    "settings.language": {"fa": "زبان رابط کاربری", "en": "Interface language"},

    # About
    "about.subtitle": {"fa": "زیرنویس هوشمند", "en": "Smart Subtitles"},
    "about.section_tech": {"fa": "اطلاعات فنی", "en": "Technical Info"},
    "about.description": {
        "fa": "MSRT ویدیوهای شما را با هوش مصنوعی رونویسی و ترجمه می‌کند — رایگان و سریع.",
        "en": "MSRT transcribes and translates your videos with AI — free and fast.",
    },
    "about.github": {"fa": "مشاهده در گیت‌هاب", "en": "View on GitHub"},
    "about.star": {"fa": "ستاره بدهید", "en": "Star the repo"},

    # Onboarding
    "onboarding.step1_title": {"fa": "۱. کلید Gemini را وارد کنید", "en": "1. Add your Gemini key"},
    "onboarding.step1_body": {"fa": "یک کلید رایگان از aistudio.google.com بگیرید و در تنظیمات وارد کنید.",
                               "en": "Grab a free key from aistudio.google.com and paste it into Settings."},
    "onboarding.step2_title": {"fa": "۲. ویدیوی خود را رها کنید", "en": "2. Drop your video"},
    "onboarding.step2_body": {"fa": "فایل ویدیو را بکشید و رها کنید یا انتخاب کنید.",
                               "en": "Drag & drop a video file, or click to browse."},
    "onboarding.step3_title": {"fa": "۳. زیرنویس را دریافت کنید", "en": "3. Get your subtitles"},
    "onboarding.step3_body": {"fa": "متن، ترجمه و فایل SRT آماده دانلود است.",
                               "en": "Text, translation and SRT are ready to download."},
    "onboarding.next": {"fa": "بعدی", "en": "Next"},
    "onboarding.done": {"fa": "شروع کنیم", "en": "Let's go"},

    "common.browse": {"fa": "انتخاب فایل", "en": "Browse"},
}


def t(key: str, lang: str = "fa") -> str:
    entry = STRINGS.get(key)
    if not entry:
        return key
    return entry.get(lang, entry.get("fa", key))
