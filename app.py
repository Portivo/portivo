import streamlit as st
import plotly.express as px
import pandas as pd
import yfinance as yf


col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&display=swap');
    </style>
    <h1 style='text-align: center; 
    font-family: "DM Serif Display", serif; 
    font-size: 3rem; 
    color: #1B3A6B; 
    letter-spacing: -0.01em;
    margin-bottom: 0;'>
        Portivo
    </h1>
""", unsafe_allow_html=True)
st.subheader("Portfolio Correlation & Risk Analysis", text_alignment='center')

st.markdown("""
    <div style='text-align: center; background-color: #F0F4FF; 
    padding: 10px; border-radius: 8px; margin-bottom: 20px;'>
        🚀 Portivo is in early development. 
        <a href='https://getportivo.com' target='_blank' style='color: #2E6BE6; font-weight: bold;'>
        Join the waitlist</a> to get early access.
    </div>
""", unsafe_allow_html=True)

# Ticker input:
st.markdown("<p style='text-align: center; color: #666;'>Enter stock tickers separated by commas</p>", unsafe_allow_html=True)
st.markdown("""
    <style>
    .stTextInput > label { display: none; }
    .stTextInput { margin-top: -30px; }
    </style>
""", unsafe_allow_html=True)
ticker_input = st.text_input(
    "",
    placeholder='For example: AAPL, MSFT, ASML.AS'
)

if ticker_input:
    tickers = [t.strip().upper() for t in ticker_input.split(',')]

    with st.spinner("Downloading price data..."):
        df = yf.download(tickers, period = '1y', auto_adjust=True, progress=False)
        valid_tickers = [t for t in tickers if t in df.Close.columns]
        invalid_tickers = [t for t in tickers if t not in df.Close.columns]
    
        if invalid_tickers:
            st.warning(f"Could not find data for: {', '.join(invalid_tickers)}. Continuing with valid tickers.")
    
        if len(valid_tickers) < 2:
            st.error("Please enter at least 2 valid tickers to calculate correlation.")
            st.stop()
        
    if df.empty:
        st.error("No data found. Please check your tickers and try again.")
    else:
        st.success(f"Loaded data for {len(tickers)} ticker(s)")

    # Correlation heatmap:
        returns = df.Close.pct_change().dropna()
        corr = returns.corr()

        st.subheader('Correlation Matrix')
        st.caption('How closely your holdings move together, lower correlation is better for risk diversification')

        htmap=px.imshow(
        corr,
        color_continuous_scale=[
            [0, 'black'],
            [0.25, 'purple'],
            [0.5, 'lightgrey'],
            [0.75, 'salmon'],
            [1, 'darkred']
        ],
        zmax = 1,
        zmin = -1,
        text_auto='.2f'
        )
        htmap.update_layout(
        xaxis_title='',
        yaxis_title='',
        coloraxis_colorbar=dict(
        title='Correlation'
        ),
        width=600,
        height=600
    )

        htmap.update_traces(
        hovertemplate='%{x} / %{y}<br>Correlation: %{z:.2f}<extra></extra>',
    )

        htmap.update_xaxes(side='bottom')

        st.plotly_chart(htmap, use_container_width=True)
        st.info("💡 **Key insight:** Holdings with correlation above 0.7 move closely together and offer limited risk mitigation.")

        # Volatility table:
        st.subheader("Annualised Volatility")
        st.caption("How much each holding's price typically fluctuates over a year.")

        TRADING_DAYS = 252
        volatility = (returns.std() * (TRADING_DAYS ** 0.5)).round(4)

        vol_df = pd.DataFrame({
    'Ticker': volatility.index,
    'Annualised Volatility': (volatility.values * 100).round(2),
})

        vol_df = vol_df.sort_values('Annualised Volatility', ascending=False).reset_index(drop=True)

        def colour_volatility(val):
            if val < 20:
                return 'background-color: #d4edda; color: #155724'  # green
            elif val < 35:
                return 'background-color: #fff3cd; color: #856404'  # yellow
            else:
                return 'background-color: #f8d7da; color: #721c24'  # red

        styled_vol = (vol_df.style
            .map(colour_volatility, subset=['Annualised Volatility'])
            .format({'Annualised Volatility': '{:.2f}%'})
)


        st.dataframe(styled_vol, use_container_width=True, hide_index=True)
        st.info("💡 **Key insight:** Higher volatility means larger price swings. A portfolio with many high-volatility holdings generally carries more risk.")
st.divider()
st.markdown("**Please help improve portivo.** [Share your feedback here](https://docs.google.com/forms/d/e/1FAIpQLScfPLqzHgZYjl7mJo7mmhoMHDUgKPkr0eM6_AT1OhCO1i21yg/viewform?usp=dialog)", text_alignment='center')