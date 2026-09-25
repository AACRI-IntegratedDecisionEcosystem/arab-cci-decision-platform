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

/* ضبط اتجاه عناصر Streamlit والتحكم في المحاذاة لليمين */
div.stMarkdown, div.stText, div.stSelectbox, div.stSlider, div.stDataFrame, div.stTable {{
    direction: rtl !important;
    text-align: right !important;
}}

table {{
    direction: rtl !important;
    text-align: right !important;
}}

th, td {{
    text-align: right !important;
    direction: rtl !important;
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
        return f"<span style='color: #16A34A; font-weight: bold;'>{score}% (أداء مرتفع 🟢)</span>"
    elif score >= 51:
        return f"<span style='color: #CA8A04; font-weight: bold;'>{score}% (أداء متوسط 🟡)</span>"
    else:
        return f"<span style='color: #DC2626; font-weight: bold;'>{score}% (فجوة هيكلية حرجة 🔴)</span>"

# دوال توليد النصوص الديناميكية المتباينة لكل محور على حدة لمنع أي تكرار
def describe_ti(val):
    if val >= 80:
        return f"البنية التقنية المتقدمة للغاية ({val}%) توفر طاقات استيعابية ضخمة للبيانات وشبكات فائقة السرعة لدعم النماذج التوليدية."
    elif val >= 50:
        return f"البنية التقنية متوسطة الكفاءة ({val}%) وتتطلب تحديث سعات تدفق البيانات والباند العريض."
    else:
        return f"البنية التقنية تعاني من قصور حاد ({val}%) يعيق توطين البنى التحتية الذكية."

def describe_ed(val):
    if val >= 80:
        return f"الديناميكيات الاقتصادية مزدهرة ({val}%) بفضل مساهمة قوية للاقتصاد البرتقالي وتدفقات استثمارية واسعة."
    elif val >= 50:
        return f"الديناميكيات الاقتصادية في نطاق متوازن (%{val}) وتحتاج لتحفيز رأس المال المخاطر."
    else:
        return f"قصور في الديناميكيات الاقتصادية (%{val}) وضعف مساهمة القطاع الإبداعي في الناتج المحلي."

def describe_hc(val):
    if val >= 80:
        return f"رأس مال بشري مؤهل وعالي الجاهزية (%{val}) في مهارات هندسة الأوامر والتعامل مع تقنيات 'المبدع المعزز'."
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
        <p>إمكانية التشخيص للدول العربية المختارة مع تسجيل وثبات النتائج في الجدول التراكمي وإدارة السجلات الموضح أدناه.</p>
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
                score_html_colored = get_colored_score_html(final_score)

                if final_score >= 80:
                    diagnosis = "🟢 جاهزية متقدمة للغاية نحو السيادة الرقمية والابتكار المستدام وتفعيل 'المبدع المعزز'."
                    detailed_diag = f"🟢 **جاهزية متقدمة ومستدامة:** إجمالي المؤشر المركب {score_html_colored}. تعكس هذه النتيجة تفوقاً هيكلياً في بيئة العمل، ورأس مال بشري مؤهل للتعامل مع التقنيات التوليدية، وبنية تقنية متطورة تتيح قيادة التحالفات الإقليمية وتوطين النماذج الثقافية الرقمية بكفاءة عالية بما يضمن صون الأمن الثقافي."
                elif final_score >= 51:
                    diagnosis = "🟡 جاهزية متوسطة، تتطلب تدخلات استباقية لمعالجة الاختناقات الهيكلية."
                    detailed_diag = f"🟡 **جاهزية متوسطة تتطلب تدخلاً استباقياً:** إجمالي المؤشر المركب {score_html_colored}. تشير المؤشرات إلى توازن نسبي يواجه بعض الاختناقات الهيكلية في سلاسل القيمة أو التشريعات التنظيمية، مما يستوجب حزم تحفيزية وبرامج إعادة تأهيل (Upskilling & Reskilling) لردم الفجوات القائمة."
                else:
                    diagnosis = "🔴 وجود فجوة ذكية هيكلية تستوجب تفعيل محاكي السياسات ولوحة دعم اتخاذ القرار فوراً."
                    detailed_diag = f"🔴 **فجوة ذكية هيكلية حرجة:** إجمالي المؤشر المركب {score_html_colored}. توضح القراءة الحالية وجود اختناقات عميقة في البنية التحتية والبيئة التشريعية ورأس المال البشري، مما يستوجب تفعيل محاكي السياسات ولوحة التطعيم الثقافي لدعم 'المبدع المعزز' وتفادي الاستلاب الخوارزمي."

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
                  <p style="font-size: 16px; margin-bottom: 12px;"><b>القيمة المركبة لمؤشر الجاهزية الذكية (AACRI):</b> <span style="font-size: 18px;">{score_html_colored}</span></p>
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
        
        html_table = f"""
        <div style="overflow-x: auto; width: 100%;">
        <table style="width: 100%; border-collapse: collapse; background-color: #FFFFFF; direction: rtl; text-align: right; font-family: 'Cairo', sans-serif; border: 1px solid #CBD5E1; border-radius: 8px;">
            <thead>
                <tr style="background-color: {CBE_NAVY}; color: #FFFFFF; text-align: right;">
                    <th style="padding: 12px; border: 1px solid #CBD5E1; text-align: right; width: 5%;">م</th>
                    <th style="padding: 12px; border: 1px solid #CBD5E1; text-align: right; width: 18%;">الدولة</th>
                    <th style="padding: 12px; border: 1px solid #CBD5E1; text-align: right; width: 12%;">المؤشر المركب (AACRI)</th>
                    <th style="padding: 12px; border: 1px solid #CBD5E1; text-align: right; width: 11%;">البنية التقنية (20%)</th>
                    <th style="padding: 12px; border: 1px solid #CBD5E1; text-align: right; width: 11%;">الديناميكيات الاقتصادية (15%)</th>
                    <th style="padding: 12px; border: 1px solid #CBD5E1; text-align: right; width: 11%;">رأس المال البشري (30%)</th>
                    <th style="padding: 12px; border: 1px solid #CBD5E1; text-align: right; width: 11%;">البيئة التنظيمية (20%)</th>
                    <th style="padding: 12px; border: 1px solid #CBD5E1; text-align: right; width: 11%;">المحددات الثقافية (15%)</th>
                    <th style="padding: 12px; border: 1px solid #CBD5E1; text-align: right; width: 10%;">التقييم المنظومي</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for idx, row in df_history.iterrows():
            row_bg = "#F8FAFC" if idx % 2 == 0 else "#FFFFFF"
            html_table += f"""
                <tr style="background-color: {row_bg}; border-bottom: 1px solid #E2E8F0;">
                    <td style="padding: 10px; border: 1px solid #CBD5E1; text-align: right; font-weight: bold;">{idx + 1}</td>
                    <td style="padding: 10px; border: 1px solid #CBD5E1; text-align: right; font-weight: bold; color: {CBE_NAVY};">{row['الدولة']}</td>
                    <td style="padding: 10px; border: 1px solid #CBD5E1; text-align: right; font-weight: bold; color: {CBE_ORANGE_MID};">{row['المؤشر المركب (AACRI)']}</td>
                    <td style="padding: 10px; border: 1px solid #CBD5E1; text-align: right;">{row['البنية التقنية (20%)']}</td>
                    <td style="padding: 10px; border: 1px solid #CBD5E1; text-align: right;">{row['الديناميكيات الاقتصادية (15%)']}</td>
                    <td style="padding: 10px; border: 1px solid #CBD5E1; text-align: right;">{row['رأس المال البشري (30%)']}</td>
                    <td style="padding: 10px; border: 1px solid #CBD5E1; text-align: right;">{row['البيئة التنظيمية والتشريعية (20%)']}</td>
                    <td style="padding: 10px; border: 1px solid #CBD5E1; text-align: right;">{row['المحددات الثقافية والهوياتية (15%)']}</td>
                    <td style="padding: 10px; border: 1px solid #CBD5E1; text-align: right; font-size: 13px;">{row['التقييم المنظومي']}</td>
                </tr>
            """
            
        html_table += """
            </tbody>
        </table>
        </div>
        """
        
        # استخدام unsafe_allow_html=True حصرياً لعرض الجدول المنظومي دون أكواد نصية
        st.markdown(html_table, unsafe_allow_html=True)

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
    if st.button("📥 تصدير وطباعة تقرير القسم الأول (PDF / طباعة)", use_container_width=True):
        st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

    with st.expander("📂 استعراض المصفوفة الإجرائية للمحاور الرئيسة والأبعاد والـ 69 متغيراً للمؤشر (AACRI)"):
        st.markdown("""
        * **البنية التقنية (وزن 20%):** يضم مؤشرات سعة وتدفق البيانات الضخمة، سرعات الإنترنت عريض الباند، وتوطين النماذج اللغوية الكبيرة (LLMs).
        * **الديناميكيات الاقتصادية (وزن 15%):** يضم مساهمة الاقتصاد البرتقالي في الناتج المحلي، الصادرات الإبداعية، وصفقات رأس المال المخاطر (VC).
        * **رأس المال البشري (وزن 30%):** يضم نسب التدريب المعتمد في هندسة الأوامر (Prompt Engineering) وبرامج إعادة التأهيل (Reskilling & Upskilling) وتمكين 'المبدع المعزز'.
        * **البيئة التنظيمية والتشريعية (وزن 20%):** يضم تشريعات الملكية الفكرية المشتركة، أطر المسؤولية (Liability), وآليات الوسم المائي (Watermarking).
        * **المحددات الثقافية والهوياتية (وزن 15%):** يضم نسبة المحتوى الرقمي المتاح بالعربية، أرشفة التراث ثلاثي الأبعاد (3D Archives), ومؤشرات الأمن الثقافي.
        """)
        axes_names = ['البنية التقنية (20%)', 'الديناميكيات الاقتصادية (15%)', 'رأس المال البشري (30%)', 'البيئة التنظيمية والتشريعية (20%)', 'المحددات الثقافية والهوياتية (15%)']
        weights_vals = [20, 15, 30, 20, 15]
        fig_bar = px.bar(x=axes_names, y=weights_vals, text=weights_vals, labels={'x': 'المحاور', 'y': 'الوزن (%)'}, title="توزيع الأوزان النسبية لمحاور المؤشر وفق التحليل الهرمي AHP")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown(f'<div class="footer-copyright">جميع الحقوق محفوظة للدراسة البحثية</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# التبويب الثاني: محاكي السياسات (Policy Simulator) - إجابات غير مكررة وديناميكية
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
                    analysis_text = f"تحذير هيكلي لـ ({sim_country_sel}): في ضوء البنية التقنية المسجلة عند ({t_val}%) وضعف استثمارات رأس المال البشري ({h_val}%)، فإن الجمود الاستثماري سيؤدي إلى تفاقم فجوة الإحلال الخوارزمي وانحسار الاقتصاد البرتقالي."
                    action_plan = f"التدخل الفوري لترميم البيئة التشريعية البالغة ({r_val}%)، وضخ تمويلات طارئة لحماية المهن الثقافية المعرضة للاندثار."
                elif scenario_dropdown.startswith("📊"):
                    simulated_val = min(100.0, base_val * (1 + (combined_boost * 0.0022)))
                    analysis_text = f"تقدم ملحوظ لـ ({sim_country_sel}): استناداً إلى توازن المحددات الثقافية ({c_val}%) وديناميكيات السوق البرتقالي ({e_val}%)، يتحقق نمو تدريجي في حوكمة الاستخدام التوليدي وتمكين مهارات 'المبدع المعزز'."
                    action_plan = f"التوسع في برامج إعادة التأهيل المستمر للاستفادة من رصيد الكوادر البشرية المقدر بـ ({h_val}%)."
                else:
                    simulated_val = min(100.0, base_val * (1 + (combined_boost * 0.0042)))
                    analysis_text = f"نجاح استراتيجي فائق لـ ({sim_country_sel}): توظيف البنية التحتية العالية ({t_val}%) والتشريعات المتقدمة ({r_val}%) لتحقيق السيادة الرقمية الكاملة وتوطين النماذج اللغوية الثقافية العربية المستقلة."
                    action_plan = "قيادة التحالفات التقنية الإقليمية، إطلاق المنصات السحابية الوطنية المفتوحة، وتكريس دروع الأمن الثقافي القومي."

                simulated_val = round(simulated_val, 2)
                delta = round(simulated_val - base_val, 2)
                sim_colored_html = get_colored_score_html(simulated_val)

                # استخدام دوال المحاور المستقلة لضمان تباين المعاني وتجنب تكرار الكلمات
                deep_analysis = f"""
                <div style='font-size: 14px; color: #1E293B; line-height: 1.8;'>
                  <b>📊 التشخيص القياسي المخصص والمبني على درجات المحاور لدولة ({sim_country_sel}):</b>
                  <ul style='margin: 5px 0 0 0; padding-right: 20px;'>
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
                  <p style="font-size: 15px; margin-bottom: 8px;"><b>القيمة المتوقعة للمؤشر:</b> {sim_colored_html} (صافي التغير: <span style="font-weight: bold;">{delta:+.2f}</span>)</p>
                  <div style="background: {CBE_BG}; padding: 12px; border-radius: 8px; border-right: 4px solid {CBE_ORANGE_MID}; margin-top: 10px;">
                    <p style="margin-bottom: 6px;"><b>🔬 التحليل القياسي:</b> {analysis_text}</p>
                    <p style="margin: 0 0 8px 0; color: {CBE_ORANGE_MID}; font-weight: bold;">🛠️ خطة التحرك: {action_plan}</p>
                    <hr style="border: 0; border-top: 1px solid #CBD5E1; margin: 10px 0;">
                    {deep_analysis}
                  </div>
                </div>
                """
                st.session_state.simulated_results_dict[sim_country_sel] = box_html

        if st.session_state.simulated_results_dict:
            for b_html in st.session_state.simulated_results_dict.values():
                st.markdown(b_html, unsafe_allow_html=True)
        else:
            st.info("📈 قم بضبط الدولة والسيناريو ومتغيرات التحفيز واضغط على زر الإضافة لتثبيت ومتابعة السيناريوهات هنا.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📥 تصدير وطباعة تقرير المحاكي (PDF / طباعة)", use_container_width=True):
        st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

    st.markdown(f'<div class="footer-copyright">جميع الحقوق محفوظة للدراسة البحثية</div>', unsafe_allow_html=True)

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

    col_dec_in, col_dec_out = st.columns([1, 2], gap="large")

    with col_dec_in:
        st.markdown('<div dir="rtl" style="text-align: right;">', unsafe_allow_html=True)
        recorded_countries_dec = [item["الدولة"] for item in st.session_state.history_state] if st.session_state.history_state else ARAB_COUNTRIES
        decision_country_sel = st.selectbox("اختر الدولة لاستعراض التوصيات", recorded_countries_dec, key="dec_country")
        generate_decision_btn = st.button("📋 إضافة وتثبيت توصيات الدولة المختارة", use_container_width=True, type="primary")
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
                    score_colored_str = get_colored_score_html(score)

                    if score >= 80:
                        recs = f"<li><b>تعزيز ريادة الابتكار الإقليمي:</b> الاستفادة من مؤشر البنية التقنية ({t_val}%) لتصدير النماذج اللغوية الثقافية.</li><li><b>الحوكمة المتقدمة للذكاء الاصطناعي:</b> تفعيل دروع الحماية عبر معايير التشريعات ({r_val}%).</li>"
                        deep_third = f"""
                        <p style='color: #14532D; font-size: 14.5px; margin-bottom: 8px;'><b>💡 إضافات تحليلية استراتيجية عميقة:</b></p>
                        <ul style='margin: 0; padding-right: 20px; color: #1E293B; line-height: 1.8;'>
                          <li>تأسيس <b>'مجلس سيادي أعلى'</b> مدعوم برصيد رأس المال البشري المتميز ({h_val}%).</li>
                          <li>تفعيل آليات <b>التطعيم الثقافي</b> لحماية الهوية استناداً إلى قوة المحددات الثقافية ({c_val}%).</li>
                          <li>قيادة الاستثمارات البرتقالية إقليمياً في ضوء الديناميكيات الاقتصادية ({e_val}%).</li>
                        </ul>
                        """
                    elif score >= 51:
                        recs = f"<li><b>ردم الفجوة التقنية والبشرية:</b> إطلاق حزم برامج إعادة التأهيل السريع اعتماداً على جاهزية الكوادر ({h_val}%).</li><li><b>سد الاختناقات الهيكلية:</b> تطوير أطر البيئة التشريعية ({r_val}%) لتحفيز القطاع الإبداعي.</li>"
                        deep_third = f"""
                        <p style='color: #713F12; font-size: 14.5px; margin-bottom: 8px;'><b>💡 إضافات تحليلية استراتيجية عميقة:</b></p>
                        <ul style='margin: 0; padding-right: 20px; color: #1E293B; line-height: 1.8;'>
                          <li>تفعيل <b>'حاضنات الأعمال الإبداعية المشتركة'</b> لتعزيز كفاءة البنية التقنية ({t_val}%).</li>
                          <li>توجيه الدعم المالي نحو الأنشطة البرتقالية لامتصاص صدمات السوق في ضوء ({e_val}%).</li>
                          <li>ترسيخ المحتوى الرقمي المتاح بالعربية لتجاوز عوائق المحددات الثقافية ({c_val}%).</li>
                        </ul>
                        """
                    else:
                        recs = f"<li><b>التدخل الاستباقي العاجل:</b> معالجة القصور الهيكلي الحاد في البنية التحتية والتقنية ({t_val}%).</li><li><b>احتواء الاقتصاد غير الرسمي:</b> دمج الأنشطة الإبداعية المستترة وتحسين البيئة التشريعية ({r_val}%).</li>"
                        deep_third = f"""
                        <p style='color: #7F1D1D; font-size: 14.5px; margin-bottom: 8px;'><b>💡 إضافات تحليلية استراتيجية عميقة:</b></p>
                        <ul style='margin: 0; padding-right: 20px; color: #1E293B; line-height: 1.8;'>
                          <li>استدعاء إطار <b>'التكامل الوظيفي الإقليمي'</b> لتعويض العجز في رأس المال البشري ({h_val}%).</li>
                          <li>تنفيذ خطط طوارئ استثمارية لرفع مساهمة الاقتصاد البرتقالي ({e_val}%).</li>
                          <li>إطلاق برامج عاجلة للأمن الثقافي لمعالجة هشاشة المحددات الهوياتية ({c_val}%).</li>
                        </ul>
                        """

                    dec_box = f"""
                    <div dir="rtl" style="text-align: right; background: #FFFFFF; padding: 22px; border-radius: 12px; border: 1.5px solid {CBE_ORANGE_MID}; margin-bottom: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
                      <h3 style="color: {CBE_NAVY}; font-weight: bold; margin-bottom: 8px;">🛡️ تقرير وتوصيات دولة: {decision_country_sel} (المؤشر المركب: {score_colored_str})</h3>
                      <ul style="margin: 0 0 10px 0; padding-right: 20px; line-height: 1.8; color: #1E293B;">
                        {recs}
                      </ul>
                      <div style='background: {CBE_BG}; padding: 14px; border-radius: 8px; border-right: 4px solid {CBE_ORANGE_MID}; margin-top: 12px;'>
                        {deep_third}
                      </div>
                    </div>
                    """
                    st.session_state.decision_results_dict[decision_country_sel] = dec_box

        if st.session_state.decision_results_dict:
            for d_html in st.session_state.decision_results_dict.values():
                st.markdown(d_html, unsafe_allow_html=True)
        else:
            st.info("🛡️ يرجى اختيار الدولة المسجلة والضغط على زر الإضافة لتثبيت التوصيات هنا.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📥 تصدير وطباعة تقرير لوحة القرار والتوصيات (PDF / طباعة)", use_container_width=True):
        st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

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
            top_score_colored = get_colored_score_html(top_score)

            countries_summary = ""
            for idx, row in df_rep.iterrows():
                s = row['المؤشر المركب (AACRI)']
                s_col = get_colored_score_html(s)
                countries_summary += f"""
                <li style="margin-bottom: 12px; line-height: 1.8; background: #F8FAFC; padding: 12px 16px; border-radius: 8px; border: 1px solid #E2E8F0;">
                    <b>المركز ({idx + 1}): {row['الدولة']}</b> — المؤشر المركب: {s_col} | البنية التقنية: {row['البنية التقنية (20%)']}% | رأس المال البشري: {row['رأس المال البشري (30%)']}% <br>
                    <span style="color: #475569; font-size: 13.5px;"><b>التقييم التشخيصي:</b> {row['التقييم المنظومي']}</span>
                </li>
                """

            exec_report_html = f"""
            <div dir="rtl" style="text-align: right; background: #FFFFFF; padding: 30px; border-radius: 14px; border: 2px solid {CBE_ORANGE_MID}; line-height: 1.9; box-shadow: 0 6px 20px rgba(0,0,0,0.08);">
              <div style="text-align: center; border-bottom: 2px solid {CBE_ORANGE_MID}; padding-bottom: 15px; margin-bottom: 25px;">
                <h2 style="color: {CBE_NAVY}; font-weight: 800; margin: 0;">📑 التقرير التنفيذي الموحد لسياسات الصناعات الثقافية والإبداعية العربية</h2>
                <p style="color: #64748B; font-size: 14.5px; margin-top: 6px;">ملخص استراتيجي موجه للقيادات العليا وصناع القرار - بناءً على مخرجات الدراسة المنهجية والتفكير المنظومي (AACRI)</p>
              </div>

              <div style="background: {CBE_BG}; padding: 18px; border-radius: 10px; border-right: 5px solid {CBE_ORANGE_MID}; margin-bottom: 25px;">
                <h4 style="color: {CBE_NAVY}; margin-top: 0;">🏆 مؤشرات الأداء العام والريادة الإقليمية:</h4>
                <p style="margin-bottom: 8px;">تتصدّر الدولة التالية قائمة الجاهزية الذكية وفق الترتيب التنازلي للمؤشر المركب: <span style="font-weight: bold; color: {CBE_ORANGE_MID};">{top_country}</span> بقيمة مركبة تبلغ {top_score_colored}.</p>
                <p style="margin: 0;">إجمالي الدول الخاضعة للتشخيص والتحليل المنظومي حتى الآن: <b>{len(df_rep)} دولة عربية</b>.</p>
              </div>

              <h4 style="color: {CBE_NAVY}; margin-bottom: 12px;">📋 ترتيب الملخص التراكمي للدول (من الأعلى للأقل أدائية):</h4>
              <ul style="margin-bottom: 25px; padding-right: 0; list-style-type: none;">
                {countries_summary}
              </ul>

              <div style="background: #F0FDF4; padding: 22px; border-radius: 12px; border: 1.5px solid #86EFAC; margin-bottom: 20px;">
                <h4 style="color: #166534; margin-top: 0; font-size: 17px;">📈 ملخص النتائج التحليلية التراكمية والمعمقة لكافة أقسام المنصة:</h4>
                <p style="color: #1E293B; font-size: 14.5px; line-height: 1.8; margin: 0;">
                  تؤكد مخرجات التشخيص المنظومي ومحاكاة السياسات ولوحة دعم القرار أن سد الفجوات الهيكلية في الصناعات الثقافية والإبداعية العربية يتطلب تكامل المحاور الخمسة (البنية التقنية، الاقتصاد البرتقالي، رأس المال البشري، التشريعات، والمحددات الثقافية). إن الدول التي تسجل أداءً متقدماً تعتمد على توطين النماذج اللغوية الكبيرة وحماية الملكية الفكرية، بينما تستوجب الدول ذات الفجوات الحرجة تفعيل برامج الطوارئ الاستثمارية والتطعيم الثقافي لتمكين 'المبدع المعزز' وتفادي الاستلاب الخوارزمي.
                </p>
              </div>

              <div style="background: #FFFBEB; padding: 22px; border-radius: 12px; border: 1.5px solid #FCD34D; margin-bottom: 15px;">
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
            """
            st.markdown(exec_report_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📥 تصدير وطباعة التقرير التنفيذي الموحد (PDF / طباعة)", use_container_width=True):
        st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

    st.markdown(f'<div class="footer-copyright">جميع الحقوق محفوظة للدراسة البحثية</div>', unsafe_allow_html=True)
