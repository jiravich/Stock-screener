import streamlit as st
import yfinance as yf
import pandas as pd

# ==========================================
# 1. Page Configuration & Custom CSS (UI)
# ==========================================
st.set_page_config(
    page_title="Lynch & Fisher Alpha Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark Modern Fintech Theme
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Metric Cards Styling */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #161b22, #21262d);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #58a6ff;
        transform: translateY(-2px);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        color: #8b949e;
        font-weight: 500;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem;
        font-weight: 700;
        color: #f0f6fc;
    }

    /* Custom Badges */
    .badge-pass {
        background-color: rgba(46, 160, 67, 0.15);
        color: #3fb950;
        border: 1px solid rgba(46, 160, 67, 0.4);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-fail {
        background-color: rgba(248, 81, 73, 0.15);
        color: #f85149;
        border: 1px solid rgba(248, 81, 73, 0.4);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-warn {
        background-color: rgba(210, 153, 34, 0.15);
        color: #d29922;
        border: 1px solid rgba(210, 153, 34, 0.4);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }

    /* Primary Action Button */
    div.stButton > button:first-child {
        background: linear-gradient(180deg, #1f6feb, #238636);
        color: #ffffff;
        border: 1px solid rgba(240, 246, 252, 0.1);
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 24px;
        box-shadow: 0 4px 12px rgba(35, 134, 54, 0.3);
        transition: all 0.2s ease;
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(180deg, #388bfd, #2ea043);
        box-shadow: 0 6px 16px rgba(46, 160, 67, 0.5);
        transform: translateY(-1px);
    }

    /* Tab Header */
    button[data-baseweb="tab"] {
        font-size: 15px;
        font-weight: 600;
        color: #8b949e;
        padding: 10px 18px;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #58a6ff !important;
        border-bottom-color: #58a6ff !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Header & Input UI
# ==========================================
st.markdown("<h1 style='margin-bottom: 0px;'>⚡ Lynch & Fisher Financial Engine</h1>", unsafe_allow_html=True)
st.caption("ระบบตรวจสอบงบการเงินอัตโนมัติ • กรองหุ้นคุณค่า • จับทุจริตบัญชี • วิเคราะห์โมเดลธุรกิจ")

col_search, col_btn = st.columns([4, 1])
with col_search:
    ticker = st.text_input("พิมพ์ชื่อย่อหุ้นสหรัฐฯ (เช่น META, AAPL, GOOGL, JPM, NVDA, KO):", value="META").upper().strip()
with col_btn:
    st.write(" ")
    st.write(" ")
    search_clicked = st.button("🚀 สแกนงบละเอียด", type="primary", use_container_width=True)

if ticker:
    try:
        with st.spinner(f"กำลังดึงงบการเงินและรันระบบตรวจสอบของ {ticker}..."):
            stock = yf.Ticker(ticker)
            info = stock.info
            bs = stock.balance_sheet
            inc = stock.financials
            cf = stock.cashflow

            if not info or "shortName" not in info:
                st.error(f"ไม่พบข้อมูลหุ้น {ticker} กรุณาตรวจสอบตัวสะกดชื่อย่อหุ้น")
                st.stop()

            # ตรวจสอบประเภทอุตสาหกรรม
            sector = info.get("sector", "N/A")
            industry = info.get("industry", "N/A")
            is_financial = sector == "Financial Services"

            # ==========================================
            # 3. Calculation Engine
            # ==========================================
            # 3.1 Valuation Metrics
            peg = info.get("pegRatio", None)
            pe_trailing = info.get("trailingPE", None)
            pe_forward = info.get("forwardPE", None)
            pb_ratio = info.get("priceToBook", None)
            dividend_yield = info.get("dividendYield", 0) * 100 if info.get("dividendYield") else 0
            market_cap = info.get("marketCap", 0)

            # 3.2 Balance Sheet & Cash Metrics
            cash = info.get("totalCash", 0)
            debt = info.get("totalDebt", 0)
            net_cash = cash - debt
            shares_out = info.get("sharesOutstanding", 1)
            net_cash_per_share = net_cash / shares_out if shares_out else 0
            de_ratio = info.get("debtToEquity", 0)

            # 3.3 Profitability & Quality (Fisher)
            op_margin = info.get("operatingMargins", 0) * 100
            gross_margin = info.get("grossMargins", 0) * 100
            net_margin = info.get("profitMargins", 0) * 100
            roe = info.get("returnOnEquity", 0) * 100
            roa = info.get("returnOnAssets", 0) * 100

            # 3.4 Growth & R&D
            rev_growth = info.get("revenueGrowth", 0) * 100
            total_rev = inc.loc["TotalRevenue"].iloc[0] if "TotalRevenue" in inc.index else 0
            rd_exp = inc.loc["ResearchAndDevelopment"].iloc[0] if "ResearchAndDevelopment" in inc.index else 0
            rd_ratio = (rd_exp / total_rev * 100) if total_rev > 0 else 0

            # 3.5 Forensic / Red Flags
            ocf = cf.loc["OperatingCashFlow"].iloc[0] if "OperatingCashFlow" in cf.index else 0
            net_income = inc.loc["NetIncome"].iloc[0] if "NetIncome" in inc.index else 0
            fcf = cf.loc["FreeCashFlow"].iloc[0] if "FreeCashFlow" in cf.index else (ocf - abs(cf.loc["CapitalExpenditure"].iloc[0] if "CapitalExpenditure" in cf.index else 0))
            
            cash_flow_divergence = (ocf < (net_income * 0.85)) and not is_financial

            # Accounts Receivable YoY Growth
            ar_growth = 0
            ar_warning = False
            if "AccountsReceivable" in bs.index and len(bs.loc["AccountsReceivable"]) > 1:
                ar_curr = bs.loc["AccountsReceivable"].iloc[0]
                ar_prev = bs.loc["AccountsReceivable"].iloc[1]
                ar_growth = ((ar_curr - ar_prev) / abs(ar_prev) * 100) if ar_prev != 0 else 0
                ar_warning = ar_growth > (rev_growth * 1.5) and ar_growth > 10

            # Inventory YoY Growth
            inv_growth = 0
            inv_warning = False
            has_inventory = "Inventory" in bs.index and pd.notna(bs.loc["Inventory"].iloc[0])
            if has_inventory and len(bs.loc["Inventory"]) > 1:
                inv_curr = bs.loc["Inventory"].iloc[0]
                inv_prev = bs.loc["Inventory"].iloc[1]
                if pd.notna(inv_curr) and pd.notna(inv_prev) and inv_prev != 0:
                    inv_growth = ((inv_curr - inv_prev) / abs(inv_prev) * 100)
                    inv_warning = inv_growth > (rev_growth * 1.5) and inv_growth > 10

            # Stock-Based Compensation
            sbc = cf.loc["StockBasedCompensation"].iloc[0] if "StockBasedCompensation" in cf.index else 0
            sbc_ratio = (sbc / ocf * 100) if ocf > 0 else 0
            sbc_warning = sbc_ratio > 20 and not is_financial

            # Dilution (Shares Growth)
            dilution_warning = False
            sh_growth = 0
            if "DilutedAverageShares" in inc.index and len(inc.loc["DilutedAverageShares"]) > 1:
                sh_curr = inc.loc["DilutedAverageShares"].iloc[0]
                sh_prev = inc.loc["DilutedAverageShares"].iloc[1]
                sh_growth = ((sh_curr - sh_prev) / sh_prev * 100)
                dilution_warning = sh_growth > 2.0

            # 3.6 Peter Lynch 6-Category Classification
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
                lynch_category = "⚙️ General Growth / Special Situation"
                cat_desc = "หุ้นที่กำลังปรับโครงสร้าง หรือเติบโตเฉพาะตัวตามกลยุทธ์ของบริษัท"

            # ==========================================
            # 4. Main Dashboard UI
            # ==========================================
            st.markdown(f"## 🏢 {info.get('shortName', ticker)} `[{ticker}]`")
            st.markdown(f"**หมวดหมู่:** `{sector}` | `{industry}` | **Market Cap:** `${market_cap:,.0f}`")

            # Category Banner
            with st.container(border=True):
                c_cat1, c_cat2 = st.columns([1.5, 3])
                with c_cat1:
                    st.markdown(f"**การจัดหมวดหมู่สไตล์ Lynch:**\n### {lynch_category}")
                with c_cat2:
                    st.write(f"💡 **คำอธิบายกลยุทธ์:** {cat_desc}")

            # Top KPI Summary Cards
            col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
            with col_kpi1:
                if is_financial:
                    st.metric("P/B Ratio (Financials)", f"{pb_ratio:.2f}" if pb_ratio else "N/A", 
                              delta="ถูก (<1.0)" if (pb_ratio and pb_ratio < 1.0) else "ปกติ/แพง",
                              delta_color="normal" if (pb_ratio and pb_ratio < 1.0) else "off")
                else:
                    st.metric("PEG Ratio (Lynch < 1.0)", f"{peg:.2f}" if peg else "N/A", 
                              delta="ผ่าน (Undervalued)" if (peg and peg < 1.0) else "แพง/ไม่ผ่าน",
                              delta_color="normal" if (peg and peg < 1.0) else "inverse")

            with col_kpi2:
                if is_financial:
                    st.metric("ROE (ความเก่งผู้บริหาร)", f"{roe:.1f}%", 
                              delta="ดีเยี่ยม (>12%)" if roe >= 12 else "ต่ำ", 
                              delta_color="normal" if roe >= 12 else "inverse")
                else:
                    st.metric("Net Cash per Share", f"${net_cash_per_share:.2f}", 
                              delta="เงินสดหนุนหลัง" if net_cash > 0 else "หนี้สินสุทธิ",
                              delta_color="normal" if net_cash > 0 else "inverse")

            with col_kpi3:
                st.metric("Operating Margin (Fisher)", f"{op_margin:.1f}%", 
                          delta="แข็งแกร่ง (>15%)" if op_margin >= 15 else "ต่ำ",
                          delta_color="normal" if op_margin >= 15 else "inverse")

            with col_kpi4:
                st.metric("Revenue Growth (YoY)", f"{rev_growth:.1f}%", 
                          delta="เติบโตสูง" if rev_growth >= 15 else "ปกติ/ชะลอ",
                          delta_color="normal" if rev_growth >= 15 else "off")

            st.write(" ")

            # ==========================================
            # 5. Deep-Dive Analytical Tabs
            # ==========================================
            tab_verdict, tab_redflag, tab_fisher, tab_lynch, tab_charts, tab_ai = st.tabs([
                "🏆 สรุปการตัดเกรด (Scorecard)",
                "🚨 ตรวจจับกลโกง & Red Flags",
                "🔬 ความได้เปรียบเชิงโครงสร้าง (Fisher)",
                "💰 มูลค่า & ความคุ้มค่า (Lynch)",
                "📈 กราฟแนวโน้ม 4 ปีย้อนหลัง",
                "🤖 Prompt สำหรับส่งให้ AI"
            ])

            # ----------------------------------------------------
            # Tab 1: Verdict
            # ----------------------------------------------------
            with tab_verdict:
                st.markdown("### 📋 สรุปผลการประเมิน 10 ด่านตรวจ")
                
                # Check Logic
                c_pass = 0
                total_c = 6

                # Evaluation points
                p1 = (peg is not None and peg < 1.0) if not is_financial else (pb_ratio is not None and pb_ratio <= 1.2)
                p2 = (net_cash > 0 or de_ratio < 50) if not is_financial else (roe >= 12)
                p3 = op_margin >= 15
                p4 = not cash_flow_divergence
                p5 = not ar_warning
                p6 = not dilution_warning

                checks = [
                    ("1. ด้านราคาและความคุ้มค่า (Valuation Criteria)", p1, f"PEG = {peg if peg else 'N/A'}" if not is_financial else f"P/B = {pb_ratio if pb_ratio else 'N/A'}"),
                    ("2. ด้านความปลอดภัยของฐานะการเงิน (Balance Sheet Safety)", p2, f"Net Cash = ${net_cash:,.0f}" if not is_financial else f"ROE = {roe:.1f}%"),
                    ("3. ความสามารถในการทำกำไร (Operating Profitability)", p3, f"Operating Margin = {op_margin:.1f}% (เกณฑ์ > 15%)"),
                    ("4. คุณภาพกระแสเงินสด (Cash Flow Integrity)", p4, f"OCF (${ocf:,.0f}) vs Net Income (${net_income:,.0f})"),
                    ("5. การควบคุมลูกหนี้การค้า (Receivables Control)", p5, f"AR Growth ({ar_growth:.1f}%) เทียบกับ Rev Growth ({rev_growth:.1f}%)"),
                    ("6. การไม่เจือจางผลประโยชน์ผู้ถือหุ้น (Anti-Dilution)", p6, f"การเติบโตของจำนวนหุ้น = {sh_growth:.1f}% ต่อปี")
                ]

                for title, passed, detail in checks:
                    with st.container(border=True):
                        c_col1, c_col2 = st.columns([4, 1])
                        with c_col1:
                            st.write(f"**{title}**")
                            st.caption(f"รายละเอียด: {detail}")
                        with c_col2:
                            if passed:
                                st.markdown("<span class='badge-pass'>✅ ผ่านเกณฑ์</span>", unsafe_allow_html=True)
                                c_pass += 1
                            else:
                                st.markdown("<span class='badge-fail'>❌ ไม่ผ่าน</span>", unsafe_allow_html=True)

                st.markdown("---")
                if c_pass == total_c:
                    st.success("🟢 **GRADE A (OUTSTANDING):** ผ่านเกณฑ์งบการเงินทั้งหมดของทั้ง Lynch และ Fisher พร้อมสำหรับการส่งให้ AI ตรวจสอบคูเมืองทางธุรกิจ (Moat) ต่อไป")
                elif c_pass >= 4:
                    st.warning(f"🟡 **GRADE B (WATCHLIST):** ผ่าน {c_pass}/{total_c} เกณฑ์ บริษัทมีคุณภาพดีแต่มีบางจุดที่ต้องเฝ้าระวัง (เช่น ราคายังไม่ถูก หรือมีภาระหนี้)")
                else:
                    st.error(f"🔴 **GRADE C (HIGH RISK):** ผ่านเพียง {c_pass}/{total_c} เกณฑ์ แนะนำให้หลีกเลี่ยงหรือศึกษาข้อมูลเพิ่มเติมอย่างระมัดระวัง")

            # ----------------------------------------------------
            # Tab 2: Red Flags
            # ----------------------------------------------------
            with tab_redflag:
                st.markdown("### 🚨 ระบบตรวจสอบการตกแต่งบัญชีและสัญญาณอันตราย")
                rf1, rf2 = st.columns(2)
                with rf1:
                    with st.container(border=True):
                        st.write("#### 1. คุณภาพเงินสดแท้จริง (Cash Flow Divergence)")
                        st.write(f"- **Operating Cash Flow:** `${ocf:,.0f}`")
                        st.write(f"- **Net Income:** `${net_income:,.0f}`")
                        if cash_flow_divergence:
                            st.error("❌ กระแสเงินสดต่ำกว่ากำไรสุทธิเกิน 15% (กำไรอาจเป็นเพียงตัวเลขตกแต่งทางบัญชี)")
                        else:
                            st.success("✅ เงินสดเข้ากระเป๋าจริงสอดคล้องกับกำไรที่รายงาน")

                    with st.container(border=True):
                        st.write("#### 2. ค่าตอบแทนหุ้นพนักงาน (Stock-Based Comp)")
                        st.write(f"- **SBC ต่อเงินสดดำเนินงาน:** `{sbc_ratio:.1f}%` (เกณฑ์เตือน > 20%)")
                        if sbc_warning:
                            st.error("❌ บริษัทจ่ายผลตอบแทนด้วยการพิมพ์หุ้นแจกพนักงานสูงเกินไป ซึ่งจะลดทอนกำไรในอนาคต")
                        else:
                            st.success("✅ สัดส่วน SBC อยู่ในระดับปลอดภัย")

                with rf2:
                    with st.container(border=True):
                        st.write("#### 3. สัญญาณยัดของ / ลูกหนี้บวม (Accounts Receivable)")
                        st.write(f"- **การเติบโตของลูกหนี้การค้า (YoY):** `{ar_growth:.1f}%`")
                        st.write(f"- **การเติบโตของยอดขาย (YoY):** `{rev_growth:.1f}%`")
                        if ar_warning:
                            st.error("❌ ลูกหนี้โตเร็วกว่ายอดขายเกิน 1.5 เท่า (ระวังการเร่งรับรู้รายได้หรือเก็บเงินไม่ได้)")
                        else:
                            st.success("✅ ลูกหนี้การค้าโตสัมพันธ์กับยอดขายจริง")

                    with st.container(border=True):
                        st.write("#### 4. สินค้าตกรุ่นค้างสต็อก (Inventory Growth)")
                        if has_inventory:
                            st.write(f"- **การเติบโตของสินค้าคงคลัง (YoY):** `{inv_growth:.1f}%`")
                            if inv_warning:
                                st.error("❌ สินค้าคงคลังโตเร็วกว่ายอดขายเกิน 1.5 เท่า (เสี่ยงโดนตัดขาดทุนสต็อก)")
                            else:
                                st.success("✅ บริหารจัดการสินค้าคงคลังได้ดี")
                        else:
                            st.info("ℹ️ บริษัทประเภทบริการ/ซอฟต์แวร์/การเงิน ไม่มีสินค้าคงคลัง")

            # ----------------------------------------------------
            # Tab 3: Philip Fisher Deep Dive
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
                        st.write(f"- **Return on Invested Capital (ROA):** `{roa:.1f}%`")
                        st.caption("💡 ฟิชเชอร์ชอบบริษัทที่รักษา Operating Margin ได้สูงสม่ำเสมอแม้ในยามวิกฤต")

                with f2:
                    with st.container(border=True):
                        st.write("#### 🔬 ความเข้มข้นของการวิจัยและนวัตกรรม (R&D)")
                        st.write(f"- **งบ R&D ประจำปี:** `${rd_exp:,.0f}`")
                        st.write(f"- **R&D ต่อรายได้รวม:** `{rd_ratio:.1f}%`")
                        if rd_ratio >= 10:
                            st.success("✅ มีการลงทุนวิจัยเข้มข้นตรงสเปกหุ้นเติบโต (>10%)")
                        else:
                            st.info("ℹ️ การลงทุนวิจัยอยู่ในระดับปกติหรือเป็นธุรกิจที่ไม่ต้องพึ่งพาเทคโนโลยี")

                    with st.container(border=True):
                        st.write("#### 👥 จริยธรรมต่อผู้ถือหุ้น (Share Dilution)")
                        st.write(f"- **อัตราการเปลี่ยนแปลงจำนวนหุ้น:** `{sh_growth:+.2f}% ต่อปี`")
                        if dilution_warning:
                            st.error("❌ มีการออกหุ้นเพิ่มทุนทำให้สัดส่วนความเป็นเจ้าของลดลง")
                        else:
                            st.success("✅ ไม่พบการเจือจางหุ้น หรือมีการซื้อหุ้นคืน (Share Buybacks) เพิ่มมูลค่า")

            # ----------------------------------------------------
            # Tab 4: Peter Lynch Deep Dive
            # ----------------------------------------------------
            with tab_lynch:
                st.markdown("### 💰 ความคุ้มค่าด้านราคาและสุขภาพงบดุล (Peter Lynch)")
                l1, l2 = st.columns(2)
                with l1:
                    with st.container(border=True):
                        st.write("#### 🏷️ การประเมินมูลค่า (Valuation Multiples)")
                        st.write(f"- **Trailing P/E (กำไรย้อนหลัง):** `{pe_trailing if pe_trailing else 'N/A'}`")
                        st.write(f"- **Forward P/E (กำไรคาดการณ์):** `{pe_forward if pe_forward else 'N/A'}`")
                        st.write(f"- **PEG Ratio:** `{peg if peg else 'N/A'}`")
                        st.write(f"- **Price to Book (P/B):** `{pb_ratio if pb_ratio else 'N/A'}`")
                        st.write(f"- **Dividend Yield:** `{dividend_yield:.2f}%`")

                with l2:
                    with st.container(border=True):
                        st.write("#### 🛡️ ป้อมปราการเงินสด (Cash & Balance Sheet)")
                        st.write(f"- **Total Cash & Short-Term Assets:** `${cash:,.0f}`")
                        st.write(f"- **Total Debt (หนี้สินรวม):** `${debt:,.0f}`")
                        st.write(f"- **Net Cash (เงินสดสุทธิ):** `${net_cash:,.0f}`")
                        st.write(f"- **Debt to Equity Ratio:** `{de_ratio:.1f}%`")
                        st.write(f"- **Free Cash Flow (เงินสดอิสระ):** `${fcf:,.0f}`")

            # ----------------------------------------------------
            # Tab 5: 4-Year Historical Charts
            # ----------------------------------------------------
            with tab_charts:
                st.markdown("### 📈 แนวโน้มผลประกอบการย้อนหลัง 4 ปี")
                try:
                    # เตรียมข้อมูลทำกราฟย้อนหลัง
                    hist_rev = inc.loc["TotalRevenue"] if "TotalRevenue" in inc.index else None
                    hist_ni = inc.loc["NetIncome"] if "NetIncome" in inc.index else None
                    hist_ocf = cf.loc["OperatingCashFlow"] if "OperatingCashFlow" in cf.index else None

                    if hist_rev is not None and hist_ni is not None:
                        df_chart = pd.DataFrame({
                            "Total Revenue (รายได้รวม)": hist_rev,
                            "Net Income (กำไรสุทธิ)": hist_ni,
                            "Operating Cash Flow (กระแสเงินสดดำเนินงาน)": hist_ocf if hist_ocf is not None else 0
                        }).sort_index()

                        st.bar_chart(df_chart)
                        st.caption("แท่งกราฟเปรียบเทียบ รายได้รวม vs กำไรสุทธิ vs เงินสดจากการดำเนินงานจริงในแต่ละปี")
                    else:
                        st.info("ไม่มีข้อมูลงบย้อนหลังเพียงพอสำหรับสร้างกราฟ")
                except Exception as chart_err:
                    st.write(f"ไม่สามารถแสดงกราฟได้: {chart_err}")

            # ----------------------------------------------------
            # Tab 6: AI Scuttlebutt Prompt
            # ----------------------------------------------------
            with tab_ai:
                st.markdown("### 🤖 นำข้อมูลไปให้ AI ช่วยวิเคราะห์คูเมืองต่อ (One-Click Prompt)")
                summary = info.get("longBusinessSummary", "ไม่มีข้อมูลอธิบายธุรกิจ")
                
                ai_prompt_text = f"""วิเคราะห์ความได้เปรียบทางการแข่งขัน (Economic Moat) และทีมผู้บริหารของบริษัทนี้อย่างละเอียด ตามหลักการ 15 ข้อของ Philip Fisher และทฤษฎีหุ้น 6 ร่างของ Peter Lynch:

1. ข้อมูลทั่วไปของบริษัท:
- ชื่อบริษัท: {info.get('shortName', ticker)} ({ticker})
- อุตสาหกรรม: {sector} / {industry}
- Market Cap: ${market_cap:,.0f}

2. ตัวเลขทางการเงินสำคัญ:
- อัตราการเติบโตของรายได้ (YoY): {rev_growth:.1f}%
- Gross Profit Margin: {gross_margin:.1f}%
- Operating Profit Margin: {op_margin:.1f}%
- R&D to Revenue: {rd_ratio:.1f}%
- PEG Ratio: {peg if peg else 'N/A'}
- เงินสดสุทธิ (Net Cash): ${net_cash:,.0f}

3. คำอธิบายโมเดลธุรกิจ:
{summary}

คำถามที่ต้องการให้ตอบ:
1. บริษัทนี้มี Economic Moat (คูเมืองทางธุรกิจ) ประเภทใดที่คู่แข่งรายใหม่ไม่สามารถลอกเลียนแบบได้ง่ายในอีก 5 ปีข้างหน้า?
2. ประสิทธิภาพทีมขายและการตลาด (Sales Organization) เหนือกว่าคู่แข่งอย่างไร?
3. สินค้าของบริษัทมีตลาดรองรับขนาดใหญ่ (Market Potential) พอที่จะขยายตัวต่อเนื่องได้อีกหลายปีหรือไม่?
4. สรุปความเสี่ยงเชิงโครงสร้าง 3 ข้อที่ต้องจับตามอง
"""
                st.text_area("คัดลอกข้อความด้านล่างนี้ไปวางใน AI Chat ของคุณได้ทันที:", value=ai_prompt_text, height=350)

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูลของ {ticker}: {e}")
