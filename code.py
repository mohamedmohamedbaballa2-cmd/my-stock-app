import streamlit as st
import yfinance as ticker_library
import pandas as pd
import numpy as np

# إعدادات الصفحة وواجهة التطبيق
st.set_page_config(page_title="Stock Analyzer Pro", page_icon="📊", layout="wide")

st.title("📊 Stock Analysis & Evaluation App")
st.write("قم بتحليل واستخراج التقارير المخططة والمستويات الفنية لأي سهم هولندي أو عالمي سحابيًا")

# حساب المؤشرات الفنية
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    roll_up = up.rolling(window).mean()
    roll_down = down.rolling(window).mean()
    rs = roll_up / roll_down
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi.iloc[-1]

def find_support_resistance(data, window=5):
    supports = []
    resistances = []
    for i in range(window, len(data) - window):
        if data['Low'].iloc[i] == data['Low'].iloc[i-window:i+window+1].min():
            supports.append(data['Low'].iloc[i])
        if data['High'].iloc[i] == data['High'].iloc[i-window:i+window+1].max():
            resistances.append(data['High'].iloc[i])
    return supports, resistances

# شريط إدخال البيانات في الواجهة
ticker_input = st.text_input("أدخل رمز السهم (مثال: SHELL.AS أو ASML.AS):", value="SHELL.AS")

if st.button("بدء التحليل السحابي 🚀"):
    with st.spinner('جاري سحب البيانات المالية والفنية الحية...'):
        try:
            stock = ticker_library.Ticker(ticker_input)
            info = stock.info
            fast_info = stock.fast_info
            
            balance_sheet = stock.quarterly_balance_sheet
            financials = stock.quarterly_financials
            cash_flow = stock.quarterly_cashflow
            history = stock.history(period="6mo")
            
            if history.empty:
                st.error("خطأ: لم يتم العثور على بيانات تاريخية لهذا الرمز.")
            else:
                # استخراج البيانات
                company_name = info.get('longName', 'N/A')
                current_price = fast_info.get('last_price', info.get('currentPrice', 0))
                market_cap = info.get('marketCap', 0)
                exchange = info.get('exchange', 'N/A')
                
                operating_margin = info.get('operatingMargins', 0) * 100
                pe_ratio = info.get('trailingPE', 'N/A')
                roe = info.get('returnOnEquity', 0) * 100

                current_assets = balance_sheet.loc['Current Assets'].iloc[0] if 'Current Assets' in balance_sheet.index else 1
                current_liabilities = balance_sheet.loc['Current Liabilities'].iloc[0] if 'Current Liabilities' in balance_sheet.index else 1
                current_ratio = current_assets / current_liabilities
                
                total_debt = info.get('totalDebt', 0)
                total_equity = info.get('totalEquity', 1)
                debt_to_equity = total_debt / total_equity if total_equity != 0 else 0

                operating_cash_flow = cash_flow.loc['Cash Flow From Operating Activities'].iloc[0] if 'Cash Flow From Operating Activities' in cash_flow.index else 0
                capex = abs(cash_flow.loc['Capital Expenditures'].iloc[0]) if 'Capital Expenditures' in cash_flow.index else 0
                free_cash_flow = operating_cash_flow - capex
                dividend_yield = info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0

                # الفني المتقدم
                latest_rsi = calculate_rsi(history, window=14)
                rsi_status = "Neutral (محايد)"
                if latest_rsi > 70: rsi_status = "Overbought (تشبع شرائي - خطر)"
                elif latest_rsi < 30: rsi_status = "Oversold (تشبع بيعي - فرصة)"

                ma_200 = info.get('twoHundredDayAverage', current_price)
                general_trend = "Bullish (صعودي)" if current_price > ma_200 else "Bearish (هبوطي)"

                all_supports, all_resistances = find_support_resistance(history, window=5)
                past_supports = [s for s in all_supports if s < current_price]
                past_resistances = [r for r in all_resistances if r > current_price]
                
                support_1 = max(past_supports) if past_supports else (current_price * 0.95)
                support_2 = min(past_supports) if len(past_supports) > 1 else (support_1 * 0.95)
                resistance_1 = min(past_resistances) if past_resistances else (current_price * 1.05)
                resistance_2 = max(past_resistances) if len(past_resistances) > 1 else (resistance_1 * 1.05)

                # عرض البيانات في واجهات تفاعلية
                col1, col2 = st.columns(2)
                with col1:
                    st.header("📌 Identification & Fundamentals")
                    st.write(f"**Company Name:** {company_name}")
                    st.write(f"**Price:** {current_price:.2f} EUR/USD")
                    st.write(f"**Market Cap:** {market_cap:,}")
                    st.write(f"**Operating Margin:** {operating_margin:.2f}%")
                    st.write(f"**P/E Ratio:** {pe_ratio}")
                    st.write(f"**ROE:** {roe:.2f}%")
                    
                with col2:
                    st.header("⚡ Liquidity & Cash Flow")
                    st.write(f"**Current Ratio:** {current_ratio:.2f}")
                    st.write(f"**D/E Ratio:** {debt_to_equity:.2f}")
                    st.write(f"**Free Cash Flow:** {free_cash_flow:,}")
                    st.write(f"**Dividend Yield:** {dividend_yield:.2f}%")

                st.header("📈 Advanced Technical Levels")
                st.write(f"**General Trend (MA200):** {general_trend}")
                st.write(f"**RSI (14):** {latest_rsi:.2f} -> **{rsi_status}**")
                
                # عرض الدعم والمقاومة في جداول منسقة
                st.subheader("🎯 Trading Levels")
                st.success(f"🟢 **Support 1:** {support_1:.2f} | **Support 2 (Stop Loss):** {support_2:.2f}")
                st.error(f"🔴 **Resistance 1:** {resistance_1:.2f} | **Resistance 2 (Peak):** {resistance_2:.2f}")
                
                # رسم بياني تفاعلي لحركة السعر
                st.subheader("📊 Price Chart (6 Months)")
                st.line_chart(history['Close'])
                
        except Exception as e:
            st.error(f"حدث خطأ أثناء معالجة البيانات المادية: {e}")
