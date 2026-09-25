import os
import random
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# إعدادات صفحة Streamlit وتطبيق الهوية البصرية (RTL)
# ==============================================================================
st.set_page_config(
    page_title="منصة منظومة القرار المتكاملة للسياسات الثقافية والإبداعية العربية",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# الألوان التراثية الرسمية للمنصة
CBE_ORANGE_DARK = "#78350F"  # برتقالي غامق جداً قاتم
CBE_ORANGE_MID = "#B45309"   # برتقالي غامق تراثي
CBE_ORANGE_LIGHT = "#D97706" # برتقالي أفتح نسبياً عند التحديد
CBE_NAVY = "#0A192F"         # أزرق ملكي عميق
CBE_BG = "#F8FAFC"           # خلفية ناعمة

CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Cairo', sans-serif !important;
    direction: rtl !important;
    text-align: right !important;
    background-color: {CBE_BG} !important;
}}

.stApp {{
    background-color: {CBE_BG} !important;
    direction: rtl !important;
    text-align: right !important;
}}

div.stMarkdown, div.stText, div.stSelectbox, div.stSlider, div.stDataFrame, div.stTable {{
    direction: rtl !important;
    text-align: right !important;
}}

/* تخصيص التبويبات (Tabs) بألوان قاتمة وعند التحديد أو المرور تصبح برتقالية */
.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
    background-color: {CBE_NAVY};
    padding: 10px;
    border-radius: 12px;
    direction: rtl !important;
}}

.stTabs [data-baseweb="tab"] {{
    background-color: {CBE_ORANGE_DARK} !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    font-weight: 700 !important;
    font-family: 'Cairo', sans-serif !important;
    border: 1px solid rgba(255,255,255,0.1);
}}

.stTabs [data-baseweb="tab"]:hover {{
    background-color: {CBE_ORANGE_MID} !important;
    color: #FFFFFF !important;
}}

.stTabs [aria-selected="true"] {{
    background-color: {CBE_ORANGE_MID} !important;
    color: #FBBF24 !important;
    border: 2px solid #FBBF24 !important;
}}

/* جعل الأزرار بعرض الشاشة وتنسيقها */
.stButton > button {{
    width: 100% !important;
    border-radius: 8px !important;
    font-family: 'Cairo', sans-serif !important;
    font-weight: 700 !important;
}}

/* تنسيق زر الطباعة المباشر الفعال */
.print-btn-html {{
    display: block;
    width: 100%;
    background-color: {CBE_ORANGE_MID};
    color: white;
    text-align: center;
    padding: 10px 20px;
    border-radius: 8px;
    font-family: 'Cairo', sans-serif;
    font-weight: 700;
    text-decoration: none;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    transition: background 0.3s ease;
    cursor: pointer;
    border: none;
    margin-top: 10px;
    margin-bottom: 10px;
}}
.print-btn-html:hover {{
    background-color: {CBE_ORANGE_DARK};
    color: #FBBF24;
}}

.header-center {{
    text-align: center !important;
    background: linear-gradient(135deg, rgba(10, 25, 47, 0.95) 0%, rgba(120, 53, 15, 0.90) 100%),
                url('https://images.unsplash.com/photo-1461360370896-922624d12aa1?q=80&w=1600&auto=format&fit=crop') !important;
    background-size: cover !important;
    background-position: center !important;
    color: #FFFFFF !important;
    padding: 40px 20px !important;
    border-radius: 16px !important;
    border-bottom: 5px solid {CBE_ORANGE_MID} !important;
    box-shadow: 0 12px 35px rgba(0,0,0,0.35) !important;
    margin-bottom: 20px !important;
    direction: rtl !important;
}}

.header-center h1 {{
    color: #FBBF24 !important;
    font-size: 26px !important;
    font-weight: 800 !important;
    margin-bottom: 12px !important;
    text-shadow: 0 2px 6px rgba(0,0,0,0.7) !important;
}}

.header-center h3 {{
    color: #F1F5F9 !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    line-height: 1.6 !important;
    margin-bottom: 0px !important;
}}

/* شريط الأخبار المتحرك */
.ticker-wrap {{
    width: 100%;
    background: linear-gradient(90deg, {CBE_NAVY} 0%, {CBE_ORANGE_DARK} 100%);
    border-top: 2px solid {CBE_ORANGE_MID};
    border-bottom: 2px solid {CBE_ORANGE_MID};
    overflow: hidden;
    white-space: nowrap;
    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    margin-bottom: 25px;
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
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==============================================================================
# إدارة جلسة الدخول (Authentication)
# ==============================================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        login_container = st.container()
        with login_container:
            st.markdown(f"""
            <div style="background: #FFFFFF; padding: 30px; border-radius: 16px; border: 2px solid {CBE_ORANGE_MID}; box-shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: right;" dir="rtl">
                <h2 style="color: {CBE_NAVY}; text-align: center; font-weight: 800; margin-bottom: 10px;">🏛️ منصة منظومة القرار المتكاملة</h2>
                <p style="color: #475569; text-align: center; font-size: 14px; line-height: 1.6; margin-bottom: 25px;">
                    نموذج تشغيلي ذكي لدعم سياسات الصناعات الثقافية والإبداعية العربية في عصر الذكاء الاصطناعي بمنظور التفكير المنظومي. يرجى تسجيل الدخول للمتابعة.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            username = st.text_input("اسم المستخدم (Username)", placeholder="أدخل اسم المستخدم...")
            password = st.text_input("كلمة المرور (Password)", type="password", placeholder="أدخل كلمة المرور...")
            
            if st.button("🔐 تسجيل الدخول للمنصة", use_container_width=True):
                if username == "user" and password == "123":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("⚠️ اسم المستخدم أو كلمة المرور غير صحيحة. (تجريبي: user / 123)")
    st.stop()

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
        return f"محددات ثقافية وهوياتية راسخة (%{val}) توفر حصانة رقمية عالية ومحتوى عربياً غنياً بالأرشفة الثلاثية."
    elif val >= 50:
        return f"محددات ثقافية متوازنة (%{val}) تتطلب تعزيز المحتوى الرقمي الثقافي والتراثي المتاح بالعربية."
    else:
        return f"هشاشة واضحة في المحددات الثقافية الهوياتية (%{val}) تستوجب تفعيل دروع الأمن الثقافي الرقمي."

def get_region_and_features(country_name):
    gulf_countries = ["دولة قطر", "المملكة العربية السعودية", "دولة الإمارات العربية المتحدة", "سلطنة عمان", "مملكة البحرين", "دولة الكويت"]
    nile_valley = ["جمهورية مصر العربية", "جمهورية السودان"]
    north_africa = ["المملكة المغربية", "الجمهورية التونسية", "الجمهورية الجزائرية الديمقراطية الشعبية", "ليبيا", "الجمهورية الإسلامية الموريتانية"]
    levant = ["المملكة الأردنية الهاشمية", "الجمهورية اللبنانية", "الجمهورية العربية السورية", "دولة فلسطين"]
    
    if country_name in gulf_countries:
        return f"تنتمي {country_name} إلى إقليم الخليج العربي (شبه الجزيرة العربية)، وهي منطقة تتميز بكتلة مالية استثمارية واعدة، وسرعات بنية تحتية رقمية فائقة، وتركيز استراتيجي عالٍ على التحول الذكي وقيادة الابتكار التقني."
    elif country_name in nile_valley:
        return f"تتمركز {country_name} في إقليم وادي النيل، متسلحة بعمق تاريخي وحضاري فريد، وثقل ديموغرافي بشري كبير، ورأس مال أكاديمي وثقافي عريق يمثل مرتكزاً أساسياً للإنتاج الإبداعي."
    elif country_name in north_africa:
        return f"تتوزع {country_name} في نطاق إقليم شمال إفريقيا، متخِذةً من التنوع الثقافي واللغوي المتوسطي والأفريقي جسوراً حية للتواصل الإبداعي وعقد الشراكات العابرة للحدود."
    elif country_name in levant:
        return f"ترتبط {country_name} بإقليم بلاد الشام التاريخي، متميزة بتراث إبداعي فكري غني، وشبكات مجتمعية نشطة، وكفاءات بشرية عالية التأهل في مختلف حقول المعرفة والفنون."
    else:
        return f"تندرج {country_name} ضمن نطاق العالم العربي الموسع، محتضنةً خصائص جيوستراتيجية وتاريخية فريدة داعمة للتكامل الإقليمي وتجسير مسارات التنمية المستدامة."

# تهيئة الذاكرة المؤقتة للبيانات
if "history_state" not in st.session_state:
    st.session_state.history_state = []
if "simulated_results_dict" not in st.session_state:
    st.session_state.simulated_results_dict = {}
if "decision_results_dict" not in st.session_state:
    st.session_state.decision_results_dict = {}

# ==============================================================================
# التروياسة والشريط الإخباري
# ==============================================================================
st.markdown(f"""
<div class="header-center">
<h1>نموذج مقترح لتطوير منصة منظومة القرار المتكاملة للسياسات الثقافية والإبداعية العربية</h1>
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
    <span class="ticker-item">| 📑 التقرير التنفيذي الموحد للقيادات العليا وإطار دونيلا ميدوز لنقاط الرفع | جميع الحقوق محفوظة للدراسة البحثية</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# التقسيم الرئيسي إلى 4 تبويبات (Tabs)
# ==============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 تشخيص مؤشر الجاهزية (AACRI)", 
    "📈 محاكي السياسات (Policy Simulator)", 
    "🛡️ لوحة دعم اتخاذ القرار", 
    "📑 التقرير التنفيذي الموحد"
])

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

                st.markdown(f"""
                <div dir="rtl" style="text-align: right; background: #FFFFFF; padding: 25px; border-radius: 12px; border: 1.5px solid {CBE_ORANGE_MID}; line-height: 1.9; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
                  <h3 style="color: {CBE_NAVY}; font-weight: bold; margin-bottom: 12px;">📊 نتائج التشخيص المنظومي للدولة العربية (إطار AACRI - 69 متغيراً)</h3>
                  <p style="font-size: 15px; margin-bottom: 8px;"><b>النموذج الخاضع للتشخيص:</b> <span style="color: {CBE_NAVY}; font-weight: bold;">{country_sel}</span></p>
                  <p style="font-size: 16px; margin-bottom: 12px;"><b>القيمة المركبة لمؤشر الجاهزية الذكية (AACRI):</b> <span style="font-size: 18px;">{score_str_plain}</span></p>
                  <div style="background: {CBE_BG}; padding: 16px; border-radius: 8px; border-right: 5px solid {CBE_ORANGE_MID}; margin-top: 10px;">
                    <p style="margin: 0 0 8px 0; font-weight: bold; color: {CBE_NAVY};">التقييم التشخيصي والتفصيل المنظومي:</p>
                    <p style="margin: 0; color: #1E293B; font-size: 14.5px;">{detailed_diag}</p>
                  </div>
                </div>
                """, unsafe_allow_html=True)

                categories = ['البنية التقنية (20%)', 'الديناميكيات الاقتصادية (15%)', 'رأس المال البشري (30%)', 'البيئة التنظيمية والتشريعية (20%)', 'المحددات الثقافية والهوياتية (15%)']
                scores_list = [ti_slider, ed_slider, hc_slider, rf_slider, cd_slider]
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=scores_list, theta=categories, fill='toself', name=country_sel, line_color=CBE_ORANGE_MID))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), paper_bgcolor="#FFFFFF", font=dict(family="Cairo", size=13))
                st.plotly_chart(fig, use_container_width=True)
        else:
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
        df_history.insert(0, "م", range(1, len(df_history) + 1))
        st.dataframe(df_history, use_container_width=True, hide_index=True)

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
        st.info("📂 لا توجد دول مسجلة حتى الآن. قم بإجراء التشخيص في الأعلى لتسجيل وترتيب الدول.")

    st.markdown("<br>", unsafe_allow_html=True)
    # تفعيل زر الطباعة الفعال عبر HTML Click Event
    st.markdown("""
    <button onclick="window.print();" class="print-btn-html">
        📥 تصدير وطباعة تقرير القسم الأول (PDF / طباعة)
    </button>
    """, unsafe_allow_html=True)

    with st.expander("📂 استعراض المصفوفة الإجرائية للمحاور الرئيسة وأبعادها وفق مؤشر (AACRI)"):
        st.markdown("""
        <div dir="rtl" style="text-align: right;">
        <ul>
            <li><b>البنية التقنية (وزن 20%):</b> يضم مؤشرات سعة وتدفق البيانات الضخمة، سرعات الإنترنت عريض الباند، وتوطين النماذج اللغوية الكبيرة (LLMs).</li>
            <li><b>الديناميكيات الاقتصادية (وزن 15%):</b> يضم مساهمة الاقتصاد البرتقالي في الناتج المحلي، الصادرات الإبداعية، وصفقات رأس المال المخاطر (VC).</li>
            <li><b>رأس المال البشري (وزن 30%):</b> يضم نسب التدريب المعتمد في هندسة الأوامر (Prompt Engineering) وبرامج إعادة التأهيل (Reskilling & Upskilling) وتمكين 'المبدع المعزز'.</li>
            <li><b>البيئة التنظيمية والتشريعية (وزن 20%):</b> يضم تشريعات الملكية الفكرية المشتركة، أطر المسؤولية (Liability), وآليات الوسم المائي (Watermarking).</li>
            <li><b>المحددات الثقافية والهوياتية (وزن 15%):</b> يضم نسبة المحتوى الرقمي المتاح بالعربية، أرشفة التراث ثلاثي الأبعاد (3D Archives), ومؤشرات الأمن الثقافي.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        axes_names = ['البنية التقنية (20%)', 'الديناميكيات الاقتصادية (15%)', 'رأس المال البشري (30%)', 'البيئة التنظيمية والتشريعية (20%)', 'المحددات الثقافية والهوياتية (15%)']
        weights_vals = [20, 15, 30, 20, 15]
        
        # ضبط اتجاه ونصوص الرسم البياني ليكون من اليمين لليسار
        fig_bar = px.bar(x=axes_names, y=weights_vals, text=weights_vals, labels={'x': 'المحاور', 'y': 'الوزن (%)'})
        fig_bar.update_layout(
            title=dict(text="توزيع الأوزان النسبية لمحاور المؤشر وفق التحليل الهرمي AHP", x=0.99, xanchor='right'),
            xaxis=dict(title="المحاور الرئيسة", categoryorder='array', categoryarray=axes_names),
            yaxis=dict(title="الوزن النسبي (%)"),
            paper_bgcolor="#FFFFFF",
            font=dict(family="Cairo", size=13)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown(f'<div class="footer-copyright">جميع الحقوق محفوظة للدراسة البحثية</div>', unsafe_allow_html=True)

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

    col_sim_in, col_sim_out = st.columns([1, 2], gap="large")

    with col_sim_in:
        st.markdown('<div dir="rtl" style="text-align: right;">', unsafe_allow_html=True)
        recorded_countries_sim = [item["الدولة"] for item in st.session_state.history_state] if st.session_state.history_state else ARAB_COUNTRIES
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
            
        st.markdown('</div>', unsafe_allow_html=True)

    with col_sim_out:
        st.markdown('<div dir="rtl" style="text-align: right;">', unsafe_allow_html=True)
        if run_sim_btn:
            if sim_country_sel == "الدولة":
                st.warning("⚠️ يرجى اختيار دولة عربية صحيحة أولاً.")
            else:
                base_val = base_aacri_input
                t_val, e_val, h_val, r_val, c_val = 68, 70, 72, 65, 82  
                if st.session_state.history_state:
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
                    <p style="font-weight: bold; color: {CBE_NAVY}; margin-bottom: 8px; text-align: right;">📊 التشخيص القياسي المخصص والمبني على درجات المحاور لدولة ({sim_country_sel}):</p>
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
                <div dir="rtl" style="text-align: right; background: #FFFFFF; padding: 22px; border-radius: 12px; border: 1.5px solid {CBE_ORANGE_MID}; margin-bottom: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
                  <h3 style="color: {CBE_NAVY}; font-weight: bold; margin-bottom: 8px;">📈 محاكاة دولة: {sim_country_sel} | السيناريو: {scenario_dropdown}</h3>
                  <p style="font-size: 15px; margin-bottom: 8px;"><b>القيمة المتوقعة للمؤشر:</b> {score_str_plain} (صافي التغير: <span style="font-weight: bold;">{delta:+.2f}</span>)</p>
                  <div style="background: {CBE_BG}; padding: 12px; border-radius: 8px; border-right: 4px solid {CBE_ORANGE_MID}; margin-top: 10px;">
                    <p style="margin-bottom: 6px;"><b>🔬 التحليل القياسي:</b> {analysis_text}</p>
                    <p style="margin: 0 0 8px 0; color: {CBE_ORANGE_MID}; font-weight: bold;">🛠️ خطة التحرك: {action_plan}</p>
                  </div>
                </div>
                """
                sim_key = f"{sim_country_sel} - {scenario_dropdown}"
                st.session_state.simulated_results_dict[sim_key] = {"html": box_html, "deep": deep_analysis}

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
    # تفعيل زر الطباعة الفعال عبر HTML Click Event
    st.markdown("""
    <button onclick="window.print();" class="print-btn-html">
        📥 تصدير وطباعة تقرير المحاكي (PDF / طباعة)
    </button>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="footer-copyright">جميع الحقوق محفوظة للدراسة البحثية</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# التبويب الثالث: لوحة دعم اتخاذ القرار (مطابق جمالياً تماماً للقسم الثاني وموجه لليمين)
# ------------------------------------------------------------------------------
with tab3:
    st.markdown("""
    <div dir="rtl" style="text-align: right;">
        <h3>🛡️ لوحة دعم اتخاذ القرار ولوحة التطعيم الثقافي (Cultural Grafting Canvas)</h3>
        <p>استعراض وتثبيت التوصيات المخصصة لكل دولة مختارة بديناميكية تمنع التكرار وتدعم السيادة الرقمية.</p>
    </div>
    """, unsafe_allow_html=True)

    col_dec_in, col_dec_out = st.columns([1, 2], gap="large")

    with col_dec_in:
        st.markdown('<div dir="rtl" style="text-align: right;">', unsafe_allow_html=True)
        recorded_countries_dec = [item["الدولة"] for item in st.session_state.history_state] if st.session_state.history_state else ARAB_COUNTRIES
        decision_country_sel = st.selectbox("اختر الدولة لاستعراض التوصيات", recorded_countries_dec, key="dec_country")
        generate_decision_btn = st.button("📋 إضافة وتثبيت توصيات الدولة المختارة", use_container_width=True, type="primary")
        
        if st.button("🗑️ مسح وإعادة تعيين لوحة القرار", use_container_width=True, type="secondary"):
            st.session_state.decision_results_dict = {}
            st.success("✅ تم مسح جميع توصيات لوحة القرار بنجاح.")
            st.rerun()
            
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
* توصي منظومة القرار بإنشاء <b>'مجلس سيادي أعلى للذكاء الاصطناعي والثقافة'</b> مستفيدين من رأس المال البشري المتميز المقدر بـ ({h_val}%).
* تفعيل آليات <b>التطعيم الثقافي (Cultural Grafting)</b> لحماية الهوية عبر استثمار المحددات الثقافية المرتفعة ({c_val}%).
* خلق شراكات إقليمية استراتيجية مدعومة بالديناميكيات الاقتصادية القوية ({e_val}%) لتمويل الابتكار المفتوح.
                        """
                    elif score >= 51:
                        recs_list = [
                            f"<b>ردم الفجوة التقنية والبشرية في ({decision_country_sel}):</b> إطلاق حزم برامج إعادة التأهيل السريع بناءً على رصيد رأس المال البشري ({h_val}%).",
                            f"<b>سد الاختناقات الهيكلية:</b> تطوير أطر البيئة التنظيمية المسجلة عند ({r_val}%) لتحفيز القطاع الإبداعي وحماية المصنفات من القرصنة."
                        ]
                        deep_analysis_text = f"""
* تتطلب صانعة القرار تفعيل <b>'حاضنات الأعمال الإبداعية المشتركة'</b> لرفع كفاءة البنية التقنية البالغة ({t_val}%).
* توجيه الدعم المالي والاقتصادي نحو الأنشطة البرتقالية لتعقيم الاقتصاد ضد صدمات البطالة التكنولوجية في ضوء ({e_val}%).
* تعزيز المحتوى الرقمي العربي لتجاوز قصور المحددات الثقافية ({c_val}%).
                        """
                    else:
                        recs_list = [
                            f"<b>التدخل الاستباقي العاجل لدولة ({decision_country_sel}):</b> معالجة الاختناقات الهيكلية الحادة في البنية التقنية ({t_val}%).",
                            f"<b>احتواء الاقتصاد غير الرسمي:</b> دمج الأنشطة الإبداعية المستترة ورفع كفاءة البيئة التشريعية ({r_val}%) لتأمين تدفقات استثمارية آمنة."
                        ]
                        deep_analysis_text = f"""
* تفرض الضرورة القصوى استدعاء إطار <b>'التكامل الوظيفي الإقليمي'</b> لتعويض الفجوة في رأس المال البشري ({h_val}%).
* تنفيذ خطط طوارئ استثمارية لرفع مساهمة الاقتصاد البرتقالي المتدنية ({e_val}%).
* إطلاق برامج عاجلة للأمن الثقافي وحماية التراث الرقمي لمعالجة هشاشة المحددات الثقافية ({c_val}%).
                        """

                    st.session_state.decision_results_dict[decision_country_sel] = {
                        "country": decision_country_sel,
                        "score_str": score_str_plain,
                        "recs": recs_list,
                        "deep": deep_analysis_text
                    }

        if st.session_state.decision_results_dict:
            for item in st.session_state.decision_results_dict.values():
                card_html = f"""
                <div style="background: #FFFFFF; padding: 22px; border-radius: 12px; border: 1.5px solid {CBE_ORANGE_MID}; margin-bottom: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.06);" dir="rtl">
                    <h3 style="color: {CBE_NAVY}; font-weight: bold; margin-bottom: 8px; text-align: right;">🛡️ تقرير وتوصيات دولة: {item['country']} (المؤشر المركب: {item['score_str']})</h3>
                    <div style="background: {CBE_BG}; padding: 12px; border-radius: 8px; border-right: 4px solid {CBE_ORANGE_MID}; margin-top: 10px;">
                        <p style="font-weight: bold; color: {CBE_NAVY}; margin-bottom: 6px; text-align: right;">🎯 التوصيات الاستراتيجية الموجهة:</p>
                        <ul style="margin: 0; padding-right: 20px; color: #1E293B; line-height: 1.8; text-align: right;">
                            <li>{item['recs'][0]}</li>
                            <li>{item['recs'][1]}</li>
                        </ul>
                        <hr style="border: 0; border-top: 1px solid #CBD5E1; margin: 10px 0;">
                        <p style="font-weight: bold; color: {CBE_NAVY}; margin-bottom: 6px; text-align: right;">💡 إضافات تحليلية استراتيجية عميقة ومخصصة:</p>
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
    # تفعيل زر الطباعة الفعال عبر HTML Click Event
    st.markdown("""
    <button onclick="window.print();" class="print-btn-html">
        📥 تصدير وطباعة تقرير لوحة القرار والتوصيات (PDF / طباعة)
    </button>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="footer-copyright">جميع الحقوق محفوظة للدراسة البحثية</div>', unsafe_allow_html=True)

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

            st.markdown(f"""
            <div dir="rtl" style="text-align: right; background: #FFFFFF; padding: 30px; border-radius: 14px; border: 2px solid {CBE_ORANGE_MID}; line-height: 1.9; box-shadow: 0 6px 20px rgba(0,0,0,0.08);">
              <div style="text-align: center; border-bottom: 2px solid {CBE_ORANGE_MID}; padding-bottom: 15px; margin-bottom: 25px;">
                <h2 style="color: {CBE_NAVY}; font-weight: 800; margin: 0;">📑 التقرير التنفيذي الموحد لسياسات الصناعات الثقافية والإبداعية العربية</h2>
                <p style="color: #64748B; font-size: 14.5px; margin-top: 6px;">ملخص استراتيجي موجه للقيادات العليا وصناع القرار - بناءً على مخرجات الدراسة المنهجية والتفكير المنظومي (AACRI)</p>
              </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background: {CBE_BG}; padding: 18px; border-radius: 10px; border-right: 5px solid {CBE_ORANGE_MID}; margin-bottom: 25px;" dir="rtl">
                <h4 style="color: {CBE_NAVY}; margin-top: 0;">🏆 مؤشرات الأداء العام والريادة الإقليمية (التصنيف الجغرافي والديموغرافي والتاريخي):</h4>
                <p style="margin-bottom: 8px;">تتصدّر الدولة التالية قائمة الجاهزية الذكية وفق الترتيب التنازلي للمؤشر المركب: <span style="font-weight: bold; color: {CBE_ORANGE_MID};">{top_country}</span> بقيمة مركبة تبلغ {top_score_str}.</p>
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

            st.markdown(f"""
            <div style="background: #F0FDF4; padding: 22px; border-radius: 12px; border: 1.5px solid #86EFAC; margin-top: 20px; margin-bottom: 20px;" dir="rtl">
                <h4 style="color: #166534; margin-top: 0; font-size: 17px;">📈 ملخص النتائج التحليلية التراكمية والمعمقة لكافة أقسام المنصة:</h4>
                <p style="color: #1E293B; font-size: 14.5px; line-height: 1.8; margin-bottom: 12px;">
                  يقدم هذا التقرير تجميعاً تحليلياً متكاملأ لمخرجات أقسام المنصة الأربعة، عاكساً رؤية استشرافية شاملة لدعم سياسات الصناعات الثقافية والإبداعية العربية في عصر الذكاء الاصطناعي وفق منظور التفكير المنظومي:
                </p>
                <p style="color: #1E293B; font-size: 14.5px; line-height: 1.8; margin-bottom: 12px;">
                  <b>1. التشخيص القياسي والترتيب التراكمي (القسم الأول):</b> أظهرت نتائج تقييم المحاور الخمسة (البنية التقنية، الديناميكيات الاقتصادية، رأس المال البشري، البيئة التشريعية، المحددات الثقافية) تفاوتات هيكلية تستوجب سياسات تفصيلية مخصصة لكل بيئة إقليمية على حدة لتقليص الفجوات الذكية.
                </p>
                <p style="color: #1E293B; font-size: 14.5px; line-height: 1.8; margin-bottom: 12px;">
                  <b>2. استشراف السياسات وبدائل السيناريوهات (القسم الثاني):</b> بينت مخرجات المحاكي أن التحفيز الموجه نحو برامج إعادة التأهيل (Reskilling) وتطوير البنية التحتية يرفع بفاعلية من القيمة المركبة للمؤشر ويقي الاقتصادات صدمات البطالة التكنولوجية والإحلال الخوارزمي للمهن الثقافية.
                </p>
                <p style="color: #1E293B; font-size: 14.5px; line-height: 1.8; margin-bottom: 12px;">
                  <b>3. لوحة دعم القرار والتطعيم الثقافي (القسم الثالث):</b> عززت التوصيات المخصصة والديناميكية ضرورة إرساء مجالس عليا للسيادة الرقمية وتفعيل حاضنات الأنشطة الإبداعية المشتركة بما يصون الأمن الثقافي القومي.
                </p>
                <p style="color: #1E293B; font-size: 14.5px; line-height: 1.8; margin: 0;">
                  <b>4. الخلاصة الاستراتيجية:</b> إن تضافر هذه المخرجات يضع بين أيدي صانعي القرار خارطة طريق إجرائية متكاملة لترسيخ ركائز الاقتصاد البرتقالي وتعظيم العائد التنموي في المنطقة العربية.
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background: #FFFBEB; padding: 22px; border-radius: 12px; border: 1.5px solid #FCD34D; margin-bottom: 15px;" dir="rtl">
                <h4 style="color: #92400E; margin-top: 0; font-size: 17px;">🌳 إطار شجرة قرارات نقاط الرفع المنظومي (Meadows Leverage Points Framework):</h4>
                <ul style="margin: 0; padding-right: 20px; line-height: 1.9; color: #78350F;">
                  <li><b>1. المعلمات والميزانيات (Parameters):</b> تعديل نسب الإنفاق المباشر وموازنات دعم التدريب وإعادة التأهيل.</li>
                  <li><b>2. تدفق المعلومات (Information Flows):</b> توفير قواعد بيانات مرجعية ومنصات حصر رقمية ومؤشرات قياس آنية.</li>
                  <li><b>3. القواعد والحوكمة (Rules):</b> تشريع أطر الملكية الفكرية المشتركة ومعايير الوسم المائي لحماية الحقوق.</li>
                  <li><b>4. أهداف النظام (Goals):</b> توجيه السياسات الوطنية نحو تحقيق السيادة الرقمية وصون الأمن الثقافي القومي.</li>
                  <li><b>5. النماذج الفكرية (Paradigms):</b> ترسيخ مفهوم الاقتصاد البرتقالي كركيزة أساسية للتنمية المستدامة في عصر الذكاء الاصطناعي.</li>
                </ul>
            </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    # تفعيل زر الطباعة الفعال عبر HTML Click Event
    st.markdown("""
    <button onclick="window.print();" class="print-btn-html">
        📥 تصدير وطباعة التقرير التنفيذي الموحد (PDF / طباعة)
    </button>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="footer-copyright">جميع الحقوق محفوظة للدراسة البحثية</div>', unsafe_allow_html=True)
