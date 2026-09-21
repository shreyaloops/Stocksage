import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import MACD

from database import (
    initialize_database,
    add_holding,
    get_holdings,
    delete_holding
)


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="StockSage",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CUSTOM UI
# ==========================================

st.markdown("""
<style>

    .main {
        background-color: #0e1117;
    }

    [data-testid="stSidebar"] {
        background-color: #161a23;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1 {
        font-size: 42px !important;
        font-weight: 700 !important;
    }

    h2 {
        font-size: 28px !important;
    }

    h3 {
        font-size: 20px !important;
    }

    div[data-testid="stMetric"] {
        background-color: #161a23;
        border: 1px solid #292f3d;
        padding: 18px;
        border-radius: 12px;
    }

</style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.title("📈 StockSage")

    st.caption("Financial Market Analytics")

    st.divider()

    page = st.radio(
            "Navigation",
            [
                "📊 Stock Analysis",
                "🔍 Compare Stocks",
                "🧪 Backtesting",
                "🔎 Stock Screener",
                "💼 Portfolio"
            ]
    )

    st.divider()

    st.caption("Built with Python • Streamlit • yFinance")

# ==========================================
# STOCK ANALYSIS
# ==========================================

if page == "📊 Stock Analysis":

    st.markdown(
    """
    <div style="padding: 10px 0 25px 0;">
        <h1 style="margin-bottom: 5px;">
            📈 StockSage
        </h1>
        <p style="font-size: 18px; color: #9aa4b2;">
            Interactive Stock Market Analytics Dashboard
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
    st.write(
        "Analyze market performance, technical indicators "
        "and risk metrics."
    )

    ticker = st.text_input(
        "Stock Symbol",
        value="RELIANCE.NS",
        help="Example: RELIANCE.NS, TCS.NS, INFY.NS"
    )

    analyze = st.button(
        "🔎 Analyze Stock",
        use_container_width=True
    )

    if analyze:

        with st.spinner("Fetching market data..."):

            data = yf.download(
                ticker,
                period="1y",
                progress=False,
                auto_adjust=False
            )

        if data.empty:

            st.error(
                "No data found. Please check the stock symbol."
            )

        else:

            close = data["Close"]

            if hasattr(close, "columns"):
                close = close.iloc[:, 0]
            
            close = close.dropna()
            data = data.loc[close.index]
            current_price = float(close.iloc[-1])
            previous_price = float(close.iloc[-2])

            daily_change = (
                (current_price - previous_price)
                / previous_price
            ) * 100

            high_52 = float(close.max())
            low_52 = float(close.min())
            
            close_for_rsi = close.iloc[:, 0] if hasattr(close, "columns") else close

            rsi_indicator = RSIIndicator(close=close_for_rsi, window=14)

            rsi_series = rsi_indicator.rsi()

            rsi_value = rsi_series.iloc[-1]

            if hasattr(rsi_value, "iloc"):
                rsi_value = rsi_value.iloc[0]

            rsi = float(rsi_value)
            
            # MACD
            macd_indicator = MACD(close=close_for_rsi)

            macd_series = macd_indicator.macd()

            macd_signal_series = macd_indicator.macd_signal()

            macd_value = macd_series.iloc[-1]

            if hasattr(macd_value, "iloc"):
                macd_value = macd_value.iloc[0]

            macd = float(macd_value)

            sma20 = close.rolling(20).mean()
            sma50 = close.rolling(50).mean()

            returns = close.pct_change().dropna()

            volatility = (
                returns.std() * (252 ** 0.5)
            ) * 100

            cumulative_max = close.cummax()

            drawdown = (
                (close - cumulative_max)
                / cumulative_max
            )

            max_drawdown = float(
                drawdown.min() * 100
            )


            st.success(
                f"Successfully loaded data for {ticker.upper()}"
            )

            # ==================================
            # PRICE HEADER
            # ==================================

            st.subheader(ticker.upper())

            price_col, change_col = st.columns([2, 1])

            price_col.metric(
                "Current Price",
                f"₹{current_price:,.2f}"
            )

            change_col.metric(
                "Daily Change",
                f"{daily_change:.2f}%"
            )

            st.divider()

            # ==================================
            # KEY METRICS
            # ==================================

            st.subheader("📊 Key Metrics")

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "52-Week High",
                f"₹{high_52:,.2f}"
            )

            c2.metric(
                "52-Week Low",
                f"₹{low_52:,.2f}"
            )

            st.metric(
                "RSI (14)",
                f"{rsi:.2f}"
            )
            st.metric(
                "MACD",
                f"{macd:.2f}"
            )

            c3.metric(
                "20-Day SMA",
                f"₹{float(sma20.iloc[-1]):,.2f}"
            )

            c4.metric(
                "50-Day SMA",
                f"₹{float(sma50.iloc[-1]):,.2f}"
            )

            # ==================================
            # RISK METRICS
            # ==================================

            st.subheader("⚠️ Risk & Momentum")

            r1, r2, r3 = st.columns(3)

            r1.metric(
                "RSI (14)",
                f"{rsi:.2f}"
            )

            r2.metric(
                "Annualized Volatility",
                f"{volatility:.2f}%"
            )

            r3.metric(
                "Maximum Drawdown",
                f"{max_drawdown:.2f}%"
            )

            # ==================================
            # PRICE CHART
            # ==================================

            st.subheader("📈 Price Performance")

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=close,
                    mode="lines",
                    name="Closing Price"
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=sma20,
                    mode="lines",
                    name="20-Day SMA"
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=sma50,
                    mode="lines",
                    name="50-Day SMA"
                )
            )

            fig.update_layout(
                template="plotly_dark",
                xaxis_title="Date",
                yaxis_title="Price (₹)",
                hovermode="x unified",
                height=500
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )
            # CANDLESTICK CHART
            st.subheader("🕯️ Candlestick Chart")

            candle_open = data["Open"]
            candle_high = data["High"]
            candle_low = data["Low"]
            candle_close = data["Close"]

            if hasattr(candle_open, "columns"):
                candle_open = candle_open.iloc[:, 0]
            if hasattr(candle_high, "columns"):
                candle_high = candle_high.iloc[:, 0]
            if hasattr(candle_low, "columns"):
                candle_low = candle_low.iloc[:, 0]
            if hasattr(candle_close, "columns"):
                candle_close = candle_close.iloc[:, 0]

            candle_fig = go.Figure(
                data=[
                    go.Candlestick(
                        x=data.index,
                        open=candle_open,
                        high=candle_high,
                        low=candle_low,
                        close=candle_close,
                        name="Price"
                    )
                ]
            )

            candle_fig.update_layout(
                title="Price Movement",
                xaxis_title="Date",
                yaxis_title="Price (₹)",
                template="plotly_dark",
                height=500,
                xaxis_rangeslider_visible=False
            )

            st.plotly_chart(
                candle_fig,
                use_container_width=True
            )

            # ==================================
            # RSI CHART
            # ==================================

            st.subheader("📉 RSI")

            rsi_fig = go.Figure()

            rsi_fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=rsi_series,
                    mode="lines",
                    name="RSI"
                )
            )

            rsi_fig.add_hline(
                y=70,
                line_dash="dash",
                annotation_text="70"
            )

            rsi_fig.add_hline(
                y=30,
                line_dash="dash",
                annotation_text="30"
            )

            rsi_fig.update_layout(
                template="plotly_dark",
                yaxis=dict(range=[0, 100]),
                height=350
            )

            st.plotly_chart(
                rsi_fig,
                use_container_width=True
            )

            # MACD Chart
            
            macd_fig = go.Figure()
            
            macd_fig.add_trace(
                go.Scatter(
                    x=close.index,
                    y=macd_series,
                    mode="lines",
                    name="MACD"
                )
            )
            
            macd_fig.add_trace(
                go.Scatter(
                    x=close.index,
                    y=macd_signal_series,
                    mode="lines",
                    name="Signal"
                )
            )
            
            macd_fig.update_layout(
                title="MACD",
                xaxis_title="Date",
                yaxis_title="MACD",
                hovermode="x unified"
            )
            
            st.plotly_chart(
                macd_fig,
                use_container_width=True
            )
        # ======================================
        # ADVANCED STOCK ANALYTICS
        # ======================================

        st.subheader("📊 Advanced Stock Analytics")

        analytics_close = close.dropna()

        if len(analytics_close) >= 21:

            return_1m = (analytics_close.iloc[-1] / analytics_close.iloc[-21] - 1) * 100

            if len(analytics_close) >= 63:
                return_3m = (analytics_close.iloc[-1] / analytics_close.iloc[-63] - 1) * 100
            else:
                return_3m = None

            if len(analytics_close) >= 126:
                return_6m = (analytics_close.iloc[-1] / analytics_close.iloc[-126] - 1) * 100
            else:
                return_6m = None

            if len(analytics_close) >= 252:
                return_1y = (analytics_close.iloc[-1] / analytics_close.iloc[-252] - 1) * 100
            else:
                return_1y = None

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "1 Month Return",
                    f"{return_1m:.2f}%"
                )

            with col2:
                if return_3m is not None:
                    st.metric(
                        "3 Month Return",
                        f"{return_3m:.2f}%"
                    )
                else:
                    st.metric("3 Month Return", "N/A")

            with col3:
                if return_6m is not None:
                    st.metric(
                        "6 Month Return",
                        f"{return_6m:.2f}%"
                    )
                else:
                    st.metric("6 Month Return", "N/A")

            with col4:
                if return_1y is not None:
                    st.metric(
                        "1 Year Return",
                        f"{return_1y:.2f}%"
                    )
                else:
                    st.metric("1 Year Return", "N/A")

        else:
            st.info("Not enough historical data to calculate returns.")
        # ======================================
        # VOLATILITY
        # ======================================

        st.subheader("📉 Volatility")

        daily_returns = analytics_close.pct_change().dropna()

        if len(daily_returns) > 1:
            annualized_volatility = daily_returns.std() * (252 ** 0.5) * 100

            st.metric(
                "Annualized Volatility",
                f"{annualized_volatility:.2f}%"
            )

            st.caption(
                "Annualized volatility measures how much the stock's daily returns fluctuate."
            )
        else:
            st.info("Not enough data to calculate volatility.")

        # ======================================
        # MAXIMUM DRAWDOWN
        # ======================================

        st.subheader("📉 Maximum Drawdown")

        running_peak = analytics_close.cummax()
        drawdown = (analytics_close - running_peak) / running_peak * 100
        max_drawdown = drawdown.min()

        st.metric(
            "Maximum Drawdown",
            f"{max_drawdown:.2f}%"
        )

        st.caption(
            "Maximum drawdown measures the largest decline from a previous price peak."
        )


        # ======================================
        # SHARPE RATIO
        # ======================================

        st.subheader("📈 Sharpe Ratio")

        if len(daily_returns) > 1:
            risk_free_rate = 0.0
            annualized_return = daily_returns.mean() * 252
            annualized_std = daily_returns.std() * (252 ** 0.5)

            if annualized_std != 0:
                sharpe_ratio = (annualized_return - risk_free_rate) / annualized_std

                st.metric(
                    "Sharpe Ratio",
                    f"{sharpe_ratio:.2f}"
                )

                st.caption(
                    "Sharpe Ratio measures return relative to the volatility of the stock."
                )
            else:
                st.info("Sharpe Ratio cannot be calculated when volatility is zero.")
        else:
            st.info("Not enough data to calculate Sharpe Ratio.")


        # ======================================
        # BETA VS NIFTY 50
        # ======================================

        st.subheader("📊 Beta vs NIFTY 50")

        nifty_data = yf.download(
            "^NSEI",
            period="1y",
            progress=False
        )

        if not nifty_data.empty:
            nifty_close = nifty_data["Close"]

            if hasattr(nifty_close, "columns"):
                nifty_close = nifty_close.iloc[:, 0]

            nifty_returns = nifty_close.pct_change().dropna()

            beta_data = daily_returns.to_frame("stock").join(
                nifty_returns.to_frame("nifty"),
                how="inner"
            ).dropna()

            if len(beta_data) > 1 and beta_data["nifty"].var() != 0:
                beta = beta_data["stock"].cov(beta_data["nifty"]) / beta_data["nifty"].var()

                st.metric(
                    "Beta vs NIFTY 50",
                    f"{beta:.2f}"
                )

                st.caption(
                    "Beta measures how much the stock has historically moved relative to the NIFTY 50."
                )
            else:
                st.info("Not enough overlapping data to calculate Beta.")
        else:
            st.info("Unable to download NIFTY 50 data for Beta calculation.")

        # ======================================
        # FUNDAMENTAL ANALYSIS
        # ======================================

        st.subheader("🏢 Fundamental Analysis")

        stock_info = yf.Ticker(ticker).info

        fundamental_data = {
            "Market Cap": stock_info.get("marketCap"),
            "P/E Ratio": stock_info.get("trailingPE"),
            "EPS": stock_info.get("trailingEps"),
            "Dividend Yield": stock_info.get("dividendYield"),
            "Price-to-Book": stock_info.get("priceToBook"),
            "Revenue": stock_info.get("totalRevenue"),
            "Profit": stock_info.get("netIncomeToCommon"),
            "Debt-to-Equity": stock_info.get("debtToEquity"),
            "ROE": stock_info.get("returnOnEquity")
        }

        def format_large_number(value):
            if value is None:
                return "N/A"

            if value >= 1_000_000_000_000:
                return f"₹{value / 1_000_000_000_000:.2f}T"
            elif value >= 1_000_000_000:
                return f"₹{value / 1_000_000_000:.2f}B"
            elif value >= 1_000_000:
                return f"₹{value / 1_000_000:.2f}M"
            else:
                return f"₹{value:,.0f}"

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Market Cap",
                format_large_number(fundamental_data["Market Cap"])
            )

        with col2:
            pe = fundamental_data["P/E Ratio"]
            st.metric(
                "P/E Ratio",
                f"{pe:.2f}" if pe is not None else "N/A"
            )

        with col3:
            eps = fundamental_data["EPS"]
            st.metric(
                "EPS",
                f"₹{eps:.2f}" if eps is not None else "N/A"
            )

        with col4:
            dividend = fundamental_data["Dividend Yield"]
            st.metric(
                "Dividend Yield",
                f"{dividend * 100:.2f}%" if dividend is not None else "N/A"
            )

        col5, col6, col7, col8 = st.columns(4)

        with col5:
            pb = fundamental_data["Price-to-Book"]
            st.metric(
                "Price-to-Book",
                f"{pb:.2f}" if pb is not None else "N/A"
            )

        with col6:
            st.metric(
                "Revenue",
                format_large_number(fundamental_data["Revenue"])
            )

        with col7:
            st.metric(
                "Net Profit",
                format_large_number(fundamental_data["Profit"])
            )

        with col8:
            de = fundamental_data["Debt-to-Equity"]
            st.metric(
                "Debt-to-Equity",
                f"{de:.2f}" if de is not None else "N/A"
            )

        roe = fundamental_data["ROE"]

        if roe is not None:
            st.metric(
                "Return on Equity (ROE)",
                f"{roe * 100:.2f}%"
            )

        st.caption(
            "Fundamental metrics are retrieved from Yahoo Finance and may vary based on the latest available company filings."
        )

    # PRICE ALERT
    # ======================================

    st.subheader("🔔 Price Alert")
    alert_stocks = {
        "Reliance Industries": "RELIANCE.NS",
        "TCS": "TCS.NS",
        "Infosys": "INFY.NS",
        "HDFC Bank": "HDFCBANK.NS",
        "ICICI Bank": "ICICIBANK.NS",
        "State Bank of India": "SBIN.NS",
        "ITC": "ITC.NS",
        "Wipro": "WIPRO.NS",
        "Tata Motors": "TATAMOTORS.NS",
        "Bharti Airtel": "BHARTIARTL.NS"
    }
    alert_col1, alert_col2, alert_col3 = st.columns(3)

    with alert_col1:
        alert_stock = st.selectbox(
            "Select Stock",
            list(alert_stocks.keys()),
            key="alert_stock"
        )

    with alert_col2:
        alert_target = st.number_input(
            "Target Price (₹)",
            min_value=0.0,
            step=10.0,
            value=1000.0,
            key="alert_target"
        )

    with alert_col3:
        alert_condition = st.selectbox(
            "Alert When",
            ["🔼 Price goes above target", "🔽 Price goes below target"],
            key="alert_condition"
        )

    alert_symbol = alert_stocks[alert_stock]

    alert_data = yf.download(
        alert_symbol,
        period="5d",
        progress=False
    )

    if not alert_data.empty:
        alert_close = alert_data["Close"]

        if hasattr(alert_close, "columns"):
            alert_close = alert_close.iloc[:, 0]

        alert_close = alert_close.dropna()

        if not alert_close.empty:
            alert_current_price = float(alert_close.iloc[-1])

            if "above" in alert_condition:
                alert_triggered = alert_current_price >= alert_target
            else:
                alert_triggered = alert_current_price <= alert_target

            st.write(
                f"Current Price: **₹{alert_current_price:.2f}**"
            )

            if alert_triggered:
                st.error(
                    f"🚨 Price Alert Triggered! "
                    f"{alert_stock} has reached your target of ₹{alert_target:.2f}."
                )
            else:
                st.info(
                    f"🔔 Alert Active — waiting for "
                    f"{'₹' + format(alert_target, '.2f') + ' or above' if 'above' in alert_condition else '₹' + format(alert_target, '.2f') + ' or below'}."
                )            
elif page == "🔍 Compare Stocks":

    st.markdown(
    """
    <div style="padding: 10px 0 25px 0;">
        <h1 style="margin-bottom: 5px;">
            📊 Stock Comparison
        </h1>
        <p style="font-size: 18px; color: #9aa4b2;">
            Compare performance, volatility, momentum, and risk
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
    st.write(
        "Compare the performance and risk of multiple stocks."
    )

    stock_options = {
        "Reliance Industries": "RELIANCE.NS",
        "TCS": "TCS.NS",
        "Infosys": "INFY.NS",
        "HDFC Bank": "HDFCBANK.NS",
        "ICICI Bank": "ICICIBANK.NS",
        "State Bank of India": "SBIN.NS",
        "ITC": "ITC.NS",
        "Wipro": "WIPRO.NS",
        "Tata Motors": "TATAMOTORS.NS",
        "Bharti Airtel": "BHARTIARTL.NS"
    }

    stock_names = list(stock_options.keys())

    col1, col2 = st.columns(2)

    with col1:
        stock_1 = st.selectbox(
            "Stock 1",
            stock_names,
            index=0
        )

    with col2:
        stock_2 = st.selectbox(
            "Stock 2",
            stock_names,
            index=1
        )

    col3, col4 = st.columns(2)

    with col3:
        stock_3 = st.selectbox(
            "Stock 3 (Optional)",
            ["None"] + stock_names
        )

    with col4:
        stock_4 = st.selectbox(
            "Stock 4 (Optional)",
            ["None"] + stock_names
        )

    selected_names = [
        stock_1,
        stock_2
    ]

    if stock_3 != "None":
        selected_names.append(stock_3)

    if stock_4 != "None":
        selected_names.append(stock_4)

    selected_symbols = [
        stock_options[name]
        for name in selected_names
    ]

    if st.button(
        "📊 Compare Selected Stocks",
        use_container_width=True
    ):

        comparison_results = []
        normalized_data = {}

        with st.spinner("Analyzing selected stocks..."):

            for name, symbol in zip(
                selected_names,
                selected_symbols
            ):

                data = yf.download(
                    symbol,
                    period="1y",
                    progress=False,
                    auto_adjust=False
                )

                if data.empty:
                    continue

                close = data["Close"]

                if hasattr(close, "columns"):
                    close = close.iloc[:, 0]
                close = close.dropna()


                normalized_data[name] = (
                    close / close.iloc[0]
                ) * 100


                # One-year return
                total_return = (
                    (close.iloc[-1] / close.iloc[0]) - 1
                ) * 100

                # Volatility
                returns = close.pct_change().dropna()

                volatility = (
                    returns.std()
                    * (252 ** 0.5)
                    * 100
                )
                # Risk Score
                if volatility < 15:
                    risk_score = "Low"
                elif volatility < 30:
                    risk_score = "Moderate"
                elif volatility < 45:
                    risk_score = "High"
                else:
                    risk_score = "Very High"
                # RSI
                delta = close.diff()

                gains = delta.clip(lower=0)
                losses = -delta.clip(upper=0)

                avg_gain = gains.rolling(14).mean()
                avg_loss = losses.rolling(14).mean()

                rs = avg_gain / avg_loss

                rsi = 100 - (
                    100 / (1 + rs)
                )

                current_rsi = float(rsi.iloc[-1])

                comparison_results.append({
                    "Stock": name,
                    "1-Year Return": f"{float(total_return):.2f}%",
                    "Volatility": f"{float(volatility):.2f}%",
                    "RSI": f"{current_rsi:.2f}",
                    "Risk Level": risk_score             
                })

                # Normalize prices to 100
                normalized = (
                    close / close.iloc[0]
                ) * 100

                normalized_data[name] = normalized

        if comparison_results:

            st.subheader("📊 Comparison Summary")

            st.dataframe(
                comparison_results,
                use_container_width=True,
                hide_index=True
            )

            st.subheader(
                "📈 1-Year Performance Comparison"
            )

            comparison_fig = go.Figure()

            for name, values in normalized_data.items():

                comparison_fig.add_trace(
                    go.Scatter(
                        x=values.index,
                        y=values,
                        mode="lines",
                        name=name
                    )
                )

            comparison_fig.update_layout(
                template="plotly_dark",
                xaxis_title="Date",
                yaxis_title="Normalized Price",
                hovermode="x unified",
                height=500
            )

            st.plotly_chart(
                comparison_fig,
                use_container_width=True
            )

        else:

            st.error(
                "Unable to retrieve data for the selected stocks."
            )


elif page == "🔎 Stock Screener":

    st.markdown(
        """
        <div style="padding: 10px 0 25px 0;">
            <h1 style="margin-bottom: 5px;">
                🔎 Stock Screener
            </h1>
            <p style="font-size: 18px; color: #9aa4b2;">
                Filter stocks using fundamental and technical metrics
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write(
        "Find stocks that match your selected investment criteria."
    )

    screener_stocks = {
        "Reliance Industries": "RELIANCE.NS",
        "TCS": "TCS.NS",
        "Infosys": "INFY.NS",
        "HDFC Bank": "HDFCBANK.NS",
        "ICICI Bank": "ICICIBANK.NS",
        "State Bank of India": "SBIN.NS",
        "ITC": "ITC.NS",
        "Wipro": "WIPRO.NS",
        "Tata Motors": "TATAMOTORS.NS",
        "Bharti Airtel": "BHARTIARTL.NS"
    }

    st.subheader("🎯 Screening Criteria")

    col1, col2, col3 = st.columns(3)

    with col1:
        max_pe = st.number_input(
            "Maximum P/E Ratio",
            min_value=0.0,
            value=50.0,
            step=5.0
        )

    with col2:
        min_roe = st.number_input(
            "Minimum ROE (%)",
            min_value=0.0,
            value=10.0,
            step=5.0
        )

    with col3:
        min_dividend = st.number_input(
            "Minimum Dividend Yield (%)",
            min_value=0.0,
            value=0.0,
            step=1.0
        )

    if st.button("🔍 Screen Stocks", use_container_width=True):

        results = []

        with st.spinner("Analyzing stocks..."):

            for name, stock_symbol in screener_stocks.items():

                try:
                    info = yf.Ticker(stock_symbol).info

                    pe = info.get("trailingPE")
                    roe = info.get("returnOnEquity")
                    dividend = info.get("dividendYield")

                    if pe is None:
                        continue

                    roe_percent = roe * 100 if roe is not None else 0
                    dividend_percent = dividend * 100 if dividend is not None else 0

                    if (
                        pe <= max_pe
                        and roe_percent >= min_roe
                        and dividend_percent >= min_dividend
                    ):
                        results.append({
                            "Stock": name,
                            "P/E": round(pe, 2),
                            "ROE": f"{roe_percent:.2f}%",
                            "Dividend Yield": f"{dividend_percent:.2f}%"
                        })

                except Exception:
                    continue

        st.subheader("📋 Screening Results")

        if results:
            st.dataframe(
                results,
                use_container_width=True,
                hide_index=True
            )

            st.success(
                f"Found {len(results)} stock(s) matching your criteria."
            )

        else:
            st.info(
                "No stocks matched your selected criteria."
            )


elif page == "🧪 Backtesting":

    st.markdown(
        """
        <div style="padding: 10px 0 25px 0;">
            <h1 style="margin-bottom: 5px;">
                🧪 Backtesting
            </h1>
            <p style="font-size: 18px; color: #9aa4b2;">
                Test trading strategies against historical market data
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write(
        "Simulate how a trading strategy would have performed using historical prices."
    )

    st.subheader("⚙️ Backtest Settings")

    col1, col2 = st.columns(2)

    with col1:
        backtest_ticker = st.text_input(
            "Stock Symbol",
            value="RELIANCE.NS",
            help="Example: RELIANCE.NS, TCS.NS, INFY.NS"
        )

    with col2:
        backtest_period = st.selectbox(
            "Historical Period",
            ["1y", "2y", "5y", "10y"],
            index=2
        )

    initial_capital = st.number_input(
        "Initial Capital (₹)",
        min_value=1000.0,
        value=100000.0,
        step=10000.0
    )

    st.info(
        "Strategy: Buy when the 50-day SMA crosses above the 200-day SMA "
        "and sell when it crosses below."
    )

    if st.button("🚀 Run Backtest", use_container_width=True):

        with st.spinner("Running historical backtest..."):

            backtest_data = yf.download(
                backtest_ticker,
                period=backtest_period,
                progress=False,
                auto_adjust=False
            )

        if backtest_data.empty:
            st.error("No historical data found. Please check the stock symbol.")

        else:
            backtest_close = backtest_data["Close"]

            if hasattr(backtest_close, "columns"):
                backtest_close = backtest_close.iloc[:, 0]

            backtest_close = backtest_close.dropna()

            if len(backtest_close) < 200:
                st.warning(
                    "Not enough historical data for a 200-day SMA strategy."
                )

            else:
                sma_50 = backtest_close.rolling(50).mean()
                sma_200 = backtest_close.rolling(200).mean()

                position = (sma_50 > sma_200).astype(int)

                daily_returns = backtest_close.pct_change().fillna(0)

                strategy_returns = position.shift(1).fillna(0) * daily_returns

                equity_curve = (
                    initial_capital *
                    (1 + strategy_returns).cumprod()
                )

                final_value = float(equity_curve.iloc[-1])

                total_return = (
                    (final_value / initial_capital) - 1
                ) * 100

                st.subheader("📊 Backtest Results")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Initial Capital",
                        f"₹{initial_capital:,.2f}"
                    )

                with col2:
                    st.metric(
                        "Final Portfolio Value",
                        f"₹{final_value:,.2f}"
                    )

                with col3:
                    st.metric(
                        "Total Return",
                        f"{total_return:.2f}%"
                    )

                # ======================================
                # BACKTEST PERFORMANCE METRICS
                # ======================================

                years = (
                    backtest_close.index[-1] - backtest_close.index[0]
                ).days / 365.25

                if years > 0:
                    cagr = (
                        (final_value / initial_capital) ** (1 / years) - 1
                    ) * 100
                else:
                    cagr = 0

                trade_changes = position.diff().fillna(0)

                buy_signals = (trade_changes == 1).sum()
                sell_signals = (trade_changes == -1).sum()

                total_trades = int(
                    buy_signals + sell_signals
                )

                winning_days = (
                    strategy_returns[strategy_returns > 0].count()
                )

                active_days = (
                    strategy_returns[strategy_returns != 0].count()
                )

                if active_days > 0:
                    win_rate = (
                        winning_days / active_days
                    ) * 100
                else:
                    win_rate = 0

                running_peak = equity_curve.cummax()

                drawdown = (
                    (equity_curve - running_peak)
                    / running_peak
                ) * 100

                max_drawdown = drawdown.min()

                annualized_return = strategy_returns.mean() * 252
                annualized_volatility = (
                    strategy_returns.std() * (252 ** 0.5)
                )

                if annualized_volatility != 0:
                    backtest_sharpe = (
                        annualized_return
                        / annualized_volatility
                    )
                else:
                    backtest_sharpe = 0

                st.subheader("📊 Performance Metrics")

                metric1, metric2, metric3, metric4, metric5 = st.columns(5)

                with metric1:
                    st.metric(
                        "CAGR",
                        f"{cagr:.2f}%"
                    )

                with metric2:
                    st.metric(
                        "Trades",
                        total_trades
                    )

                with metric3:
                    st.metric(
                        "Win Rate",
                        f"{win_rate:.2f}%"
                    )

                with metric4:
                    st.metric(
                        "Max Drawdown",
                        f"{max_drawdown:.2f}%"
                    )

                with metric5:
                    st.metric(
                        "Sharpe Ratio",
                        f"{backtest_sharpe:.2f}"
                    )

                st.subheader("📈 Strategy Performance")

                backtest_fig = go.Figure()

                backtest_fig.add_trace(
                    go.Scatter(
                        x=backtest_close.index,
                        y=backtest_close,
                        mode="lines",
                        name="Stock Price"
                    )
                )

                backtest_fig.add_trace(
                    go.Scatter(
                        x=sma_50.index,
                        y=sma_50,
                        mode="lines",
                        name="50-Day SMA"
                    )
                )

                backtest_fig.add_trace(
                    go.Scatter(
                        x=sma_200.index,
                        y=sma_200,
                        mode="lines",
                        name="200-Day SMA"
                    )
                )

                backtest_fig.update_layout(
                    title="SMA Crossover Strategy",
                    xaxis_title="Date",
                    yaxis_title="Price (₹)",
                    template="plotly_dark",
                    height=500
                )

                st.plotly_chart(
                    backtest_fig,
                    use_container_width=True
                )

                st.subheader("💰 Portfolio Equity Curve")

                equity_fig = go.Figure()

                equity_fig.add_trace(
                    go.Scatter(
                        x=equity_curve.index,
                        y=equity_curve,
                        mode="lines",
                        name="Portfolio Value"
                    )
                )

                equity_fig.update_layout(
                    title="Backtested Portfolio Value",
                    xaxis_title="Date",
                    yaxis_title="Portfolio Value (₹)",
                    template="plotly_dark",
                    height=450
                )

                st.plotly_chart(
                    equity_fig,
                    use_container_width=True
                )

elif page == "💼 Portfolio":

    st.markdown(
    """
    <div style="padding: 10px 0 25px 0;">
        <h1 style="margin-bottom: 5px;">
            💼 My Portfolio
        </h1>
        <p style="font-size: 18px; color: #9aa4b2;">
            Track holdings, performance, allocation, and portfolio risk
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
    st.write(
        "Track your holdings, portfolio value and overall performance."
    )

    # ==========================================
    # STOCK OPTIONS
    # ==========================================

    portfolio_options = {
        "Reliance Industries": "RELIANCE.NS",
        "TCS": "TCS.NS",
        "Infosys": "INFY.NS",
        "HDFC Bank": "HDFCBANK.NS",
        "ICICI Bank": "ICICIBANK.NS",
        "State Bank of India": "SBIN.NS",
        "ITC": "ITC.NS",
        "Wipro": "WIPRO.NS",
        "Tata Motors": "TATAMOTORS.NS",
        "Bharti Airtel": "BHARTIARTL.NS"
    }

    # ==========================================
    # ADD HOLDING
    # ==========================================

    st.subheader("➕ Add Holding")

    col1, col2, col3 = st.columns(3)

    with col1:

        selected_stock = st.selectbox(
            "Select Stock",
            list(portfolio_options.keys())
        )

    with col2:

        quantity = st.number_input(
            "Quantity",
            min_value=1,
            value=1,
            step=1
        )

    with col3:

        buy_price = st.number_input(
            "Buy Price (₹)",
            min_value=0.01,
            value=100.0,
            step=0.01
        )

    if st.button(
        "➕ Add Holding",
        use_container_width=True
    ):

        add_holding(
            selected_stock,
            portfolio_options[selected_stock],
            quantity,
            buy_price
        )

        st.success(
            f"{selected_stock} added to your portfolio!"
        )

        st.rerun()

    # ==========================================
    # GET HOLDINGS
    # ==========================================

    holdings = get_holdings()

    if not holdings:

        st.info(
            "Your portfolio is empty. Add your first holding above."
        )

    else:

        st.divider()

        st.subheader("📊 Your Holdings")

        total_invested = 0
        total_current = 0

        allocation_names = []
        allocation_values = []
        
        performance_data = []
        # ======================================
        # DISPLAY HOLDINGS
        # ======================================

        for holding in holdings:

            holding_id = holding[0]
            name = holding[1]
            symbol = holding[2]
            quantity = holding[3]
            buy_price = holding[4]

            data = yf.download(
                symbol,
                period="5d",
                progress=False,
                auto_adjust=False
            )

            if data.empty:

                st.warning(
                    f"Could not retrieve data for {name}."
                )

                continue

            close = data["Close"]

            if hasattr(close, "columns"):
                close = close.iloc[:, 0]
            close = close.dropna()
            current_price = float(
                close.iloc[-1]
            )

            invested = quantity * buy_price

            current_value = (
                quantity * current_price
            )

            profit_loss = (
                current_value - invested
            )

            return_percentage = (
                profit_loss / invested
            ) * 100

            total_invested += invested
            total_current += current_value

            allocation_names.append(name)
            allocation_values.append(current_value)
            
            performance_data.append({
                "name": name,
                "return": return_percentage
            })
            # ==================================
            # HOLDING DISPLAY
            # ==================================

            st.markdown(f"### {name}")

            h1, h2, h3, h4 = st.columns(4)

            h1.metric(
                "Quantity",
                quantity
            )

            h2.metric(
                "Current Price",
                f"₹{current_price:,.2f}"
            )

            h3.metric(
                "Current Value",
                f"₹{current_value:,.2f}"
            )

            h4.metric(
                "P&L",
                f"₹{profit_loss:,.2f}",
                f"{return_percentage:.2f}%"
            )

            if st.button(
                f"🗑️ Remove {name}",
                key=f"remove_{holding_id}"
            ):

                delete_holding(holding_id)

                st.success(
                    f"{name} removed from your portfolio."
                )

                st.rerun()

            st.divider()

        # ======================================
        # PORTFOLIO SUMMARY
        # ======================================
        # ======================================
        # PORTFOLIO DIVERSIFICATION
        # ======================================

        if total_current > 0 and allocation_values:
            largest_holding = max(allocation_values)
            concentration = (
                largest_holding / total_current
            ) * 100

            if concentration <= 40:
                diversification_status = "🟢 Well Diversified"
            elif concentration <= 60:
                diversification_status = "🟡 Moderately Concentrated"
            else:
                diversification_status = "🔴 Highly Concentrated"

            st.subheader("🛡️ Portfolio Diversification")

            d1, d2 = st.columns(2)

            d1.metric(
                "Largest Holding",
                f"{concentration:.1f}%"
            )

            d2.metric(
                "Diversification",
                diversification_status
            )
        if total_invested > 0:

            total_profit_loss = (
                total_current - total_invested
            )

            total_return = (
                total_profit_loss
                / total_invested
            ) * 100

            st.subheader("💰 Portfolio Summary")

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Invested Value",
                f"₹{total_invested:,.2f}"
            )

            c2.metric(
                "Current Value",
                f"₹{total_current:,.2f}"
            )

            c3.metric(
                "Total P&L",
                f"₹{total_profit_loss:,.2f}"
            )

            c4.metric(
                "Total Return",
                f"{total_return:.2f}%"
            )

            # ==================================
            # PORTFOLIO ALLOCATION
            # ==================================
        # PORTFOLIO PERFORMANCE ANALYTICS

        if performance_data:
            best_holding = max(
                performance_data,
                key=lambda x: x["return"]
            )

            worst_holding = min(
                performance_data,
                key=lambda x: x["return"]
            )

            st.subheader("📊 Portfolio Performance")

            p1, p2, p3 = st.columns(3)

            p1.metric(
                "🏆 Best Performer",
                best_holding["name"],
                f'{best_holding["return"]:.2f}%'
            )

            p2.metric(
                "📉 Worst Performer",
                worst_holding["name"],
                f'{worst_holding["return"]:.2f}%'
            )
            p3.metric(
                "📦 Holdings",
                len(performance_data)
            )

            if allocation_values:

                st.subheader(
                    "🥧 Portfolio Allocation"
                )

                allocation_fig = go.Figure(
                    data=[
                        go.Pie(
                            labels=allocation_names,
                            values=allocation_values,
                            hole=0.45
                        )
                    ]
                )

                allocation_fig.update_layout(
                    template="plotly_dark",
                    height=450
                )

                st.plotly_chart(
                    allocation_fig,
                    use_container_width=True
                )
