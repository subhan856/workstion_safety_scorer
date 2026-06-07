# HEALTH PROFILE FORM  (shown after first login / register)
# ---------------------------------------------------------------------
def health_profile_page():
    u = st.session_state.user
    st.markdown("""
    <div class='welcome-banner' style='text-align:center;'>
        <div class='welcome-title'>Complete Your <span>Health Profile</span></div>
        <div class='welcome-sub'>
            This information personalises your risk assessment and PDF report
        </div>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        with st.form("health_profile_form"):
            st.markdown("<div class='section-heading'>PERSONAL HEALTH DATA</div>",
                        unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            age    = c1.number_input("Age (years)",    min_value=10, max_value=100, value=22, step=1)
            gender = c2.selectbox("Gender",
                ["Prefer not to say", "Male", "Female", "Non-binary / Other"])

            c3, c4 = st.columns(2)
            height = c3.number_input("Height (cm)",    min_value=100.0, max_value=250.0, value=170.0, step=0.5)
            weight = c4.number_input("Weight (kg)",    min_value=30.0,  max_value=300.0, value=70.0,  step=0.5)

            bmi_preview = round(weight / ((height / 100) ** 2), 1) if height > 0 else 0
            bmi_cat = ("Underweight" if bmi_preview < 18.5 else
                       "Normal weight" if bmi_preview < 25 else
                       "Overweight" if bmi_preview < 30 else "Obese")
            st.markdown(f"""
            <div style='background:rgba(56,189,248,0.07);border:1px solid rgba(56,189,248,0.2);
                        border-radius:10px;padding:10px 16px;margin:6px 0 14px;
                        font-family:JetBrains Mono,monospace;font-size:.9rem;color:#38BDF8;'>
                BMI: {bmi_preview} — {bmi_cat}
            </div>
            """, unsafe_allow_html=True)

            activity = st.selectbox("Physical Activity Level", [
                "Sedentary (little or no exercise)",
                "Light (1-3 days/week)",
                "Moderate (3-5 days/week)",
                "Active (6-7 days/week)",
                "Very Active (athlete / physical job)",
            ])

            med_hist = st.text_area(
                "Relevant Medical History (optional)",
                placeholder="e.g. Back pain, carpal tunnel, hypertension, diabetes...",
                height=80,
            )

            submitted = st.form_submit_button("SAVE HEALTH PROFILE", use_container_width=True)
            if submitted:
                bmi_val = save_health_profile(
                    u["username"], age, gender, height, weight,
                    activity, med_hist
                )
                # Refresh user in session
                updated = login_user.__wrapped__(u["username"]) if hasattr(login_user, "__wrapped__") else None
                conn = get_conn()
                row = conn.execute(
                    "SELECT id,username,full_name,dept,role,age,gender,height_cm,weight_kg,bmi,activity,medical_hist FROM users WHERE username=?",
                    (u["username"],)
                ).fetchone()
                conn.close()
                if row:
                    st.session_state.user = {
                        "id": row[0], "username": row[1], "full_name": row[2],
                        "dept": row[3], "role": row[4], "age": row[5],
                        "gender": row[6], "height_cm": row[7], "weight_kg": row[8],
                        "bmi": row[9], "activity": row[10], "medical_hist": row[11]
                    }
                st.session_state.show_health_profile = False
                st.success(f"✅ Profile saved! BMI: {bmi_val}")
                st.rerun()

        if st.button("Skip for now", use_container_width=False):
            st.session_state.show_health_profile = False
            st.rerun()

# ---------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------
def sidebar():
    u = st.session_state.user
    with st.sidebar:
        st.markdown(f"""
        <div style='padding:4px 8px 20px;'>
            <div style='font-family:Syne,sans-serif;font-size:1.4rem;font-weight:800;
                        background:linear-gradient(135deg,#38BDF8,#818CF8);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>WSS</div>
            <div style='font-family:Syne,sans-serif;font-size:.58rem;letter-spacing:3px;
                        color:#8899AA;'>ERGO PLATFORM v4.0</div>
        </div>
        <div style='padding:12px 8px;border-top:1px solid rgba(56,189,248,0.1);
                    border-bottom:1px solid rgba(56,189,248,0.1);margin-bottom:16px;'>
            <div style='font-weight:600;font-size:.9rem;color:#F0F4FF;font-family:Syne,sans-serif;'>
                {u["full_name"]}
            </div>
            <div style='font-size:.7rem;color:#8899AA;margin-top:3px;font-family:DM Sans,sans-serif;'>
                {u["dept"]} &nbsp;·&nbsp;
                <span style='color:{"#34D399" if u["role"]=="admin" else "#818CF8"};
                             font-family:JetBrains Mono,monospace;font-size:.65rem;'>
                    {u["role"].upper()}
                </span>
            </div>
            {"<div style='font-size:.7rem;color:#FBBF24;margin-top:4px;'>⚠️ Profile incomplete</div>" if not u.get("age") else ""}
        </div>
        """, unsafe_allow_html=True)

        pages = [
            ("dashboard",  "📊  Dashboard"),
            ("assessment", "📝  New Assessment"),
            ("history",    "📈  My History"),
            ("analytics",  "🔬  Analytics"),
            ("profile",    "👤  Health Profile"),
        ]
        if u["role"] == "admin":
            pages.append(("admin", "⚙️  Admin Panel"))

        for pid, label in pages:
            is_active = st.session_state.page == pid
            btn_style = "sidebar-nav-btn-active" if is_active else ""
            with st.container():
                st.markdown(f"<div class='{btn_style}'>", unsafe_allow_html=True)
                if st.button(label, key=f"nav_{pid}", use_container_width=True):
                    st.session_state.page = pid
                    st.session_state.assessment_done = False
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        if st.button("🚪  Sign Out", use_container_width=True):
            for k, v in defaults.items():
                st.session_state[k] = v
            st.rerun()

        # BMI widget
        if u.get("bmi"):
            bmi = u["bmi"]
            bmi_color = ("#34D399" if bmi < 25 else "#FBBF24" if bmi < 30 else "#F87171")
            st.markdown(f"""
            <div style='margin-top:16px;padding:12px;background:rgba(13,22,37,0.8);
                        border:1px solid rgba(56,189,248,0.12);border-radius:12px;'>
                <div style='font-family:Syne,sans-serif;font-size:.6rem;letter-spacing:2px;
                            color:#8899AA;text-transform:uppercase;'>Health Profile</div>
                <div style='font-family:JetBrains Mono,monospace;font-size:1.1rem;
                            color:{bmi_color};font-weight:600;margin-top:4px;'>
                    BMI {bmi}
                </div>
                <div style='font-size:.72rem;color:#8899AA;margin-top:2px;'>
                    {u.get("height_cm","")} cm · {u.get("weight_kg","")} kg
                </div>
            </div>
            """, unsafe_allow_html=True)

# ---------------------------------------------------------------------
# PAGE: DASHBOARD
# ---------------------------------------------------------------------
def page_dashboard():
    u    = st.session_state.user
    rows = load_user_assessments(u["username"])

    latest_score = rows[0][1] if rows else None
    risk_str, risk_color, _ = risk_label(latest_score) if latest_score is not None else ("No Data", "#8899AA", "")

    trend_html = ""
    if len(rows) >= 2:
        diff  = rows[0][1] - rows[1][1]
        col   = "#34D399" if diff >= 0 else "#F87171"
        arrow = "↑" if diff >= 0 else "↓"
        trend_html = f"<span style='color:{col};font-size:.85rem;font-family:JetBrains Mono,monospace;'>{arrow} {abs(diff):.1f}% vs last</span>"

    # Health advisory strip
    advisory = ""
    if u.get("bmi") and u["bmi"] > 0:
        if u["bmi"] >= 30:
            advisory = "⚕️ BMI indicates obesity — prolonged sedentary work significantly increases musculoskeletal risk. Consider an active workstation."
        elif u["bmi"] >= 25:
            advisory = "⚕️ BMI is in the overweight range — regular movement breaks are especially important for you."

    st.markdown(f"""
    <div class='welcome-banner'>
        <div class='welcome-title'>Welcome back, <span>{u['full_name'].split()[0]}</span></div>
        <div class='welcome-sub'>
            ICT IN HEALTH & ERGONOMICS: WORKSTATION SAFETY SCORER &nbsp;·&nbsp; {u['dept'].upper()}
        </div>
        <div style='margin-top:16px;display:flex;gap:28px;flex-wrap:wrap;align-items:center;'>
            <div style='font-size:.88rem;color:#8899AA;'>
                Latest Score:
                <span style='color:{risk_color};font-size:1.15rem;
                             font-family:JetBrains Mono,monospace;font-weight:600;'>
                    {(str(latest_score)+'%') if latest_score is not None else '--'}
                </span>
                &nbsp; {trend_html}
            </div>
            <div style='font-size:.88rem;color:#8899AA;'>
                Risk: <span style='color:{risk_color};font-weight:700;font-family:Syne,sans-serif;'>
                    {risk_str}
                </span>
            </div>
        </div>
        {"<div class='alert-warn' style='margin-top:14px;'>"+advisory+"</div>" if advisory else ""}
    </div>
    """, unsafe_allow_html=True)

    # KPIs
    total     = len(rows)
    avg       = round(sum(r[1] for r in rows) / total, 1) if rows else 0
    best      = max((r[1] for r in rows), default=0)
    high_risk = sum(1 for r in rows if r[2] == "High Risk")

    c1, c2, c3, c4 = st.columns(4)
    for col, val, label, color, sub in [
        (c1, total,       "Total Assessments", "#38BDF8", "All time"),
        (c2, f"{avg}%",   "Average Score",     "#818CF8", "All sessions"),
        (c3, f"{best}%",  "Best Score",        "#34D399", "Personal peak"),
        (c4, high_risk,   "High Risk Count",   "#F87171", "Needs action"),
    ]:
        col.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-value' style='color:{color};'>{val}</div>
            <div class='kpi-label'>{label}</div>
            <div class='kpi-sub'>{sub}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    if rows:
        latest_cat = json.loads(rows[0][3]) if rows[0][3] else {}
        col_l, col_r = st.columns([1, 1.35])
        with col_l:
            st.markdown("<div class='section-heading'>ERGONOMIC RADAR</div>", unsafe_allow_html=True)
            if latest_cat:
                st.plotly_chart(radar_chart(latest_cat), use_container_width=True,
                                config={"displayModeBar": False})
        with col_r:
            st.markdown("<div class='section-heading'>SCORE HISTORY</div>", unsafe_allow_html=True)
            if len(rows) >= 2:
                st.plotly_chart(history_chart(rows), use_container_width=True,
                                config={"displayModeBar": False})
            else:
                st.markdown("""
                <div class='alert-warn'>
                    Complete at least 2 assessments to unlock the score-trend chart.
                </div>
                """, unsafe_allow_html=True)

        # Category tiles
        st.markdown("<div class='section-heading' style='margin-top:8px;'>LATEST CATEGORY BREAKDOWN</div>",
                    unsafe_allow_html=True)
        if latest_cat:
            cols = st.columns(4)
            for i, (cat, s) in enumerate(latest_cat.items()):
                rl, rc, _ = risk_label(s)
                icon = CAT_ICONS.get(cat, "")
                cols[i % 4].markdown(f"""
                <div class='kpi-card' style='margin-bottom:10px;'>
                    <div style='font-size:.95rem;margin-bottom:2px;'>{icon}</div>
                    <div style='font-family:JetBrains Mono,monospace;font-size:1.35rem;
                                font-weight:600;color:{CAT_COLORS.get(cat,"#38BDF8")};'>
                        {s}%
                    </div>
                    <div class='kpi-label'>{cat}</div>
                    <span class='{risk_badge_class(s)}'>{rl}</span>
                    <div class='risk-bar-wrap'>
                        <div class='risk-bar-fill'
                             style='width:{s}%;background:{CAT_COLORS.get(cat,"#38BDF8")};'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='glass-card' style='text-align:center;padding:48px;'>
            <div style='font-size:2.5rem;margin-bottom:12px;'>📋</div>
            <div style='font-family:Syne,sans-serif;font-size:1.1rem;color:#F0F4FF;'>
                No Assessments Yet
            </div>
            <div style='font-size:.88rem;color:#8899AA;margin-top:8px;'>
                Click <b style='color:#38BDF8;'>New Assessment</b> in the sidebar to get started.
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------------------
# PAGE: ASSESSMENT
# ---------------------------------------------------------------------
def page_assessment():
    st.markdown("<div class='section-heading'>NEW ERGONOMIC ASSESSMENT</div>",
                unsafe_allow_html=True)

    # ── RESULTS VIEW ──
    if st.session_state.assessment_done and st.session_state.last_score is not None:
        score   = st.session_state.last_score
        cat_sc  = st.session_state.last_cat_scores
        risk_str, risk_color, _ = risk_label(score)

        # Score banner
        gauge_color = risk_color
        st.markdown(f"""
        <div class='glass-card' style='text-align:center;padding:40px;'>
            <div style='font-family:Syne,sans-serif;font-size:.65rem;letter-spacing:4px;
                        color:#8899AA;text-transform:uppercase;margin-bottom:8px;'>
                Assessment Complete
            </div>
            <div style='font-family:JetBrains Mono,monospace;font-size:5rem;font-weight:600;
                        color:{gauge_color};text-shadow:0 0 40px {gauge_color}55;
                        line-height:1;'>{score}%</div>
            <div style='font-family:Syne,sans-serif;font-size:1rem;font-weight:700;
                        letter-spacing:3px;color:{gauge_color};margin-top:8px;'>
                {risk_str}
            </div>
            <div style='margin-top:16px;'>
                <span class='{risk_badge_class(score)}'>{risk_str}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Category mini-bars
        st.markdown("<div class='section-heading'>CATEGORY SCORES</div>", unsafe_allow_html=True)
        st.plotly_chart(category_bar(cat_sc), use_container_width=True,
                        config={"displayModeBar": False})

        # Smart suggestions for HIGH RISK categories
        urgent = {c: s for c, s in cat_sc.items() if s < 50}
        if urgent:
            st.markdown("""
            <div class='alert-danger'>
                <strong>🚨 High-Risk Areas Detected</strong> — Immediate action recommended for the categories below.
            </div>
            """, unsafe_allow_html=True)
            for cat, s in sorted(urgent.items(), key=lambda x: x[1]):
                icon = CAT_ICONS.get(cat, "")
                alts = HIGH_RISK_ALTERNATIVES.get(cat, [])
                with st.expander(f"{icon} {cat} — {s}% (High Risk) · Click for alternatives"):
                    st.markdown(f"""
                    <div class='suggest-card'>
                        <div class='suggest-title'>⚡ Immediate Alternatives & Solutions</div>
                        {"".join(f"<div class='suggest-item'>{a}</div>" for a in alts)}
                    </div>
                    """, unsafe_allow_html=True)

        # Recommendations
        st.markdown("<div class='section-heading' style='margin-top:16px;'>PERSONALISED RECOMMENDATIONS</div>",
                    unsafe_allow_html=True)
        low_cats = {c: s for c, s in cat_sc.items() if s < 75}
        if low_cats:
            for cat, s in sorted(low_cats.items(), key=lambda x: x[1]):
                rl, _, _ = risk_label(s)
                icon = CAT_ICONS.get(cat, "")
                with st.expander(f"{icon} {cat} — {s}% ({rl})"):
                    for rec in RECOMMENDATIONS.get(cat, []):
                        st.markdown(f"- {rec}")
        else:
            st.markdown("""
            <div class='alert-success'>
                🎉 Excellent! All categories are in the low-risk zone. Keep up the great habits!
            </div>
            """, unsafe_allow_html=True)

        notes = st.text_area("Add notes (optional)", placeholder="Additional observations or comments...")

        # Auto-generate PDF
        pdf_bytes = generate_pdf(
            st.session_state.user, score, risk_str, cat_sc,
            notes, datetime.now().strftime("%Y-%m-%d %H:%M")
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💾  Save Assessment", use_container_width=True):
                save_assessment(
                    st.session_state.user["id"],
                    st.session_state.user["username"],
                    score, risk_str,
                    st.session_state.answers, cat_sc, notes
                )
                st.success("Assessment saved successfully!")

        with col2:
            st.download_button(
                "📄  Download PDF Report", data=pdf_bytes,
                file_name=f"WSS_Report_{st.session_state.user['username']}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf", use_container_width=True,
            )

        with col3:
            if st.button("🔄  New Assessment", use_container_width=True):
                st.session_state.assessment_done = False
                st.session_state.answers = {}
                st.rerun()
        return

    # ── QUESTIONS VIEW ──
    st.markdown("""
    <div style='font-family:DM Sans,sans-serif;color:#8899AA;font-size:.88rem;
                margin-bottom:22px;line-height:1.6;'>
        Answer all <b style='color:#38BDF8;font-family:Syne,sans-serif;'>30 questions</b>
        honestly based on your typical daily workstation setup.
        Each answer is weighted by its ergonomic importance.
        <span style='color:#818CF8;'>Likert questions</span> use frequency options;
        <span style='color:#34D399;'>Multiple-choice questions</span> reflect your situation.
    </div>
    """, unsafe_allow_html=True)

    answers  = {}
    curr_cat = None
    for q in QUESTIONS:
        # Category header
        if q[1] != curr_cat:
            curr_cat = q[1]
            icon = CAT_ICONS.get(curr_cat, "")
            color = CAT_COLORS.get(curr_cat, "#38BDF8")
            st.markdown(f"""
            <div style='font-family:Syne,sans-serif;font-size:.7rem;letter-spacing:3.5px;
                        color:{color};text-transform:uppercase;
                        padding:16px 0 6px;margin-top:6px;
                        border-top:1px solid rgba(255,255,255,0.04);'>
                {icon} &nbsp; {curr_cat}
            </div>
            """, unsafe_allow_html=True)

        q_type = q[4]
        st.markdown(f"""
        <div class='q-card'>
            <div class='q-number'>
                Q{q[0]:02d} &nbsp;·&nbsp; WEIGHT {q[3]}
                &nbsp;·&nbsp;
                <span style='color:{"#818CF8" if q_type=="likert" else "#34D399"};'>
                    {"FREQUENCY" if q_type=="likert" else "MULTIPLE CHOICE"}
                </span>
            </div>
            <div class='q-text'>{q[2]}</div>
        </div>
        """, unsafe_allow_html=True)

        if q_type == "likert":
            choice = st.radio(
                label=f"q{q[0]}",
                options=list(LIKERT.keys()),
                horizontal=True,
                label_visibility="collapsed",
                key=f"q_{q[0]}",
            )
            answers[q[0]] = LIKERT[choice]
        else:
            opts = q[5]
            choice_mc = st.radio(
                label=f"q{q[0]}",
                options=opts,
                horizontal=False,
                label_visibility="collapsed",
                key=f"q_{q[0]}",
            )
            idx = opts.index(choice_mc)
            answers[q[0]] = mcq_score(q[0], idx, len(opts))

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    if st.button("🧮  CALCULATE ERGONOMIC SCORE", use_container_width=True):
        score, cat_sc = compute_scores(answers)
        st.session_state.last_score      = score
        st.session_state.last_cat_scores = cat_sc
        st.session_state.last_risk       = risk_label(score)[0]
        st.session_state.answers         = answers
        st.session_state.assessment_done = True
        st.rerun()

# ---------------------------------------------------------------------
# PAGE: HISTORY
# ---------------------------------------------------------------------
def page_history():
    u    = st.session_state.user
    rows = load_user_assessments(u["username"])
    st.markdown("<div class='section-heading'>MY ASSESSMENT HISTORY</div>",
                unsafe_allow_html=True)

    if not rows:
        st.info("No assessments yet. Complete your first assessment to see history here.")
        return

    if len(rows) >= 2:
        st.plotly_chart(history_chart(rows), use_container_width=True,
                        config={"displayModeBar": False})

    records = []
    for r in rows:
        rl, _, _ = risk_label(r[1])
        records.append({
            "Date":       r[5][:16],
            "Score":      f"{r[1]:.1f}%",
            "Risk Level": rl,
            "Notes":      (r[4] or "")[:60] or "—",
        })
    st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)

    st.markdown("<div class='section-heading' style='margin-top:20px;'>DEEP-DIVE REVIEW</div>",
                unsafe_allow_html=True)
    options = {
        f"Assessment {i+1}  ·  {r[5][:16]}  ·  {r[1]:.1f}%": r
        for i, r in enumerate(rows)
    }
    chosen_label = st.selectbox("Select an assessment to review:", list(options.keys()))
    chosen = options[chosen_label]
    cat_sc = json.loads(chosen[3]) if chosen[3] else {}

    if cat_sc:
        col_l, col_r = st.columns(2)
        with col_l:
            st.plotly_chart(radar_chart(cat_sc), use_container_width=True,
                            config={"displayModeBar": False})
        with col_r:
            st.plotly_chart(category_bar(cat_sc), use_container_width=True,
                            config={"displayModeBar": False})

    pdf_bytes = generate_pdf(
        u, chosen[1], chosen[2], cat_sc,
        chosen[4] or "", chosen[5]
    )
    st.download_button(
        "📄  Download PDF for This Assessment", data=pdf_bytes,
        file_name=f"WSS_{u['username']}_{chosen[5][:10]}.pdf",
        mime="application/pdf",
    )

# ---------------------------------------------------------------------
# PAGE: ANALYTICS
# ---------------------------------------------------------------------
def page_analytics():
    u    = st.session_state.user
    rows = load_user_assessments(u["username"])
    st.markdown("<div class='section-heading'>PERSONAL ANALYTICS</div>",
                unsafe_allow_html=True)

    if not rows:
        st.info("No data yet. Complete an assessment first.")
        return

    if len(rows) >= 2:
        st.markdown("<div class='section-heading'>CATEGORY TRENDS OVER TIME</div>",
                    unsafe_allow_html=True)
        cat_over_time = {cat: [] for cat in CATEGORIES}
        dates = []
        for r in reversed(rows):
            cat_sc = json.loads(r[3]) if r[3] else {}
            dates.append(r[5][:10])
            for cat in CATEGORIES:
                cat_over_time[cat].append(cat_sc.get(cat, 0))

        fig = go.Figure()
        for cat in CATEGORIES:
            fig.add_trace(go.Scatter(
                x=dates, y=cat_over_time[cat], name=cat,
                mode="lines+markers",
                line=dict(color=CAT_COLORS.get(cat, "#38BDF8"), width=2, shape="spline"),
                marker=dict(size=5),
            ))
        fig.update_layout(
            **PLOTLY_LAYOUT, height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=10)),
            xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
            yaxis=dict(range=[0, 108], gridcolor="rgba(255,255,255,0.04)", ticksuffix="%"),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    if rows:
        all_cats = json.loads(rows[0][3]) if rows[0][3] else {}
        if all_cats:
            best_cat  = max(all_cats, key=all_cats.get)
            worst_cat = min(all_cats, key=all_cats.get)
            c1, c2 = st.columns(2)
            c1.markdown(f"""
            <div class='kpi-card'>
                <div style='font-size:1.5rem;margin-bottom:6px;'>
                    {CAT_ICONS.get(best_cat,"")}
                </div>
                <div class='kpi-value' style='color:#34D399;font-size:1.7rem;'>
                    {all_cats[best_cat]}%
                </div>
                <div class='kpi-label'>Strongest Area</div>
                <div class='kpi-sub'>{best_cat}</div>
            </div>""", unsafe_allow_html=True)
            c2.markdown(f"""
            <div class='kpi-card'>
                <div style='font-size:1.5rem;margin-bottom:6px;'>
                    {CAT_ICONS.get(worst_cat,"")}
                </div>
                <div class='kpi-value' style='color:#F87171;font-size:1.7rem;'>
                    {all_cats[worst_cat]}%
                </div>
                <div class='kpi-label'>Priority Focus Area</div>
                <div class='kpi-sub'>{worst_cat}</div>
            </div>""", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# PAGE: HEALTH PROFILE (edit)
# ---------------------------------------------------------------------
def page_profile():
    u = st.session_state.user
    st.markdown("<div class='section-heading'>MY HEALTH PROFILE</div>",
                unsafe_allow_html=True)

    profile = get_user_profile(u["username"])
    defaults_p = profile if profile else (0, "", 170.0, 70.0, 0, "", "")

    with st.form("edit_profile"):
        c1, c2 = st.columns(2)
        age    = c1.number_input("Age (years)", min_value=10, max_value=100,
                                  value=int(defaults_p[0]) if defaults_p[0] else 22, step=1)
        gender = c2.selectbox("Gender",
            ["Prefer not to say", "Male", "Female", "Non-binary / Other"],
            index=["Prefer not to say", "Male", "Female", "Non-binary / Other"].index(defaults_p[1])
                  if defaults_p[1] in ["Prefer not to say","Male","Female","Non-binary / Other"] else 0)

        c3, c4 = st.columns(2)
        height = c3.number_input("Height (cm)",  min_value=100.0, max_value=250.0,
                                   value=float(defaults_p[2]) if defaults_p[2] else 170.0, step=0.5)
        weight = c4.number_input("Weight (kg)",  min_value=30.0, max_value=300.0,
                                   value=float(defaults_p[3]) if defaults_p[3] else 70.0, step=0.5)

        bmi_p = round(weight / ((height / 100) ** 2), 1) if height > 0 else 0
        bmi_cat = ("Underweight" if bmi_p < 18.5 else
                   "Normal weight" if bmi_p < 25 else
                   "Overweight" if bmi_p < 30 else "Obese")
        bmi_col = "#34D399" if bmi_p < 25 else "#FBBF24" if bmi_p < 30 else "#F87171"
        st.markdown(f"""
        <div style='background:rgba(56,189,248,0.06);border:1px solid rgba(56,189,248,0.18);
                    border-radius:10px;padding:10px 16px;margin:6px 0 14px;
                    font-family:JetBrains Mono,monospace;font-size:.9rem;color:{bmi_col};'>
            BMI: {bmi_p} — {bmi_cat}
        </div>
        """, unsafe_allow_html=True)

        activity_opts = [
            "Sedentary (little or no exercise)",
            "Light (1-3 days/week)",
            "Moderate (3-5 days/week)",
            "Active (6-7 days/week)",
            "Very Active (athlete / physical job)",
        ]
        current_act = defaults_p[5] if defaults_p[5] in activity_opts else activity_opts[0]
        activity = st.selectbox("Physical Activity Level", activity_opts,
                                 index=activity_opts.index(current_act))

        med_hist = st.text_area("Relevant Medical History (optional)",
                                  value=defaults_p[6] or "",
                                  placeholder="e.g. Back pain, carpal tunnel, hypertension...",
                                  height=80)

        if st.form_submit_button("UPDATE PROFILE", use_container_width=True):
            bmi_val = save_health_profile(u["username"], age, gender, height, weight, activity, med_hist)
            conn = get_conn()
            row = conn.execute(
                "SELECT id,username,full_name,dept,role,age,gender,height_cm,weight_kg,bmi,activity,medical_hist FROM users WHERE username=?",
                (u["username"],)
            ).fetchone()
            conn.close()
            if row:
                st.session_state.user = {
                    "id": row[0], "username": row[1], "full_name": row[2],
                    "dept": row[3], "role": row[4], "age": row[5],
                    "gender": row[6], "height_cm": row[7], "weight_kg": row[8],
                    "bmi": row[9], "activity": row[10], "medical_hist": row[11]
                }
            st.success(f"✅ Profile updated! BMI: {bmi_val}")
            st.rerun()

# ---------------------------------------------------------------------
# PAGE: ADMIN
# ---------------------------------------------------------------------
def page_admin():
    if st.session_state.user["role"] != "admin":
        st.error("Access denied.")
        return

    st.markdown("<div class='section-heading'>ADMIN PANEL</div>", unsafe_allow_html=True)

    all_rows  = load_all_assessments()
    all_users = load_all_users()

    tab_ov, tab_users, tab_ass = st.tabs(["Overview", "Users", "All Assessments"])

    with tab_ov:
        scores = [r[4] for r in all_rows]
        c1, c2, c3, c4 = st.columns(4)
        for col, val, label, color in [
            (c1, len(all_users), "Total Users",       "#38BDF8"),
            (c2, len(all_rows),  "Total Assessments", "#818CF8"),
            (c3, f"{sum(scores)/len(scores):.1f}%" if scores else "--", "Platform Avg", "#34D399"),
            (c4, sum(1 for r in all_rows if r[5] == "High Risk"), "High Risk Users", "#F87171"),
        ]:
            col.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-value' style='color:{color};'>{val}</div>
                <div class='kpi-label'>{label}</div>
            </div>""", unsafe_allow_html=True)

        if all_rows:
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            fig = dept_bar(all_rows)
            if fig:
                st.markdown("<div class='section-heading'>AVG SCORE BY DEPARTMENT</div>",
                            unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            risk_counts = pd.Series([r[5] for r in all_rows]).value_counts()
            colors_pie = []
            for lbl in risk_counts.index:
                if lbl == "Low Risk":     colors_pie.append("#34D399")
                elif lbl == "Moderate Risk": colors_pie.append("#FBBF24")
                else:                     colors_pie.append("#F87171")
            fig_pie = go.Figure(go.Pie(
                labels=risk_counts.index, values=risk_counts.values,
                marker=dict(colors=colors_pie, line=dict(color="#060B14", width=2)),
                textfont=dict(family="DM Sans", color="#FFFFFF"),
                hole=0.4,
            ))
            fig_pie.update_layout(**PLOTLY_LAYOUT, height=300, showlegend=True)
            st.markdown("<div class='section-heading'>RISK DISTRIBUTION</div>",
                        unsafe_allow_html=True)
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    with tab_users:
        df_u = pd.DataFrame(all_users,
            columns=["ID", "Username", "Full Name", "Email", "Dept", "Role", "Created"])
        st.dataframe(df_u, use_container_width=True, hide_index=True)

    with tab_ass:
        if all_rows:
            df_a = pd.DataFrame(all_rows,
                columns=["ID", "Username", "Full Name", "Dept", "Score", "Risk", "Created"])
            df_a["Score"] = df_a["Score"].apply(lambda x: f"{x:.1f}%")
            st.dataframe(df_a, use_container_width=True, hide_index=True)
            csv = df_a.to_csv(index=False).encode()
            st.download_button(
                "📥  Export as CSV", data=csv,
                file_name=f"WSS_AllAssessments_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
        else:
            st.info("No assessments recorded yet.")

# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------
def main():
    if not st.session_state.logged_in:
        login_page()
        return

    # Show health profile modal after registration/first login
    if st.session_state.show_health_profile:
        health_profile_page()
        return

    sidebar()
    page = st.session_state.page

    if   page == "dashboard":  page_dashboard()
    elif page == "assessment": page_assessment()
    elif page == "history":    page_history()
    elif page == "analytics":  page_analytics()
    elif page == "profile":    page_profile()
    elif page == "admin":      page_admin()

if __name__ == "__main__":
    main()
