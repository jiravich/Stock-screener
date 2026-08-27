import streamlit as st
import yfinance as yf
import pandas as pd

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="Lynch & Fisher Stock Screener", layout="wide", initial_sidebar_state="collapsed")
st.title("🎯 Lynch & Fisher Stock Screener")

ticker = st.text_input("พิมพ์ชื่อย่อหุ้นสหรัฐฯ (เช่น AAPL, NVDA, KO, JNJ):", value="AAPL").upper().strip()

if st.button("🚀 สแกนงบการเงิน", type="primary"):
    if not ticker:
        st.warning("กรุณากรอกชื่อหุ้น")
    else:
        try:
            with st.spinner("กำลังดึงข้อมูลงบการเงินจาก Yahoo Finance..."):
                stock = yf.Ticker(ticker)
                info = stock.info
                bs = stock.balance_sheet
                inc = stock.financials
                cf = stock.cashflow

                # 1. ข้อมูล Lynch
                peg = info.get("pegRatio", None)
                cash = info.get("totalCash", 0)
                debt = info.get("totalDebt", 0)
                net_cash = cash - debt

                # 2. ข้อมูล Fisher
                op_margin = info.get("operatingMargins", 0) * 100
                roe = info.get("returnOnEquity", 0) * 100

                # 3. ตรวจจับ Red Flag (เงินสด vs กำไรสุทธิ)
                ocf = cf.loc["OperatingCashFlow"].iloc[0] if "OperatingCashFlow" in cf.index else 0
                net_income = inc.loc["NetIncome"].iloc[0] if "NetIncome" in inc.index else 0
                cash_flow_divergence = ocf < (net_income * 0.7)  # เงินสดจากการดำเนินงานต่ำกว่ากำไร 30% ขึ้นไป

                # แสดงผล Metrics หลัก
                st.subheader(f"📊 ผลการวิเคราะห์: {info.get('shortName', ticker)}")
                
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    peg_display = f"{peg:.2f}" if peg else "N/A"
                    st.metric("PEG Ratio (< 1.0)", peg_display, delta="ผ่าน" if (peg and peg < 1.0) else "แพง/ไม่มีข้อมูล", delta_color="normal" if (peg and peg < 1.0) else "inverse")
                with c2:
                    st.metric("Net Cash (เงินสดสุทธิ)", f"${net_cash:,.0f}", delta="ปลอดภัย (เงินสดหนา)" if net_cash > 0 else "หนี้มากกว่าเงินสด", delta_color="normal" if net_cash > 0 else "inverse")
                with c3:
                    st.metric("Operating Margin", f"{op_margin:.1f}%", delta="กำไรดี" if op_margin >= 15 else "มาร์จิ้นต่ำ")
                with c4:
                    st.metric("ROE (ผู้บริหารเก่ง)", f"{roe:.1f}%", delta="ยอดเยี่ยม" if roe >= 15 else "ปานกลาง")

                st.divider()

                # สรุปสัญญาณไฟเขียว / ไฟแดง
                st.write("### 🔍 สรุปการตรวจสอบ (Checklist Result)")
                
                # ตรวจสอบด่านปลอดภัย
                if peg and peg < 1.0 and net_cash > 0 and op_margin >= 15 and not cash_flow_divergence:
                    st.success("✅ **PASS ALL CRITERIA:** หุ้นตัวนี้ผ่านด่านการเงินเชิงปริมาณของ Lynch & Fisher พร้อมให้ AI ตรวจสอบ Moat ต่อไป")
                else:
                    st.info("ℹ️ **ผลการประเมิน:** มีบางตัวเลขที่ยังไม่ตรงตามสเปก ควรรีเช็กรายละเอียดก่อนตัดสินใจ")

                if cash_flow_divergence:
                    st.error("🚨 **RED FLAG WARNING:** Operating Cash Flow ต่ำกว่า Net Income อย่างมีนัยสำคัญ ระวังตัวเลขกำไรแต่งทางบัญชี")

                # ข้อมูลธุรกิจสำหรับให้ผู้ใช้คัดลอกไปถาม AI
                with st.expander("🏢 ข้อมูลธุรกิจสำหรับนำไปวิเคราะห์ต่อกับ AI"):
                    summary = info.get("longBusinessSummary", "ไม่มีข้อมูล")
                    st.write(summary)

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูลหุ้น {ticker}: {e}")
