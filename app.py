st.markdown("---")
    st.markdown("""
    <div dir="rtl" style="text-align: right;">
        <h3>📋 قائمة ترتيب الدول العربية المسجلة</h3>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.history_state:
        df_history = pd.DataFrame(st.session_state.history_state).sort_values(by="المؤشر المركب (AACRI)", ascending=False).reset_index(drop=True)
        
        # بناء جدول HTML مخصص لضمان الترتيب العربي الصحيح (من اليمين لليسار)
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
