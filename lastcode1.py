import streamlit as st
import yfinance as ticker_library
import pandas as pd
import numpy as np

# إعدادات الصفحة وواجهة التطبيق
st.set_page_config(page_title="Stock Analyzer Pro (Bilingual Targets)", page_icon="📊", layout="wide")

st.title("📊 Global Stock Analysis & Investment Pro App")
st.markdown("تطبيق متكامل لتحليل الأسهم، التوقع الفني المستقبلي، وحساب عوائد الاستثمار مع توضيح المصطلحات والمستهدفات الاستثمارية باللغتين.")

# 1. قاعدة البيانات الشاملة للأسواق والشركات
MARKETS_DATA = {
    "🇸🇦 السوق السعودي (Tadawul Market)": {
        "شركة أرامكو السعودية (Saudi Aramco)": "2222.SR",
        "مصرف الراجحي (Al Rajhi Bank)": "1120.SR",
        "شركة إس تي سي (STC)": "7010.SR",
        "شركة ألبان المراعي (Almarai)": "2280.SR",
        "شركة سابك (SABIC)": "2010.SR",
        "شركة الإنماء (Al Inma Bank)": "1150.SR"
    },
    "🇺🇸 السوق الأمريكي (US Market - S&P 500 / NASDAQ)": {
        "شركة أبل (Apple Inc.)": "AAPL",
        "شركة مايكروسوفت (Microsoft Corporation)": "MSFT",
        "شركة إنفيديا (NVIDIA)": "NVDA",
        "شركة تسلا (Tesla, Inc.)": "TSLA",
        "شركة أمازون (Amazon)": "AMZN",
        "شركة جوجل / ألفابت (Alphabet Inc.)": "GOOGL",
        "شركة ميتا (Meta Platforms)": "META"
    },
    "🇦🇪 السوق الإماراتي (UAE Market - DFM / ADX)": {
        "إعمار العقارية (Emaar Properties)": "EMAAR.DU",
        "بنك أبوظبي الأول (First Abu Dhabi Bank)": "FAB.AD",
        "شركة الدار العقارية (Aldar Properties)": "ALDAR.AD"
    },
    "🇳🇱 السوق الهولندي (Dutch Market - Euronext Amsterdam)": {
        "شركة شل للطاقة (Shell plc)": "SHELL.AS",
        "شركة إيه إس إم إل (ASML Holding)": "ASML.AS",
        "مجموعة آي إن جي (ING Groep N.V.)": "INGA.AS"
    },
    "🇬🇧 السوق البريطاني (UK Market - FTSE 100)": {
        "شركة أسترازينيكا (AstraZeneca)": "AZN.L",
        "شركة بي بي للطاقة (BP p.l.c.)": "BP.L",
        "مجموعة إتش إس بي سي (HSBC)": "HSBA.L"
    }
}

# الشريط الجانبي للاختيارات
st.sidebar.header("🔍 إعدادات السوق والأسهم (Market & Stock Settings)")
selected_market = st.sidebar.selectbox("1️⃣ اختر السوق العالمي (Select Market):", list(MARKETS_DATA.keys()))

companies = MARKETS_DATA[selected_market]
selected_company = st.sidebar.selectbox("2️⃣ اختر الشركة (Select Company):", list(companies.keys()))
ticker_input = companies[selected_company]

time_period = st.sidebar.selectbox("3️⃣ النطاق الزمني للتحليل (Time Period):", ["3mo", "6mo", "1y", "2y"], index=1)

# دوال الحساب الفني
def calculate_rsi(data, window=14):
    try:
        delta = data['Close'].diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        roll_up = up.rolling(window).mean()
        roll_down = down.rolling(window).mean()
        rs = roll_up / roll_down
        rsi = 100.0 - (100.0 / (1.0 + rs))
        return float(rsi.iloc[-1])
    except:
        return 50.0

def find_support_resistance(data, window=5):
    supports, resistances = [], []
    try:
        for i in range(window, len(data) - window):
            if data['Low'].iloc[i] == data['Low'].iloc[i-window:i+window+1].min():
                supports.append(float(data['Low'].iloc[i]))
            if data['High'].iloc[i] == data['High'].iloc[i-window:i+window+1].max():
                resistances.append(float(data['High'].iloc[i]))
    except:
        pass
    return supports, resistances

# زر تنفيذ التحليل
if st.sidebar.button("🚀 بدء التحليل الشامل والتوقع (Start Analysis & Prediction)"):
    with st.spinner(f'جاري جلب بيانات وحساب توقعات سهم {selected_company}...'):
        try:
            stock = ticker_library.Ticker(ticker_input)
            info = stock.info
            history = stock.history(period=time_period)
            
            if history.empty:
                st.error("خطأ: لم يتم العثور على بيانات تاريخية لهذا السهم (No historical data found).")
            else:
                current_price = float(history['Close'].iloc[-1])
                prev_close = float(history['Close'].iloc[-2]) if len(history) > 1 else current_price
                price_change_pct = ((current_price - prev_close) / prev_close) * 100
                
                company_name = info.get('longName', selected_company)
                market_cap = info.get('marketCap', 0)
                currency = info.get('currency', 'USD')
                
                # المؤشرات المالية
                operating_margin = (info.get('operatingMargins') or 0.0) * 100
                pe_ratio = info.get('trailingPE', 'غير متوفر (N/A)')
                roe = (info.get('returnOnEquity') or 0.0) * 100
                current_ratio = info.get('currentRatio') or 1.0
                total_debt = info.get('totalDebt', 0) or 0
                total_equity = info.get('totalEquity', 1) or 1
                debt_to_equity = (total_debt / total_equity) if total_equity != 0 else 0.0
                dividend_yield = (info.get('dividendYield') or 0.0) * 100

                # مؤشرات فنية
                latest_rsi = calculate_rsi(history, window=14)
                rsi_status = "محايد (Neutral)"
                if latest_rsi > 70: rsi_status = "تشبع شرائي - احتمال تصحيح هبوطي (Overbought - Bearish Correction Risk ⚠️)"
                elif latest_rsi < 30: rsi_status = "تشبع بيعي - فرصة ارتداد محتملة (Oversold - Potential Rebound 💡)"

                ma_200 = info.get('twoHundredDayAverage', current_price) or current_price
                general_trend = "صعودي (Bullish 🟢)" if current_price > ma_200 else "هبوطي (Bearish 🔴)"

                all_supports, all_resistances = find_support_resistance(history, window=5)
                past_supports = [s for s in all_supports if s < current_price]
                past_resistances = [r for r in all_resistances if r > current_price]
                
                support_1 = max(past_supports) if past_supports else (current_price * 0.95)
                support_2 = min(past_supports) if len(past_supports) > 1 else (support_1 * 0.95)
                resistance_1 = min(past_resistances) if past_resistances else (current_price * 1.05)
                resistance_2 = max(past_resistances) if len(past_resistances) > 1 else (resistance_1 * 1.05)

                # محرك التوقع المستقبلي
                returns_series = history['Close'].pct_change().dropna()
                daily_volatility = returns_series.std()
                avg_daily_return = returns_series.mean()
                
                projected_return_30d = (1 + avg_daily_return)**30 - 1
                predicted_price_30d = current_price * (1 + projected_return_30d)
                
                prediction_outlook = "إيجابي ومتفائل (Positive & Optimistic)" if avg_daily_return > 0 and latest_rsi < 65 else "حذر أو تداولات عرضية (Cautious / Sideways)"
                if latest_rsi > 70: prediction_outlook = "توقع جني أرباح هبوطي مؤقت (Temporary Profit-Taking Expected)"

                # تنظيم العرض في تبويبات (Tabs)
                st.markdown(f"## 📈 تقرير سهم (Stock Report): {company_name} (`{ticker_input}`)")
                
                # بطاقات سريعة
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("السعر الحالي (Current Price)", f"{current_price:.2f} {currency}", f"{price_change_pct:+.2f}%")
                m2.metric("القيمة السوقية (Market Cap)", f"{market_cap:,.0f}" if market_cap else "غير متوفر (N/A)")
                m3.metric("مكرر الربحية (P/E Ratio)", f"{pe_ratio}")
                m4.metric("عائد التوزيعات (Dividend Yield)", f"{dividend_yield:.2f}%")

                st.divider()

                tab1, tab2, tab3 = st.tabs([
                    "📊 التحليل المالي والفني والأهداف (Analysis & Trading Targets)", 
                    "🔮 توقع الحركة المستقبلية (Future Price Outlook)", 
                    "💰 حاسبة عوائد الاستثمار (Investment Return Calculator)"
                ])

                with tab1:
                    st.subheader("📌 الأداء الأساسي والمالي (Fundamental & Financial Performance)")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**هامش الربح التشغيلي (Operating Margin):** نسبة الأرباح المتبقية بعد دفع تكاليف التشغيل -> **{operating_margin:.2f}%**")
                        st.write(f"**العائد على حقوق الملكية (ROE - Return on Equity):** مدى كفاءة الشركة في توليد الأرباح من أموال المساهمين -> **{roe:.2f}%**")
                    with c2:
                        st.write(f"**نسبة التداول (Current Ratio):** مقياس قدرة الشركة على سداد التزاماتها قصيرة الأجل -> **{current_ratio:.2f}**")
                        st.write(f"**نسبة الدين إلى حقوق الملكية (D/E Ratio - Debt to Equity):** حجم التمويل بالديون مقارنة برأس المال -> **{debt_to_equity:.2f}**")

                    st.subheader("📊 المؤشرات الفنية (Technical Indicators)")
                    f1, f2 = st.columns(2)
                    with f1:
                        st.info(f"**الاتجاه العام بناءً على المتوسط المتحرك 200 يوم (MA200 - 200-Day Moving Average):** {general_trend}")
                    with f2:
                        st.info(f"**مؤشر القوة النسبية للزخم (RSI 14 - Relative Strength Index):** {latest_rsi:.2f} — {rsi_status}")
                    
                    # قسم الأهداف ومستويات التداول بالشرح المفصل واللغتين
                    st.subheader("🎯 الأهداف ومستويات التداول (Trading Targets & Price Levels)")
                    st.markdown("يوضح الجدول التالي مستويات الدعم والمقاومة وأهداف البيع والشراء مع شرح كل مصطلح باللغة الإنجليزية والعربية:")

                    target_data = [
                        {
                            "المصطلح الإنجليزي (English Term)": "Support 1 (الدعم الأول)",
                            "القيمة (Value)": f"{support_1:.2f} {currency}",
                            "الشرح والتوضيح باللغة العربية (Description)": "مستوى سعري يتوقع أن يرتد منه السهم صعوداً نتيجة زيادة قوى الشراء (Buying Pressure)."
                        },
                        {
                            "المصطلح الإنجليزي (English Term)": "Support 2 / Stop Loss (الدعم الثاني / وقف الخسارة)",
                            "القيمة (Value)": f"{support_2:.2f} {currency}",
                            "الشرح والتوضيح باللغة العربية (Description)": "مستوى حرج يُستخدم لحماية رأس المال وبيع السهم عنده لتجنب خسائر أكبر في حال الهبوط الحاد."
                        },
                        {
                            "المصطلح الإنجليزي (English Term)": "Resistance 1 / Target 1 (المقاومة الأولى / الهدف الأول)",
                            "القيمة (Value)": f"{resistance_1:.2f} {currency}",
                            "الشرح والتوضيح باللغة العربية (Description)": "مستوى سعري مستهدف لجني الأرباح الجزئية، حيث تواجه الأسعار ضغوط بيعية عادةً."
                        },
                        {
                            "المصطلح الإنجليزي (English Term)": "Resistance 2 / Target 2 (المقاومة الثانية / الهدف الأقصى)",
                            "القيمة (Value)": f"{resistance_2:.2f} {currency}",
                            "الشرح والتوضيح باللغة العربية (Description)": "هدف سعري أعلى يمثل قمة سابقة قد يصل إليها السهم في حال استمرار الزخم الإيجابي القوي."
                        }
                    ]
                    
                    st.table(pd.DataFrame(target_data))

                    st.subheader(f"📉 حركة السعر التاريخية خلال فترة {time_period} (Historical Price Chart)")
                    st.line_chart(history['Close'])

                with tab2:
                    st.subheader("🔮 توقع حركة السهم خلال الـ 30 يوماً القادمة (30-Day Price Outlook)")
                    st.markdown("يعتمد هذا التوقع التقريبي على التحليل الإحصائي للعائد اليومي التاريخي ومؤشر الزخم (RSI):")
                    
                    p1, p2, p3 = st.columns(3)
                    p1.metric("السعر المتوقع خلال شهر (Projected 30D Price)", f"{predicted_price_30d:.2f} {currency}", f"{projected_return_30d*100:+.2f}%")
                    p2.metric("النظرة المستقبلية (Outlook Status)", prediction_outlook)
                    p3.metric("معدل التذبذب اليومي (Daily Volatility)", f"{daily_volatility*100:.2f}%")
                    
                    if projected_return_30d > 0:
                        st.success("💡 **تحليل النظرة (Outlook Analysis):** السهم يظهر ميلاً إيجابياً في الأداء التاريخي للفترة المختارة، مع ضرورة مراقبة مستويات المقاومة المذكورة.")
                    else:
                        st.warning("⚠️ **تحليل النظرة (Outlook Analysis):** السهم يمر بضغوطات تصحيحية سلبية، ويُفضل الانتظار حتى يصل إلى مستويات الدعم القوية.")

                with tab3:
                    st.subheader("💰 حاسبة عوائد الاستثمار المستقبلية (Investment Return Calculator)")
                    st.markdown("قم بتقدير نمو استثماراتك المستقبلية بناءً على مبلغ الاستثمار وعدد سنوات الاحتفاظ (Investment Horizon):")
                    
                    inv_col1, inv_col2 = st.columns(2)
                    with inv_col1:
                        investment_amount = st.number_input("مبلغ الاستثمار الأساسي (Initial Investment Amount):", min_value=100.0, value=10000.0, step=500.0)
                        investment_years = st.slider("مدة الاستثمار بالسنوات (Investment Period in Years):", min_value=1, max_value=10, value=3)
                    with inv_col2:
                        expected_annual_growth = st.slider("معدل النمو السنوي المتوقع (Expected Annual Growth Rate %):", min_value=-20.0, max_value=50.0, value=8.0, step=0.5)
                        include_dividends = st.checkbox("إضافة عائد التوزيعات النقدية السنوي (Include Annual Dividend Yield)?", value=True)

                    effective_rate = expected_annual_growth + (dividend_yield if include_dividends else 0.0)
                    
                    # حساب الفائدة المركبة (Compound Interest Formula)
                    future_value = investment_amount * ((1 + (effective_rate / 100)) ** investment_years)
                    total_profit = future_value - investment_amount
                    total_return_pct = (total_profit / investment_amount) * 100

                    st.divider()
                    r1, r2, r3 = st.columns(3)
                    r1.metric("القيمة الإجمالية المتوقعة (Projected Future Value)", f"{future_value:,.2f} {currency}")
                    r2.metric("صافي الربح المتوقع (Expected Net Profit)", f"{total_profit:,.2f} {currency}")
                    r3.metric("نسبة العائد الإجمالي (Total Return Percentage)", f"{total_return_pct:+.2f}%")

        except Exception as e:
            st.error(f"حدث خطأ أثناء معالجة البيانات (Error processing data): {e}")
else:
    st.info("👈 يرجى اختيار السوق والشركة من الشريط الجانبي ثم الضغط على زر **بدء التحليل الشامل والتوقع**.")
