import os
import random
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 0. إعدادات صفحة Streamlit وتفعيل تخطيط الشاشة بالكامل
# ==============================================================================
st.set_page_config(
    page_title="منصة منظومة القرار المتكاملة - AACRI",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# 1. الهوية البصرية وتصميم الصف العلوي والأقسام الأربعة للمنصة (RTL Support)
# ==============================================================================
CBE_ORANGE_DARK = "#78350F"  # برتقالي غامق جداً قاتم
CBE_ORANGE_MID = "#B45309"   # برتقالي غامق تراثي
CBE_ORANGE_LIGHT = "#D97706" # برتقالي أفتح نسبياً عند التحديد
CBE_NAVY = "#0A192F"         # أزرق ملكي عميق
CBE_BG = "#F8FAFC"           # خلفية ناعمة

CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {{
    background-color: {CBE_BG} !important;
    font-family: 'Cairo', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    direction: rtl !important;
    text-align: right !important;
}}

.header-center {{
    text-align: center !important;
    background: linear-gradient(135deg, rgba(10, 25, 47, 0.95) 0%, rgba(120, 53, 15, 0.90) 100%),
                url('https://images.unsplash.com/photo-1461360370896-922624d12aa1?q=80&w=1600&auto=format&fit=crop') !important;
    background-size: cover !important;
    background-position: center !important;
    backdrop-filter: blur(12px) !important;
    color: #FFFFFF !important;
    padding: 40px 20px !important;
    border-radius: 16px !important;
    border-bottom: 5px solid {CBE_ORANGE_MID} !important;
    box-shadow: 0 12px 35px rgba(0,0,0,0.35) !important;
    margin-bottom: 20px !important;
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

/* شريط الأخبار المتحرك الانسيابي */
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

.primary-btn {{
    background: linear-gradient(135deg, {CBE_ORANGE_MID} 0%, {CBE_ORANGE_LIGHT} 100%) !important;
    color: #FFFFFF !important;
    font-weight: bold !important;
    font-size: 15px !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 12px 24px !important;
    box-shadow: 0 4px 12px rgba(180, 83, 9, 0.4) !important;
}}

.danger-btn {{
    background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%) !important;
    color: #FFFFFF !important;
    font-weight: bold !important;
    font-size: 14px !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 10px 20px !important;
}}

.export-btn {{
    background: linear-gradient(135deg, {CBE_NAVY} 0%, #1E293B 100%) !important;
    color: #FBBF24 !important;
    font-weight: bold !important;
    font-size: 14px !important;
    border: 1px solid {CBE_ORANGE_MID} !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    margin-top: 12px !important;
}}

.footer-copyright {{
    text-align: center;
    color: #64748B;
    font-size: 13px;
    margin-top: 30px;
    border-top: 1px solid #E2E8F0;
    padding-top: 15px;
    font-weight: bold;
}}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==============================================================================
# 2. إدارة حالة تسجيل الدخول (Authentication State)
# ==============================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown(f"""
        <div style="background: #FFFFFF; padding: 35px; border-radius: 16px; border: 2px solid {CBE_ORANGE_MID}; box-shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: right; direction: rtl; margin-top: 50px;">
            <h2 style="color: {CBE_NAVY}; text-align: center; font-weight: 800; margin-bottom: 10px;">🏛️ منصة منظومة القرار المتكاملة</h2>
            <p style="color: #475569; text-align: center; font-size: 14px; line-height: 1.6; margin-bottom: 25px;">
                نموذج تفاعلي متقدم لتطوير مهن الصناعات الثقافية والإبداعية العربية في عصر الذكاء الاصطناعي بمنظور التفكير المنظومي. يرجى تسجيل الدخول للولوج إلى بيئة التشخيص والمحاكاة.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        username = st.text_input("اسم المستخدم (Username)", placeholder="أدخل اسم المستخدم...")
        password = st.text_input("كلمة المرور (Password)", type="password", placeholder="أدخل كلمة المرور...")
        
        if st.button("🔐 تسجيل الدخول للمنصة", use_container_width=True):
            if username == "user" and password == "123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("⚠️ اسم المستخدم أو كلمة المرور غير صحيحة. (اسم المستخدم: user | كلمة المرور: 123)")
    st.stop()

# ==============================================================================
# 3. القائمة الرسمية الكاملة للدول العربية وحفظ السجلات
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

if "comparison_history_state" not in st.session_state:
    st.session_state.comparison_history_state = []

def get_colored_score_html(score):
    if score >= 80:
        return f"<span style='color: #16A34A; font-weight: bold;'>{score}% (أداء مرتفع 🟢)</span>"
    elif score >= 51:
        return f"<span style='color: #CA8A04; font-weight: bold;'>{score}% (أداء متوسط 🟡)</span>"
    else:
        return f"<span style='color: #DC2626; font-weight: bold;'>{score}% (فجوة هيكلية حرجة 🔴)</span>"

# ==============================================================================
# 4. التروياسة والشريط الإخباري المتحرك
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
# 5. التبويبات الأربعة الرئيسية للمنصة
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
    st.markdown("### 🌐 التشخيص القياسي لمؤشر الجاهزية الذكية للصناعات الثقافية والإبداعية (AACRI)")
    st.markdown("إمكانية التشخيص للدول العربية المختارة مع تسجيل وثبات النتائج في الجدول التراكمي وإدارة السجلات.")

    col1, col2 = st.columns([1, 2])
    with col1:
        country_sel = st.selectbox("اختر الدولة العربية", ARAB_COUNTRIES, key="c_sel")
        ti_slider = st.slider("1️⃣ البنية التقنية (وزن 20%)", 0, 100, 68, key="ti_s")
        ed_slider = st.slider("2️⃣ الديناميكيات الاقتصادية (وزن 15%)", 0, 100, 70, key="ed_s")
        hc_slider = st.slider("3️⃣ رأس المال البشري (وزن 30%)", 0, 100, 72, key="hc_s")
        rf_slider = st.slider("4️⃣ البيئة التنظيمية والتشريعية (وزن 20%)", 0, 100, 65, key="rf_s")
        cd_slider = st.slider("5️⃣ المحددات الثقافية والهوياتية (وزن 15%)", 0, 100, 82, key="cd_s")

        calc_btn = st.button("🚀 احسب وسجل قياس الدولة", key="calc_btn")

    with col2:
        if calc_btn:
            if country_sel == "الدولة":
                st.markdown("<div style='padding:20px; text-align:center; color:#991B1B; background:#FEF2F2; border-radius:10px; border:1px solid #F87171;'><b>⚠️ يرجى اختيار دولة عربية حقيقية من القائمة لتنفيذ التشخيص القياسي.</b></div>", unsafe_allow_html=True)
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
                for i, item in enumerate(st.session_state.comparison_history_state):
                    if item["الدولة"] == country_sel:
                        st.session_state.comparison_history_state[i] = entry
                        updated = True
                        break
                if not updated:
                    st.session_state.comparison_history_state.append(entry)

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
            st.markdown("<div style='padding:20px; text-align:center; color:#0A192F; background:#FFFFFF; border-radius:10px; border:1px solid #B45309;'><b>📊 يرجى اختيار الدولة وضبط درجات المحاور ثم الضغط على زر الحساب.</b></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📋 قائمة ترتيب الدول العربية")
    
    recorded_countries = [item["الدولة"] for item in st.session_state.comparison_history_state]
    if recorded_countries:
        col_del1, col_del2 = st.columns([2, 1])
        with col_del1:
            country_to_delete = st.selectbox("اختر دولة من السجل لحذفها", recorded_countries, key="del_sel")
        with col_del2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ حذف الدولة المحددة", key="del_btn"):
                st.session_state.comparison_history_state = [item for item in st.session_state.comparison_history_state if item["الدولة"] != country_to_delete]
                st.success(f"✅ تم حذف سجل دولة ({country_to_delete}) بنجاح.")
                st.rerun()

    if st.session_state.comparison_history_state:
        df_history = pd.DataFrame(st.session_state.comparison_history_state)
        df_history = df_history.sort_values(by="المؤشر المركب (AACRI)", ascending=False).reset_index(drop=True)
        # إظهار الجدول من اليمين لليسار في واجهة Streamlit عبر تنظيم الأعمدة
        st.dataframe(df_history, use_container_width=True)
    else:
        st.info("📂 لا توجد سجلات مدخلة حتى الآن. يرجى حساب قياس دولة عبر النماذج أعلاه.")

    if st.button("📥 تصدير وطباعة تقرير القسم الأول (PDF / طباعة)", key="exp_1"):
        st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

    with st.expander("📂 استعراض المصفوفة الإجرائية للمحاور الرئيسة والأبعاد والـ 69 متغيراً للمؤشر (AACRI)"):
        st.markdown("""
        * **البنية التقنية (وزن 20%):** يضم مؤشرات سعة وتدفق البيانات الضخمة، سرعات الإنترنت عريض الباند، وتوطين النماذج اللغوية الكبيرة (LLMs).
        * **الديناميكيات الاقتصادية (وزن 15%):** يضم مساهمة الاقتصاد البرتقالي في الناتج المحلي، الصادرات الإبداعية، وصفقات رأس المال المخاطر (VC).
        * **رأس المال البشري (وزن 30%):** يضم نسب التدريب المعتمد في هندسة الأوامر (Prompt Engineering) وبرامج إعادة التأهيل (Reskilling & Upskilling) وتمكين 'المبدع المعزز'.
        * **البيئة التنظيمية والتشريعية (وزن 20%):** يضم تشريعات الملكية الفكرية المشتركة، أطر المسؤولية (Liability)، وآليات الوسم المائي (Watermarking).
        * **المحددات الثقافية والهوياتية (وزن 15%):** يضم نسبة المحتوى الرقمي المتاح بالعربية، أرشفة التراث ثلاثي الأبعاد (3D Archives), ومؤشرات الأمن الثقافي.
        """)
        axes_names = ['البنية التقنية (20%)', 'الديناميكيات الاقتصادية (15%)', 'رأس المال البشري (30%)', 'البيئة التنظيمية والتشريعية (20%)', 'المحددات الثقافية والهوياتية (15%)']
        weights_vals = [20, 15, 30, 20, 15]
        fig_h = px.bar(x=axes_names, y=weights_vals, text=weights_vals, title="توزيع الأوزان النسبية لمحاور مؤشر الجاهزية الذكية (AACRI) وفق التحليل الهرمي AHP", color=weights_vals, color_continuous_scale="Oranges")
        st.plotly_chart(fig_h, use_container_width=True)

    st.markdown('<div class="footer-copyright">جميع الحقوق محفوظة للدراسة البحثية</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# التبويب الثاني: محاكي السياسات (Policy Simulator)
# ------------------------------------------------------------------------------
with tab2:
    st.markdown("### 🔬 محاكي السياسات الاستشرافي والمتابعة التراكمية للسيناريوهات")
    st.markdown("استشراف أثر التدخلات الاستثمارية والتقنية عبر النمذجة القياسية ومتغيرات التحفيز الاستراتيجي.")

    col_sim1, col_sim2 = st.columns([1, 2])
    with col_sim1:
        recorded_list = [item["الدولة"] for item in st.session_state.comparison_history_state]
        sim_country_sel = st.selectbox("اختر الدولة للمحاكاة", recorded_list if recorded_list else ["اختر دولة مسجلة أولاً"], key="sim_c")
        base_aacri_input = st.slider("قيمة المؤشر الافتراضي الحالي", 30.0, 100.0, 68.5, step=0.5, key="base_s")
        scenario_dropdown = st.selectbox(
            "اختر السيناريو الاستراتيجي",
            [
                "📉 السيناريو التشاؤمي (غياب التدخل وضعف الاستثمار)",
                "📊 السيناريو المعتدل / التفاؤلي (استثمارات تقليدية تدريجية)",
                "🚀 السيناريو الطموح / الاستباقي (إصلاحات هيكلية شاملة وسيادة تقنية)"
            ],
            key="scen_s"
        )
        var1_tech = st.slider("1️⃣ نسبة الزيادة في البنية التقنية (%)", 0, 50, 20, key="v1")
        var2_eco = st.slider("2️⃣ نسبة الزيادة في الديناميكيات الاقتصادية (%)", 0, 50, 15, key="v2")
        var3_hc = st.slider("3️⃣ نسبة الزيادة في رأس المال البشري (%)", 0, 50, 15, key="v3")
        var4_reg = st.slider("4️⃣ معدل تطوير البيئة التنظيمية (%)", 0, 50, 10, key="v4")
        var5_cult = st.slider("5️⃣ نسبة التوسع في المحددات الثقافية (%)", 0, 50, 25, key="v5")

        run_sim_btn = st.button("📋 تثبيت وتشغيل المحاكاة", key="run_s_btn")

    with col_sim2:
        if run_sim_btn:
            base_val = base_aacri_input
            if st.session_state.comparison_history_state:
                for item in st.session_state.comparison_history_state:
                    if item["الدولة"] == sim_country_sel:
                        base_val = item["المؤشر المركب (AACRI)"]
                        break

            combined_boost = (var1_tech * 0.25) + (var2_eco * 0.15) + (var3_hc * 0.3) + (var4_reg * 0.2) + (var5_cult * 0.1)

            if scenario_dropdown.startswith("📉"):
                simulated_val = max(0.0, base_val * 0.90)
                analysis_text = f"تحذير هيكلي لـ ({sim_country_sel}): استمرار الركود وغياب الإصلاحات سيؤدي إلى تفاقم فجوة الإحلال الخوارزمي واندثار المهن الثقافية بنسبة تصل إلى 32%."
                action_plan = "التدخل الفوري لإيقاف التدهور وإعادة تخصيص ميزانيات طارئة وتفعيل لوحة التطعيم الثقافي."
            elif scenario_dropdown.startswith("📊"):
                simulated_val = min(100.0, base_val * (1 + (combined_boost * 0.0022)))
                analysis_text = f"تقدم ملحوظ لـ ({sim_country_sel}): نجاح تدريجي في ترشيد استخدام الأدوات التوليدية، دعم مهارات 'المبدع المعزز'، وتقليص الفجوة المهنية."
                action_plan = "توسيع برامج التدريب المستمر (Upskilling & Reskilling) واعتماد حزم تحفيزية."
            else:
                simulated_val = min(100.0, base_val * (1 + (combined_boost * 0.0042)))
                analysis_text = f"نجاح استراتيجي فائق لـ ({sim_country_sel}): تحقيق السيادة الرقمية الكاملة، توطين النماذج اللغوية الثقافية العربية، وتفعيل دور المبدع كشريك إبداعي مهيمن."
                action_plan = "قيادة التحالفات التقنية الإقليمية وإطلاق المنصات السحابية المفتوحة وتأمين الأمن الثقافي."

            simulated_val = round(simulated_val, 2)
            delta = round(simulated_val - base_val, 2)
            sim_colored_html = get_colored_score_html(simulated_val)

            st.markdown(f"""
            <div dir="rtl" style="text-align: right; background: #FFFFFF; padding: 22px; border-radius: 12px; border: 1.5px solid {CBE_ORANGE_MID}; margin-bottom: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
              <h3 style="color: {CBE_NAVY}; font-weight: bold; margin-bottom: 8px;">📈 محاكاة دولة: {sim_country_sel} | السيناريو: {scenario_dropdown}</h3>
              <p style="font-size: 15px; margin-bottom: 8px;"><b>القيمة المتوقعة للمؤشر بعد المحاكاة:</b> {sim_colored_html} (صافي التغير: <span style="font-weight: bold;">{delta:+.2f}</span>)</p>
              <div style="background: {CBE_BG}; padding: 12px; border-radius: 8px; border-right: 4px solid {CBE_ORANGE_MID}; margin-top: 10px;">
                <p style="margin-bottom: 6px;"><b>🔬 التحليل القياسي:</b> {analysis_text}</p>
                <p style="margin: 0 0 8px 0; color: {CBE_ORANGE_MID}; font-weight: bold;">🛠️ خطة التحرك الاستباقية: {action_plan}</p>
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='padding:20px; text-align:center; color:#0A192F; background:#FFFFFF; border-radius:10px; border:1px solid #B45309;'><b>📈 قم بضبط الدولة والسيناريو ومتغيرات التحفيز واضغط على زر التثبيت لمتابعة السيناريوهات هنا.</b></div>", unsafe_allow_html=True)

    if st.button("📥 تصدير وطباعة تقرير المحاكي (PDF / طباعة)", key="exp_2"):
        st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

    st.markdown('<div class="footer-copyright">جميع الحقوق محفوظة للدراسة البحثية</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# التبويب الثالث: لوحة دعم اتخاذ القرار
# ------------------------------------------------------------------------------
with tab3:
    st.markdown("### 🛡️ لوحة دعم اتخاذ القرار ولوحة التطعيم الثقافي (Cultural Grafting Canvas)")
    st.markdown("استعراض وتثبيت التوصيات المخصصة لكل دولة مختارة بديناميكية تمنع التكرار وتدعم السيادة الرقمية.")

    col_d1, col_d2 = st.columns([1, 2])
    with col_d1:
        rec_list = [item["الدولة"] for item in st.session_state.comparison_history_state]
        dec_country_sel = st.selectbox("اختر الدولة لاستعراض التوصيات", rec_list if rec_list else ["اختر دولة مسجلة أولاً"], key="dec_c")
        gen_dec_btn = st.button("📋 توليد وتثبيت توصيات الدولة", key="gen_dec")

    with col_d2:
        if gen_dec_btn and st.session_state.comparison_history_state:
            country_data = next((item for item in st.session_state.comparison_history_state if item["الدولة"] == dec_country_sel), None)
            if country_data:
                score = country_data["المؤشر المركب (AACRI)"]
                score_col_str = get_colored_score_html(score)
                st.markdown(f"""
                <div dir="rtl" style="text-align: right; background: #FFFFFF; padding: 22px; border-radius: 12px; border: 1.5px solid {CBE_ORANGE_MID}; margin-bottom: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
                  <h3 style="color: {CBE_NAVY}; font-weight: bold; margin-bottom: 8px;">🛡️ تقرير وتوصيات دولة: {dec_country_sel} (المؤشر المركب: {score_col_str})</h3>
                  <ul style="margin: 0 0 10px 0; padding-right: 20px; line-height: 1.8; color: #1E293B;">
                    <li><b>تعزيز ريادة الابتكار الإقليمي:</b> الاستفادة من الجاهزية المرتفعة لتصدير النماذج اللغوية الثقافية العربية الموطنة.</li>
                    <li><b>الحوكمة المتقدمة للذكاء الاصطناعي:</b> قيادة الجهود التشريعية الإقليمية لإلزام الشركات الكبرى بمعايير الوسم المائي والشفافية.</li>
                    <li><b>دعم الاقتصاد البرتقالي:</b> التوسع في توظيف استراتيجية المحيط الأزرق في السياحة الثقافية الافتراضية.</li>
                  </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("يرجى اختيار دولة تمتلك سجلاً مسجلاً.")
        else:
            st.markdown("<div style='padding:20px; text-align:center; color:#0A192F; background:#FFFFFF; border-radius:10px; border:1px solid #B45309;'><b>🛡️ يرجى اختيار الدولة المسجلة والضغط على زر التوليد لعرض التوصيات.</b></div>", unsafe_allow_html=True)

    if st.button("📥 تصدير وطباعة تقرير لوحة القرار (PDF / طباعة)", key="exp_3"):
        st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

    st.markdown('<div class="footer-copyright">جميع الحقوق محفوظة للدراسة البحثية</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# التبويب الرابع: التقرير التنفيذي الموحد
# ------------------------------------------------------------------------------
with tab4:
    st.markdown("### 📑 أداة تصدير التقرير التنفيذي الموحد لسياسات الصناعات الثقافية والإبداعية")
    st.markdown("ملخص استراتيجي شامل يدمج نتائج التشخيص الوصفي، التحليل العميق للمحاور، وشجرة نقاط الرفع لدونيلا ميدوز في تقرير موحد جاهز للعرض على القيادات العليا.")

    if st.button("🔄 تحديث وتوليد التقرير التنفيذي الموحد", key="gen_exec"):
        if st.session_state.comparison_history_state:
            df_ex = pd.DataFrame(st.session_state.comparison_history_state)
            top_row = df_ex.iloc[0]
            top_c = top_row["الدولة"]
            top_s_col = get_colored_score_html(top_row["المؤشر المركب (AACRI)"])

            st.markdown(f"""
            <div dir="rtl" style="text-align: right; background: #FFFFFF; padding: 30px; border-radius: 14px; border: 2px solid {CBE_ORANGE_MID}; line-height: 1.9; box-shadow: 0 6px 20px rgba(0,0,0,0.08);">
              <div style="text-align: center; border-bottom: 2px solid {CBE_ORANGE_MID}; padding-bottom: 15px; margin-bottom: 25px;">
                <h2 style="color: {CBE_NAVY}; font-weight: 800; margin: 0;">📑 التقرير التنفيذي الموحد لسياسات الصناعات الثقافية والإبداعية العربية</h2>
                <p style="color: #64748B; font-size: 14.5px; margin-top: 6px;">ملخص استراتيجي موجه للقيادات العليا وصناع القرار - بناءً على مخرجات الدراسة المنهجية والتفكير المنظومي (AACRI)</p>
              </div>
              <div style="background: {CBE_BG}; padding: 18px; border-radius: 10px; border-right: 5px solid {CBE_ORANGE_MID}; margin-bottom: 25px;">
                <h4 style="color: {CBE_NAVY}; margin-top: 0;">🏆 مؤشرات الأداء العام والريادة الإقليمية:</h4>
                <p>الدولة المتصدرة حالياً في مؤشر الجاهزية الذكية هي: <b>{top_c}</b> بقيمة مركبة تبلغ {top_s_col}.</p>
                <p>إجمالي الدول الخاضعة للتشخيص: <b>{len(df_ex)} دولة عربية</b>.</p>
              </div>
              <div style="background: #FFFBEB; padding: 22px; border-radius: 12px; border: 1.5px solid #FCD34D;">
                <h4 style="color: #92400E; margin-top: 0;">🌳 إطار شجرة قرارات نقاط الرفع المنظومي (Meadows Leverage Points Framework):</h4>
                <p style="color: #78350F;">تعتمد المنظومة في قراراتها على مستويات التأثير لدونيلا ميدوز مرتبة من المعلمات والميزانيات وصولاً إلى النماذج الفكرية والبارادايمات (الأشد تأثيراً).</p>
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("📂 لا توجد بيانات مسجلة. يرجى إدخال تشخيص دولة واحدة على الأقل في القسم الأول.")

    if st.button("📥 تصدير وطباعة التقرير التنفيذي الموحد (PDF / طباعة)", key="exp_4"):
        st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

    st.markdown('<div class="footer-copyright">جميع الحقوق محفوظة للدراسة البحثية</div>', unsafe_allow_html=True)
