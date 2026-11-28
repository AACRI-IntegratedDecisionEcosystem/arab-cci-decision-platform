import io
import os
import re
import json
import html
import hashlib
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

try:
    from docx import Document
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    HAS_PYTHON_DOCX = True
except ImportError:
    HAS_PYTHON_DOCX = False

# ==============================================================================
# إعدادات صفحة Streamlit وتطبيق الهوية البصرية (RTL + Responsive)
# ==============================================================================
st.set_page_config(
    page_title="منصة منظومة القرار المتكاملة للسياسات الثقافية والإبداعية العربية",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="auto"
)

# الألوان التراثية الرسمية للمنصة وحالات التفاعل
CCI_ORANGE_DARK = "#78350F"    # برتقالي غامق جداً قاتم
CCI_ORANGE_MID = "#B45309"      # برتقالي غامق تراثي
CCI_ORANGE_LIGHT = "#D97706"    # برتقالي أفتح نسبياً عند التحديد
CCI_NAVY = "#0A192F"           # أزرق ملكي عميق
CCI_NAVY_HOVER = "#162A4A"     # درجة تمرير متناسقة مع الخلفية الأساسية
CCI_GOLD_BRIGHT = "#FBBF24"    # لون ذهبي مشرق في الوضع العادي
CCI_WHITE_ACTIVE = "#FFFFFF"   # لون أبيض واضح عند المرور / الضغط / التحديد
CCI_BG = "#F8FAFC"             # خلفية ناعمة
UI_CSS_VERSION = "cci-tabs-v21"

# خط عربي مجاني واضح وثابت للمواقع الإلكترونية عبر Google Fonts
APP_FONT = "'Cairo', 'Tajawal', 'Readex Pro', system-ui, -apple-system, sans-serif"


def clean_text(text) -> str:
    if not isinstance(text, str):
        return str(text)
    t = re.sub(r"<[^>]+>", "", text)
    t = html.unescape(t)
    t = t.replace("\xa0", " ").replace("\u200b", "")
    return re.sub(r"\s+", " ", t).strip()


def flat_html(s: str) -> str:
    """يزيل المسافات البادئة والأسطر الفارغة حتى لا يحوّل Markdown الـ HTML إلى كتلة كود."""
    return " ".join(l.strip() for l in s.splitlines() if l.strip())


def bullets_to_html(text: str) -> str:
    items = [re.sub(r"^[-•]\s*", "", l.strip()) for l in text.strip().splitlines() if l.strip()]
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def score_band(score):
    if score >= 80:
        return "مرتفع", "#15803D", "#DCFCE7"
    if score >= 51:
        return "متوسط", "#B45309", "#FEF3C7"
    return "حرج", "#B91C1C", "#FEE2E2"


AXES = [
    ("ti", "البنية التقنية", 0.20, CCI_NAVY),
    ("ed", "الديناميكيات الاقتصادية", 0.15, "#0F766E"),
    ("hc", "رأس المال البشري", 0.30, "#92400E"),
    ("rf", "البيئة التنظيمية والتشريعية", 0.20, "#1E3A8A"),
    ("cd", "المحددات الثقافية والهوياتية", 0.15, CCI_ORANGE_DARK),
]


def axis_counts(dimensions):
    n_dims = len(dimensions)
    n_subs = sum(len(d[2]) for d in dimensions)
    n_vars = sum(len(sd[2]) for d in dimensions for sd in d[2])
    return n_dims, n_subs, n_vars


# ==============================================================================
# المصفوفة الهرمية الكاملة لمؤشر الجاهزية الذكية (AACRI - 5 محاور / 69 متغيراً)
# بأسلوب القوائم المتداخلة لكل محور وبعد أساسي وبعد فرعي ومتغير
# ==============================================================================
AACRI_HIERARCHY_MATRIX = [
    [
        "ti",
        "1. البنية التقنية والتحول الرقمي الإبداعي (وزن 20%)",
        20.0,
        "المحور الأول | بعدان أساسيان | 4 أبعاد فرعية | 13 متغيراً | وزن المحور: 20%",
        CCI_NAVY,
        "#EFF6FF",
        "#BFDBFE",
        [
            [
                "1.1",
                "جاهزية البنية التحتية السحابية والحاسوبية",
                [
                    [
                        "1.1.1",
                        "سعات وتدفق البيانات الضخمة (Open Big Data) والتخزين",
                        [
                            ["متغير 1.1.1.1: نسبة المؤسسات الثقافية التي تعتمد على الحوسبة السحابية في الإنتاج (% من مسح سنوي).", "%"],
                            ["متغير 1.1.1.2: حجم السعة التخزينية الرقمية المخصصة للمؤسسات الثقافية على السحابة الوطنية (تيرا بايت).", "تيرا بايت"],
                            ["متغير 1.1.1.3: عدد مجموعات البيانات الوطنية المفتوحة القابلة لتدريب النماذج الإبداعية.", "عدد"],
                        ],
                    ],
                    [
                        "1.1.2",
                        "سرعات الإنترنت والاتصال عريض الباند (Broadband) والقدرات الحاسوبية (HPC)",
                        [
                            ["متغير 1.1.2.1: متوسط سرعة الإنترنت النطاق العريض (Mbps) في المراكز الثقافية.", "Mbps"],
                            ["متغير 1.1.2.2: نسبة المؤسسات التي تمتلك إمكانية الوصول لقدرات حاسوبية عالية الأداء (HPC).", "%"],
                            ["متغير 1.1.2.3: نسبة تغطية الألياف الضوئية للمناطق التاريخية والمراكز الحاضنة للإبداع (%).", "%"],
                        ],
                    ],
                ],
            ],
            [
                "1.2",
                "توطين أدوات الذكاء الاصطناعي",
                [
                    [
                        "1.2.1",
                        "توافر منصات محلية مفتوحة المصدر وبرمجيات الدعم",
                        [
                            ["متغير 1.2.1.1: عدد المنصات الرقمية المحلية المفتوحة المصدر لخدمة الفنون والإبداع الرقمي.", "عدد"],
                            ["متغير 1.2.1.2: نسبة الدعم الحكومي الموجه لتطوير برمجيات ومكتبات مفتوحة المصدر (مليون دولار).", "مليون دولار"],
                            ["متغير 1.2.1.3: عدد المطورين المحليين المساهمين في مشاريع الذكاء الاصطناعي الإبداعي المفتوحة.", "عدد"],
                        ],
                    ],
                    [
                        "1.2.2",
                        "دمج النماذج اللغوية الكبيرة (LLMs) وقابلية التشغيل البيني والمعايير الأمنية",
                        [
                            ["متغير 1.2.2.1: عدد النماذج والتطبيقات التوليدية الموطنة محلياً والمدعومة بالبيانات العربية.", "عدد"],
                            ["متغير 1.2.2.2: متوسط درجات اختبارات المعيارية اللغوية والثقافية العربية المطبقة على النماذج الموطنة (مُقاساً عبر مصفوفة تقييم الخبراء أو الاختبارات القياسية NLP Benchmarks) من 100 بند.", "درجة من 100"],
                            ["متغير 1.2.2.3: النسبة المئوية لنجاح تكامل برمجيات الإنتاج الفني مع النماذج الذكية دون أخطاء تقنية (مُقاساً بعدد حالات التكامل الناجحة من إجمالي محاولات الربط).", "%"],
                            ["متغير 1.2.2.4: نسبة المنصات الإبداعية الوطنية الحاصلة على شهادات الأمان السيبراني الدولية (ISO/IEC).", "%"],
                        ],
                    ],
                ],
            ],
        ],
    ],
    [
        "ed",
        "2. الديناميكيات الاقتصادية وسلاسل القيمة الإبداعية (وزن 15%)",
        15.0,
        "المحور الثاني | 3 أبعاد أساسية | 6 أبعاد فرعية | 15 متغيراً | وزن المحور: 15%",
        "#0F766E",
        "#F0FDFA",
        "#99F6E4",
        [
            [
                "2.1",
                "مساهمة الاقتصاد البرتقالي في الناتج المحلي (GDP)",
                [
                    [
                        "2.1.1",
                        "حجم العوائد المالية لقطاع الصناعات الثقافية والإبداعية (CCIs)",
                        [
                            ["متغير 2.1.1.1: النسبة المئوية لمساهمة قطاع (CCIs) في الناتج المحلي الإجمالي (GDP).", "%"],
                            ["متغير 2.1.1.2: إجمالي القيمة المضافة الإجمالية (GVA) للأنشطة الإبداعية (بالعملة المحلية).", "عملة محلية"],
                            ["متغير 2.1.1.3: حجم الاستثمار الحكومي والخاص في البنية التحتية للخوادم ومراكز البيانات الإبداعية (مليون دولار).", "مليون دولار"],
                        ],
                    ],
                    [
                        "2.1.2",
                        "حجم الصادرات الإبداعية وكفاءة سلاسل القيمة",
                        [
                            ["متغير 2.1.2.1: قيمة الصادرات السنوية للسلع والخدمات الإبداعية (قاعدة بيانات UN Comtrade).", "دولار / UN Comtrade"],
                            ["متغير 2.1.2.2: عدد التصاميم الصناعية المودعة محلياً ودولياً في فئات الأزياء، الفنون التطبيقية، والتصميم المعماري سنوياً.", "عدد"],
                            ["متغير 2.1.2.3: معدل النمو السنوي لصادرات الصناعات الإبداعية الثقافية (%).", "%"],
                            ["متغير 2.1.2.4: نسبة التخفيض المئوية في تكاليف الإنتاج والتوزيع الزمنية والمالية للمؤسسات الإبداعية بعد استخدام الذكاء الاصطناعي مقارنة بالعام السابق %.", "%"],
                        ],
                    ],
                ],
            ],
            [
                "2.2",
                "الاستثمار ودعم ريادة الأعمال",
                [
                    [
                        "2.2.1",
                        "حجم تمويل رأس المال المخاطر (VC) للشركات الإبداعية الناشئة",
                        [
                            ["متغير 2.2.1.1: حجم الاستثمار المالي الموجه للمشاريع الناشئة في الاقتصاد البرتقالي (مليون دولار).", "مليون دولار"],
                            ["متغير 2.2.1.2: عدد طلبات تسجيل العلامات التجارية المرتبطة بقطاعات الخدمات الثقافية، الإعلامية، والترفيهية والمستحدثة بالذكاء الاصطناعي سنوياً.", "عدد"],
                            ["متغير 2.2.1.3: عدد صفقات الاستثمار الجريء (Venture Capital) المنعقدة في قطاع التقنيات الإبداعية سنوياً.", "عدد"],
                        ],
                    ],
                    [
                        "2.2.2",
                        "التسهيلات الائتمانية ومؤشر الاحتكار التقني للشركات الكبرى",
                        [
                            ["متغير 2.2.2.1: نسبة القروض المصرفية الميسرة الموجهة للمنشآت الإبداعية الصغيرة والمتوسطة.", "%"],
                            ["متغير 2.2.2.2: عدد الحاضنات ومسرعات الأعمال المتخصصة في دعم الاقتصاد البرتقالي في الدولة.", "عدد"],
                            ["متغير 2.2.2.3: مستوى تركز السوق واعتماد الاقتصاد الإبداعي على منصات Big Tech الأجنبية (مقياس عكسي).", "مقياس عكسي"],
                        ],
                    ],
                ],
            ],
            [
                "2.3",
                "السياحة الثقافية والتكامل الإبداعي",
                [
                    [
                        "2.3.1",
                        "العوائد السياحية المرتبطة بالمنتجات الإبداعية والتراثية",
                        [
                            ["متغير 2.3.1.1: نسبة إنفاق السياح الدوليين والمحليين على اقتناء الفنون والحرف التراثية من إجمالي الإنفاق السياحي.", "%"],
                            ["متغير 2.3.1.2: عدد الفاعليات والمهرجانات الثقافية الكبرى المدرجة في الأجندة السياحية الرسمية.", "عدد"],
                        ],
                    ],
                    [
                        "2.3.2",
                        "اندماج المبدعين المحليين في المنظومة السياحية الكبرى",
                        [
                            ["متغير 2.3.2.1: عدد الشراكات الرسمية بين المنشآت الفندقية/السياحية ومشاغل الحرف والفنانين المحليين.", "عدد"],
                            ["متغير 2.3.2.2: عدد منافذ ومتاجر بيع الفنون والحرف التراثية الرسمية المتاحة فعلياً لكل ألف سائح في المقاصد السياحية الرئيسة.", "منفذ / 1000 سائح"],
                        ],
                    ],
                ],
            ],
        ],
    ],
    [
        "hc",
        "3. رأس المال البشري والمهارات التوليدية (وزن 30%)",
        30.0,
        "المحور الثالث | بعدان أساسيان | 4 أبعاد فرعية | 12 متغيراً | وزن المحور: 30%",
        "#92400E",
        "#FFFBEB",
        "#FDE68A",
        [
            [
                "3.1",
                "جاهزية مهارات القوى العاملة (Upskilling / Reskilling)",
                [
                    [
                        "3.1.1",
                        "التدريب المستمر على الذكاء الاصطناعي وهندسة الأوامر وإدارتها",
                        [
                            ["متغير 3.1.1.1: نسبة العمالة الشابة (15-24 سنة) المشتغلة في المهن الثقافية والإبداعية.", "%"],
                            ["متغير 3.1.1.2: نسبة العاملين الحاصلين على برامج معتمدة في هندسة الأوامر (Prompt Engineering) والتحكم بالمخرجات التوليدية.", "%"],
                            ["متغير 3.1.1.3: نسبة المبدعين المستقلين (Freelancers) المستخدمين للأدوات التوليدية بانتظام في أعمالهم.", "%"],
                        ],
                    ],
                    [
                        "3.1.2",
                        "المرونة المهنية وساعات البرامج التدريبية المتقدمة وإعادة التأهيل",
                        [
                            ["متغير 3.1.2.1: نسبة الكوادر الإبداعية القادرة على اجتياز اختبارات التكيف المهني وبرامج إعادة التأهيل السريع (Reskilling).", "%"],
                            ["متغير 3.1.2.2: عدد الساعات التدريبية المعتمدة المقدمة للمبدعين في التقنيات الرقمية والذكاء الاصطناعي.", "ساعة تدريبية"],
                        ],
                    ],
                ],
            ],
            [
                "3.2",
                "ريادة الأعمال الإبداعية والتعليم البيني",
                [
                    [
                        "3.2.1",
                        "دمج علوم البيانات والفنون والوعي الأخلاقي بالمناهج",
                        [
                            ["متغير 3.2.1.1: عدد الأقسام الجامعية التي تقدم برامج دمج بين التكنولوجيا والفنون.", "عدد"],
                            ["متغير 3.2.1.2: عدد المقررات الدراسية البينية المرتبطة بالاقتصاد الإبداعي في مؤسسات التعليم العالي.", "عدد"],
                            ["متغير 3.2.1.3: متوسط درجات استجابة عينة المبدعين في استبيان قياس الوعي الأخلاقي والمسؤولية تجاه المحتوى المُولَد.", "متوسط درجات"],
                        ],
                    ],
                    [
                        "3.2.2",
                        "شراكات التعاون، الحاضنات، ودعم المبادرات الشبابية والنسائية",
                        [
                            ["متغير 3.2.2.1: عدد اتفاقيات الشراكة الرسمية بين الجامعات ومشاغل الصناعات الثقافية.", "عدد"],
                            ["متغير 3.2.2.2: حجم الإنفاق على المشاريع البحثية المشتركة (R&D) بين التعليم العالي والقطاع الإبداعي.", "قيمة مالية / R&D"],
                            ["متغير 3.2.2.3: نسبة رائدات الأعمال وصانعات المحتوى اللاتي يقدن مشاريع إبداعية ناشئة (%).", "%"],
                            ["متغير 3.2.2.4: عدد الحاضنات الجامعية المخصصة لدعم المشاريع الطلابية الناشئة في مجالات الفنون والتقنية.", "عدد"],
                        ],
                    ],
                ],
            ],
        ],
    ],
    [
        "rf",
        "4. البيئة التنظيمية والتشريعية (الحوكمة الرقمية) (وزن 20%)",
        20.0,
        "المحور الرابع | 3 أبعاد أساسية | 6 أبعاد فرعية | 14 متغيراً | وزن المحور: 20%",
        "#1E3A8A",
        "#EEF2FF",
        "#C7D2FE",
        [
            [
                "4.1",
                "حماية حقوق الملكية الفكرية",
                [
                    [
                        "4.1.1",
                        "فاعلية تشريعات حقوق الطبع والنشر للمحتوى المولد آلياً (GenAI)",
                        [
                            ["متغير 4.1.1.1: تسجيل طلبات البراءات وحقوق الملكية الفكرية السارية.", "عدد / سجل"],
                            ["متغير 4.1.1.2: درجة حماية الملكية الفكرية في تقرير التنافسية العالمية الصادر عن المنتدى الاقتصادي العالمي (WEF).", "درجة / WEF"],
                            ["متغير 4.1.1.3: وجود نصوص تشريعية صريحة للملكية المشتركة بين المبدع البشري وأدوات الذكاء الاصطناعي (0/1).", "مؤشر ثنائي (0/1)"],
                            ["متغير 4.1.1.4: وجود أطر قانونية واضحة تحدد المسؤولية (Liability) عن أضرار المحتوى الخوارزمي.", "إطار قانوني"],
                        ],
                    ],
                    [
                        "4.1.2",
                        "آليات إنفاذ قوانين الملكية والتصدي للقرصنة الرقمية",
                        [
                            ["متغير 4.1.2.1: عدد القضايا والنزاعات المتعلقة بالملكية الفكرية الرقمية التي تم الفصل فيها بنجاح قضائياً.", "عدد"],
                            ["متغير 4.1.2.2: نسبة القضايا والمخالفات الرقمية التي تم تتبعها والبت فيها قانونياً بنجاح من إجمالي البلاغات المسجلة سنوياً.", "%"],
                        ],
                    ],
                ],
            ],
            [
                "4.2",
                "أطر الشفافية والإفصاح",
                [
                    [
                        "4.2.1",
                        "اللوائح التنظيمية للتعامل مع منصات البث والشركات التقنية الكبرى",
                        [
                            ["متغير 4.2.1.1: عدد التشريعات الصادرة لإلزام المنصات بالوسم المائي (Watermarking) للمحتوى الآلي.", "عدد"],
                            ["متغير 4.2.1.2: وجود قوانين منع الممارسات الاحتكارية الرقمية (Digital Antitrust) لحماية صناع المحتوى المحلي.", "إطار تشريعي"],
                        ],
                    ],
                    [
                        "4.2.2",
                        "حوكمة البيانات ومواءمتها مع أهداف التنمية المستدامة (SDGs)",
                        [
                            ["متغير 4.2.2.1: وجود قانون وطني سارٍ لحماية بيانات المستهلكين والمبدعين الرقمية.", "قانون وطني"],
                            ["متغير 4.2.2.2: عدد سياسات الذكاء الاصطناعي الوطنية المنسجمة مع أهداف التنمية المستدامة (SDGs).", "عدد"],
                        ],
                    ],
                ],
            ],
            [
                "4.3",
                "أطر التحفيز الضريبي والمؤسسي",
                [
                    [
                        "4.3.1",
                        "الحوافز والسياسات الضريبية الموجهة للصناعات الثقافية",
                        [
                            ["متغير 4.3.1.1: وجود إعفاءات أو تخفيضات ضريبية للمنشآت والمشاريع الناشئة العاملة في الاقتصاد البرتقالي (0/1).", "مؤشر ثنائي (0/1)"],
                            ["متغير 4.3.1.2: قيمة الحزم التحفيزية المالية الموجهة لدعم الإنتاج الثقافي المحلي (بالمليون دولار).", "مليون دولار"],
                        ],
                    ],
                    [
                        "4.3.2",
                        "التنسيق المؤسسي بين قطاعات الثقافة والتقنية والاقتصاد",
                        [
                            ["متغير 4.3.2.1: وجود لجنة وطنية عليا أو منصة تنسيقية مشتركة بين وزارات الثقافة والاتصالات والاقتصاد (0/1).", "مؤشر ثنائي (0/1)"],
                            ["متغير 4.3.2.2: متوسط تقييم خبراء الإدارة والثقافة لفاعلية اللجان والمنصات التنسيقية المشتركة بين وزارات الثقافة والاتصالات.", "متوسط تقييم"],
                        ],
                    ],
                ],
            ],
        ],
    ],
    [
        "cd",
        "5. المحددات الثقافية والهوياتية والأمن الثقافي (وزن 15%)",
        15.0,
        "المحور الخامس | 3 أبعاد أساسية | 6 أبعاد فرعية | 15 متغيراً | وزن المحور: 15%",
        CCI_ORANGE_DARK,
        "#FFF7ED",
        "#FED7AA",
        [
            [
                "5.1",
                "السيادة السردية وحماية المحتوى",
                [
                    [
                        "5.1.1",
                        "حجم الإنتاج الثقافي الرقمي الموطن باللغة العربية والملامح المحلية",
                        [
                            ["متغير 5.1.1.1: نسبة المحتوى الثقافي الرقمي المتاح باللغة العربية على المنصات الرقمية مقارنة باللغات الأخرى.", "%"],
                            ["متغير 5.1.1.2: معدل خلو المخرجات التوليدية من التحيز الثقافي والنمطية الغربية من إجمالي عينة عشوائية تم توليدها واختبارها محلياً.", "معدل / %"],
                        ],
                    ],
                    [
                        "5.1.2",
                        "الوعي المجتمعي والتقبل النقدي للاستهلاك الثقافي الرقمي",
                        [
                            ["متغير 5.1.2.1: نسبة الإنفاق المحلي للأسرة أو الأفراد على اقتناء المنتجات والمحتوى الإبداعي ذي الهوية الوطنية مقارنة بالاستهلاك الأجنبي من بيانات أجهزة الإحصاء الوطنية).", "%"],
                            ["متغير 5.1.2.2: معدل نمو التفاعل الجماهيري مع المنصات والمنتجات الثقافية الرقمية ذات الهوية المحلية (%).", "%"],
                        ],
                    ],
                ],
            ],
            [
                "5.2",
                "رقمنة التراث اللامادي والمادي",
                [
                    [
                        "5.2.1",
                        "الأرشيف الرقمي وقواعد البيانات الوطنية للأصول التراثية",
                        [
                            ["متغير 5.2.1.1: نسبة المواقع التراثية، المتاحف، والمكتوزات الثقافية التي تمت أرشفتها ووضعت في قواعد بيانات (3D/Digital Archives).", "%"],
                            ["متغير 5.2.1.2: عدد القطع التراثية والمخطوطات والمأثورات الشعبية الموثقة رقمياً ومتاحة للجمهور عبر بوابات مفتوحة.", "عدد"],
                        ],
                    ],
                    [
                        "5.2.2",
                        "توظيف التراث الرقمي واستمرارية النسخ الاحتياطي",
                        [
                            ["متغير 5.2.2.1: عدد المبادرات الوطنية المخصصة لتغذية النماذج اللغوية والبصرية بالبيانات التاريخية والثقافية العربية الموثوقة.", "عدد"],
                            ["متغير 5.2.2.2: وجود مراكز وطنية مؤمنة للنسخ الاحتياطي الآلي للأصول الرقمية الثقافية (0/1).", "مؤشر ثنائي (0/1)"],
                        ],
                    ],
                ],
            ],
            [
                "5.3",
                "الدبلوماسية الثقافية والقوة الناعمة",
                [
                    [
                        "5.3.1",
                        "الترويج الدولي للمنتج الثقافي الإبداعي عبر المنصات الرقمية",
                        [
                            ["متغير 5.3.1.1: عدد المعارض والمهرجانات الثقافية الافتراضية الدولية المنظمة للترويج للهوية الثقافية سنوياً.", "عدد"],
                            ["متغير 5.3.1.2: عدد طلبات الحماية الدولية المودعة من قِبل المبدعين والشركات الوطنية عبر نظام مدريد للعلامات وتصاميم لاهاي.", "عدد"],
                            ["متغير 5.3.1.3: عدد الزيارات/ التفاعلات الدولية (بالمليون) على المنصات الإبداعية الوطنية الرسمية عبر شبكة الإنترنت.", "مليون زيارة/تفاعل"],
                        ],
                    ],
                    [
                        "5.3.2",
                        "الشراكات الثقافية العابرة للحدود وتبادل الخبرات المبتكرة",
                        [
                            ["متغير 5.3.2.1: عدد الاتفاقيات والشراكات الدولية المبرمة بين المؤسسات الثقافية الوطنية والمراكز العالمية للإبداع الرقمي.", "عدد"],
                            ["متغير 5.3.2.2: حجم المشاركات العربية في المؤتمرات والفعاليات الدولية المعنية بمستقبل الفنون والذكاء الاصطناعي.", "حجم المشاركات"],
                        ],
                    ],
                ],
            ],
        ],
    ],
]

# ------------------------------------------------------------------------------
# تنسيق الشريط العلوي (التبويبات): بعرض الشاشة ومتجاوب 100% بين اللابتوب والموبايل
# ------------------------------------------------------------------------------
TABS_RULES = f"""
/* ---- تمدد حاوية التبويبات بعرض الشاشة كاملاً ---- */
div[data-testid="stTabs"],
div.stTabs {{
    width: 100% !important;
    max-width: 100% !important;
    min-width: 100% !important;
    direction: rtl !important;
    border: none !important;
    margin: 0 !important;
    padding: 0 !important;
}}

div[data-testid="stTabs"] > div,
div[data-testid="stTabs"] [data-baseweb="tabs"],
div.stTabs [data-baseweb="tabs"] {{
    width: 100% !important;
    max-width: 100% !important;
}}

/* ---- إخفاء الخط السفلي لـ BaseWeb نهائياً ---- */
div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
div[data-testid="stTabs"] [data-baseweb="tab-border"] {{
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    opacity: 0 !important;
    background-color: transparent !important;
}}

/* ---- التنسيق الأساسي لشريط التبويبات المتناسق مع الخلفية ---- */
html body div[data-testid="stTabs"] [data-baseweb="tab-list"],
html body [role="tablist"] {{
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: stretch !important;
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    gap: 6px !important;
    padding: 8px !important;
    margin: 0 0 16px 0 !important;
    background: linear-gradient(135deg, {CCI_NAVY} 0%, {CCI_ORANGE_DARK} 100%) !important;
    border: 2px solid {CCI_GOLD_BRIGHT} !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 25px rgba(10, 25, 47, 0.22) !important;
    direction: rtl !important;
}}

/* الحاوية الداخلية إن وجدت في بعض إصدارات Streamlit */
div[data-testid="stTabs"] [data-baseweb="tab-list"] > div,
div[data-testid="stTabs"] [data-baseweb="tab-list"] [role="tablist"] {{
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 6px !important;
    padding: 0 !important;
    margin: 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    direction: rtl !important;
}}

/* ---- شاشات اللابتوب والكمبيوتر (> 768px): توزيع متساوٍ بعرض الشاشة الكامل ---- */
@media (min-width: 769px) {{
    html body div[data-testid="stTabs"] [data-baseweb="tab-list"],
    html body [role="tablist"] {{
        justify-content: space-between !important;
        overflow: visible !important;
    }}

    div[data-testid="stTabs"] [data-baseweb="tab-list"] > div,
    div[data-testid="stTabs"] [data-baseweb="tab-list"] [role="tablist"] {{
        flex: 1 1 100% !important;
        width: 100% !important;
    }}

    html body div[data-testid="stTabs"] button[role="tab"],
    html body div[data-testid="stTabs"] button[baseweb="tab"],
    html body [role="tablist"] [role="tab"] {{
        flex: 1 1 0% !important;
        min-width: 0 !important;
        width: 100% !important;
        max-width: none !important;
        height: auto !important;
        min-height: 48px !important;
        margin: 0 !important;
        padding: 8px 6px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border: 1.5px solid rgba(251, 191, 36, 0.45) !important;
        border-radius: 8px !important;
        font-family: {APP_FONT} !important;
        font-weight: 700 !important;
        font-size: 12px !important;
        line-height: 1.35 !important;
        text-align: center !important;
        white-space: normal !important;
        outline: none !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }}

    html body div[data-testid="stTabs"] button[role="tab"] *,
    html body [role="tablist"] [role="tab"] * {{
        white-space: normal !important;
    }}
}}

/* ---- شاشات الموبايل والتابلت الصغير (<= 768px): تمرير أفقي واضح بلا تقطيع ---- */
@media (max-width: 768px) {{
    html body div[data-testid="stTabs"] [data-baseweb="tab-list"],
    html body [role="tablist"] {{
        overflow-x: auto !important;
        overflow-y: hidden !important;
        justify-content: flex-start !important;
        padding: 8px !important;
        gap: 8px !important;
        -webkit-overflow-scrolling: touch !important;
        scrollbar-width: thin !important;
        scrollbar-color: {CCI_GOLD_BRIGHT} {CCI_NAVY} !important;
    }}

    html body div[data-testid="stTabs"] [data-baseweb="tab-list"]::-webkit-scrollbar,
    html body [role="tablist"]::-webkit-scrollbar {{
        height: 4px !important;
    }}
    html body div[data-testid="stTabs"] [data-baseweb="tab-list"]::-webkit-scrollbar-track,
    html body [role="tablist"]::-webkit-scrollbar-track {{
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 4px !important;
    }}
    html body div[data-testid="stTabs"] [data-baseweb="tab-list"]::-webkit-scrollbar-thumb,
    html body [role="tablist"]::-webkit-scrollbar-thumb {{
        background: {CCI_GOLD_BRIGHT} !important;
        border-radius: 4px !important;
    }}

    div[data-testid="stTabs"] [data-baseweb="tab-list"] > div,
    div[data-testid="stTabs"] [data-baseweb="tab-list"] [role="tablist"] {{
        flex: 0 0 auto !important;
        width: max-content !important;
        gap: 8px !important;
    }}

    html body div[data-testid="stTabs"] button[role="tab"],
    html body div[data-testid="stTabs"] button[baseweb="tab"],
    html body [role="tablist"] [role="tab"] {{
        flex: 0 0 auto !important;
        min-width: max-content !important;
        width: auto !important;
        max-width: none !important;
        height: auto !important;
        min-height: 42px !important;
        margin: 0 !important;
        padding: 8px 14px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        border: 1.5px solid rgba(251, 191, 36, 0.55) !important;
        border-radius: 8px !important;
        font-family: {APP_FONT} !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        line-height: 1.4 !important;
        text-align: center !important;
        white-space: nowrap !important;
        outline: none !important;
        box-shadow: none !important;
    }}

    html body div[data-testid="stTabs"] button[role="tab"] *,
    html body [role="tablist"] [role="tab"] * {{
        white-space: nowrap !important;
        display: inline !important;
    }}

    /* إخفاء زر السهم الجانبي التلقائي لـ BaseWeb الذي يغطي التبويبات في الموبايل */
    div[data-testid="stTabs"] button[aria-label*="scroll"],
    div[data-testid="stTabs"] [data-baseweb="tab-list"] ~ button {{
        display: none !important;
    }}
}}

/* ---- تنسيق النصوص والأيقونات داخل التبويبات ---- */
div[data-testid="stTabs"] button[role="tab"] *,
html body [role="tablist"] [role="tab"] * {{
    font-family: {APP_FONT} !important;
    font-size: inherit !important;
    line-height: inherit !important;
    text-align: center !important;
    margin: 0 !important;
}}
"""

TABS_COLOR_RULES = f"""
/* الوضع العادي: خلفية داكنة متسقة مع نص ذهبي مشرق واضح */
html body [data-baseweb="tab-list"] button[role="tab"],
html body [data-baseweb="tab-list"] button[role="tab"] *,
html body [role="tablist"] [role="tab"],
html body [role="tablist"] [role="tab"] * {{
    color: {CCI_GOLD_BRIGHT} !important;
    -webkit-text-fill-color: {CCI_GOLD_BRIGHT} !important;
    opacity: 1 !important;
}}

html body [data-baseweb="tab-list"] button[role="tab"],
html body [role="tablist"] [role="tab"] {{
    background: linear-gradient(135deg, {CCI_NAVY} 0%, {CCI_ORANGE_DARK} 100%) !important;
}}

html body [data-baseweb="tab-list"] button[role="tab"] *,
html body [role="tablist"] [role="tab"] * {{
    background: transparent !important;
}}

/* عند المرور أو الضغط أو التركيز أو التحديد: لون أبيض واضح مع خلفية بارزة */
html body [data-baseweb="tab-list"] button[role="tab"]:is(:hover, :active, :focus-visible, [aria-selected="true"]),
html body [data-baseweb="tab-list"] button[role="tab"]:is(:hover, :active, :focus-visible, [aria-selected="true"]) *,
html body [role="tablist"] [role="tab"]:is(:hover, :active, :focus-visible, [aria-selected="true"]),
html body [role="tablist"] [role="tab"]:is(:hover, :active, :focus-visible, [aria-selected="true"]) * {{
    color: {CCI_WHITE_ACTIVE} !important;
    -webkit-text-fill-color: {CCI_WHITE_ACTIVE} !important;
}}

html body [data-baseweb="tab-list"] button[role="tab"]:hover,
html body [role="tablist"] [role="tab"]:hover {{
    background: linear-gradient(135deg, {CCI_NAVY_HOVER} 0%, {CCI_ORANGE_MID} 100%) !important;
    border-color: {CCI_GOLD_BRIGHT} !important;
}}

html body [data-baseweb="tab-list"] button[role="tab"][aria-selected="true"],
html body [role="tablist"] [role="tab"][aria-selected="true"] {{
    background: linear-gradient(135deg, {CCI_ORANGE_MID} 0%, {CCI_ORANGE_LIGHT} 100%) !important;
    font-weight: 800 !important;
    border: 2px solid {CCI_GOLD_BRIGHT} !important;
    box-shadow: 0 4px 15px rgba(180, 83, 9, 0.45) !important;
}}
"""

TABS_RULES = TABS_RULES + TABS_COLOR_RULES
TABS_CSS = f"<style id='cci-tabs-{UI_CSS_VERSION}'>{TABS_RULES}</style>"

TABS_GUARD_JS = """
(function () {
  var W = window;
  var P = window;   // السكربت يعمل أصلاً داخل الصفحة الأم
  if (W.__cciTabsObserver) { try { W.__cciTabsObserver.disconnect(); } catch (e) {} }
  var BASE_BG = '%BASE_BG%';
  var HOVER_BG = '%HOVER%';
  var ACTIVE_BG = '%ACTIVE_BG%';
  var GOLD = '%GOLD%';
  var WHITE = '%WHITE%';
  var SEL = '[role="tablist"] [role="tab"]';

  /* ضمان تحميل خط Cairo و Tajawal في الصفحة الأم لمنع أي خط غير مفهوم */
  try {
    if (!P.document.getElementById('cci-google-font-cairo')) {
      var fontLink = P.document.createElement('link');
      fontLink.id = 'cci-google-font-cairo';
      fontLink.rel = 'stylesheet';
      fontLink.href = 'https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Tajawal:wght@400;500;700;800&display=swap';
      P.document.head.appendChild(fontLink);
    }
  } catch (e) {}

  /* صوت نقرة خفيف وناعم جداً ("تك" خفيفة) عند الضغط على أي مفتاح أو عنصر تفاعلي */
  function playSoftTickSound() {
    try {
      var AudioCtx = P.AudioContext || P.webkitAudioContext || W.AudioContext || W.webkitAudioContext;
      if (!AudioCtx) return;
      if (!P.__cciAudioCtx) {
        P.__cciAudioCtx = new AudioCtx();
      }
      var ctx = P.__cciAudioCtx;
      if (ctx.state === 'suspended') {
        ctx.resume().catch(function () {});
      }
      var now = ctx.currentTime;
      var osc = ctx.createOscillator();
      var gain = ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(680, now);
      osc.frequency.exponentialRampToValueAtTime(220, now + 0.025);

      gain.gain.setValueAtTime(0.0008, now);
      gain.gain.linearRampToValueAtTime(0.022, now + 0.004);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.028);

      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now);
      osc.stop(now + 0.032);
    } catch (e) {}
  }

  if (!P.__cciSoftSoundAttached) {
    P.__cciSoftSoundAttached = true;
    P.document.addEventListener('pointerdown', function (ev) {
      var target = ev.target && ev.target.closest ? ev.target.closest('button, [role="tab"], [data-cci-tab], summary, a, input[type="checkbox"], input[type="radio"]') : null;
      if (target) {
        playSoftTickSound();
      }
    }, { passive: true });
    P.document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Enter' || ev.key === ' ') {
        playSoftTickSound();
      }
    }, { passive: true });
  }

  function setColor(el, c) {
    el.style.setProperty('color', c, 'important');
    el.style.setProperty('-webkit-text-fill-color', c, 'important');
  }

  function paint(btn, hot) {
    var sel = btn.getAttribute('aria-selected') === 'true';
    var c = (sel || hot) ? WHITE : GOLD;
    setColor(btn, c);
    if (sel) {
      btn.style.setProperty('background', ACTIVE_BG, 'important');
    } else if (hot) {
      btn.style.setProperty('background', HOVER_BG, 'important');
    } else {
      btn.style.setProperty('background', BASE_BG, 'important');
    }
    btn.querySelectorAll('*').forEach(function (n) { setColor(n, c); });
  }

  function saveActiveTabToUrl(idx) {
    try {
      var u = new URL(P.location.href);
      u.searchParams.set('tab', String(idx));
      P.history.replaceState({}, '', u.toString());
    } catch (e) {}
  }

  function triggerNativeTabClick(tabEl) {
    if (!tabEl) return;
    tabEl.focus();
    tabEl.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true, view: P }));
    tabEl.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true, view: P }));
    tabEl.click();
  }

  function goToTab(idx, shouldScroll) {
    var tabs = P.document.querySelectorAll(SEL);
    if (tabs && idx >= 0 && idx < tabs.length && tabs[idx]) {
      triggerNativeTabClick(tabs[idx]);
      saveActiveTabToUrl(idx);
      setTimeout(run, 30);
      setTimeout(run, 120);
      if (P.innerWidth <= 768) {
        try { tabs[idx].scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' }); } catch (e) {}
      }
      if (shouldScroll) {
        var tabList = P.document.querySelector('[role="tablist"]');
        if (tabList) {
          try { tabList.scrollIntoView({ behavior: 'smooth', block: 'start' }); } catch (e) {}
        }
      }
    }
  }

  function restoreTabFromUrl() {
    if (P.__cciTabRestored) return;
    try {
      var u = new URL(P.location.href);
      var t = u.searchParams.get('tab');
      if (t !== null && t !== '0') {
        var idx = parseInt(t, 10);
        var tabs = P.document.querySelectorAll(SEL);
        if (!isNaN(idx) && tabs && tabs[idx]) {
          P.__cciTabRestored = true;
          triggerNativeTabClick(tabs[idx]);
          setTimeout(run, 40);
        }
      } else {
        P.__cciTabRestored = true;
      }
    } catch (e) {}
  }

  /* مستمع واحد مفوَّض: لا يتأثر بإعادة رسم Streamlit ولا يحتاج ربطاً لكل بطاقة */
  function cardToIndex(card) {
    var idx = parseInt(card.getAttribute('data-cci-tab'), 10);
    if (!isNaN(idx)) return idx;
    var all = Array.prototype.slice.call(P.document.querySelectorAll('.home-section-card'));
    var pos = all.indexOf(card);
    return pos >= 0 ? pos + 1 : -1;     // احتياط: ترتيب البطاقة إن حُذفت سمة data
  }
  function findCard(ev) {
    return ev.target && ev.target.closest ? ev.target.closest('.home-section-card') : null;
  }
  if (P.__cciCardClick) P.document.removeEventListener('click', P.__cciCardClick, true);
  if (P.__cciCardKey)   P.document.removeEventListener('keydown', P.__cciCardKey, true);

  P.__cciCardClick = function (ev) {
    var card = findCard(ev);
    if (!card) return;
    ev.preventDefault();
    var idx = cardToIndex(card);
    if (idx >= 0) goToTab(idx, true);
  };
  P.__cciCardKey = function (ev) {
    if (ev.key !== 'Enter' && ev.key !== ' ') return;
    var card = findCard(ev);
    if (!card) return;
    ev.preventDefault();
    var idx = cardToIndex(card);
    if (idx >= 0) goToTab(idx, true);
  };
  P.document.addEventListener('click', P.__cciCardClick, true);
  P.document.addEventListener('keydown', P.__cciCardKey, true);

  function run() {
    P.document.querySelectorAll('[data-baseweb="tab-highlight"], [data-baseweb="tab-border"]')
      .forEach(function (el) { el.style.setProperty('display', 'none', 'important'); });

    P.document.querySelectorAll(SEL).forEach(function (b, idx) {
      b.setAttribute('data-tab-index', String(idx));
      paint(b, b.matches(':hover'));
      if (!b.__cciBound) {
        b.__cciBound = 1;
        b.addEventListener('pointerenter', function () { paint(b, true); });
        b.addEventListener('pointerleave', function () { paint(b, false); });
        b.addEventListener('pointerdown',  function () { paint(b, true); });
        b.addEventListener('pointerup',    function () { paint(b, false); });
        b.addEventListener('click', function () {
          saveActiveTabToUrl(idx);
          setTimeout(run, 0);
          if (P.innerWidth <= 768) {
            try { b.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' }); } catch (e) {}
          }
        });
      }
    });
  }

  var queued = false;
  function schedule() {
    if (queued) return;
    queued = true;
    P.requestAnimationFrame(function () { queued = false; run(); });
  }

  run();
  setTimeout(function () { restoreTabFromUrl(); run(); }, 120);
  setTimeout(run, 400);
  setTimeout(run, 900);

  W.__cciTabsObserver = new MutationObserver(schedule);
  W.__cciTabsObserver.observe(P.document.body, {
    childList: true, subtree: true,
    attributes: true, attributeFilter: ['aria-selected']
  });
})();
"""


def inject_tabs_css():
    """يحقن CSS والسكربت في الصفحة الأم ليبقيا فعّالين بعد كل إعادة تشغيل."""
    st.markdown(TABS_CSS, unsafe_allow_html=True)

    guard_js = (
        TABS_GUARD_JS
        .replace("%BASE_BG%", f"linear-gradient(135deg, {CCI_NAVY} 0%, {CCI_ORANGE_DARK} 100%)")
        .replace("%HOVER%", f"linear-gradient(135deg, {CCI_NAVY_HOVER} 0%, {CCI_ORANGE_MID} 100%)")
        .replace("%ACTIVE_BG%", f"linear-gradient(135deg, {CCI_ORANGE_MID} 0%, {CCI_ORANGE_LIGHT} 100%)")
        .replace("%GOLD%", CCI_GOLD_BRIGHT)
        .replace("%WHITE%", CCI_WHITE_ACTIVE)
    )

    components.html(
        f"""
        <head>
          <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Tajawal:wght@400;500;700;800&display=swap">
        </head>
        <script>
        (function() {{
            var doc = window.parent.document;

            doc.querySelectorAll('style[id^="cci-tabs-css-"], script[id^="cci-tabs-guard-"], style[id^="cci-tabs-"]')
               .forEach(function (n) {{ n.remove(); }});

            var st = doc.createElement('style');
            st.id = 'cci-tabs-css-{UI_CSS_VERSION}';
            st.textContent = {json.dumps(TABS_RULES)};
            doc.head.appendChild(st);

            var sc = doc.createElement('script');
            sc.id = 'cci-tabs-guard-{UI_CSS_VERSION}';
            sc.textContent = {json.dumps(guard_js)};
            doc.head.appendChild(sc);
        }})();
        </script>
        """,
        height=0,
        width=0,
    )


def sync_session_browser_backup():
    """حفظ نسخة احتياطية من حالة الجلسة في localStorage بالمتصفح لدعم الثبات عند التحديث."""
    backup_payload = json.dumps({
        "history_state": st.session_state.get("history_state", []),
        "simulated_results": {
            k: {
                "country": v.get("country"),
                "simulated_val": v.get("simulated_val"),
                "delta": v.get("delta"),
                "scenario": v.get("scenario"),
                "analysis_text": v.get("analysis_text"),
                "action_plan": v.get("action_plan"),
            }
            for k, v in st.session_state.get("simulated_results_dict", {}).items()
        },
        "decision_results": st.session_state.get("decision_results_dict", {}),
    }, ensure_ascii=False)

    components.html(
        f"""
        <script>
        (function() {{
            try {{
                var data = {backup_payload};
                window.parent.localStorage.setItem('cci_platform_state_v1', JSON.stringify(data));
            }} catch (e) {{}}
        }})();
        </script>
        """,
        height=0,
        width=0,
    )


CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Tajawal:wght@400;500;700;800&family=Readex+Pro:wght@300;400;500;600;700&display=swap');

/* إخفاء شريط أدوات Streamlit العلوي وأي هامش علوي زائد */
header,
.stAppToolbar,
div[data-testid="stHeader"],
div[data-testid="stDecoration"] {{
    visibility: hidden !important;
    display: none !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}}

/* إخفاء إطارات السكربت المخفية دون إيقاف تنفيذ JavaScript */
iframe[height="0"] {{
    position: absolute !important;
    width: 0 !important;
    height: 0 !important;
    border: 0 !important;
    opacity: 0 !important;
    pointer-events: none !important;
    margin: 0 !important;
    padding: 0 !important;
}}

html, body, [class*="css"] {{
    font-family: {APP_FONT} !important;
    direction: rtl !important;
    text-align: right !important;
    background-color: {CCI_BG} !important;
    margin-top: 0 !important;
    padding-top: 0 !important;
    text-rendering: optimizeLegibility !important;
    -webkit-font-smoothing: antialiased !important;
}}

.stApp p, .stApp label, .stApp li, .stApp td, .stApp th, .stApp h1, .stApp h2, .stApp h3,
.stApp h4, .stApp h5, .stApp h6, .stApp input, .stApp textarea, .stApp select,
.stApp button, .stApp a, .stApp div[data-baseweb] {{
    font-family: {APP_FONT} !important;
}}

.stApp {{
    background-color: {CCI_BG} !important;
    direction: rtl !important;
    text-align: right !important;
    overflow-x: hidden !important;
}}

[data-testid="stAppViewContainer"],
section[data-testid="stMain"],
.main {{
    padding-top: 0 !important;
    margin-top: 0 !important;
}}

.block-container,
[data-testid="stMainBlockContainer"],
[data-testid="stAppViewBlockContainer"] {{
    width: 100% !important;
    max-width: 100% !important;
    padding-top: 0.45rem !important;
    padding-bottom: 1.5rem !important;
    padding-left: 1.25rem !important;
    padding-right: 1.25rem !important;
    margin-top: 0 !important;
}}

div.stMarkdown, div.stText, div.stSelectbox, div.stSlider, div.stDataFrame, div.stTable {{
    direction: rtl !important;
    text-align: right !important;
}}

/* فرض محاذاة اليمين على كافة عناصر القوائم المنسدلة والقوائم المنبثقة */
div[data-baseweb="select"] *,
div[data-baseweb="popover"] *,
ul[data-baseweb="menu"] *,
div[role="listbox"] *,
div[role="option"] {{
    direction: rtl !important;
    text-align: right !important;
}}

/* بطاقات التبويب الرئيسي */
.home-hero-card {{
    background: linear-gradient(135deg, #FFFFFF 0%, #FFFBEB 100%) !important;
    padding: clamp(20px, 3.5vw, 30px) !important;
    border-radius: 14px !important;
    border: 1.5px solid #E2E8F0 !important;
    border-right: 6px solid {CCI_ORANGE_MID} !important;
    box-shadow: 0 6px 20px rgba(10, 25, 47, 0.06) !important;
    margin-bottom: 22px !important;
}}

.home-section-card {{
    background: #FFFFFF !important;
    padding: 20px !important;
    border-radius: 12px !important;
    border: 1.5px solid #E2E8F0 !important;
    border-top: 4px solid {CCI_NAVY} !important;
    border-right: 4px solid {CCI_ORANGE_MID} !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04) !important;
    height: 100% !important;
    margin-bottom: 16px !important;
    cursor: pointer !important;
    user-select: none !important;
    transition: all 0.22s ease !important;
}}

.home-section-card:hover {{
    background: linear-gradient(135deg, {CCI_NAVY} 0%, {CCI_ORANGE_DARK} 100%) !important;
    border-color: {CCI_GOLD_BRIGHT} !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 10px 24px rgba(10, 25, 47, 0.22) !important;
}}

.home-section-card:active {{
    transform: scale(0.985) !important;
}}

.home-section-card h4 {{
    color: {CCI_NAVY} !important;
    font-weight: 800 !important;
    margin-top: 0 !important;
    margin-bottom: 10px !important;
    transition: color 0.2s ease !important;
}}

.home-section-card p {{
    color: #334155 !important;
    font-size: 13.8px !important;
    line-height: 1.75 !important;
    margin: 0 0 12px 0 !important;
    transition: color 0.2s ease !important;
}}

.home-section-cta {{
    display: inline-block !important;
    background: #FEF3C7 !important;
    color: {CCI_NAVY} !important;
    border: 1px solid {CCI_ORANGE_MID} !important;
    border-radius: 50px !important;
    padding: 4px 12px !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    transition: all 0.2s ease !important;
}}

.home-section-card:hover h4 {{
    color: {CCI_GOLD_BRIGHT} !important;
}}

.home-section-card:hover p {{
    color: #F8FAFC !important;
}}

.home-section-card:hover .home-section-cta {{
    background: {CCI_GOLD_BRIGHT} !important;
    color: {CCI_NAVY} !important;
    border-color: #FFFFFF !important;
}}

.home-kpi-box {{
    background: linear-gradient(135deg, {CCI_NAVY} 0%, {CCI_ORANGE_DARK} 100%) !important;
    color: #FFFFFF !important;
    padding: 16px 18px !important;
    border-radius: 12px !important;
    border: 1.5px solid {CCI_GOLD_BRIGHT} !important;
    text-align: center !important;
    box-shadow: 0 4px 14px rgba(10, 25, 47, 0.14) !important;
}}

.home-kpi-val {{
    font-size: 24px !important;
    font-weight: 800 !important;
    color: {CCI_GOLD_BRIGHT} !important;
    line-height: 1.3 !important;
}}

.home-kpi-lbl {{
    font-size: 13px !important;
    color: #F8FAFC !important;
    margin-top: 4px !important;
}}

/* تنسيق القوائم المنسدلة الهرمية للمحاور والأبعاد الأساسية والفرعية والمتغيرات */
.aacri-axis-block {{
    background: #FFFFFF;
    border: 1.5px solid #E2E8F0;
    border-radius: 14px;
    padding: 16px 18px;
    margin: 12px 0 18px 0;
    box-shadow: 0 3px 12px rgba(10, 25, 47, 0.04);
    direction: rtl;
    text-align: right;
}}
.aacri-axis-header {{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding-bottom: 10px;
    margin-bottom: 12px;
    border-bottom: 2px solid {CCI_GOLD_BRIGHT};
}}
.aacri-axis-title {{
    font-size: 16.5px;
    font-weight: 800;
    color: {CCI_NAVY};
}}
.aacri-axis-pill {{
    font-size: 12.5px;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 20px;
}}
details.aacri-dim-dropdown {{
    border: 1.5px solid #E2E8F0;
    border-radius: 10px;
    margin-bottom: 10px;
    background: #FFFFFF;
    overflow: hidden;
    transition: all 0.2s ease;
}}
details.aacri-dim-dropdown[open] {{
    border-color: {CCI_ORANGE_MID};
    box-shadow: 0 4px 14px rgba(10, 25, 47, 0.08);
}}
details.aacri-dim-dropdown > summary {{
    list-style: none;
    cursor: pointer;
    padding: 11px 15px;
    background: #F8FAFC;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    font-weight: 800;
    font-size: 14.5px;
    color: {CCI_NAVY};
    user-select: none;
    transition: background 0.2s ease, color 0.2s ease;
}}
details.aacri-dim-dropdown > summary::-webkit-details-marker {{
    display: none;
}}
details.aacri-dim-dropdown > summary:hover {{
    background: {CCI_NAVY};
    color: #FFFFFF;
}}
details.aacri-dim-dropdown[open] > summary {{
    background: linear-gradient(135deg, {CCI_NAVY} 0%, {CCI_ORANGE_DARK} 100%);
    color: {CCI_GOLD_BRIGHT};
    border-bottom: 2px solid {CCI_GOLD_BRIGHT};
}}
.aacri-dim-summary-right {{
    display: flex;
    align-items: center;
    gap: 9px;
}}
.aacri-dim-num {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 34px;
    height: 26px;
    border-radius: 14px;
    background: {CCI_GOLD_BRIGHT};
    color: {CCI_NAVY};
    font-size: 13px;
    font-weight: 900;
    padding: 0 8px;
}}
.aacri-dim-meta {{
    display: inline-flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    font-size: 12.5px;
    font-weight: 700;
    opacity: 0.95;
}}
.aacri-dim-weight-badge {{
    background: rgba(251, 191, 36, 0.22);
    border: 1px solid {CCI_GOLD_BRIGHT};
    border-radius: 14px;
    padding: 2px 10px;
    font-size: 12px;
    font-weight: 800;
}}
.aacri-dim-chevron {{
    display: inline-block;
    transition: transform 0.2s ease;
    font-size: 12px;
}}
details.aacri-dim-dropdown[open] .aacri-dim-chevron {{
    transform: rotate(180deg);
}}
.aacri-dim-body {{
    padding: 14px 16px;
    background: #FFFFFF;
    display: flex;
    flex-direction: column;
    gap: 12px;
}}
.aacri-sub-card {{
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-right: 4px solid {CCI_ORANGE_MID};
    border-radius: 9px;
    padding: 11px 14px;
}}
.aacri-sub-title-row {{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 8px;
    padding-bottom: 6px;
    border-bottom: 1px dashed #CBD5E1;
}}
.aacri-sub-title-left {{
    display: flex;
    align-items: center;
    gap: 8px;
}}
.aacri-sub-code-badge {{
    background: {CCI_NAVY};
    color: {CCI_GOLD_BRIGHT};
    font-size: 12px;
    font-weight: 800;
    padding: 2px 9px;
    border-radius: 16px;
    direction: ltr;
}}
.aacri-sub-name {{
    font-size: 14px;
    font-weight: 800;
    color: {CCI_NAVY};
}}
.aacri-sub-weight-pill {{
    background: #FFFFFF;
    color: #475569;
    border: 1px solid #CBD5E1;
    border-radius: 14px;
    padding: 2px 10px;
    font-size: 12px;
    font-weight: 700;
}}
.aacri-var-item {{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 7px;
    padding: 7px 11px;
    margin-top: 6px;
    font-size: 13.5px;
}}
.aacri-var-label {{
    color: #1E293B;
    font-weight: 600;
    flex: 1 1 320px;
}}
.aacri-var-badges {{
    display: inline-flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
}}
.aacri-unit-tag {{
    background: #EFF6FF;
    color: {CCI_NAVY};
    border: 1px solid #BFDBFE;
    border-radius: 16px;
    padding: 2px 10px;
    font-size: 11.5px;
    font-weight: 700;
    white-space: nowrap;
}}
.aacri-weight-tag {{
    background: #FFFBEB;
    color: #92400E;
    border: 1px solid #FDE68A;
    border-radius: 16px;
    padding: 2px 10px;
    font-size: 11.5px;
    font-weight: 700;
    white-space: nowrap;
}}

/* تصميم جدول RTL مخصص ومصغر ومريح بصرياً */
.custom-rtl-table {{
    width: 100% !important;
    border-collapse: collapse !important;
    direction: rtl !important;
    text-align: right !important;
    margin-top: 8px !important;
    margin-bottom: 12px !important;
    font-family: {APP_FONT} !important;
    background-color: #FFFFFF !important;
    border-radius: 6px !important;
    overflow: hidden !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
    border: 1px solid #CBD5E1 !important;
}}

.custom-rtl-table th {{
    background: linear-gradient(135deg, #334155 100%, #1E293B 100%) !important;
    color: #F8FAFC !important;
    padding: 8px 6px !important;
    font-weight: 700 !important;
    border: 1px solid #475569 !important;
    text-align: right !important;
    font-size: 12px !important;
    white-space: nowrap !important;
}}

.custom-rtl-table td {{
    padding: 6px 6px !important;
    border: 1px solid #E2E8F0 !important;
    color: #1E293B !important;
    font-size: 11.5px !important;
    text-align: right !important;
    line-height: 1.3 !important;
}}

.custom-rtl-table tr:nth-child(even) {{
    background-color: #F8FAFC !important;
}}

.custom-rtl-table tr:hover {{
    background-color: #FEF3C7 !important;
}}

.stButton > button,
.stDownloadButton > button {{
    width: 100% !important;
    border-radius: 50px !important;
    font-family: {APP_FONT} !important;
    font-weight: 700 !important;
}}

.header-center {{
    text-align: center !important;
    background: linear-gradient(135deg, rgba(10, 25, 47, 0.95) 0%, rgba(120, 53, 15, 0.90) 100%),
                url('https://images.unsplash.com/photo-1461360370896-922624d12aa1?q=80&w=1600&auto=format&fit=crop') !important;
    background-size: cover !important;
    background-position: center !important;
    color: #FFFFFF !important;
    padding: clamp(20px, 3.5vw, 34px) clamp(12px, 3vw, 20px) !important;
    border-radius: 16px !important;
    border-bottom: 5px solid {CCI_ORANGE_MID} !important;
    box-shadow: 0 12px 35px rgba(0,0,0,0.35) !important;
    margin-bottom: 16px !important;
    direction: rtl !important;
}}

.header-center h1 {{
    color: #FBBF24 !important;
    font-size: clamp(19px, 4.5vw, 26px) !important;
    font-weight: 800 !important;
    margin-bottom: 10px !important;
    line-height: 1.45 !important;
    text-shadow: 0 2px 6px rgba(0,0,0,0.7) !important;
}}

.header-center h3 {{
    color: #F1F5F9 !important;
    font-size: clamp(13px, 3.2vw, 15px) !important;
    font-weight: 500 !important;
    line-height: 1.6 !important;
    margin-bottom: 0px !important;
}}

.ticker-wrap {{
    width: 100%;
    background: linear-gradient(90deg, {CCI_NAVY} 0%, {CCI_ORANGE_DARK} 100%);
    border-top: 2px solid {CCI_ORANGE_MID};
    border-bottom: 2px solid {CCI_ORANGE_MID};
    overflow: hidden;
    white-space: nowrap;
    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    margin-bottom: 18px;
    border-radius: 8px;
    direction: ltr !important;
}}

.ticker {{
    display: inline-block;
    padding-right: 100%;
    animation: marquee-infinite 55s linear infinite;
}}

.ticker-item {{
    display: inline-block;
    padding: 8px 30px;
    font-size: 14.5px;
    font-weight: bold;
    color: #FFFFFF !important;
    direction: rtl !important;
}}

@keyframes marquee-infinite {{
    0% {{ transform: translate(-100%, 0); }}
    100% {{ transform: translate(100%, 0); }}
}}

.footer-copyright {{
    text-align: center;
    color: #64748B;
    font-size: 13px;
    margin-top: 40px;
    border-top: 1px solid #E2E8F0;
    padding-top: 15px;
    font-weight: bold;
    direction: rtl !important;
}}

{TABS_RULES}

@media (max-width: 768px) {{
    .block-container,
    [data-testid="stMainBlockContainer"],
    [data-testid="stAppViewBlockContainer"] {{
        padding-top: 0.4rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }}

    .stButton > button,
    .stDownloadButton > button {{
        min-height: 44px !important;
        font-size: 13.5px !important;
        white-space: normal !important;
        line-height: 1.4 !important;
    }}

    input, textarea, select {{
        font-size: 16px !important;
    }}

    [data-testid="stDataFrame"], .js-plotly-plot {{
        max-width: 100% !important;
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
    }}

    .custom-rtl-table {{
        min-width: 560px !important;
    }}

    .ticker-item {{
        font-size: 12.5px !important;
        padding: 6px 18px !important;
    }}
}}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

EXTRA_CSS = f"""
<style>
/* حاويات السكربتات الصفرية لا تترك فراغاً بين العناصر */
.element-container:has(> iframe[height="0"]),
div[data-testid="stElementContainer"]:has(> iframe[height="0"]) {{
    position: absolute !important; width: 0 !important; height: 0 !important;
    margin: 0 !important; overflow: hidden !important;
}}

.score-chip {{
    display: inline-block; padding: 2px 11px; border-radius: 14px;
    font-weight: 800; font-size: 12.5px; white-space: nowrap;
}}
.score-chip.big {{ font-size: 14px; padding: 5px 16px; }}

.aacri-result-head {{
    display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between;
    gap: 10px; padding-bottom: 10px; margin-bottom: 6px; border-bottom: 2px solid {CCI_GOLD_BRIGHT};
}}
.aacri-result-kicker {{ font-size: 12.5px; color: #64748B; font-weight: 700; }}
.aacri-result-country {{ font-size: 21px; font-weight: 800; color: {CCI_NAVY}; }}

.aacri-bar-row {{ margin: 9px 0; direction: rtl; }}
.aacri-bar-head {{
    display: flex; justify-content: space-between; gap: 8px;
    font-size: 13px; font-weight: 700; color: #1E293B; margin-bottom: 4px;
}}
.aacri-bar-track {{ height: 10px; background: #E2E8F0; border-radius: 8px; overflow: hidden; }}
.aacri-bar-fill {{ height: 100%; border-radius: 8px; }}

.aacri-diag-box {{
    background: {CCI_BG}; border-right: 5px solid {CCI_ORANGE_MID};
    border-radius: 8px; padding: 14px 16px; margin-top: 10px;
    font-size: 14.2px; line-height: 1.85; color: #1E293B; direction: rtl;
}}

.aacri-kpi-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
    gap: 10px; margin: 6px 0 14px 0; direction: rtl;
}}
.aacri-kpi {{ border-radius: 10px; padding: 12px 14px; border: 1px solid #E2E8F0; text-align: right; }}
.aacri-kpi-w {{ font-size: 22px; font-weight: 900; line-height: 1.2; }}
.aacri-kpi-t {{ font-size: 13px; font-weight: 800; color: {CCI_NAVY}; margin: 3px 0; }}
.aacri-kpi-m {{ font-size: 12px; color: #475569; font-weight: 600; }}
</style>
"""
st.markdown(EXTRA_CSS, unsafe_allow_html=True)

# ==============================================================================
# دوال مساعدة لتوليد ملفات Word (.docx) الأصلية بدون أي تحذيرات
# ==============================================================================
def _clean_word_text(text) -> str:
    return clean_text(text)


def _set_rtl_paragraph(p):
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    pPr = p._p.get_or_add_pPr()
    bidi = OxmlElement("w:bidi")
    pPr.append(bidi)


def build_word_document(title: str, subtitle: str, html_body: str) -> tuple[bytes, str, str]:
    """توليد ملف .docx أصلي متوافق مع Microsoft Word وLibreOffice مع ترويسة وتذييل واتجاه RTL."""
    if HAS_PYTHON_DOCX:
        doc = Document()
        section = doc.sections[0]

        header = section.header
        hp = header.paragraphs[0]
        hp.text = "منصة منظومة القرار المتكاملة للسياسات الثقافية والإبداعية العربية"
        _set_rtl_paragraph(hp)
        if hp.runs:
            hp.runs[0].font.size = Pt(9)
            hp.runs[0].font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

        footer = section.footer
        fp = footer.paragraphs[0]
        fp.text = f"جميع الحقوق محفوظة للدراسة البحثية © 2026 | تاريخ التوليد: {datetime.now().strftime('%Y-%m-%d')}"
        _set_rtl_paragraph(fp)
        if fp.runs:
            fp.runs[0].font.size = Pt(9)
            fp.runs[0].font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

        h_main = doc.add_heading(_clean_word_text(title), level=0)
        h_main.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if h_main.runs:
            h_main.runs[0].font.color.rgb = RGBColor(0x0A, 0x19, 0x2F)

        if subtitle:
            p_sub = doc.add_paragraph(_clean_word_text(subtitle))
            p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if p_sub.runs:
                p_sub.runs[0].font.size = Pt(11)
                p_sub.runs[0].font.color.rgb = RGBColor(0xB4, 0x53, 0x09)

        normalized = re.sub(r"<(br|hr)\s*/?>", "\n", html_body, flags=re.IGNORECASE)
        normalized = re.sub(r"</(p|div|h[1-6]|li|tr)>", "\n", normalized, flags=re.IGNORECASE)
        normalized = re.sub(r"<li[^>]*>", "• ", normalized, flags=re.IGNORECASE)
        normalized = re.sub(r"<h[1-4][^>]*>", "### ", normalized, flags=re.IGNORECASE)

        for raw_line in normalized.splitlines():
            line = _clean_word_text(raw_line)
            if not line:
                continue
            if line.startswith("### "):
                sec_title = line[4:].strip()
                if sec_title:
                    hd = doc.add_heading(sec_title, level=2)
                    _set_rtl_paragraph(hd)
                    if hd.runs:
                        hd.runs[0].font.color.rgb = RGBColor(0x0A, 0x19, 0x2F)
            elif line.startswith("• "):
                p = doc.add_paragraph(line[2:].strip(), style="List Bullet")
                _set_rtl_paragraph(p)
            else:
                p = doc.add_paragraph(line)
                _set_rtl_paragraph(p)

        buf = io.BytesIO()
        doc.save(buf)
        return (
            buf.getvalue(),
            ".docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

    fallback_html = f"""
    <html dir="rtl">
    <head><meta charset="utf-8"><title>{title}</title></head>
    <body style="font-family: 'Cairo', Arial, sans-serif; text-align: right; direction: rtl; line-height: 1.8;">
        <h1 style="color: #0A192F; text-align: center;">{title}</h1>
        <p style="text-align: center; color: #B45309;">{subtitle}</p>
        <hr>
        {html_body}
    </body>
    </html>
    """
    return fallback_html.encode("utf-8-sig"), ".doc", "application/msword"


# ==============================================================================
# دالة استخراج عنوان الـ IP الحقيقي للزائر بدقة
# ==============================================================================
def get_visitor_ip():
    try:
        ctx = st.runtime.scriptrunner.get_script_run_ctx()
        if ctx and hasattr(ctx, "session_id"):
            from streamlit.web.server.websocket_headers import _get_websocket_headers
            headers = _get_websocket_headers()
            if headers:
                ip = headers.get("X-Forwarded-For") or headers.get("X-Real-Ip") or headers.get("Remote-Addr")
                if ip:
                    return ip.split(",")[0].strip()
    except Exception:
        pass
    return "127.0.0.1 (محلي / Local)"

# ==============================================================================
# دوال إدارة وحفظ سجلات الزوار بشكل دائم في ملف خارجي (visitors_log.csv)
# ==============================================================================
LOG_FILE_PATH = "visitors_log.csv"

def init_visitor_log_file():
    if not os.path.exists(LOG_FILE_PATH):
        try:
            df_init = pd.DataFrame(columns=["عنوان IP", "اسم المستخدم", "الدور", "وقت الدخول"])
            df_init.to_csv(LOG_FILE_PATH, index=False, encoding='utf-8-sig')
        except Exception:
            pass

init_visitor_log_file()

def load_visitors_log_from_file():
    if os.path.exists(LOG_FILE_PATH):
        try:
            df = pd.read_csv(LOG_FILE_PATH, encoding='utf-8-sig')
            return df.to_dict(orient="records")
        except Exception:
            return []
    return []

def append_visitor_to_file(visitor_entry):
    existing_logs = load_visitors_log_from_file()
    exists = any(
        item.get("عنوان IP") == visitor_entry.get("عنوان IP") and
        item.get("اسم المستخدم") == visitor_entry.get("اسم المستخدم")
        for item in existing_logs
    )
    if not exists:
        existing_logs.append(visitor_entry)
        df_out = pd.DataFrame(existing_logs)
        df_out.to_csv(LOG_FILE_PATH, index=False, encoding='utf-8-sig')

# ==============================================================================
# إدارة جلسة الدخول المستمرة (الصمود أمام Refresh / F5) ودعم user بأي حالة أحرف
# ==============================================================================
ADMIN_USER = "admin"
ADMIN_PASS = "2621326_a"
USER_PASS = "123"

ADMIN_AUTH_TOKEN = hashlib.sha256(f"cci_admin_{ADMIN_USER}_{ADMIN_PASS}".encode()).hexdigest()[:24]
USER_AUTH_TOKEN = hashlib.sha256(f"cci_user_role_{USER_PASS}".encode()).hexdigest()[:24]

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""

# استعادة الجلسة تلقائياً عند عمل Refresh للمتصفح إذا كان رمز الجلسة موجوداً في الرابط
if not st.session_state.authenticated:
    url_auth = str(st.query_params.get("auth", "")).strip()
    if url_auth == ADMIN_AUTH_TOKEN:
        st.session_state.authenticated = True
        st.session_state.current_user = "admin"
    elif url_auth == USER_AUTH_TOKEN:
        st.session_state.authenticated = True
        st.session_state.current_user = "user"

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        login_container = st.container()
        with login_container:
            st.markdown(f"""
            <div style="background: #FFFFFF; padding: clamp(18px, 4vw, 30px); border-radius: 16px; border: 2px solid {CCI_ORANGE_MID}; box-shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: right;" dir="rtl">
                <h2 style="color: {CCI_NAVY}; text-align: center; font-weight: 800; margin-bottom: 10px;">🏛️ منصة منظومة القرار المتكاملة</h2>
                <p style="color: #475569; text-align: center; font-size: 14px; line-height: 1.6; margin-bottom: 25px;">
                    نموذج تشغيلي ذكي لدعم سياسات الصناعات الثقافية والإبداعية العربية في عصر الذكاء الاصطناعي بمنظور التفكير المنظومي. يرجى تسجيل الدخول للمتابعة.
                </p>
            </div>
            """, unsafe_allow_html=True)

            username = st.text_input("اسم المستخدم (Username)", placeholder="أدخل اسم المستخدم...")
            password = st.text_input("كلمة المرور (Password)", type="password", placeholder="أدخل كلمة المرور...")

            if st.button("🔐 تسجيل الدخول للمنصة", use_container_width=True):
                visitor_ip_addr = get_visitor_ip()
                current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                norm_user = str(username).strip().lower()
                clean_pass = str(password).strip()

                if norm_user == ADMIN_USER and clean_pass == ADMIN_PASS:
                    st.session_state.authenticated = True
                    st.session_state.current_user = "admin"
                    st.query_params["auth"] = ADMIN_AUTH_TOKEN

                    new_record = {
                        "عنوان IP": visitor_ip_addr,
                        "اسم المستخدم": "admin",
                        "الدور": "مشرف (Admin)",
                        "وقت الدخول": current_time_str
                    }
                    append_visitor_to_file(new_record)
                    st.rerun()

                elif norm_user == "user" and clean_pass == USER_PASS:
                    st.session_state.authenticated = True
                    st.session_state.current_user = "user"
                    st.query_params["auth"] = USER_AUTH_TOKEN

                    new_record = {
                        "عنوان IP": visitor_ip_addr,
                        "اسم المستخدم": str(username).strip() or "user",
                        "الدور": "مستخدم عادي (User)",
                        "وقت الدخول": current_time_str
                    }
                    append_visitor_to_file(new_record)
                    st.rerun()
                else:
                    st.error("⚠️ اسم المستخدم أو كلمة المرور غير صحيحة.")
    st.stop()

# ==============================================================================
# شريط تسجيل الخروج
# ==============================================================================
logout_col1, logout_col2 = st.columns([6, 1])
with logout_col2:
    if st.button("🚪 تسجيل الخروج", use_container_width=True, type="secondary"):
        st.session_state.authenticated = False
        st.session_state.current_user = ""
        st.query_params.clear()
        st.rerun()

# ==============================================================================
# القائمة الرسمية الكاملة للدول العربية
# ==============================================================================
ARAB_COUNTRIES = [
    "الدولة", "جمهورية مصر العربية", "دولة قطر", "المملكة العربية السعودية",
    "دولة الإمارات العربية المتحدة", "المملكة الأردنية الهاشمية",
    "المملكة المغربية", "الجمهورية التونسية", "الجمهورية الجزائرية الديمقراطية الشعبية",
    "سلطنة عمان", "مملكة البحرين", "دولة الكويت", "جمهورية العراق",
    "الجمهورية اللبنانية", "الجمهورية العربية السورية", "الجمهورية اليمنية",
    "جمهورية السودان", "ليبيا", "الجمهورية الإسلامية الموريتانية",
    "جمهورية جيبوتي", "جمهورية الصومال الفيدرالية", "اتحاد جزر القمر", "دولة فلسطين"
]

def get_colored_score_html(score):
    if score >= 80:
        return f"{score}% (أداء مرتفع 🟢)"
    elif score >= 51:
        return f"{score}% (أداء متوسط 🟡)"
    else:
        return f"{score}% (فجوة هيكلية حرجة 🔴)"

def describe_ti(val):
    if val >= 80:
        return f"البنية التقنية المتقدمة للغاية ({val}%) تتيح بيئة عريضة النطاق لتوطين وتشغيل النماذج التوليدية الضخمة."
    elif val >= 50:
        return f"البنية التقنية متوسطة الكفاءة ({val}%) وتتطلب ترقية سعات تدفق البيانات ودعم الباند عريض النطاق."
    else:
        return f"البنية التقنية تعاني من فجوة هيكلية حرجة ({val}%) تعيق استيعاب البنى التحتية الذكية."

def describe_ed(val):
    if val >= 80:
        return f"الديناميكيات الاقتصادية قوية وواعدة ({val}%) مع مساهمة عالية للاقتصاد البرتقالي وصادرات إبداعية مزدهرة."
    elif val >= 50:
        return f"الديناميكيات الاقتصادية في نطاق متوازن ({val}%) تستوجب تحفيز تدفقات رأس المال المخاطر للقطاع الإبداعي."
    else:
        return f"قصور حاد في الديناميكيات الاقتصادية ({val}%) وضعف في عوائد الصناعات الإبداعية يستوجب حزم طوارئ."

def describe_hc(val):
    if val >= 80:
        return f"رأس مال بشري مؤهل وعالي الجاهزية ({val}%) في مهارات هندسة الأوامر والتعامل مع تقنيات 'المبدع المعزز'."
    elif val >= 50:
        return f"رأس المال البشري بحاجة لبرامج إعادة تأهيل متوسطة المدى (Upskilling) في ظل تقييم بلغ ({val}%)."
    else:
        return f"فجوة حرجة في رأس المال البشري الماهر ({val}%) تهدد باستبعاد الكوادر الوطنية من سوق العمل الرقمي."

def describe_rf(val):
    if val >= 80:
        return f"بيئة تنظيمية وتشريعية رصينة ومتقدمة ({val}%) تكفل حماية الملكية الفكرية المشتركة ومعايير الوسم المائي."
    elif val >= 50:
        return f"البيئة التشريعية متوسطة الفاعلية ({val}%) وتحتاج لتحديث قوانين المسؤولية القانونية وحماية المصنفات."
    else:
        return f"ضعف هيكلي في المنظومة التشريعية والبيئة التنظيمية ({val}%) يعرض الحقوق الإبداعية للقرصنة."

def describe_cd(val):
    if val >= 80:
        return f"محددات ثقافية وهوياتية راسخة ({val}%) توفر حصانة رقمية عالية ومحتوى عربياً غنياً بالأرشفة الثلاثية."
    elif val >= 50:
        return f"محددات ثقافية متوازنة ({val}%) تتطلب تعزيز المحتوى الرقمي الثقافي والتراثي المتاح بالعربية."
    else:
        return f"هشاشة واضحة في المحددات الثقافية الهوياتية ({val}%) تستوجب تفعيل دروع الأمن الثقافي الرقمي."

def get_region_and_features(country_name):
    gulf_countries = ["دولة قطر", "المملكة العربية السعودية", "دولة الإمارات العربية المتحدة", "سلطنة عمان", "مملكة البحرين", "دولة الكويت"]
    nile_valley = ["جمهورية مصر العربية", "جمهورية السودان"]
    north_africa = ["المملكة المغربية", "الجمهورية التونسية", "الجمهورية الجزائرية الديمقراطية الشعبية", "ليبيا", "الجمهورية الإسلامية الموريتانية"]
    levant = ["المملكة الأردنية الهاشمية", "الجمهورية اللبنانية", "الجمهورية العربية السورية", "دولة فلسطين"]

    if country_name in gulf_countries:
        return f"تنتمي {country_name} إلى إقليم الخليج العربي (شبه الجزيرة العربية)، وهي منطقة تتميز بكتلة مالية استثمارية واعدة، وسرعات بنية تحتية رقمية فائقة، وتركيز استراتيجي عالٍ على التحول الذكي وقيادة الابتكار التقني."
    elif country_name in nile_valley:
        return f"تتمركز {country_name} في إقليم وادي النيل، متسلحة بعمق تاريخي الحضاري فريد، وثقل ديموغرافي بشري كبير، ورأس مال أكاديمي وثقافي عريق يمثل مرتكزاً أساسياً للإنتاج الإبداعي."
    elif country_name in north_africa:
        return f"تتوزع {country_name} في نطاق إقليم شمال إفريقيا، متخِذةً من التنوع الثقافي واللغوي المتوسطي والأفريقي جسوراً حية للتواصل الإبداعي وعقد الشراكات العابرة للحدود."
    elif country_name in levant:
        return f"ترتبط {country_name} بإقليم بلاد الشام التاريخي، متميزة بتراث إبداعي فكري غني، وشبكات مجتمعية نشطة، وكفاءات بشرية عالية التأهل في مختلف حقول المعرفة والفنون."
    else:
        return f"تندرج {country_name} ضمن نطاق العالم العربي الموسع، محتضنةً خصائص جيوستراتيجية وتاريخية فريدة داعمة للتكامل الإقليمي وتجسير مسارات التنمية المستدامة."

if "history_state" not in st.session_state:
    st.session_state.history_state = []
if "simulated_results_dict" not in st.session_state:
    st.session_state.simulated_results_dict = {}
if "decision_results_dict" not in st.session_state:
    st.session_state.decision_results_dict = {}

# ==============================================================================
# الترويسة والشريط الإخباري
# ==============================================================================
st.markdown(f"""
<div class="header-center">
<h1>نموذج مقترح لتطوير منصة منظومة القرار المتكاملة للسياسات الثقافية والإبداعية العربية</h1>
<h1>منصة مشكاة</h1>
<h3>ضمن مخرجات دراسة بحثية مقاربة منهجية لتطوير مهن الصناعات الثقافية والإبداعية العربية في عصر الذكاء الاصطناعي بمنظور التفكير المنظومي</h3>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="ticker-wrap">
  <div class="ticker">
    <span class="ticker-item">🏛️ ضمن مخرجات دراسة بحثية مقاربة منهجية لتطوير مهن الصناعات الثقافية والإبداعية العربية في عصر الذكاء الاصطناعي بمنظور التفكير المنظومي</span>
    <span class="ticker-item">| 📊 مؤشر الجاهزية الذكية المركب (AACRI): الهيكل الهرمي الخماسي والمتغيرات الـ 69</span>
    <span class="ticker-item">| 📈 محاكي السياسات الاستشرافي العميق لاختبار السيناريوهات الاستراتيجية (Multiple Regression)</span>
    <span class="ticker-item">| 🛡️ لوحة دعم اتخاذ القرار ولوحة التطعيم الثقافي (Cultural Grafting Canvas)</span>
    <span class="ticker-item">| 📑 التقرير التنفيذي الموحد للقيادات العليا وإطار دونيلا ميدوز لنقاط الرفع | جميع الحقوق محفوظة للدراسة البحثية © 2026</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# التقسيم الرئيسي إلى التبويبات (مع إضافة تبويب الرئيسة في المقدمة)
# ==============================================================================
if st.session_state.current_user == "admin":
    tab_home, tab1, tab2, tab3, tab4, tab5, tab6, tab_admin = st.tabs([
        "🏠 الرئيسة",
        "📊  مؤشر الجاهزية (AACRI)",
        "📈 محاكي السياسات ",
        "🛡️ لوحة دعم اتخاذ القرار",
        "📑 التقرير التنفيذي الموحد",
        "📚 ملاحق المشروع والوثائق ",
        "📖 دليل المستخدم الرسمي",
        "🔒 سجل الزوار والأفراد (Admin)"
    ])
else:
    tab_home, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 الرئيسة",
        "📊  مؤشر الجاهزية (AACRI)",
        "📈 محاكي السياسات ",
        "🛡️ لوحة دعم اتخاذ القرار",
        "📑 التقرير التنفيذي الموحد",
        "📚 ملاحق المشروع والوثائق ",
        "📖 دليل المستخدم الرسمي"
    ])
    tab_admin = None

# حقن وتثبيت تنسيق الشريط العلوي بعرض الشاشة الكامل + استعادة التبويب عند التحديث
inject_tabs_css()

# ------------------------------------------------------------------------------
# التبويب الرئيسي: الرئيسة (التعريف بالمنصة ومفاتيح الانتقال السريع لأقسامها)
# ------------------------------------------------------------------------------
with tab_home:
    st.markdown(f"""
    <div class="home-hero-card" dir="rtl" style="text-align: right;">
        <h3 style="color: {CCI_NAVY}; font-weight: 800; margin-top: 0; margin-bottom: 10px;">
            🏛️ مرحباً بك في منصة منظومة القرار المتكاملة للسياسات الثقافية والإبداعية العربية
        </h3>
        <p style="color: #1E293B; font-size: 14.8px; line-height: 1.85; margin-bottom: 10px;">
            تُعد هذه المنصة نموذجاً تشغيلياً تفاعلياً لدعم صُنّاع القرار والباحثين والخبراء في صياغة وتطوير سياسات <b>الصناعات الثقافية والإبداعية العربية (CCIs)</b> في ظل التحولات المتسارعة للذكاء الاصطناعي التوليدي، مستندةً إلى <b>التفكير المنظومي (Systems Thinking)</b>، والتحليل الهرمي (AHP)، ومؤشر الجاهزية الذكية المركب (AACRI) المبني على خمسة محاور رئيسة و69 متغيراً.
        </p>
        <p style="color: #475569; font-size: 13.8px; line-height: 1.75; margin: 0;">
            <b>الهدف الاستراتيجي:</b> تمكين «المبدع المعزز»، وحماية الهوية والأمن الثقافي الرقمي، وتحويل التحديات الخوارزمية إلى فرص نمو مستدام للاقتصاد البرتقالي العربي.
        </p>
    </div>
    """, unsafe_allow_html=True)

    kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="medium")
    with kpi1:
        st.markdown(f"""
        <div class="home-kpi-box" dir="rtl">
            <div class="home-kpi-val">22</div>
            <div class="home-kpi-lbl">دولة عربية ضمن الإطار الجغرافي</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""
        <div class="home-kpi-box" dir="rtl">
            <div class="home-kpi-val">5 / 69</div>
            <div class="home-kpi-lbl">محاور هرمية و69 متغيراً في AACRI</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"""
        <div class="home-kpi-box" dir="rtl">
            <div class="home-kpi-val">{len(st.session_state.history_state)}</div>
            <div class="home-kpi-lbl">دول مُشخّصة في الجلسة الحالية</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi4:
        st.markdown(f"""
        <div class="home-kpi-box" dir="rtl">
            <div class="home-kpi-val">{len(st.session_state.simulated_results_dict) + len(st.session_state.decision_results_dict)}</div>
            <div class="home-kpi-lbl">سيناريوهات وتوصيات مُثبّتة</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div dir="rtl" style="text-align: right; margin-bottom: 14px;">
        <h3 style="color: {CCI_NAVY}; font-weight: 800; margin: 0;">🧭 أقسام المنصة وآلية العمل المتكاملة</h3>
        <p style="color: #475569; font-size: 14px; margin-top: 4px;">
            انقر على أي بطاقة قسم للانتقال المباشر والمرن إليه داخل المنصة:
        </p>
    </div>
    """, unsafe_allow_html=True)

    r1_c1, r1_c2, r1_c3 = st.columns(3, gap="medium")
    with r1_c1:
        st.markdown("""
        <div class="home-section-card" data-cci-tab="1" data-tab-target="1" role="button" tabindex="0" dir="rtl" style="text-align: right;">
            <h4>📊 تشخيص مؤشر الجاهزية (AACRI)</h4>
            <p>قياس جاهزية الدول العربية عبر خمسة محاور موزونة (البنية التقنية 20%، الاقتصاد 15%، رأس المال البشري 30%، البيئة التشريعية 20%، المحددات الثقافية 15%) مع رسم راداري وترتيب تراكمي وتصدير CSV.</p>
            <span class="home-section-cta">انتقال مباشر للقسم ⬅️</span>
        </div>
        """, unsafe_allow_html=True)
    with r1_c2:
        st.markdown("""
        <div class="home-section-card" data-cci-tab="2" data-tab-target="2" role="button" tabindex="0" dir="rtl" style="text-align: right;">
            <h4>📈 محاكي السياسات (Policy Simulator)</h4>
            <p>اختبار السيناريوهات الاستراتيجية (التشاؤمي، المعتدل، الطموح) وضبط نسب التحفيز عبر المحاور الخمسة لاستشراف الأثر المستقبلي وتثبيت ومقارنة السيناريوهات وتصديرها في ملف Word.</p>
            <span class="home-section-cta">انتقال مباشر للقسم ⬅️</span>
        </div>
        """, unsafe_allow_html=True)
    with r1_c3:
        st.markdown("""
        <div class="home-section-card" data-cci-tab="3" data-tab-target="3" role="button" tabindex="0" dir="rtl" style="text-align: right;">
            <h4>🛡️ لوحة دعم اتخاذ القرار</h4>
            <p>توليد وتثبيت توصيات سياساتية مخصصة لكل دولة وفق مستوى جاهزيتها، وتفعيل آليات التطعيم الثقافي (Cultural Grafting) وصون الهوية والسيادة الرقمية.</p>
            <span class="home-section-cta">انتقال مباشر للقسم ⬅️</span>
        </div>
        """, unsafe_allow_html=True)

    r2_c1, r2_c2, r2_c3 = st.columns(3, gap="medium")
    with r2_c1:
        st.markdown("""
        <div class="home-section-card" data-cci-tab="4" data-tab-target="4" role="button" tabindex="0" dir="rtl" style="text-align: right;">
            <h4>📑 التقرير التنفيذي الموحد</h4>
            <p>دمج مخرجات التشخيص والترتيب الإقليمي والمحاكاة والتوصيات في تقرير تنفيذي موحد للقيادات العليا مع إمكانية تحميله بصيغة مستند Word (.docx) جاهز للعرض.</p>
            <span class="home-section-cta">انتقال مباشر للقسم ⬅️</span>
        </div>
        """, unsafe_allow_html=True)
    with r2_c2:
        st.markdown("""
        <div class="home-section-card" data-cci-tab="5" data-tab-target="5" role="button" tabindex="0" dir="rtl" style="text-align: right;">
            <h4>📚 ملاحق المشروع والوثائق (PDF)</h4>
            <p>إتاحة الملاحق العلمية والمنهجية الستة للدراسة (الاستقراء الببليومتري، حلقات السببية CLDs، المصفوفة الإجرائية، المقارنات الزوجية، المعادلات، وبروتوكول الاختبار الميداني).</p>
            <span class="home-section-cta">انتقال مباشر للقسم ⬅️</span>
        </div>
        """, unsafe_allow_html=True)
    with r2_c3:
        st.markdown("""
        <div class="home-section-card" data-cci-tab="6" data-tab-target="6" role="button" tabindex="0" dir="rtl" style="text-align: right;">
            <h4>📖 دليل المستخدم الرسمي</h4>
            <p>مرجع إرشادي متكامل يوضح خطوات استخدام المنصة وتفسير مؤشراتها ومخرجاتها للمحكمين والباحثين وصُنّاع السياسات بصيغة PDF.</p>
            <span class="home-section-cta">انتقال مباشر للقسم ⬅️</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background: #FFFFFF; padding: 18px 22px; border-radius: 12px; border: 1px solid #CBD5E1; border-right: 5px solid {CCI_NAVY}; margin-top: 8px;" dir="rtl">
        <h4 style="color: {CCI_NAVY}; font-weight: 800; margin-top: 0; margin-bottom: 8px;">⚡ مسار العمل الموصى به داخل المنصة:</h4>
        <ol style="margin: 0; padding-right: 20px; color: #1E293B; font-size: 14px; line-height: 1.85;">
            <li>ابدأ من تبويب <b>«تشخيص مؤشر الجاهزية (AACRI)»</b> لاختيار الدولة وتسجيل درجات محاورها الخمسة.</li>
            <li>انتقل إلى <b>«محاكي السياسات»</b> لاختبار السيناريوهات الاستراتيجية وتثبيت النتائج التراكمية.</li>
            <li>فعّل <b>«لوحة دعم اتخاذ القرار»</b> لاعتماد التوصيات المخصصة لكل دولة.</li>
            <li>استخرج <b>«التقرير التنفيذي الموحد»</b> أو استعرض <b>«الملاحق ودليل المستخدم»</b> حسب حاجتك البحثية أو المؤسسية.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="footer-copyright">جميع الحقوق محفوظة للدراسة البحثية © 2026</div>', unsafe_allow_html=True)


def render_aacri_result(rec: dict, detail_html: str = ""):
    score = rec["المؤشر المركب (AACRI)"]
    label, fg, bg = score_band(score)
    vals = [
        rec["البنية التقنية (20%)"],
        rec["الديناميكيات الاقتصادية (15%)"],
        rec["رأس المال البشري (30%)"],
        rec["البيئة التنظيمية والتشريعية (20%)"],
        rec["المحددات الثقافية والهوياتية (15%)"],
    ]
    detail_html = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", detail_html or "")

    with st.container(border=True):
        st.markdown(flat_html(f"""
            <div dir="rtl" class="aacri-result-head">
              <div>
                <div class="aacri-result-kicker">التشخيص المنظومي · إطار AACRI (69 متغيراً)</div>
                <div class="aacri-result-country">{rec['الدولة']}</div>
              </div>
              <span class="score-chip big" style="color:{fg};background:{bg};">مستوى الجاهزية: {label}</span>
            </div>
        """), unsafe_allow_html=True)

        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "%", "font": {"size": 44, "family": "Cairo", "color": CCI_NAVY}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1},
                "bar": {"color": CCI_NAVY, "thickness": 0.28},
                "steps": [
                    {"range": [0, 51], "color": "#FECACA"},
                    {"range": [51, 80], "color": "#FDE68A"},
                    {"range": [80, 100], "color": "#BBF7D0"},
                ],
                "threshold": {"line": {"color": CCI_ORANGE_MID, "width": 4}, "thickness": 0.85, "value": score},
            },
        ))
        fig_g.update_layout(height=235, margin=dict(l=25, r=25, t=15, b=5),
                            paper_bgcolor="#FFFFFF", font=dict(family="Cairo"))
        st.plotly_chart(fig_g, use_container_width=True)

        bars = ""
        for (_code, name, w, color), v in zip(AXES, vals):
            bars += (
                f'<div class="aacri-bar-row"><div class="aacri-bar-head">'
                f'<span>{name}</span><span>{v}% × {int(w * 100)}% = <b>{v * w:.1f}</b></span></div>'
                f'<div class="aacri-bar-track"><div class="aacri-bar-fill" '
                f'style="width:{v}%;background:{color};"></div></div></div>'
            )
        st.markdown(f'<div dir="rtl">{bars}</div>', unsafe_allow_html=True)

        if detail_html:
            st.markdown(f'<div class="aacri-diag-box"><b>التقييم التشخيصي والتفصيل المنظومي:</b><br>{detail_html}</div>',
                        unsafe_allow_html=True)

        names = [f"{n} ({int(w * 100)}%)" for _c, n, w, _col in AXES]
        fig_r = go.Figure(go.Scatterpolar(
            r=vals + vals[:1], theta=names + names[:1], fill="toself",
            name=rec["الدولة"], line_color=CCI_ORANGE_MID, fillcolor="rgba(180,83,9,0.22)"))
        fig_r.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                            height=340, margin=dict(l=40, r=40, t=20, b=20),
                            paper_bgcolor="#FFFFFF", font=dict(family="Cairo", size=12), showlegend=False)
        st.plotly_chart(fig_r, use_container_width=True)


def build_axes_summary_html() -> str:
    cards = []
    for axis_id, title, weight, _b, accent, bg_soft, border_soft, dims in AACRI_HIERARCHY_MATRIX:
        n_dims, n_subs, n_vars = axis_counts(dims)
        short = title.split(". ", 1)[-1].split(" (وزن")[0]
        cards.append(
            f'<div class="aacri-kpi" style="border-top:4px solid {accent};background:{bg_soft};">'
            f'<div class="aacri-kpi-w" style="color:{accent};">{weight:g}%</div>'
            f'<div class="aacri-kpi-t">{html.escape(short)}</div>'
            f'<div class="aacri-kpi-m">{n_dims} أبعاد · {n_subs} فرعية · {n_vars} متغيراً</div></div>'
        )
    return '<div class="aacri-kpi-grid">' + "".join(cards) + "</div>"


def build_hierarchy_html(target_axis_id: str = "all") -> str:
    out = ['<div dir="rtl" style="width:100%;">']
    for axis_id, axis_title, axis_weight, _b, accent, bg_soft, border_soft, dimensions in AACRI_HIERARCHY_MATRIX:
        if target_axis_id != "all" and axis_id != target_axis_id:
            continue
        n_dims, n_subs, n_vars = axis_counts(dimensions)
        dim_w = axis_weight / n_dims

        out.append(
            f'<div class="aacri-axis-block" style="border-top:4px solid {accent};">'
            f'<div class="aacri-axis-header">'
            f'<span class="aacri-axis-title" style="color:{accent};">{html.escape(axis_title)}</span>'
            f'<span class="aacri-axis-pill" style="background:{bg_soft};color:{accent};border:1px solid {border_soft};">'
            f'{n_dims} أبعاد أساسية | {n_subs} فرعية | {n_vars} متغيراً</span></div>'
        )

        for dim_code, dim_title, sub_dims in dimensions:
            sub_w = dim_w / len(sub_dims)
            dim_vars = sum(len(sd[2]) for sd in sub_dims)
            out.append(
                f'<details class="aacri-dim-dropdown"><summary>'
                f'<span class="aacri-dim-summary-right"><span class="aacri-dim-num">{dim_code}</span>'
                f'<span>البُعد الأساسي: {html.escape(dim_title)}</span></span>'
                f'<span class="aacri-dim-meta"><span class="aacri-dim-weight-badge">⚖️ {dim_w:.2f}%</span>'
                f'<span>({len(sub_dims)} فرعية | {dim_vars} متغيراً)</span>'
                f'<span class="aacri-dim-chevron">▼</span></span></summary>'
                f'<div class="aacri-dim-body">'
            )
            for sd_code, sd_title, variables in sub_dims:
                var_w = sub_w / len(variables)
                out.append(
                    f'<div class="aacri-sub-card" style="border-right-color:{accent};">'
                    f'<div class="aacri-sub-title-row"><div class="aacri-sub-title-left">'
                    f'<span class="aacri-sub-code-badge" style="background:{accent};color:#FFFFFF;">{sd_code}</span>'
                    f'<span class="aacri-sub-name" style="color:{accent};">{html.escape(sd_title)}</span></div>'
                    f'<span class="aacri-sub-weight-pill">⚖️ <b>{sub_w:.3f}%</b></span></div>'
                )
                for var_name, unit_name in variables:
                    out.append(
                        f'<div class="aacri-var-item"><span class="aacri-var-label">🔹 {html.escape(clean_text(var_name))}</span>'
                        f'<span class="aacri-var-badges"><span class="aacri-weight-tag">⚖️ <b>{var_w:.3f}%</b></span>'
                        f'<span class="aacri-unit-tag" style="background:{bg_soft};color:{accent};border-color:{border_soft};">'
                        f'{html.escape(clean_text(unit_name))}</span></span></div>'
                    )
                out.append('</div>')
            out.append('</div></details>')
        out.append('</div>')
    out.append('</div>')
    return "".join(out)


# ------------------------------------------------------------------------------
# التبويب الأول: تشخيص مؤشر الجاهزية (AACRI)
# ------------------------------------------------------------------------------
with tab1:
    st.markdown("""
    <div dir="rtl" style="text-align: right;">
        <h3>🌐 التشخيص القياسي لمؤشر الجاهزية الذكية للصناعات الثقافية والإبداعية (AACRI)</h3>
        <p>إمكانية تشخيص الدول العربية المختارة مع تسجيل وثبات النتائج في الجدول التراكمي وإدارة السجلات الموضح أدناه.</p>
    </div>
    """, unsafe_allow_html=True)

    col_input, col_result = st.columns([1, 2], gap="large")

    with col_input:
        st.markdown('<div dir="rtl" style="text-align: right;">', unsafe_allow_html=True)
        country_sel = st.selectbox("اختر الدولة العربية", ARAB_COUNTRIES, key="t1_country")
        ti_slider = st.slider("1️⃣ البنية التقنية (وزن 20%)", 0, 100, 68, key="t1_ti")
        ed_slider = st.slider("2️⃣ الديناميكيات الاقتصادية (وزن 15%)", 0, 100, 70, key="t1_ed")
        hc_slider = st.slider("3️⃣ رأس المال البشري (وزن 30%)", 0, 100, 72, key="t1_hc")
        rf_slider = st.slider("4️⃣ البيئة التنظيمية والتشريعية (وزن 20%)", 0, 100, 65, key="t1_rf")
        cd_slider = st.slider("5️⃣ المحددات الثقافية والهوياتية (وزن 15%)", 0, 100, 82, key="t1_cd")

        calc_clicked = st.button("🚀 احسب وسجل قياس الدولة", use_container_width=True, type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_result:
        st.markdown('<div dir="rtl" style="text-align: right;">', unsafe_allow_html=True)
        if calc_clicked:
            if country_sel == "الدولة":
                st.warning("⚠️ يرجى اختيار دولة عربية حقيقية من القائمة لتنفيذ التشخيص القياسي.")
            else:
                weights = {'TI': 0.20, 'ED': 0.15, 'HC': 0.30, 'RF': 0.20, 'CD': 0.15}
                final_score = round((ti_slider * weights['TI']) + (ed_slider * weights['ED']) + (hc_slider * weights['HC']) + (rf_slider * weights['RF']) + (cd_slider * weights['CD']), 2)
                score_str_plain = get_colored_score_html(final_score)

                if final_score >= 80:
                    diagnosis = "🟢 جاهزية متقدمة للغاية نحو السيادة الرقمية والابتكار المستدام وتفعيل 'المبدع المعزز'."
                    detailed_diag = f"🟢 **جاهزية متقدمة ومستدامة:** إجمالي المؤشر المركب {score_str_plain}. تعكس هذه النتيجة تفوقاً هيكلياً في بيئة العمل، ورأس مال بشري مؤهل للتعامل مع التقنيات التوليدية، وبنية تقنية متطورة تتيح قيادة التحالفات الإقليمية وتوطين النماذج الثقافية الرقمية بكفاءة عالية بما يضمن صون الأمن الثقافي."
                elif final_score >= 51:
                    diagnosis = "🟡 جاهزية متوسطة، تتطلب تدخلات استباقية لمعالجة الاختناقات الهيكلية."
                    detailed_diag = f"🟡 **جاهزية متوسطة تتطلب تدخلاً استباقياً:** إجمالي المؤشر المركب {score_str_plain}. تشير المؤشرات إلى توازن نسبي يواجه بعض الاختناقات الهيكلية في سلاسل القيمة أو التشريعات التنظيمية، مما يستوجب حزم تحفيزية وبرامج إعادة تأهيل (Upskilling & Reskilling) لردم الفجوات القائمة."
                else:
                    diagnosis = "🔴 وجود فجوة ذكية هيكلية تستوجب تفعيل محاكي السياسات ولوحة دعم اتخاذ القرار فوراً."
                    detailed_diag = f"🔴 **فجوة ذكية هيكلية حرجة:** إجمالي المؤشر المركب {score_str_plain}. توضح القراءة الحالية وجود اختناقات عميقة في البنية التحتية والبيئة التشريعية ورأس المال البشري، مما يستوجب تفعيل محاكي السياسات ولوحة التطعيم الثقافي لدعم 'المبدع المعزز' وتفادي الاستلاب الخوارزمي."

                entry = {
                    "الدولة": country_sel,
                    "المؤشر المركب (AACRI)": final_score,
                    "البنية التقنية (20%)": ti_slider,
                    "الديناميكيات الاقتصادية (15%)": ed_slider,
                    "رأس المال البشري (30%)": hc_slider,
                    "البيئة التنظيمية والتشريعية (20%)": rf_slider,
                    "المحددات الثقافية والهوياتية (15%)": cd_slider,
                    "التقييم المنظومي": diagnosis
                }

                updated = False
                for idx, item in enumerate(st.session_state.history_state):
                    if item["الدولة"] == country_sel:
                        st.session_state.history_state[idx] = entry
                        updated = True
                        break
                if not updated:
                    st.session_state.history_state.append(entry)

                st.session_state.last_aacri = {"country": country_sel, "detail": detailed_diag}

        last = st.session_state.get("last_aacri")
        rec = None
        if last:
            rec = next((r for r in st.session_state.history_state if r["الدولة"] == last["country"]), None)
        if rec:
            render_aacri_result(rec, last["detail"])
        elif not calc_clicked:
            st.info("📊 يرجى اختيار الدولة وضبط درجات المحاور ثم الضغط على زر الحساب لعرض النتائج والتمثيل الراداري.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div dir="rtl" style="text-align: right;">
        <h3>📋 قائمة ترتيب الدول العربية المسجلة</h3>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.history_state:
        df_history = pd.DataFrame(st.session_state.history_state).sort_values(by="المؤشر المركب (AACRI)", ascending=False).reset_index(drop=True)

        medals = {0: "🥇", 1: "🥈", 2: "🥉"}
        headers = ["م", "الدولة", "المؤشر المركب", "رأس المال البشري", "البنية التقنية",
                   "البيئة التنظيمية", "الديناميكيات الاقتصادية", "المحددات الثقافية", "التقييم المنظومي"]
        rows_html = ""
        for idx, row in df_history.iterrows():
            sc = row["المؤشر المركب (AACRI)"]
            _lbl, fg, bg = score_band(sc)
            rows_html += (
                f'<tr><td style="text-align:center;font-weight:bold;">{medals.get(idx, idx + 1)}</td>'
                f'<td style="font-weight:bold;color:{CCI_NAVY};">{row["الدولة"]}</td>'
                f'<td><span class="score-chip" style="color:{fg};background:{bg};">{sc}%</span></td>'
                f'<td>{row["رأس المال البشري (30%)"]}%</td>'
                f'<td>{row["البنية التقنية (20%)"]}%</td>'
                f'<td>{row["البيئة التنظيمية والتشريعية (20%)"]}%</td>'
                f'<td>{row["الديناميكيات الاقتصادية (15%)"]}%</td>'
                f'<td>{row["المحددات الثقافية والهوياتية (15%)"]}%</td>'
                f'<td style="font-size:11px;">{row["التقييم المنظومي"]}</td></tr>'
            )
        table_html = (
            '<div dir="rtl" style="width:100%;overflow-x:auto;max-height:340px;">'
            '<table class="custom-rtl-table"><thead><tr>'
            + "".join(f"<th>{h}</th>" for h in headers)
            + "</tr></thead><tbody>" + rows_html + "</tbody></table></div>"
        )
        st.markdown(table_html, unsafe_allow_html=True)

        csv_data = df_history.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 تحميل جدول ترتيب الدول العربية المسجلة (Excel/CSV)",
            data=csv_data,
            file_name="ترتيب_الدول_العربية_AACRI.csv",
            mime="text/csv",
            use_container_width=True
        )

        col_del1, col_del2 = st.columns([2, 1])
        with col_del1:
            recorded_countries = [item["الدولة"] for item in st.session_state.history_state]
            country_to_delete = st.selectbox("اختر دولة من السجل لحذفها", recorded_countries, key="del_country_box")
        with col_del2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ حذف الدولة المحددة", use_container_width=True, type="secondary"):
                st.session_state.history_state = [item for item in st.session_state.history_state if item["الدولة"] != country_to_delete]
                st.success(f"✅ تم حذف سجل دولة ({country_to_delete}) بنجاح.")
                st.rerun()
    else:
        st.info("📂 لا توجد دول مسجلة حتى الآن. قم إجراء التشخيص في الأعلى لتسجيل وترتيب الدول.")

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("📂 استعراض المصفوفة الهرمية والمحاور والأبعاد والمتغيرات الـ 69 لمؤشر (AACRI)", expanded=False):
        st.markdown(build_axes_summary_html(), unsafe_allow_html=True)
        st.markdown(
            f'<div dir="rtl" style="background:#F8FAFC;border:1px solid #CBD5E1;border-right:4px solid {CCI_ORANGE_MID};'
            f'border-radius:8px;padding:10px 14px;font-size:13.5px;color:{CCI_NAVY};font-weight:700;margin-bottom:8px;">'
            f'💡 اضغط على أي <b>بُعد أساسي</b> لفتحه واستعراض الأبعاد الفرعية والمتغيرات ووحدات القياس. '
            f'الأوزان الفرعية موزعة بالتساوي ضمن كل محور؛ استبدلها بأوزان AHP إن كانت مختلفة.</div>',
            unsafe_allow_html=True,
        )

        filter_axis_choice = st.radio(
            "تصفية العرض حسب المحور الرئيسي:",
            options=[
                "🌐 عرض جميع المحاور الخمسة (13 بُعداً أساسياً | 69 متغيراً)",
                "💻 1. البنية التقنية والتحول الرقمي الإبداعي",
                "💹 2. الديناميكيات الاقتصادية وسلاسل القيمة الإبداعية",
                "🧠 3. رأس المال البشري والمهارات التوليدية",
                "⚖️ 4. البيئة التنظيمية والتشريعية (الحوكمة الرقمية)",
                "🏛️ 5. المحددات الثقافية والهوياتية والأمن الثقافي",
            ],
            horizontal=True,
            key="aacri_hierarchy_axis_filter",
        )

        selected_axis_map = {
            "💻 1. البنية التقنية والتحول الرقمي الإبداعي": "ti",
            "💹 2. الديناميكيات الاقتصادية وسلاسل القيمة الإبداعية": "ed",
            "🧠 3. رأس المال البشري والمهارات التوليدية": "hc",
            "⚖️ 4. البيئة التنظيمية والتشريعية (الحوكمة الرقمية)": "rf",
            "🏛️ 5. المحددات الثقافية والهوياتية والأمن الثقافي": "cd",
        }
        target_axis_id = selected_axis_map.get(filter_axis_choice, "all")
        st.markdown(build_hierarchy_html(target_axis_id), unsafe_allow_html=True)

        axes_names = [
            '1. البنية التقنية (20%)',
            '2. الديناميكيات الاقتصادية (15%)',
            '3. رأس المال البشري (30%)',
            '4. البيئة التنظيمية والتشريعية (20%)',
            '5. المحددات الثقافية والهوياتية (15%)'
        ]
        weights_vals = [20, 15, 30, 20, 15]
        custom_pie_colors = [CCI_NAVY, CCI_ORANGE_DARK, CCI_ORANGE_MID, CCI_ORANGE_LIGHT, "#334155"]

        fig_pie = px.pie(
            names=axes_names,
            values=weights_vals,
            hole=0.4,
            title="توزيع الأوزان النسبية لمحاور المؤشر وفق التحليل الهرمي AHP",
            color=axes_names,
            color_discrete_map=dict(zip(axes_names, custom_pie_colors))
        )
        fig_pie.update_layout(
            title=dict(text="توزيع الأوزان النسبية لمحاور المؤشر وفق التحليل الهرمي AHP", x=0.99, xanchor='right'),
            paper_bgcolor="#FFFFFF",
            font=dict(family="Cairo", size=13)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown(f'<div class="footer-copyright">جميع الحقوق محفوظة للدراسة البحثية © 2026</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# التبويب الثاني: محاكي السياسات (Policy Simulator)
# ------------------------------------------------------------------------------
with tab2:
    st.markdown("""
    <div dir="rtl" style="text-align: right;">
        <h3>🔬 محاكي السياسات الاستشرافي والمتابعة التراكمية للسيناريوهات</h3>
        <p>استشراف أثر التدخلات الاستثمارية والتقنية عبر النمذجة القياسية ومتغيرات التحفيز الاستراتيجي.</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.history_state:
        st.warning("يرجى أولاً إدخال بيانات الدولة وحساب مؤشر AACRI في القسم الأول.")
    else:
        col_sim_in, col_sim_out = st.columns([1, 2], gap="large")

        with col_sim_in:
            st.markdown('<div dir="rtl" style="text-align: right;">', unsafe_allow_html=True)
            recorded_countries_sim = [item["الدولة"] for item in st.session_state.history_state]
            sim_country_sel = st.selectbox("اختر الدولة للمحاكاة", recorded_countries_sim, key="sim_country")
            base_aacri_input = st.slider("قيمة المؤشر الافتراضي الحالي", 30.0, 100.0, 68.5, 0.5, key="sim_base")

            scenario_dropdown = st.selectbox("اختر السيناريو الاستراتيجي", [
                "📉 السيناريو التشاؤمي (غياب التدخل وضعف الاستثمار)",
                "📊 السيناريو المعتدل / التفاؤلي (استثمارات تقليدية تدريجية)",
                "🚀 السيناريو الطموح / الاستباقي (إصلاحات هيكلية شاملة وسيادة تقنية)"
            ], index=1, key="sim_scen")

            var1_tech = st.slider("1️⃣ نسبة الزيادة في البنية التقنية وتوطين النماذج (%)", 0, 50, 20, key="sim_v1")
            var2_eco = st.slider("2️⃣ نسبة الزيادة في الديناميكيات الاقتصادية (%)", 0, 50, 15, key="sim_v2")
            var3_hc = st.slider("3️⃣ نسبة الزيادة في رأس المال البشري (%)", 0, 50, 15, key="sim_v3")
            var4_reg = st.slider("4️⃣ معدل تطوير البيئة التشريعية (%)", 0, 50, 10, key="sim_v4")
            var5_cult = st.slider("5️⃣ نسبة التوسع في المحددات الثقافية (%)", 0, 50, 25, key="sim_v5")

            run_sim_btn = st.button("📋 إضافة وتثبيت سيناريو الدولة", use_container_width=True, type="primary")

            if st.button("🗑️ مسح وإعادة تعيين استجابات المحاكي", use_container_width=True, type="secondary"):
                st.session_state.simulated_results_dict = {}
                st.success("✅ تم مسح جميع سيناريوهات المحاكي بنجاح.")
                st.rerun()

            sim_body_parts = ["<h3>📋 مقارنة السيناريوهات المثبتة للدول (المختارة):</h3>"]
            if st.session_state.simulated_results_dict:
                for k, v in st.session_state.simulated_results_dict.items():
                    sim_body_parts.append(f"<h4>السيناريو: {k}</h4>")
                    sim_body_parts.append(v["html"])
                    sim_body_parts.append(v["deep"])
            else:
                sim_body_parts.append("<p>لا توجد سيناريوهات مسجلة حالياً.</p>")

            sim_body_parts.append(
                "<hr><h3>📈 ملخص النتائج التحليلية التراكمية والمعمقة لكافة أقسام المنصة:</h3>"
                "<p>يغطي هذا التقرير مخرجات النمذجة القياسية ومتغيرات التحفيز الاستراتيجي لصنّاع القرار.</p>"
                "<p><b>يُنصح بالمراجعة الدقيقة للقرارات الاستراتيجية</b></p>"
            )
            sim_docx_bytes, sim_ext, sim_mime = build_word_document(
                "تقرير محاكي السياسات الاستشرافي والمتابعة التراكمية",
                "منصة منظومة القرار المتكاملة للسياسات الثقافية والإبداعية العربية",
                "\n".join(sim_body_parts),
            )
            st.download_button(
                label="📥 تحميل تقرير محاكي السياسات (Word)",
                data=sim_docx_bytes,
                file_name=f"تقرير_محاكي_السياسات{sim_ext}",
                mime=sim_mime,
                use_container_width=True
            )

            st.markdown('</div>', unsafe_allow_html=True)

        with col_sim_out:
            st.markdown('<div dir="rtl" style="text-align: right;">', unsafe_allow_html=True)
            if run_sim_btn:
                if sim_country_sel == "الدولة":
                    st.warning("⚠️ يرجى اختيار دولة عربية صحيحة أولاً.")
                else:
                    base_val = base_aacri_input
                    t_val, e_val, h_val, r_val, c_val = 68, 70, 72, 65, 82
                    for item in st.session_state.history_state:
                        if item["الدولة"] == sim_country_sel:
                            base_val = item["المؤشر المركب (AACRI)"]
                            t_val = item["البنية التقنية (20%)"]
                            e_val = item["الديناميكيات الاقتصادية (15%)"]
                            h_val = item["رأس المال البشري (30%)"]
                            r_val = item["البيئة التنظيمية والتشريعية (20%)"]
                            c_val = item["المحددات الثقافية والهوياتية (15%)"]
                            break

                    combined_boost = (var1_tech * 0.25) + (var2_eco * 0.15) + (var3_hc * 0.3) + (var4_reg * 0.2) + (var5_cult * 0.1)

                    if scenario_dropdown.startswith("📉"):
                        simulated_val = max(0.0, base_val * 0.90)
                        if base_val >= 80:
                            analysis_text = f"تحذير استباقي لدولة رائدة ({sim_country_sel}): على الرغم من رصيد البنية التقنية ({t_val}%) ورأس المال البشري ({h_val}%)، فإن غياب التدخل الاستثماري سيؤدي إلى تراجع طفيف بنسبة 10% واهتزاز مؤقت في السيادة الرقمية."
                            action_plan = f"الحفاظ على وتيرة الاستثمار في التشريعات القائمة ({r_val}%) وتجنب الجمود التكنولوجي لضمان بقاء المؤشر ضمن نطاق الأداء المرتفع."
                        elif base_val >= 51:
                            analysis_text = f"انكماش هيكلي متوسط لـ ({sim_country_sel}): تشير محاكاة السيناريو التشاؤمي في ظل البنية التقنية البالغة ({t_val}%) والتشريعات ({r_val}%) إلى تفاقم فجوة الإحلال الخوارزمي وهبوط المؤشر المركب."
                            action_plan = f"تفعيل موازنات الطوارئ الموجهة لدعم رأس المال البشري ({h_val}%) لردم الفجوات المتولدة عن ضعف الاستثمار."
                        else:
                            analysis_text = f"أزمة هيكلية حرجة لـ ({sim_country_sel}): قراءة مؤشرات البنية التحتية المتدنية ({t_val}%) ورأس المال المحدود ({h_val}%) تعكس اندثاراً محتملاً للمهن الثقافية بنسبة تفوق 32% في حال غياب الإصلاحات."
                            action_plan = f"إعلان حالة طوارئ اقتصادية واستثمارية عاجلة لترميم البنية التحتية ورفع سقف البيئة التشريعية المقدرة حالياً بـ ({r_val}%)."
                    elif scenario_dropdown.startswith("📊"):
                        simulated_val = min(100.0, base_val * (1 + (combined_boost * 0.0022)))
                        if base_val >= 80:
                            analysis_text = f"استقرار تطوري مستدام لـ ({sim_country_sel}): استناداً إلى توازن المحددات الثقافية ({c_val}%) وديناميكيات السوق البرتقالي ({e_val}%)، يتحقق نمو تدريجي مستقر نحو ريادة الابتكار."
                            action_plan = f"مواصلة برامج التحفيز التقليدي وتوسيع دائرة الشراكات الإقليمية للاستفادة القصوى من رصيد الكوادر البشرية ({h_val}%)."
                        elif base_val >= 51:
                            analysis_text = f"تقدم ملحوظ لـ ({sim_country_sel}): نجاح تدريجي في ترشيد استخدام الأدوات التوليدية، دعم مهارات 'المبدع المعزز'، وتقليص الفجوة المهنية استناداً إلى ({c_val}%)."
                            action_plan = f"توسيع برامج إعادة التأهيل المستمر (Upskilling & Reskilling) واعتماد حزم تحفيزية تستهدف الاقتصاد البرتقالي ({e_val}%)."
                        else:
                            analysis_text = f"تعافي تدريجي بطيء لـ ({sim_country_sel}): تساهم الحزم التقليدية في تقليص جزء من الفجوة الهيكلية الحرجة، متحسنة بمقدار طفيف بفضل المحددات الثقافية ({c_val}%)."
                            action_plan = f"مضاعفة التدريب المعتمد للكوادر للتعويض عن ضعف البنية التقنية الأساسية ({t_val}%) وتأهيل سوق العمل الإبداعي."
                    else:
                        simulated_val = min(100.0, base_val * (1 + (combined_boost * 0.0042)))
                        if base_val >= 80:
                            analysis_text = f"سيادة إقليمية مطلقة لـ ({sim_country_sel}): توظيف البنية التقنية المتقدمة ({t_val}%) والتشريعات المتميزة ({r_val}%) لتحقيق الريادة العالمية وتصدير النماذج الثقافية العربية الموطنة."
                            action_plan = "قيادة التحالفات التقنية الدولية، إطلاق المنصات السحابية المفتوحة، وترسيخ معايير الوسم المائي العالمية لحماية الهوية."
                        elif base_val >= 51:
                            analysis_text = f"قفزة استراتيجية كبرى لـ ({sim_country_sel}): الانتقال الناجح من الفجوة إلى مصاف الدول المتقدمة عبر الإصلاحات الهيكلية الشاملة وتوطين الذكاء الاصطناعي التوليدي."
                            action_plan = f"تفعيل مخرجات التحليل الهرمي AHP، إنشاء حاضنات تكنولوجية كبرى، واستثمار رأس المال البشري ({h_val}%) لقيادة التحول الرقمي الإبداعي."
                        else:
                            analysis_text = f"إصلاح هيكلي جذري لـ ({sim_country_sel}): نجاح غير مسبوق في كسر حاجز الجمود وتحقيق طفرة استثنائية في مؤشر الجاهزية الذكية مدفوعة بالسياسات الاستباقية."
                            action_plan = f"توجيه التدفقات الاستثمارية نحو قطاع الاتصالات والبنية التقنية ({t_val}%) وتهيئة البيئة التشريعية ({r_val}%) لحماية حقوق المبدعين."

                    simulated_val = round(simulated_val, 2)
                    delta = round(simulated_val - base_val, 2)
                    score_str_plain = get_colored_score_html(simulated_val)

                    deep_analysis = f"""
                    <div style="background: #F8FAFC; padding: 16px; border-radius: 8px; border: 1px solid #CBD5E1; margin-top: 10px;" dir="rtl">
                        <p style="font-weight: bold; color: {CCI_NAVY}; margin-bottom: 8px; text-align: right;">📊 التشخيص القياسي المخصص والمبني على درجات المحاور لدولة ({sim_country_sel}):</p>
                        <ul style="margin: 0; padding-right: 20px; color: #1E293B; line-height: 1.8; text-align: right;">
                            <li><b>1. البنية التقنية:</b> {describe_ti(t_val)}</li>
                            <li><b>2. الديناميكيات الاقتصادية:</b> {describe_ed(e_val)}</li>
                            <li><b>3. رأس المال البشري:</b> {describe_hc(h_val)}</li>
                            <li><b>4. البيئة التنظيمية:</b> {describe_rf(r_val)}</li>
                            <li><b>5. المحددات الثقافية:</b> {describe_cd(c_val)}</li>
                        </ul>
                    </div>
                    """

                    box_html = f"""
                    <div dir="rtl" style="text-align: right; background: #FFFFFF; padding: 22px; border-radius: 12px; border: 1.5px solid {CCI_ORANGE_MID}; margin-bottom: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
                      <h3 style="color: {CCI_NAVY}; font-weight: bold; margin-bottom: 8px;">📈 محاكاة دولة: {sim_country_sel} | السيناريو: {scenario_dropdown}</h3>
                      <p style="font-size: 15px; margin-bottom: 8px;"><b>القيمة المتوقعة للمؤشر:</b> {score_str_plain} (صافي التغير: <span style="font-weight: bold;">{delta:+.2f}</span>)</p>
                      <div style="background: {CCI_BG}; padding: 12px; border-radius: 8px; border-right: 4px solid {CCI_ORANGE_MID}; margin-top: 10px;">
                        <p style="margin-bottom: 6px;"><b>🔬 التحليل القياسي:</b> {analysis_text}</p>
                        <p style="margin: 0 0 8px 0; color: {CCI_ORANGE_MID}; font-weight: bold;">🛠️ خطة التحرك: {action_plan}</p>
                      </div>
                    </div>
                    """
                    sim_key = f"{sim_country_sel} - {scenario_dropdown}"
                    st.session_state.simulated_results_dict[sim_key] = {
                        "html": box_html,
                        "deep": deep_analysis,
                        "country": sim_country_sel,
                        "simulated_val": simulated_val,
                        "delta": delta,
                        "scenario": scenario_dropdown,
                        "analysis_text": analysis_text,
                        "action_plan": action_plan
                    }

            if st.session_state.simulated_results_dict:
                st.markdown("---")
                st.markdown("<h4>📋 مقارنة السيناريوهات المثبتة للدول:</h4>", unsafe_allow_html=True)
                for item in st.session_state.simulated_results_dict.values():
                    st.markdown(item["html"], unsafe_allow_html=True)
                    st.markdown(item["deep"], unsafe_allow_html=True)
                    st.markdown("---")
            else:
                st.info("📈 قم بضبط الدولة والسيناريو ومتغيرات التحفيز واضغط على زر الإضافة لتثبيت ومتابعة السيناريوهات هنا بغرض المقارنة.")
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="footer-copyright">جميع الحقوق محفوظة للدراسة البحثية © 2026</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# التبويب الثالث: لوحة دعم اتخاذ القرار
# ------------------------------------------------------------------------------
with tab3:
    st.markdown("""
    <div dir="rtl" style="text-align: right;">
        <h3>🛡️ لوحة دعم اتخاذ القرار ولوحة التطعيم الثقافي (Cultural Grafting Canvas)</h3>
        <p>استعراض وتثبيت التوصيات المخصصة لكل دولة مختارة بديناميكية تمنع التكرار وتدعم السيادة الرقمية.</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.history_state:
        st.warning("يرجى أولاً إدخال بيانات الدولة وحساب مؤشر AACRI في القسم الأول.")
    else:
        col_dec_in, col_dec_out = st.columns([1, 2], gap="large")

        with col_dec_in:
            st.markdown('<div dir="rtl" style="text-align: right;">', unsafe_allow_html=True)
            recorded_countries_dec = [item["الدولة"] for item in st.session_state.history_state]
            decision_country_sel = st.selectbox("اختر الدولة لاستعراض التوصيات", recorded_countries_dec, key="dec_country")
            generate_decision_btn = st.button("📋 إضافة وتثبيت توصيات الدولة المختارة", use_container_width=True, type="primary")

            if st.button("🗑️ مسح وإعادة تعيين لوحة القرار", use_container_width=True, type="secondary"):
                st.session_state.decision_results_dict = {}
                st.success("✅ تم مسح جميع توصيات لوحة القرار بنجاح.")
                st.rerun()

            dec_body_parts = ["<h3>🛡️ تقرير وتوصيات الدول المسجلة:</h3>"]
            if st.session_state.decision_results_dict:
                for k, v in st.session_state.decision_results_dict.items():
                    dec_body_parts.append(
                        f"<h3>تقرير وتوصيات دولة: {v['country']} (المؤشر المركب: {v['score_str']})</h3>"
                        f"<p><b>🎯 التوصيات الاستراتيجية الموجهة:</b></p>"
                        f"<ul><li>{v['recs'][0]}</li><li>{v['recs'][1]}</li></ul>"
                        f"<p><b>💡 إضافات تحليلية استراتيجية عميقة ومخصصة:</b></p>"
                        f"<div>{v['deep']}</div>"
                    )
            else:
                dec_body_parts.append("<p>لا توجد توصيات مسجلة حالياً.</p>")

            dec_body_parts.append(
                "<hr><h3>📈 ملخص النتائج التحليلية التراكمية والمعمقة لكافة أقسام المنصة:</h3>"
                "<p>تعكس هذه التوصيات متطلبات الأمن الثقافي والسيادة الرقمية ودعم المبدع المعزز.</p>"
                "<p><b>يُنصح بالمراجعة الدقيقة للقرارات الاستراتيجية</b></p>"
            )
            dec_docx_bytes, dec_ext, dec_mime = build_word_document(
                "تقرير لوحة دعم اتخاذ القرار والتطعيم الثقافي",
                "منصة منظومة القرار المتكاملة للسياسات الثقافية والإبداعية العربية",
                "\n".join(dec_body_parts),
            )
            st.download_button(
                label="📥 تحميل تقرير لوحة دعم القرار (Word)",
                data=dec_docx_bytes,
                file_name=f"تقرير_لوحة_دعم_القرار{dec_ext}",
                mime=dec_mime,
                use_container_width=True
            )

            st.markdown('</div>', unsafe_allow_html=True)

        with col_dec_out:
            st.markdown('<div dir="rtl" style="text-align: right;">', unsafe_allow_html=True)
            if generate_decision_btn:
                if not st.session_state.history_state or decision_country_sel == "الدولة":
                    st.warning("⚠️ يرجى أولاً إدخال بيانات الدولة وحساب مؤشر AACRI في القسم الأول.")
                else:
                    country_data = next((item for item in st.session_state.history_state if item["الدولة"] == decision_country_sel), None)
                    if country_data:
                        score = country_data["المؤشر المركب (AACRI)"]
                        t_val = country_data["البنية التقنية (20%)"]
                        e_val = country_data["الديناميكيات الاقتصادية (15%)"]
                        h_val = country_data["رأس المال البشري (30%)"]
                        r_val = country_data["البيئة التنظيمية والتشريعية (20%)"]
                        c_val = country_data["المحددات الثقافية والهوياتية (15%)"]
                        score_str_plain = get_colored_score_html(score)

                        if score >= 80:
                            recs_list = [
                                f"<b>تعزيز ريادة الابتكار الإقليمي لدولة ({decision_country_sel}):</b> توظيف البنية التقنية المتقدمة ({t_val}%) لتصدير النماذج اللغوية الثقافية العربية وتأسيس معايير إقليمية ناظمة.",
                                f"<b>الحوكمة المتقدمة للذكاء الاصطناعي:</b> استثمار رصيد البيئة التنظيمية ({r_val}%) لقيادة الجهود التشريعية العالمية للوسم المائي وحماية الملكية الفكرية."
                            ]
                            deep_analysis_text = f"""
- توصي منظومة القرار بإنشاء <b>'مجلس سيادي أعلى للذكاء الاصطناعي والثقافة'</b> مستفيدين من رأس المال البشري المتميز المقدر بـ ({h_val}%).
- تفعيل آليات <b>التطعيم الثقافي (Cultural Grafting)</b> لحماية الهوية عبر استثمار المحددات الثقافية المرتفعة ({c_val}%).
- خلق شراكات إقليمية استراتيجية مدعومة بالديناميكيات الاقتصادية القوية ({e_val}%) لتمويل الابتكار المفتوح.
                            """
                        elif score >= 51:
                            recs_list = [
                                f"<b>ردم الفجوة التقنية والبشرية في ({decision_country_sel}):</b> إطلاق حزم برامج إعادة التأهيل السريع بناءً على رصيد رأس المال البشري ({h_val}%).",
                                f"<b>سد الاختناقات الهيكلية:</b> تطوير أطر البيئة التنظيمية المسجلة عند ({r_val}%) لتحفيز القطاع الإبداعي وحماية المصنفات من القرصنة."
                            ]
                            deep_analysis_text = f"""
- تتطلب صانعة القرار تفعيل <b>'حاضنات الأعمال الإبداعية المشتركة'</b> لرفع كفاءة البنية التقنية البالغة ({t_val}%).
- توجيه الدعم المالي والاقتصادي نحو الأنشطة البرتقالية لتعقيم الاقتصاد ضد صدمات البطالة التكنولوجية في ضوء ({e_val}%).
- تعزيز المحتوى الرقمي العربي لتجاوز قصور المحددات الثقافية ({c_val}%).
                            """
                        else:
                            recs_list = [
                                f"<b>التدخل الاستباقي العاجل لدولة ({decision_country_sel}):</b> معالجة الاختناقات الهيكلية الحادة في البنية التقنية ({t_val}%).",
                                f"<b>احتواء الاقتصاد غير الرسمي:</b> دمج الأنشطة الإبداعية المستترة ورفع كفاءة البيئة التشريعية ({r_val}%) لتأمين تدفقات استثمارية آمنة."
                            ]
                            deep_analysis_text = f"""
- تفرض الضرورة القصوى استدعاء إطار <b>'التكامل الوظيفي الإقليمي'</b> لتعويض الفجوة في رأس المال البشري ({h_val}%).
- تنفيذ خطط طوارئ استثمارية لرفع مساهمة الاقتصاد البرتقالي المتدنية ({e_val}%).
- إطلاق برامج عاجلة للأمن الثقافي وحماية التراث الرقمي لمعالجة هشاشة المحددات الثقافية ({c_val}%).
                            """

                        st.session_state.decision_results_dict[decision_country_sel] = {
                            "country": decision_country_sel,
                            "score_str": score_str_plain,
                            "recs": recs_list,
                            "deep": bullets_to_html(deep_analysis_text)
                        }

            if st.session_state.decision_results_dict:
                for item in st.session_state.decision_results_dict.values():
                    card_html = f"""
                    <div style="background: #FFFFFF; padding: 22px; border-radius: 12px; border: 1.5px solid {CCI_ORANGE_MID}; margin-bottom: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.06);" dir="rtl">
                        <h3 style="color: {CCI_NAVY}; font-weight: bold; margin-bottom: 8px; text-align: right;">🛡️ تقرير وتوصيات دولة: {item['country']} (المؤشر المركب: {item['score_str']})</h3>
                        <div style="background: {CCI_BG}; padding: 12px; border-radius: 8px; border-right: 4px solid {CCI_ORANGE_MID}; margin-top: 10px;">
                            <p style="font-weight: bold; color: {CCI_NAVY}; margin-bottom: 6px; text-align: right;">🎯 التوصيات الاستراتيجية الموجهة:</p>
                            <ul style="margin: 0; padding-right: 20px; color: #1E293B; line-height: 1.8; text-align: right;">
                                <li>{item['recs'][0]}</li>
                                <li>{item['recs'][1]}</li>
                            </ul>
                            <hr style="border: 0; border-top: 1px solid #CBD5E1; margin: 10px 0;">
                            <p style="font-weight: bold; color: {CCI_NAVY}; margin-bottom: 6px; text-align: right;">💡 إضافات تحليلية استراتيجية عميقة ومخصصة:</p>
                            <div style="color: #1E293B; line-height: 1.8; text-align: right; padding-right: 20px;">
                                {item['deep']}
                            </div>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
            else:
                st.info("🛡️ يرجى اختيار الدولة المسجلة والضغط على زر الإضافة لتثبيت التوصيات هنا.")
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="footer-copyright">جميع الحقوق محفوظة للدراسة البحثية © 2026</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# التبويب الرابع: التقرير التنفيذي الموحد
# ------------------------------------------------------------------------------
with tab4:
    st.markdown("""
    <div dir="rtl" style="text-align: right;">
        <h3>📑 أداة تصدير التقرير التنفيذي الموحد لسياسات الصناعات الثقافية والإبداعية</h3>
        <p>ملخص استراتيجي شامل يدمج نتائج التشخيص الوصفي، التحليل العميق للمحاور، وشجرة نقاط الرفع لدونيلا ميدوز في تقرير موحد جاهز للعرض على القيادات العليا.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 تحديث وتوليد التقرير التنفيذي الموحد", use_container_width=True, type="primary"):
        if not st.session_state.history_state:
            st.warning("📂 لا توجد بيانات مسجلة كافية حتى الآن. يرجى إدخال تشخيص دولة واحدة على الأقل في القسم الأول.")
        else:
            df_rep = pd.DataFrame(st.session_state.history_state).sort_values(
                by="المؤشر المركب (AACRI)", ascending=False
            ).reset_index(drop=True)

            top_row = df_rep.iloc[0]
            top_country = top_row["الدولة"]
            top_score = top_row["المؤشر المركب (AACRI)"]
            top_score_str = get_colored_score_html(top_score)
            region_info = get_region_and_features(top_country)

            cards_html_list = []
            word_blocks_html = ""

            for idx, row in df_rep.iterrows():
                c_name = row['الدولة']
                c_score = row['المؤشر المركب (AACRI)']
                c_diag = row['التقييم المنظومي']

                t_val = row['البنية التقنية (20%)']
                e_val = row['الديناميكيات الاقتصادية (15%)']
                h_val = row['رأس المال البشري (30%)']
                r_val = row['البيئة التنظيمية والتشريعية (20%)']
                c_val = row['المحددات الثقافية والهوياتية (15%)']

                if c_score >= 80:
                    specific_strategic_angle = f"تتمتع دولة ({c_name}) بأداء متقدم ومستدام ({c_score}%)، مما يمنحها ميزة قيادة التحالفات الرقمية الإقليمية، وتوطين النماذج التوليدية الضخمة، وتعظيم عوائد الاقتصاد البرتقالي المستند للابتكار المفتوح."
                    specific_policy_action = f"تأسيس 'مجلس سيادي أعلى للذكاء الاصطناعي'، إطلاق مبادرات تصدير المعايير الثقافية، وتوظيف رأس المال البشري المتميز ({h_val}%)."
                elif c_score >= 51:
                    specific_strategic_angle = f"تسجل دولة ({c_name}) جاهزية متوسطة ({c_score}%) تواجه بعض الاختناقات الهيكلية في سلاسل القيمة الإبداعية والتشريعات التنظيمية؛ وهو ما يتطلب تدخلاً استباقياً لردم الفجوات."
                    specific_policy_action = f"تنفيذ برامج إعادة تأهيل مكثفة (Upskilling) للكوادر العاملة، وتوسيع نطاق الحاضنات الاستثمارية لدعم الاقتصاد البرتقالي ({e_val}%)."
                else:
                    specific_strategic_angle = f"تظهر قراءة دولة ({c_name}) فجوة هيكلية حرجة ({c_score}%) تهدد باستبعاد الكوادر الوطنية من سوق العمل الرقمي وتستوجب خطط طوارئ عاجلة لترميم البنية التحتية."
                    specific_policy_action = f"إعلان حالة طوارئ استثمارية لرفع سقف البنية التقنية المتدنية ({t_val}%) وتطوير أطر البيئة التشريعية المقدرة بـ ({r_val}%)."

                matched_sims = [s_key for s_key in st.session_state.simulated_results_dict.keys() if s_key.startswith(c_name)]
                if matched_sims:
                    latest_sim_key = matched_sims[-1]
                    sim_data_obj = st.session_state.simulated_results_dict[latest_sim_key]
                    sim_detail = (
                        f"تم تطبيق سيناريو ({sim_data_obj['scenario']})؛ "
                        f"حيث بلغت القيمة المتوقعة للمؤشر ({sim_data_obj['simulated_val']}%) بصافي تغير قدره ({sim_data_obj['delta']:+.2f}). "
                        f"<b>التحليل:</b> {sim_data_obj['analysis_text']} "
                        f"<b>خطة التحرك:</b> {sim_data_obj['action_plan']}"
                    )
                else:
                    sim_detail = (
                        "<span style='background-color: #FEF3C7; color: #92400E; padding: 3px 8px; border-radius: 4px; font-weight: bold; border: 1px solid #FCD34D;'>"
                        "⚠️ تنبيه توثيقي: لم يتم تسجيل أو تثبيت أي سيناريو استشرافي لهذا البلد في محاكي السياسات."
                        "</span>"
                    )

                if c_name in st.session_state.decision_results_dict:
                    dec_item = st.session_state.decision_results_dict[c_name]
                    dec_detail = f"{dec_item['recs'][0]} — وكذلك: {dec_item['recs'][1]}"
                else:
                    dec_detail = (
                        "<span style='background-color: #FEF3C7; color: #92400E; padding: 3px 8px; border-radius: 4px; font-weight: bold; border: 1px solid #FCD34D;'>"
                        "⚠️ تنبيه توثيقي: لم يتم اعتماد أو تثبيت توصيات لوحة القرار والتطعيم الثقافي لهذا البلد."
                        "</span>"
                    )

                single_card_html = f"""
                <div style="background: #FFFFFF; padding: 22px; border-radius: 12px; border: 1.5px solid {CCI_ORANGE_MID}; margin-bottom: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);" dir="rtl">
                    <h4 style="color: {CCI_NAVY}; font-weight: bold; margin-top: 0; margin-bottom: 10px; font-size: 16.5px;">
                        📌 التشخيص المنظومي والنتائج الاستراتيجية المستقلة لدولة: <span style="color: {CCI_ORANGE_MID};">{c_name}</span> (المؤشر المركب: {c_score}%)
                    </h4>
                    <p style="margin-bottom: 8px; color: #334155; font-size: 14px;"><b>التقييم التشخيصي الشامل:</b> {c_diag}</p>
                    <div style="background: {CCI_BG}; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-right: 4px solid {CCI_ORANGE_MID};">
                        <p style="margin: 0 0 6px 0; font-weight: bold; color: {CCI_NAVY}; font-size: 13.5px;">• زاوية التحليل الاستراتيجي المتميزة:</p>
                        <p style="margin: 0; color: #1E293B; font-size: 13.5px; line-height: 1.7;">{specific_strategic_angle}</p>
                    </div>
                    <ul style="margin: 0; padding-right: 20px; color: #1E293B; font-size: 13.5px; line-height: 1.8;">
                        <li><b>محاور الجاهزية الذكية المرصودة:</b> البنية التقنية ({t_val}%) | رأس المال البشري ({h_val}%) | البيئة التشريعية ({r_val}%) | الاقتصاد البرتقالي ({e_val}%) | المحددات الثقافية ({c_val}%)</li>
                        <li><b>المسار التنفيذي الموصى به:</b> {specific_policy_action}</li>
                        <li style="margin-top: 8px;"><b>🔬 مخرجات محاكي السياسات الاستشرافي:</b><br>{sim_detail}</li>
                        <li style="margin-top: 8px;"><b>🛡️ مخرجات لوحة دعم القرار والتطعيم الثقافي:</b><br>{dec_detail}</li>
                    </ul>
                </div>
                """
                cards_html_list.append(single_card_html)
                word_blocks_html += single_card_html

            st.markdown(f"""
            <div dir="rtl" style="text-align: right; background: #FFFFFF; padding: 30px; border-radius: 14px; border: 2px solid {CCI_ORANGE_MID}; line-height: 1.9; box-shadow: 0 6px 20px rgba(0,0,0,0.08);">
              <div style="text-align: center; border-bottom: 2px solid {CCI_ORANGE_MID}; padding-bottom: 15px; margin-bottom: 25px;">
                <h2 style="color: {CCI_NAVY}; font-weight: 800; margin: 0;">📑 التقرير التنفيذي الموحد لسياسات الصناعات الثقافية والإبداعية العربية</h2>
                <p style="color: #64748B; font-size: 14.5px; margin-top: 6px;">ملخص استراتيجي موجه للقيادات العليا وصناع القرار - بناءً على مخرجات الدراسة المنهجية والتفكير المنظومي (AACRI)</p>
              </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background: {CCI_BG}; padding: 18px; border-radius: 10px; border-right: 5px solid {CCI_ORANGE_MID}; margin-bottom: 25px;" dir="rtl">
                <h4 style="color: {CCI_NAVY}; margin-top: 0;">🏆 مؤشرات الأداء العام والريادة الإقليمية (التصنيف الجغرافي والديموغرافي والتاريخي):</h4>
                <p style="margin-bottom: 8px;">تتصدّر الدولة التالية قائمة الجاهزية الذكية وفق الترتيب التنازلي للمؤشر المركب: <span style="font-weight: bold; color: {CCI_ORANGE_MID};">{top_country}</span> بقيمة مركبة تبلغ {top_score_str}.</p>
                <p style="margin-bottom: 8px; line-height: 1.8;"><b>الإطار الإقليمي والأبعاد الديموغرافية والتاريخية:</b> {region_info}</p>
                <p style="margin: 0;">إجمالي الدول الخاضعة للتشخيص والتحليل المنظومي حتى الآن: <b>{len(df_rep)} دولة عربية</b>.</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<h4 style='color: #0A192F; margin-bottom: 12px;'>📋 ترتيب الملخص التراكمي للدول:</h4>", unsafe_allow_html=True)
            for idx, row in df_rep.iterrows():
                s = row['المؤشر المركب (AACRI)']
                s_str = get_colored_score_html(s)
                summary_card = f"""
                <div style="margin-bottom: 12px; line-height: 1.8; background: #F8FAFC; padding: 12px 16px; border-radius: 8px; border: 1px solid #E2E8F0;" dir="rtl">
                    <b>المركز ({idx + 1}): {row['الدولة']}</b> — المؤشر المركب: {s_str} | البنية التقنية: {row['البنية التقنية (20%)']}% | رأس المال البشري: {row['رأس المال البشري (30%)']}% <br>
                    <span style="color: #475569; font-size: 13.5px;"><b>التقييم التشخيصي:</b> {row['التقييم المنظومي']}</span>
                </div>
                """
                st.markdown(summary_card, unsafe_allow_html=True)

            for card_code in cards_html_list:
                st.markdown(card_code, unsafe_allow_html=True)

            st.markdown("""
            </div>
            """, unsafe_allow_html=True)

            exec_body_html = f"""
                <h3>🏆 مؤشرات الأداء العام والريادة الإقليمية:</h3>
                <p>تتصدّر الدولة التالية قائمة الجاهزية الذكية وفق الترتيب التنازلي للمؤشر المركب: <b>{top_country}</b> بقيمة مركبة تبلغ {top_score_str}.</p>
                <p><b>الإطار الإقليمي والأبعاد الديموغرافية والتاريخية:</b> {region_info}</p>
                <p>إجمالي الدول الخاضعة للتشخيص والتحليل المنظومي حتى الآن: <b>{len(df_rep)} دولة عربية</b>.</p>
                <hr>
                <h3>📈 ملخص النتائج التحليلية التراكمية والمعمقة لكافة أقسام المنصة:</h3>
                {word_blocks_html}
                <p><b>يُنصح بالمراجعة الدقيقة للقرارات الاستراتيجية</b></p>
            """
            exec_docx_bytes, exec_ext, exec_mime = build_word_document(
                "التقرير التنفيذي الموحد لسياسات الصناعات الثقافية والإبداعية العربية",
                "ملخص استراتيجي موجه للقيادات العليا وصناع القرار (AACRI)",
                exec_body_html,
            )
            st.download_button(
                label="📥 تحميل التقرير التنفيذي في ملف مستند (Word)",
                data=exec_docx_bytes,
                file_name=f"التقرير_التنفيذي_للسياسات_الثقافية{exec_ext}",
                mime=exec_mime,
                use_container_width=True
            )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="footer-copyright">جميع الحقوق محفوظة للدراسة البحثية © 2026</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# التبويب الخامس: ملاحق المشروع والوثائق (PDF)
# ------------------------------------------------------------------------------
with tab5:
    st.markdown("""
    <div dir="rtl" style="text-align: right;">
        <h3>📚 ملاحق المشروع والوثائق البحثية الداعمة (PDF)</h3>
        <p>استعراض وتحميل ملاحق الدراسة الأساسية المرفقة مستودعياً بصيغة PDF لتمكين لجان التحكيم والباحثين من الاطلاع على التوثيق العلمي والمنهجي الكامل.</p>
    </div>
    """, unsafe_allow_html=True)

    appendices = [
        {"title": "ملحق 1: الاستقراء الببليومتري ونمذجة الموضوعات وتشخيص الفجوة المعرفية", "filename": "1 ملحق .pdf"},
        {"title": "ملحق 2: المسارات الفرعية لخرائط حلقات السببية (CLDs)", "filename": "2 ملحق.pdf"},
        {"title": "ملحق 3: المصفوفة الإجرائية للمحاور الرئيسة والأبعاد الأساسية والأبعاد الفرعية والمتغيرات للمؤشر (AACRI)", "filename": "3 ملحق.pdf"},
        {"title": "ملحق 4: المقارنات الزوجية (Pairwise Comparisons)", "filename": "4 ملحق.pdf"},
        {"title": "ملحق 5: معادلات المؤشر المركب والتطبيع والقياس", "filename": "5 ملحق.pdf"},
        {"title": "ملحق 6: بروتوكول الاختبار الميداني والوصول التفاعلي لمنصة 'منظومة القرار المتكاملة'", "filename": "6 ملحق.pdf"}
    ]

    for app in appendices:
        with st.expander(f"📑 {app['title']}"):
            file_path = app["filename"]
            if os.path.exists(file_path):
                st.success(f"✅ الملف متوفر وجاهز للتحميل: `{file_path}`")

                with open(file_path, "rb") as f:
                    pdf_bytes = f.read()
                st.download_button(
                    label=f"📥 تحميل {app['title']} (PDF)",
                    data=pdf_bytes,
                    file_name=file_path,
                    mime="application/pdf",
                    use_container_width=True,
                    key=f"dl_{file_path}"
                )
            else:
                st.warning(f"⚠️ تنبيه: الملف `{file_path}` غير موجود حالياً في مجلد المشروع الرئيسي على GitHub. تأكد من تطابق اسم الملف تماماً في المستودع.")

    st.markdown(f'<div class="footer-copyright">جميع الحقوق محفوظة للدراسة البحثية © 2026</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# التبويب السادس: دليل المستخدم الرسمي (User Guide)
# ------------------------------------------------------------------------------
with tab6:
    st.markdown("""
    <div dir="rtl" style="text-align: right;">
        <h3>📖 دليل المستخدم الرسمي لمنصة "منظومة القرار المتكاملة" (PDF)</h3>
        <p>استعراض وتحميل دليل المستخدم والتوثيق المنهجي الرسمي للمنصة بصيغة PDF لتمكين المحكمين والمستخدمين من الاطلاع الفوري.</p>
    </div>
    """, unsafe_allow_html=True)

    user_guide_filename = "دليل المستخدم.pdf"

    with st.expander(f"📑 دليل المستخدم الرسمي للمنصة"):
        if os.path.exists(user_guide_filename):
            st.success(f"✅ ملف دليل المستخدم متوفر وجاهز للتحميل: `{user_guide_filename}`")

            with open(user_guide_filename, "rb") as f:
                pdf_bytes_ug = f.read()
            st.download_button(
                label="📥 تحميل دليل المستخدم الرسمي (PDF)",
                data=pdf_bytes_ug,
                file_name=user_guide_filename,
                mime="application/pdf",
                use_container_width=True,
                key=f"dl_{user_guide_filename}"
            )
        else:
            st.warning(f"⚠️ تنبيه: الملف `{user_guide_filename}` غير موجود حالياً في مجلد المشروع الرئيسي على GitHub. تأكد من تطابق اسم الملف تماماً في المستودع.")

    st.markdown(f'<div class="footer-copyright">جميع الحقوق محفوظة للدراسة البحثية © 2026</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# التبويب السابع: سجل الزوار والأفراد (مخصص للأدمن فقط) - مع استعراض السجلات القديمة
# ------------------------------------------------------------------------------
if st.session_state.current_user == "admin" and tab_admin is not None:
    with tab_admin:
        st.markdown("""
        <div dir="rtl" style="text-align: right;">
            <h3>🔒 سجل الزوار والأفراد المسجلين (خاص بالأدمن فقط)</h3>
            <p>يتيح لك هذا القسم متابعة جميع الزيارات القديمة والجديدة وتواريخ الدخول المسجلة بشكل دائم عبر ملف السيرفر.</p>
        </div>
        """, unsafe_allow_html=True)

        visitors_data_list = load_visitors_log_from_file()
        if visitors_data_list:
            df_visitors = pd.DataFrame(visitors_data_list)
            st.dataframe(df_visitors, use_container_width=True)

            csv_visitors = df_visitors.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 تحميل سجل الزوار والأفراد وعناوين IP (CSV)",
                data=csv_visitors,
                file_name="سجل_الزوار_وعناوين_IP.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("ℹ️ لا توجد سجلات زوار مسجلة حتى الآن في الملف الخارجي.")

        st.markdown(f'<div class="footer-copyright">جميع الحقوق محفوظة للدراسة البحثية © 2026</div>', unsafe_allow_html=True)
