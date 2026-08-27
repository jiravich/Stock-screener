import streamlit as st
import yfinance as yf
import pandas as pd
from google import genai

# ==========================================
# 1. Page Configuration & Fintech SaaS UI
# ==========================================
st.set_page_config(
    page_title="Lynch & Fisher Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Live Price Header */
    .price-container {
        display: flex;
        align-items: baseline;
        gap: 15px;
        margin-top: -10px;
        margin-bottom: 15px;
    }
    .live-price {
        font-size: 2.2rem;
        font-weight: 800;
        color: #f0f6fc;
    }
    .price-up {
        color: #3fb950;
        font-size: 1.1rem;
        font-weight: 600;
    }
    .price-down {
        color: #f85149;
        font-size: 1.1rem;
        font-weight: 600;
    }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #161b22, #21262d);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 14px 18px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        color: #8b949e;
        font-weight: 500;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.4rem;
        font-weight: 700;
        color: #f0f6fc;
    }

    /* Badges */
    .badge-pass {
        background-color: rgba(46, 160, 67, 0.15);
        color: #3fb950;
        border: 1px solid rgba(46, 160, 67, 0.4);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-fail {
        background-color: rgba(248, 81, 73, 0.15);
        color: #f85149;
        border: 1px solid rgba(248, 81, 73, 0.4);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    div.stButton > button:first-child {
        background: linear-gradient(180deg, #1f6feb, #238636);
        color: #ffffff;
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 24px;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# Helper Functions
def get_financial_item(df, keys):
    if df is None or df.empty:
        return None
    for key in keys:
        if key in df.index:
            return df.loc[key]
    return None

def get_latest_value(series):
    if series is not None and len(series) > 0:
        val = series.iloc[0]
        return float(val) if pd.notna(val) else 0.0
    return 0.0

# ==========================================
# 2. Sidebar Settings & AI Key
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ การตั้งค่าระบบ")
    gemini_key = st.text_input("🔑 Gemini API Key (ฟรี):", type="password", help="รับ API Key ฟรีได้ที่ aistudio.google.com")
    st.markdown("---")
    st.caption("⚡ **Lynch & Fisher Engine v3.0**\nระบบสแกนหุ้นแบบ Real-time ผสานพลัง AI Agent")

# ==========================================
# 3. Main Header & Search
# ==========================================
st.markdown("<h1 style='margin-bottom: 0px;'>⚡ Lynch & Fisher Intelligence Terminal</h1>", unsafe_allow_html=True)
st.caption("ระบบตรวจงบการเงินเรียลไทม์ • ประเมินมูลค่า • ตรวจทุจริตบัญชี • วิเคราะห์ Moat เชิงลึก")

col_search, col_btn = st.columns([4, 1])
with col_search:
    ticker = st.text_input("พิมพ์ชื่อย่อหุ้นสหรัฐฯ:", value="META").upper().strip()
with col_btn:
    st.write(" ")
    st.write(" ")
    search_clicked = st.button("🚀 รันการตรวจสอบ", type="primary", use_container_width=True)

if ticker:
    try:
        with st.spinner(f"กำลังดึงข้อมูลเรียลไทม์และตรวจสอบงบการเงินของ {ticker}..."):
            stock = yf.Ticker(ticker)
            info = stock.info
            bs = stock.balance_sheet
            inc = stock.financials
            cf = stock.cashflow

            if not info or "shortName" not in info:
                st.error(f"ไม่พบข้อมูลหุ้น {ticker} กรุณาตรวจสอบตัวสะกดชื่อย่อหุ้น")
                st.stop()

            # ----------------------------------------------------
            # 3.1 Real-Time Price Engine
            # ----------------------------------------------------
            current_price = info.get("currentPrice") or info.get("regularMarketPrice") or 0.0
            prev_close = info.get("regularMarketPreviousClose") or info.get("previousClose") or current_price
            price_change = current_price - prev_close
            price_change_pct = (price_change / prev_close * 100) if prev_close else 0.0
            
            day_high = info.get("dayHigh", current_price)
            day_low = info.get("dayLow", current_price)
            year_high = info.get("fiftyTwoWeekHigh", current_price)
            year_low = info.get("fiftyTwoWeekLow", current_price)

            sector = info.get("sector", "N/A")
            industry = info.get("industry", "N/A")
            is_financial = sector == "Financial Services"
            market_cap = info.get("marketCap", 0)

            # ----------------------------------------------------
            # 3.2 Fundamental Calculations
            # ----------------------------------------------------
            rev_series = get_financial_item(inc, ["Total Revenue", "Operating Revenue", "TotalRevenue"])
            ni_series = get_financial_item(inc, ["Net Income", "Net Income Common Stockholders", "NetIncome"])
            op_inc_series = get_financial_item(inc, ["Operating Income", "Operating Profit", "Total Operating Income As Reported"])
            rd_series = get_financial_item(inc, ["Research And Development", "Research Development"])
            shares_series = get_financial_item(inc, ["Diluted Average Shares", "Diluted Weighted Average Shares"])

            cash_series = get_financial_item(bs, ["Cash Cash Equivalents And Short Term Investments", "Cash And Cash Equivalents"])
            sec_series = get_financial_item(bs, ["Other Short Term Investments", "Marketable Securities"])
            debt_series = get_financial_item(bs, ["Total Debt", "Long Term Debt And Capital Lease Obligation"])
            ar_series = get_financial_item(bs, ["Accounts Receivable", "Receivables"])
            inv_series = get_financial_item(bs, ["Inventory", "Inventories"])

            ocf_series = get_financial_item(cf, ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"])
            fcf_series = get_financial_item(cf, ["Free Cash Flow"])
            sbc_series = get_financial_item(cf, ["Stock Based Compensation", "Stock-Based Compensation"])

            total_rev = get_latest_value(rev_series)
            net_income = get_latest_value(ni_series)
            op_income = get_latest_value(op_inc_series)
            rd_exp = get_latest_value(rd_series)

            pure_cash = get_latest_value(cash_series)
            short_inv = get_latest_value(sec_series)
            total_cash_calc = pure_cash if (pure_cash > 0 and pure_cash >= (pure_cash + short_inv)) else (pure_cash + short_inv)
            if total_cash_calc == 0:
                total_cash_calc = info.get("totalCash", 0)

            total_debt_calc = get_latest_value(debt_series)
            if total_debt_calc == 0:
                total_debt_calc = info.get("totalDebt", 0)

            net_cash = total_cash_calc - total_debt_calc
            shares_out = info.get("sharesOutstanding", 1)
            net_cash_per_share = net_cash / shares_out if shares_out else 0

            op_margin = (op_income / total_rev * 100) if total_rev > 0 else (info.get("operatingMargins", 0) * 100)
            gross_margin = info.get("grossMargins", 0) * 100
            net_margin = (net_income / total_rev * 100) if total_rev > 0 else (info.get("profitMargins", 0) * 100)
            roe = info.get("returnOnEquity", 0) * 100
            roa = info.get("returnOnAssets", 0) * 100

            peg = info.get("pegRatio", None)
            pe_trailing = info.get("trailingPE", None)
            pe_forward = info.get("forwardPE", None)
            pb_ratio = info.get("priceToBook", None)
            de_ratio = info.get("debtToEquity", 0)
            dividend_yield = info.get("dividendYield", 0) * 100 if info.get("dividendYield") else 0
            rd_ratio = (rd_exp / total_rev * 100) if total_rev > 0 else 0

            # Red Flags
            ocf = get_latest_value(ocf_series) or info.get("operatingCashflow", 0)
            fcf = get_latest_value(fcf_series) or info.get("freeCashflow", 0)
            cash_flow_divergence = (ocf < (net_income * 0.85)) and not is_financial

            rev_growth = info.get("revenueGrowth", 0) * 100
            if rev_growth == 0 and rev_series is not None and len(rev_series) > 1:
                r0, r1 = rev_series.iloc[0], rev_series.iloc[1]
                rev_growth = ((r0 - r1) / abs(r1) * 100) if r1 != 0 else 0

            ar_growth = 0
            ar_warning = False
            if ar_series is not None and len(ar_series) > 1:
                a0, a1 = ar_series.iloc[0], ar_series.iloc[1]
                if pd.notna(a0) and pd.notna(a1) and a1 != 0:
                    ar_growth = ((a0 - a1) / abs(a1) * 100)
                    ar_warning = ar_growth > (rev_growth * 1.5) and ar_growth > 10

            inv_growth = 0
            inv_warning = False
            has_inventory = inv_series is not None and len(inv_series) > 0 and pd.notna(inv_series.iloc[0])
            if has_inventory and len(inv_series) > 1:
                i0, i1 = inv_series.iloc[0], inv_series.iloc[1]
                if pd.notna(i0) and pd.notna(i1) and i1 != 0:
                    inv_growth = ((i0 - i1) / abs(i1) * 100)
                    inv_warning = inv_growth > (rev_growth * 1.5) and inv_growth > 10

            sbc = get_latest_value(sbc_series)
            sbc_ratio = (sbc / ocf * 100) if ocf > 0 else 0
            sbc_warning = sbc_ratio > 20 and not is_financial

            sh_growth = 0
            dilution_warning = False
            if shares_series is not None and len(shares_series) > 1:
                s0, s1 = shares_series.iloc[0], shares_series.iloc[1]
                if pd.notna(s0) and pd.notna(s1) and s1 != 0:
                    sh_growth = ((s0 - s1) / abs(s1) * 100)
                    dilution_warning = sh_growth > 2.0

            # ----------------------------------------------------
            # 3.3 Lynch 6-Category Classifier
            # ----------------------------------------------------
            if rev_growth >= 18 and (peg and peg < 1.8):
                lynch_category = "🚀 Fast Grower (หุ้นเติบโตเร็วระเบิด)"
                cat_desc = "ธุรกิจเติบโตสูงสองหลัก เน้นดูว่า PEG ต่ำกว่า 1.0 และหนี้ต้องไม่สูง"
            elif rev_growth >= 6 and rev_growth < 18:
                lynch_category = "🛡️ Stalwart (หุ้นยักษ์ใหญ่แข็งแกร่ง)"
                cat_desc = "โตปานกลาง 6-18% มั่นคงสูง ซื้อเมื่อ P/E ต่ำกว่าอดีต ปลอดภัยยามวิกฤต"
            elif dividend_yield > 4.0 and rev_growth < 6:
                lynch_category = "🐢 Slow Grower (หุ้นโตช้าเน้นปันผล)"
                cat_desc = "เติบโตใกล้เคียง GDP มักจ่ายปันผลสูง ไม่เหมาะกับพอร์ตเน้นกำไรก้าวกระโดด"
            elif sector in ["Basic Materials", "Energy", "Industrials", "Financial Services"]:
                lynch_category = "🔄 Cyclical (หุ้นวัฏจักร)"
                cat_desc = "ผลประกอบการขึ้นลงตามรอบเศรษฐกิจ ต้องจับจังหวะซื้อตอนกำไรต่ำสุด"
            elif net_cash > (market_cap * 0.25):
                lynch_category = "💎 Asset Play (หุ้นสินทรัพย์ซ่อนเร้น)"
                cat_desc = "มีเงินสดหรือสินทรัพย์มากกว่า 25% ของมูลค่าตลาด มีความคุ้มค่าสูง"
            else:
                lynch_category = "⚙️ General Growth / Stalwart"
                cat_desc = "หุ้นพื้นฐานแข็งแกร่ง กำไรเติบโตสม่ำเสมอ"

            # ==========================================
            # 4. Live Price & Summary UI
            # ==========================================
            st.markdown(f"## {info.get('shortName', ticker)} `[{ticker}]`")
            
            # Live Price Badge
            change_class = "price-up" if price_change >= 0 else "price-down"
            change_sign = "+" if price_change >= 0 else ""
            st.markdown(f"""
            <div class="price-container">
                <span class="live-price">${current_price:,.2f}</span>
                <span class="{change_class}">{change_sign}{price_change:.2f} ({change_sign}{price_change_pct:.2f}%)</span>
                <span style="color: #8b949e; font-size: 0.9rem;">• กรอบ 52 สัปดาห์: ${year_low:,.2f} - ${year_high:,.2f}</span>
            </div>
            """, unsafe_allow_html=True)

            st.caption(f"**หมวดหมู่:** `{sector}` | `{industry}` | **Market Cap:** `${market_cap:,.0f}`")

            # Category Banner
            with st.container(border=True):
                c_cat1, c_cat2 = st.columns([1.5, 3])
                with c_cat1:
                    st.markdown(f"**การจัดหมวดหมู่สไตล์ Lynch:**\n### {lynch_category}")
                with c_cat2:
                    st.write(f"💡 **กลยุทธ์:** {cat_desc}")

            # Top KPI Summary Cards
            col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
            with col_kpi1:
                if is_financial:
                    st.metric("P/B Ratio", f"{pb_ratio:.2f}" if pb_ratio else "N/A", 
                              delta="ถูก (<1.0)" if (pb_ratio and pb_ratio < 1.0) else "ปกติ/แพง",
                              delta_color="normal" if (pb_ratio and pb_ratio < 1.0) else "off")
                else:
                    st.metric("PEG Ratio (< 1.0)", f"{peg:.2f}" if peg else "N/A", 
                              delta="ผ่าน (Undervalued)" if (peg and peg < 1.0) else "แพง/ไม่ผ่าน",
                              delta_color="normal" if (peg and peg < 1.0) else "inverse")

            with col_kpi2:
                if is_financial:
                    st.metric("ROE (ผู้บริหารเก่ง)", f"{roe:.1f}%", 
                              delta="ดีเยี่ยม (>12%)" if roe >= 12 else "ต่ำ", 
                              delta_color="normal" if roe >= 12 else "inverse")
                else:
                    st.metric("Net Cash per Share", f"${net_cash_per_share:.2f}", 
                              delta="เงินสดหนุนหลัง" if net_cash > 0 else "หนี้สินสุทธิ",
                              delta_color="normal" if net_cash > 0 else "inverse")

            with col_kpi3:
                st.metric("Operating Margin", f"{op_margin:.1f}%", 
                          delta="แข็งแกร่ง (>15%)" if op_margin >= 15 else "ต่ำ",
                          delta_color="normal" if op_margin >= 15 else "inverse")

            with col_kpi4:
                st.metric("Revenue Growth", f"{rev_growth:.1f}%", 
                          delta="เติบโตสูง" if rev_growth >= 15 else "ปกติ/ชะลอ",
                          delta_color="normal" if rev_growth >= 15 else "off")

            st.write(" ")

            # ==========================================
            # 5. Interactive Tabs Engine
            # ==========================================
            tab_ai, tab_verdict, tab_redflag, tab_fisher, tab_lynch, tab_charts, tab_insider = st.tabs([
                "🤖 AI Moat Analysis (คลิกเดียว)",
                "🏆 สรุปการตัดเกรด",
                "🚨 ตรวจจับ Red Flags",
                "🔬 คุณภาพธุรกิจ (Fisher)",
                "💰 มูลค่างบดุล (Lynch)",
                "📈 กราฟ 4 ปีย้อนหลัง & Valuation",
                "👥 การซื้อขายของคนใน (Insiders)"
            ])

            # ----------------------------------------------------
            # Tab: In-App AI Agent (Gemini)
            # ----------------------------------------------------
            with tab_ai:
                st.markdown("### 🤖 วิเคราะห์คูเมืองและการแข่งขันด้วย Gemini Agent")
                if not gemini_key:
                    st.info("💡 กรุณาใส่ **Gemini API Key** ในแถบเมนูด้านซ้าย (Sidebar) เพื่อเปิดใช้งานฟีเจอร์วิเคราะห์อัตโนมัติ")
                else:
                    if st.button("🧠 สั่ง AI เริ่มวิเคราะห์เดี๋ยวนี้", type="secondary"):
                        with st.spinner("AI กำลังวิเคราะห์โมเดลธุรกิจ, Moat และจุดเสี่ยง 15 ข้อของ Fisher..."):
                            try:
                                client = genai.Client(api_key=gemini_key)
                                prompt = f"""
                                คุณคือนักวิเคราะห์หุ้นอาวุโสสาย Philip Fisher และ Peter Lynch จงวิเคราะห์หุ้น {info.get('shortName', ticker)} ({ticker}) จากข้อมูลการเงินต่อไปนี้:
                                - ราคาปัจจุบัน: ${current_price:.2f}
                                - กลุ่ม: {sector} / {industry}
                                - Revenue Growth: {rev_growth:.1f}% | Operating Margin: {op_margin:.1f}% | R&D/Rev: {rd_ratio:.1f}%
                                - Net Cash: ${net_cash:,.0f} | PEG: {peg if peg else 'N/A'}
                                - รายละเอียดธุรกิจ: {info.get('longBusinessSummary', '')}

                                ตอบเป็นภาษาไทยอย่างกระชับและตรงไปตรงมาใน 4 หัวข้อ:
                                1. **Economic Moat (คูเมืองทางธุรกิจ):** บริษัทมีอะไรที่คู่แข่งเจาะไม่เข้าใน 5 ปีข้างหน้า?
                                2. **Sales Organization & Market Potential:** ตลาดมีโอกาสขยายตัวได้อีกนานแค่ไหน และทีมขายเก่งไหม?
                                3. **Management Quality & Integrity:** มีความน่าเชื่อถือแค่ไหนจากตัวเลขงบและการจัดสรรเงินทุน?
                                4. **3 จุดเสี่ยงตายที่ต้องจับตา:** สิ่งที่อาจทำให้ธุรกิจพังทลาย
                                """
                                response = client.models.generate_content(
                                    model='gemini-2.5-flash',
                                    contents=prompt
                                )
                                st.markdown("---")
                                st.markdown(response.text)
                            except Exception as ai_err:
                                st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ AI: {ai_err}")

            # ----------------------------------------------------
            # Tab: Verdict
            # ----------------------------------------------------
            with tab_verdict:
                st.markdown("### 📋 สรุปผลการประเมิน 6 ด่านตรวจหลัก")
                p1 = (peg is not None and peg < 1.0) if not is_financial else (pb_ratio is not None and pb_ratio <= 1.2)
                p2 = (net_cash > 0 or de_ratio < 60) if not is_financial else (roe >= 12)
                p3 = op_margin >= 15
                p4 = not cash_flow_divergence
                p5 = not ar_warning
                p6 = not dilution_warning

                checks = [
                    ("1. ด้านราคาและความคุ้มค่า (Valuation)", p1, f"PEG = {peg if peg else 'N/A'}" if not is_financial else f"P/B = {pb_ratio if pb_ratio else 'N/A'}"),
                    ("2. ฐานะการเงินและสภาพคล่อง (Balance Sheet)", p2, f"Net Cash = ${net_cash:,.0f}" if not is_financial else f"ROE = {roe:.1f}%"),
                    ("3. อัตรากำไรจากการดำเนินงาน (Operating Margin)", p3, f"{op_margin:.1f}% (เกณฑ์ขั้นต่ำ > 15%)"),
                    ("4. คุณภาพกระแสเงินสด (Cash Flow Integrity)", p4, f"OCF (${ocf:,.0f}) vs Net Income (${net_income:,.0f})"),
                    ("5. การควบคุมลูกหนี้การค้า (Receivables)", p5, f"AR Growth ({ar_growth:.1f}%) vs Rev Growth ({rev_growth:.1f}%)"),
                    ("6. จริยธรรมการไม่เจือจางหุ้น (Anti-Dilution)", p6, f"การเปลี่ยนแปลงจำนวนหุ้น = {sh_growth:+.2f}% ต่อปี")
                ]

                c_pass = 0
                for title, passed, detail in checks:
                    with st.container(border=True):
                        c1, c2 = st.columns([4, 1])
                        c1.write(f"**{title}**")
                        c1.caption(f"รายละเอียด: {detail}")
                        if passed:
                            c2.markdown("<span class='badge-pass'>✅ ผ่านเกณฑ์</span>", unsafe_allow_html=True)
                            c_pass += 1
                        else:
                            c2.markdown("<span class='badge-fail'>❌ ไม่ผ่าน</span>", unsafe_allow_html=True)

                st.markdown("---")
                if c_pass == 6:
                    st.success("🟢 **GRADE A (OUTSTANDING):** ผ่านเกณฑ์งบการเงินทั้งหมดของ Lynch & Fisher และปลอดภัยจาก Red Flags")
                elif c_pass >= 4:
                    st.warning(f"🟡 **GRADE B (WATCHLIST):** ผ่าน {c_pass}/6 เกณฑ์ ธุรกิจแข็งแกร่งแต่ราคาอาจจะยังไม่ถูกที่สุด")
                else:
                    st.error(f"🔴 **GRADE C (HIGH RISK):** ผ่านเพียง {c_pass}/6 เกณฑ์ ควรศึกษาเพิ่มเติมอย่างระมัดระวัง")

            # ----------------------------------------------------
            # Tab: Red Flags
            # ----------------------------------------------------
            with tab_redflag:
                st.markdown("### 🚨 ระบบตรวจสอบความโปร่งใสทางบัญชี")
                rf1, rf2 = st.columns(2)
                with rf1:
                    with st.container(border=True):
                        st.write("#### 1. คุณภาพเงินสดแท้จริง (Cash Flow Divergence)")
                        st.write(f"- **Operating Cash Flow:** `${ocf:,.0f}`")
                        st.write(f"- **Net Income:** `${net_income:,.0f}`")
                        if cash_flow_divergence:
                            st.error("❌ กระแสเงินสดต่ำกว่ากำไรสุทธิเกิน 15% (ระวังกำไรตัวเลขทางบัญชี)")
                        else:
                            st.success("✅ เงินสดเข้ากระเป๋าจริงสอดคล้องกับกำไรที่รายงาน")

                    with st.container(border=True):
                        st.write("#### 2. ค่าตอบแทนหุ้นพนักงาน (Stock-Based Comp)")
                        st.write(f"- **SBC ต่อเงินสดดำเนินงาน:** `{sbc_ratio:.1f}%`")
                        if sbc_warning:
                            st.error("❌ บริษัทพิมพ์หุ้นแจกพนักงานสูงเกิน 20% ของเงินสดดำเนินงาน")
                        else:
                            st.success("✅ สัดส่วน SBC อยู่ในระดับปลอดภัย")

                with rf2:
                    with st.container(border=True):
                        st.write("#### 3. สัญญาณลูกหนี้บวม (Accounts Receivable)")
                        st.write(f"- **ลูกหนี้การค้าโต (YoY):** `{ar_growth:.1f}%`")
                        st.write(f"- **ยอดขายโต (YoY):** `{rev_growth:.1f}%`")
                        if ar_warning:
                            st.error("❌ ลูกหนี้โตเร็วกว่ายอดขายเกิน 1.5 เท่า")
                        else:
                            st.success("✅ ลูกหนี้การค้าโตสัมพันธ์กับยอดขายจริง")

                    with st.container(border=True):
                        st.write("#### 4. สินค้าตกรุ่นค้างสต็อก (Inventory Growth)")
                        if has_inventory:
                            st.write(f"- **สินค้าคงคลังโต (YoY):** `{inv_growth:.1f}%`")
                            if inv_warning:
                                st.error("❌ สินค้าคงคลังโตเร็วกว่ายอดขายเกิน 1.5 เท่า")
                            else:
                                st.success("✅ จัดการสินค้าคงคลังได้ดี")
                        else:
                            st.info("ℹ️ บริษัทประเภทบริการ/ซอฟต์แวร์/การเงิน ไม่มีสินค้าคงคลัง")

            # ----------------------------------------------------
            # Tab: Fisher Deep Dive
            # ----------------------------------------------------
            with tab_fisher:
                st.markdown("### 🔬 ดัชนีคุณภาพและความยั่งยืน (Philip Fisher)")
                f1, f2 = st.columns(2)
                with f1:
                    with st.container(border=True):
                        st.write("#### 📊 อัตรากำไรและอำนาจการตั้งราคา (Pricing Power)")
                        st.write(f"- **Gross Profit Margin:** `{gross_margin:.1f}%`")
                        st.write(f"- **Operating Margin:** `{op_margin:.1f}%`")
                        st.write(f"- **Net Profit Margin:** `{net_margin:.1f}%`")
                        st.write(f"- **ROA:** `{roa:.1f}%`")

                with f2:
                    with st.container(border=True):
                        st.write("#### 🔬 การวิจัยพัฒนา & จริยธรรมผู้บริหาร")
                        st.write(f"- **งบ R&D ประจำปี:** `${rd_exp:,.0f}`")
                        st.write(f"- **R&D ต่อยอดขาย:** `{rd_ratio:.1f}%`")
                        st.write(f"- **การเปลี่ยนแปลงจำนวนหุ้น:** `{sh_growth:+.2f}% ต่อปี`")
                        if dilution_warning:
                            st.error("❌ มีการออกหุ้นเพิ่มทุนเจือจางมูลค่า")
                        else:
                            st.success("✅ ไม่พบการเจือจางหุ้น หรือมีการซื้อหุ้นคืน (Buybacks)")

            # ----------------------------------------------------
            # Tab: Lynch Deep Dive
            # ----------------------------------------------------
            with tab_lynch:
                st.markdown("### 💰 ความคุ้มค่าด้านราคาและสุขภาพงบดุล (Peter Lynch)")
                l1, l2 = st.columns(2)
                with l1:
                    with st.container(border=True):
                        st.write("#### 🏷️ การประเมินมูลค่า (Valuation Multiples)")
                        st.write(f"- **Trailing P/E:** `{pe_trailing if pe_trailing else 'N/A'}`")
                        st.write(f"- **Forward P/E:** `{pe_forward if pe_forward else 'N/A'}`")
                        st.write(f"- **PEG Ratio:** `{peg if peg else 'N/A'}`")
                        st.write(f"- **Price to Book (P/B):** `{pb_ratio if pb_ratio else 'N/A'}`")
                        st.write(f"- **Dividend Yield:** `{dividend_yield:.2f}%`")

                with l2:
                    with st.container(border=True):
                        st.write("#### 🛡️ ป้อมปราการเงินสด (Cash & Balance Sheet)")
                        st.write(f"- **เงินสด & เงินลงทุนระยะสั้น:** `${total_cash_calc:,.0f}`")
                        st.write(f"- **หนี้สินรวม (Total Debt):** `${total_debt_calc:,.0f}`")
                        st.write(f"- **เงินสดสุทธิ (Net Cash):** `${net_cash:,.0f}`")
                        st.write(f"- **Debt to Equity Ratio:** `{de_ratio:.1f}%`")
                        st.write(f"- **Free Cash Flow:** `${fcf:,.0f}`")

            # ----------------------------------------------------
            # Tab: Historical Charts & Valuation Line
            # ----------------------------------------------------
            with tab_charts:
                st.markdown("### 📈 แนวโน้มผลประกอบการย้อนหลัง 4 ปี (หน่วย: พันล้านดอลลาร์ $B)")
                try:
                    if rev_series is not None and ni_series is not None and len(rev_series) > 0:
                        years = [pd.to_datetime(d).strftime('%Y') for d in rev_series.index]
                        rev_vals = [float(v) / 1e9 if pd.notna(v) else 0.0 for v in rev_series.values]
                        ni_vals = [float(v) / 1e9 if pd.notna(v) else 0.0 for v in ni_series.values]
                        
                        ocf_vals = []
                        if ocf_series is not None and len(ocf_series) > 0:
                            ocf_vals = [float(v) / 1e9 if pd.notna(v) else 0.0 for v in ocf_series.values]
                        else:
                            ocf_vals = [0.0] * len(years)

                        df_plot = pd.DataFrame({
                            "Year": years,
                            "รายได้รวม (Revenue)": rev_vals,
                            "กำไรสุทธิ (Net Income)": ni_vals,
                            "เงินสดดำเนินงาน (OCF)": ocf_vals
                        }).set_index("Year").sort_index(ascending=True)

                        st.bar_chart(df_plot)
                        st.caption("เปรียบเทียบ Revenue vs Net Income vs Operating Cash Flow ย้อนหลัง")
                    else:
                        st.info("ไม่มีข้อมูลงบย้อนหลังเพียงพอสำหรับสร้างกราฟ")
                except Exception as chart_err:
                    st.error(f"เกิดข้อผิดพลาดในการวาดกราฟ: {chart_err}")

            # ----------------------------------------------------
            # Tab: Insider Transactions
            # ----------------------------------------------------
            with tab_insider:
                st.markdown("### 👥 การทำรายการของผู้บริหารและคนในบริษัท (Insider Trading)")
                try:
                    insider_df = stock.insider_transactions
                    if insider_df is not None and not insider_df.empty:
                        clean_insider = insider_df[["Shares", "Value", "Text", "Start Date"]].head(15)
                        st.dataframe(clean_insider, use_container_width=True)
                        st.caption("💡 ลินซ์ให้ความสนใจเป็นพิเศษหากพบรายการ 'Purchase' (ซื้อ) จากผู้บริหารระดับสูง")
                    else:
                        st.info("ไม่มีข้อมูลรายการซื้อขายของผู้บริหารในช่วงล่าสุด")
                except Exception as ins_err:
                    st.info("ไม่สามารถดึงข้อมูล Insider Transactions ได้ในขณะนี้")

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูลของ {ticker}: {e}")
