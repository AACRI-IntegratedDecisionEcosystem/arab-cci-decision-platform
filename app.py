import os
import random
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 0. إعدادات الصفحة وتهيئة الجلسة لـ Streamlit
# ==============================================================================
st.set_page_config(
    page_title="منصة منظومة القرار المتكاملة للسياسات الثقافية والإبداعية العربية",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# تهيئة حالة الجلسة للتسجيل والبيانات
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "history_state" not in st.session_state:
    st.session_state.history_state = []
if "simulated_results_dict" not in st.session_state:
    st.session_state.simulated_results_dict = {}
if "decision_results_dict" not in st.session_state:
    st.session_state.decision_results_dict = {}

# ==============================================================================
# 1. الهوية البصرية والتصميم (Custom CSS للألوان والاتجاه من اليمين لليسار)
# ==============================================================================
CBE_ORANGE_DARK = "#78350F" # برتقالي غامق جداً قاتم
CBE_ORANGE_MID = "#B45309"  # برتقالي غامق تراثي
CBE_ORANGE_LIGHT = "#D97706"# برتقالي أفتح نسبياً عند التحديد
CBE_NAVY = "#0A192F"        # أزرق ملكي عميق
CBE_BG = "#F8FAFC"          # خلفية ناعمة

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap');

html, body, [class*="css"] {{
    background-color: {CBE_BG} !important;
    font-family: 'Cairo', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    direction: rtl !important;
    text-align: right !important;
}}

.stApp {{
    background-color: {CBE_BG} !important;
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
""", unsafe_allow_html=True)

# ==============================================================================
# 2. واجهة الدخول (Login Modal / Box) في منتصف الشاشة
# ==============================================================================
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="background: #FFFFFF; padding: 35px; border-radius: 16px; border: 2px solid {CBE_ORANGE_MID}; box-shadow: 0 10px 30px rgba(0,0,0,0.15); text-align: right;" dir="rtl">
            <h2 style="color: {CBE_NAVY}; font-weight: 800; text-align: center; margin-bottom: 10px;">🏛️ منصة منظومة القرار المتكاملة</h2>
            <p style="color: #475569; font-size: 14px; text-align: center; line-height: 1.6; margin-bottom: 25px;">
                نموذج رقمي استراتيجي لتطوير مهن الصناعات الثقافية والإبداعية العربية في عصر الذكاء الاصطناعي بمنظور التفكير المنظومي. يرجى تسجيل الدخول للمتابعة.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("اسم المستخدم (User)", value="")
            password = st.text_input("كلمة المرور (Password)", type="password", value="")
            submit_login = st.form_submit_button("تسجيل الولوج للمنصة 🚀", use_container_width=True)
            
            if submit_login:
                if username == "user" and password == "123":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("⚠️ اسم المستخدم أو كلمة المرور غير صحيحة. (جرّب user و 123)")
    st.stop()

# ==============================================================================
# 3. القائمة الرسمية للدول العربية والمكتبات المساعدة
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

# ==============================================================================
# 4. التروياسة والشريط الإخباري العلوي
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
# 5. التبويبات الأربعة الرئيسية للمنصة عبر Streamlit Tabs
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

    col_a, col_b = st.columns([1, 2], gap="large")
    
    with col_a:
        country_sel = st.selectbox("اختر الدولة العربية", ARAB_COUNTRIES, key="c_sel")
        ti_slider = st.slider("1️⃣ البنية التقنية (وزن 20%)", 0, 100, 68)
        ed_slider = st.slider("2️⃣ الديناميكيات الاقتصادية (وزن 15%)", 0, 100, 70)
        hc_slider = st.slider("3️⃣ رأس المال البشري (وزن 30%)", 0, 100, 72)
        rf_slider = st.slider("4️⃣ البيئة التنظيمية والتشريعية (وزن 20%)", 0, 100, 65)
        cd_slider = st.slider("5️⃣ المحددات الثقافية والهوياتية (وزن 15%)", 0, 100, 82)

        calc_btn = st.button("🚀 احسب وسجل قياس الدولة", use_container_width=True)

    with col_b:
        result_placeholder = st.empty()
        radar_placeholder = st.empty()

    if calc_btn:
        if country_sel == "الدولة":
            result_placeholder.markdown("<div style='padding:20px; text-align:center; color:#991B1B; background:#FEF2F2; border-radius:10px; border:1px solid #F87171;'><b>⚠️ يرجى اختيار دولة عربية حقيقية من القائمة لتنفيذ التشخيص القياسي.</b></div>", unsafe_allow_html=True)
        else:
            weights = {'TI': 0.20, 'ED': 0.15, 'HC': 0.30, 'RF': 0.20, 'CD': 0.15}
            final_score = (ti_slider * weights['TI']) + (ed_slider * weights['ED']) + (hc_slider * weights['HC']) + (rf_slider * weights['RF']) + (cd_slider * weights['CD'])
            final_score = round(final_score, 2)
            score_colored = get_colored_score_html(final_score)

            if final_score >= 80:
                diagnosis = "🟢 جاهزية متقدمة للغاية نحو السيادة الرقمية والابتكار المستدام وتفعيل 'المبدع المعزز'."
                detailed_diag = f"🟢 **جاهزية متقدمة ومستدامة:** إجمالي المؤشر المركب {score_colored}. تعكس هذه النتيجة تفوقاً هيكلياً في بيئة العمل، ورأس مال بشري مؤهل للتعامل مع التقنيات التوليدية، وبنية تقنية متطورة تتيح قيادة التحالفات الإقليمية وتوطين النماذج الثقافية الرقمية بكفاءة عالية بما يضمن صون الأمن الثقافي."
            elif final_score >= 51:
                diagnosis = "🟡 جاهزية متوسطة، تتطلب تدخلات استباقية لمعالجة الاختناقات الهيكلية."
                detailed_diag = f"🟡 **جاهزية متوسطة تتطلب تدخلاً استباقياً:** إجمالي المؤشر المركب {score_colored}. تشير المؤشرات إلى توازن نسبي يواجه بعض الاختناقات الهيكلية في سلاسل القيمة أو التشريعات التنظيمية، مما يستوجب حزم تحفيزية وبرامج إعادة تأهيل (Upskilling & Reskilling) لردم الفجوات القائمة."
            else:
                diagnosis = "🔴 وجود فجوة ذكية هيكلية تستوجب تفعيل محاكي السياسات ولوحة دعم اتخاذ القرار فوراً."
                detailed_diag = f"🔴 **فجوة ذكية هيكلية حرجة:** إجمالي المؤشر المركب {score_colored}. توضح القراءة الحالية وجود اختناقات عميقة في البنية التحتية والبيئة التشريعية ورأس المال البشري، مما يستوجب تفعيل محاكي السياسات ولوحة التطعيم الثقافي لدعم 'المبدع المعزز' وتفادي الاستلاب الخوارزمي."

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

            # تحديث السجل التراكمي
            updated = False
            for idx, item in enumerate(st.session_state.history_state):
                if item["الدولة"] == country_sel:
                    st.session_state.history_state[idx] = entry
                    updated = True
                    break
            if not updated:
                st.session_state.history_state.append(entry)

            result_html = f"""
            <div dir="rtl" style="text-align: right; background: #FFFFFF; padding: 25px; border-radius: 12px; border: 1.5px solid {CBE_ORANGE_MID}; line-height: 1.9; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
              <h3 style="color: {CBE_NAVY}; font-weight: bold; margin-bottom: 12px;">📊 نتائج التشخيص المنظومي للدولة العربية (إطار AACRI - 69 متغيراً)</h3>
              <p style="font-size: 15px; margin-bottom: 8px;"><b>النموذج الخاضع للتشخيص:</b> <span style="color: {CBE_NAVY}; font-weight: bold;">{country_sel}</span></p>
              <p style="font-size: 16px; margin-bottom: 12px;"><b>القيمة المركبة لمؤشر الجاهزية الذكية (AACRI):</b> <span style="font-size: 18px;">{score_colored}</span></p>
              <div style="background: {CBE_BG}; padding: 16px; border-radius: 8px; border-right: 5px solid {CBE_ORANGE_MID}; margin-top: 10px;">
                <p style="margin: 0 0 8px 0; font-weight: bold; color: {CBE_NAVY};">التقييم التشخيصي والتفصيل المنظومي:</p>
                <p style="margin: 0; color: #1E293B; font-size: 14.5px;">{detailed_diag}</p>
              </div>
            </div>
            """
            result_placeholder.markdown(result_html, unsafe_allow_html=True)

            categories = ['البنية التقنية (20%)', 'الديناميكيات الاقتصادية (15%)', 'رأس المال البشري (30%)', 'البيئة التنظيمية والتشريعية (20%)', 'المحددات الثقافية والهوياتية (15%)']
            scores_list = [ti_slider, ed_slider, hc_slider, rf_slider, cd_slider]
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=scores_list, theta=categories, fill='toself', name=country_sel, line_color=CBE_ORANGE_MID))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), paper_bgcolor="#FFFFFF", font=dict(family="Cairo", size=13))
            radar_placeholder.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📋 قائمة ترتيب الدول العربية المسجلة")

    if st.session_state.history_state:
        df_hist = pd.DataFrame(st.session_state.history_state).sort_values(by="المؤشر المركب (AACRI)", ascending=False).reset_index(drop=True)
        # جعل الجدول يبدأ من رقم 1 بدلاً من 0 وتوجيهه من اليمين لليسار
        df_hist.index = range(1, len(df_hist) + 1)
        st.dataframe(df_hist, use_container_width=True)

        col_del1, col_del2 = st.columns([2, 1])
        with col_del1:
            countries_in_hist = [item["الدولة"] for item in st.session_state.history_state]
            del_choice = st.selectbox("اختر دولة من السجل لحذفها", countries_in_hist, key="del_sel")
        with col_del2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ حذف الدولة المحددة", use_container_width=True):
                st.session_state.history_state = [item for item in st.session_state.history_state if item["الدولة"] != del_choice]
                st.success(f"تم حذف سجل دولة ({del_choice}) بنجاح.")
                st.rerun()
    else:
        st.info("📂 لا توجد دول مسجلة حتى الآن. قم بإدخال بيانات الدولة في الأعلى واضغط على زر الحساب.")

    if st.button("📥 تصدير وطباعة تقرير القسم الأول (طباعة رسمية)", key="exp1"):
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
        weights = [20, 15, 30, 20, 15]
        fig_bar = px.bar(x=axes_names, y=weights, text=weights, title="توزيع الأوزان النسبية لمحاور مؤشر الجاهزية الذكية (AACRI) وفق التحليل الهرمي AHP", color=weights, color_continuous_scale="Oranges")
        st.plotly_chart(fig_bar, use_container_width=True)

# ------------------------------------------------------------------------------
# التبويب الثاني: محاكي السياسات (Policy Simulator)
# ------------------------------------------------------------------------------
with tab2:
    st.markdown("### 🔬 محاكي السياسات الاستشرافي والمتابعة التراكمية للسيناريوهات")
    st.markdown("استشراف أثر التدخلات الاستثمارية والتقنية عبر النمذجة القياسية ومتغيرات التحفيز الاستراتيجي.")

    col_s1, col_s2 = st.columns([1, 2], gap="large")
    with col_s1:
        registered_countries = [item["الدولة"] for item in st.session_state.history_state] if st.session_state.history_state else ARAB_COUNTRIES[1:]
        sim_country = st.selectbox("اختر الدولة للمحاكاة", registered_countries, key="sim_c")
        base_aacri_val = st.slider("قيمة المؤشر الافتراضي الحالي", 30.0, 100.0, 68.5, 0.5)
        
        # ربط القيمة الفعلية إن كانت مسجلة في التبويب الأول لضمان الثبات والاتساق
        for item in st.session_state.history_state:
            if item["الدولة"] == sim_country:
                base_aacri_val = item["المؤشر المركب (AACRI)"]

        scenario_type = st.selectbox("اختر السيناريو الاستراتيجي", [
            "📊 السيناريو المعتدل / التفاؤلي (استثمارات تقليدية تدريجية)",
            "📉 السيناريو التشاؤمي (غياب التدخل وضعف الاستثمار)",
            "🚀 السيناريو الطموح / الاستباقي (إصلاحات هيكلية شاملة وسيادة تقنية)"
        ])
        var1_t = st.slider("1️⃣ نسبة الزيادة في البنية التقنية (%)", 0, 50, 20)
        var2_e = st.slider("2️⃣ نسبة الزيادة في الديناميكيات الاقتصادية (%)", 0, 15, 15)
        var3_h = st.slider("3️⃣ نسبة الزيادة في رأس المال البشري (%)", 0, 50, 15)
        var4_r = st.slider("4️⃣ معدل تطوير البيئة التنظيمية (%)", 0, 50, 10)
        var5_cu = st.slider("5️⃣ نسبة التوسع في المحددات الثقافية (%)", 0, 50, 25)

        run_sim_btn = st.button("📋 إضافة وتثبيت سيناريو الدولة", use_container_width=True)

    with col_s2:
        sim_box_placeholder = st.empty()
        
        if run_sim_btn:
            combined_boost = (var1_t * 0.25) + (var2_e * 0.15) + (var3_h * 0.3) + (var4_r * 0.2) + (var5_cu * 0.1)
            if scenario_type.startswith("📉"):
                sim_val = max(0.0, base_aacri_val * 0.90)
                analysis_text = f"تحذير هيكلي لـ ({sim_country}): استمرار الركود وغياب الإصلاحات سيؤدي إلى تفاقم فجوة الإحلال الخوارزمي واندثار المهن الثقافية بنسبة تصل إلى 32%."
                action_plan = "التدخل الفوري لإيقاف التدهور وإعادة تخصيص ميزانيات طارئة وتفعيل لوحة التطعيم الثقافي."
            elif scenario_type.startswith("📊"):
                sim_val = min(100.0, base_aacri_val * (1 + (combined_boost * 0.0022)))
                analysis_text = f"تقدم ملحوظ لـ ({sim_country}): نجاح تدريجي في ترشيد استخدام الأدوات التوليدية، دعم مهارات 'المبدع المعزز'، وتقليص الفجوة المهنية."
                action_plan = "توسيع برامج التدريب المستمر (Upskilling & Reskilling) واعتماد حزم تحفيزية."
            else:
                sim_val = min(100.0, base_aacri_val * (1 + (combined_boost * 0.0042)))
                analysis_text = f"نجاح استراتيجي فائق لـ ({sim_country}): تحقيق السيادة الرقمية الكاملة، توطين النماذج اللغوية الثقافية العربية، وتفعيل دور المبدع كشريك إبداعي مهيمن."
                action_plan = "قيادة التحالفات التقنية الإقليمية وإطلاق المنصات السحابية المفتوحة وتأمين الأمن الثقافي."

            sim_val = round(sim_val, 2)
            delta = round(sim_val - base_aacri_val, 2)
            sim_colored_html = get_colored_score_html(sim_val)

            if base_aacri_val >= 80:
                deep_analysis = "<div style='background: #F0FDF4; padding: 14px; border-radius: 8px; border-right: 4px solid #16A34A; margin-top: 10px;'><p style='margin: 0; color: #14532D; font-size: 14px;'>الدولة تتمتع بامتصاص صدمات تقنية عالية؛ لذا فإن السياسات المستهدفة يجب أن تركز على قيادة المعايير العالمية للوسم المائي وحماية الهوية.</p></div>"
            elif base_aacri_val >= 51:
                deep_analysis = "<div style='background: #FEFCE8; padding: 14px; border-radius: 8px; border-right: 4px solid #CA8A04; margin-top: 10px;'><p style='margin: 0; color: #713F12; font-size: 14px;'>يتضح وجود تفاوت بين البنية التقنية ورأس المال البشري؛ يتطلب الأمر التركيز على سد الفجوة بين مخرجات التعليم العالي واحتياجات الاقتصاد البرتقالي.</p></div>"
            else:
                deep_analysis = "<div style='background: #FEF2F2; padding: 14px; border-radius: 8px; border-right: 4px solid #DC2626; margin-top: 10px;'><p style='margin: 0; color: #7F1D1D; font-size: 14px;'>الدولة تواجه هشاشة في سلاسل القيمة الإبداعية؛ تتطلب المحاكاة هنا تدخلات عاجلة وحزم طوارئ استثمارية لدعم البنية التحتية واحتواء الاقتصاد غير الرسمي.</p></div>"

            new_sim_box = f"""
            <div dir="rtl" style="text-align: right; background: #FFFFFF; padding: 22px; border-radius: 12px; border: 1.5px solid {CBE_ORANGE_MID}; margin-bottom: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
              <h3 style="color: {CBE_NAVY}; font-weight: bold; margin-bottom: 8px;">📈 محاكاة دولة: {sim_country} | السيناريو: {scenario_type}</h3>
              <p style="font-size: 15px; margin-bottom: 8px;"><b>القيمة المتوقعة للمؤشر بعد المحاكاة:</b> {sim_colored_html} (صافي التغير: <span style="font-weight: bold;">{delta:+.2f}</span>)</p>
              <div style="background: {CBE_BG}; padding: 12px; border-radius: 8px; border-right: 4px solid {CBE_ORANGE_MID}; margin-top: 10px;">
                <p style="margin-bottom: 6px;"><b>🔬 التحليل القياسي:</b> {analysis_text}</p>
                <p style="margin: 0 0 8px 0; color: {CBE_ORANGE_MID}; font-weight: bold;">🛠️ خطة التحرك الاستباقية: {action_plan}</p>
              </div>
              {deep_analysis}
            </div>
            """
            st.session_state.simulated_results_dict[sim_country] = new_sim_box

        # عرض جميع السيناريوهات المثبتة للحفاظ على الثبات والاتساق
        if st.session_state.simulated_results_dict:
            combined_sim_html = "".join(st.session_state.simulated_results_dict.values())
            sim_box_placeholder.markdown(combined_sim_html, unsafe_allow_html=True)
        else:
            sim_box_placeholder.markdown("<div style='padding:20px; text-align:center; color:#0A192F; background:#FFFFFF; border-radius:10px; border:1px solid #B45309;'><b>📈 قم بضبط الدولة والسيناريو ومتغيرات التحفيز واضغط على زر الإضافة لتثبيت ومتابعة السيناريوهات هنا.</b></div>", unsafe_allow_html=True)

    if st.button("📥 تصدير وطباعة تقرير المحاكي (PDF / طباعة)", key="exp2"):
        st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# التبويب الثالث: لوحة دعم اتخاذ القرار
# ------------------------------------------------------------------------------
with tab3:
    st.markdown("### 🛡️ لوحة دعم اتخاذ القرار ولوحة التطعيم الثقافي (Cultural Grafting Canvas)")
    st.markdown("استعراض وتثبيت التوصيات المخصصة لكل دولة مختارة بديناميكية تمنع التكرار وتدعم السيادة الرقمية.")

    col_d1, col_d2 = st.columns([1, 2], gap="large")
    with col_d1:
        registered_countries_d = [item["الدولة"] for item in st.session_state.history_state] if st.session_state.history_state else ARAB_COUNTRIES[1:]
        decision_country = st.selectbox("اختر الدولة لاستعراض وإضافة التوصيات", registered_countries_d, key="dec_c")
        gen_dec_btn = st.button("📋 إضافة وتثبيت توصيات الدولة المختارة", use_container_width=True)

    with col_d2:
        dec_box_placeholder = st.empty()

        if gen_dec_btn:
            score = 70.0
            for item in st.session_state.history_state:
                if item["الدولة"] == decision_country:
                    score = item["المؤشر المركب (AACRI)"]
                    break

            score_colored_str = get_colored_score_html(score)

            if score >= 80:
                recs = f"<li><b>تعزيز ريادة الابتكار الإقليمي:</b> الاستفادة من جاهزية ({decision_country}) لتصدير النماذج اللغوية الثقافية.</li><li><b>الحوكمة المتقدمة للذكاء الاصطناعي:</b> قيادة الجهود التشريعية بمعايير الوسم المائي.</li>"
                deep_d = "<div style='background: #F0FDF4; padding: 14px; border-radius: 8px; border-right: 4px solid #16A34A; margin-top: 12px;'><p style='margin:0; color:#14532D; font-size:14px;'>توصي منظومة القرار بإنشاء مجلس سيادي أعلى للذكاء الاصطناعي والثقافة لربط البحث والتطوير بالأسواق الإقليمية.</p></div>"
            elif score >= 51:
                recs = f"<li><b>ردم الفجوة التقنية والبشرية:</b> إطلاق حزم إعادة التأهيل السريع (Upskilling & Reskilling) في ({decision_country}).</li><li><b>توثيق التراث الرقمي:</b> تسريع أرشفة الأصول عبر قواعد بيانات ثلاثية الأبعاد.</li>"
                deep_d = "<div style='background: #FEFCE8; padding: 14px; border-radius: 8px; border-right: 4px solid #CA8A04; margin-top: 12px;'><p style='margin:0; color:#713F12; font-size:14px;'>تتطلب صانعة القرار هنا تفعيل حاضنات الأعمال الإبداعية المشتركة وتوجيه الدعم نحو القطاعات الأكثر عرضة للإحلال.</p></div>"
            else:
                recs = f"<li><b>التدخل الاستباقي العاجل:</b> معالجة الاختناقات الهيكلية الحادة لـ ({decision_country}).</li><li><b>احتواء الاقتصاد غير الرسمي:</b> دمج الأنشطة المستترة عبر أدوات الحصر الرقمي.</li>"
                deep_d = "<div style='background: #FEF2F2; padding: 14px; border-radius: 8px; border-right: 4px solid #DC2626; margin-top: 12px;'><p style='margin:0; color:#7F1D1D; font-size:14px;'>تفرض الضرورة استدعاء إطار التكامل الوظيفي الإقليمي ونقل الخبرات التقنية والبنية التحتية.</p></div>"

            new_dec_box = f"""
            <div dir="rtl" style="text-align: right; background: #FFFFFF; padding: 22px; border-radius: 12px; border: 1.5px solid {CBE_ORANGE_MID}; margin-bottom: 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
              <h3 style="color: {CBE_NAVY}; font-weight: bold; margin-bottom: 8px;">🛡️ تقرير وتوصيات دولة: {decision_country} (المؤشر المركب: {score_colored_str})</h3>
              <ul style="margin: 0 0 10px 0; padding-right: 20px; line-height: 1.8; color: #1E293B;">
                {recs}
              </ul>
              {deep_d}
            </div>
            """
            st.session_state.decision_results_dict[decision_country] = new_dec_box

        if st.session_state.decision_results_dict:
            combined_dec_html = "".join(st.session_state.decision_results_dict.values())
            dec_box_placeholder.markdown(combined_dec_html, unsafe_allow_html=True)
        else:
            dec_box_placeholder.markdown("<div style='padding:20px; text-align:center; color:#0A192F; background:#FFFFFF; border-radius:10px; border:1px solid #B45309;'><b>🛡️ يرجى اختيار الدولة المسجلة والضغط على زر الإضافة لتثبيت التوصيات هنا.</b></div>", unsafe_allow_html=True)

    if st.button("📥 تصدير وطباعة تقرير لوحة القرار والتوصيات (طباعة)", key="exp3"):
        st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# التبويب الرابع: التقرير التنفيذي الموحد
# ------------------------------------------------------------------------------
with tab4:
    st.markdown("### 📑 أداة تصدير التقرير التنفيذي الموحد لسياسات الصناعات الثقافية والإبداعية")
    st.markdown("ملخص استراتيجي شامل يدمج نتائج التشخيص الوصفي، التحليل العميق للمحاور، وشجرة نقاط الرفع لدونيلا ميدوز في تقرير موحد جاهز للعرض على القيادات العليا.")

    if st.button("🔄 تحديث وتوليد التقرير التنفيذي الموحد بناءً على البيانات المدخلة", use_container_width=True):
        if not st.session_state.history_state:
            st.warning("📂 لا توجد بيانات مسجلة كافية حتى الآن. يرجى إدخال تشخيص دولة واحدة على الأقل في القسم الأول.")
        else:
            df_rep = pd.DataFrame(st.session_state.history_state)
            top_row = df_rep.iloc[0] if not df_rep.empty else None
            top_country = top_row["الدولة"] if top_row is not None else "غير محدد"
            top_score = top_row["المؤشر المركب (AACRI)"] if top_row is not None else 0
            top_score_col = get_colored_score_html(top_score)

            countries_summary = ""
            for idx, row in df_rep.iterrows():
                s = row['المؤشر المركب (AACRI)']
                s_col = get_colored_score_html(s)
                countries_summary += f"""
                <li style="margin-bottom: 15px; background: #F8FAFC; padding: 14px; border-radius: 8px; border: 1px solid #E2E8F0;">
                    <b>{row['الدولة']}</b> — المؤشر المركب: {s_col} — التقييم: {row['التقييم المنظومي']}
                </li>
                """

            exec_html = f"""
            <div dir="rtl" style="text-align: right; background: #FFFFFF; padding: 30px; border-radius: 14px; border: 2px solid {CBE_ORANGE_MID}; line-height: 1.9;">
              <div style="text-align: center; border-bottom: 2px solid {CBE_ORANGE_MID}; padding-bottom: 15px; margin-bottom: 25px;">
                <h2 style="color: {CBE_NAVY}; font-weight: 800; margin: 0;">📑 التقرير التنفيذي الموحد لسياسات الصناعات الثقافية والإبداعية العربية</h2>
                <p style="color: #64748B; font-size: 14.5px; margin-top: 6px;">ملخص استراتيجي موجه للقيادات العليا وصناع القرار - بناءً على مخرجات الدراسة المنهجية والتفكير المنظومي (AACRI)</p>
              </div>
              <div style="background: {CBE_BG}; padding: 18px; border-radius: 10px; border-right: 5px solid {CBE_ORANGE_MID}; margin-bottom: 25px;">
                <h4 style="color: {CBE_NAVY}; margin-top: 0;">🏆 مؤشرات الأداء العام والريادة الإقليمية:</h4>
                <p style="margin-bottom: 8px;">الدولة المتصدرة حالياً في مؤشر الجاهزية الذكية هي: <span style="font-weight: bold;">{top_country}</span> بقيمة مركبة تبلغ {top_score_col}.</p>
                <p style="margin: 0;">إجمالي الدول الخاضعة للتشخيص والتحليل المنظومي حتى الآن: <b>{len(df_rep)} دولة عربية</b>.</p>
              </div>
              <h4 style="color: {CBE_NAVY}; margin-bottom: 12px;">📋 ملخص نتائج التشخيص التراكمي للدول:</h4>
              <ul style="margin-bottom: 25px; padding-right: 0; list-style-type: none;">
                {countries_summary}
              </ul>
              <div style="background: #FFFBEB; padding: 22px; border-radius: 12px; border: 1.5px solid #FCD34D; margin-bottom: 15px;">
                <h4 style="color: #92400E; margin-top: 0; font-size: 17px;">🌳 إطار شجرة قرارات نقاط الرفع المنظومي (Meadows Leverage Points Framework):</h4>
                <ul style="margin: 0; padding-right: 20px; line-height: 1.9; color: #78350F;">
                  <li><b>1. المعلمات والميزانيات:</b> تعديل نسب الإنفاق المباشر وموازنات دعم التدريب.</li>
                  <li><b>2. تدفق المعلومات وحلقات التغذية الراجعة:</b> توفير قواعد بيانات مرجعية ومنصات حصر رقمي.</li>
                  <li><b>3. القواعد والحوكمة:</b> تشريع أطر الملكية الفكرية المشتركة وحماية حقوق المبدع المعزز.</li>
                  <li><b>4. أهداف النظام:</b> توجيه السياسات الوطنية نحو تحقيق السيادة الرقمية والأمن الثقافي.</li>
                  <li><b>5. النماذج الفكرية والبارادايمات:</b> ترسيخ مفهوم الاقتصاد البرتقالي والبنفسجي.</li>
                </ul>
              </div>
            </div>
            """
            st.markdown(exec_html, unsafe_allow_html=True)

    if st.button("📥 تصدير وطباعة التقرير التنفيذي الموحد (طباعة رسمية للقيادات)", key="exp4"):
        st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

st.markdown(f'<div class="footer-copyright">جميع الحقوق محفوظة للدراسة البحثية</div>', unsafe_allow_html=True)
