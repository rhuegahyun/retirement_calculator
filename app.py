import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# mpl.rcParams['font.family'] = 'NanumGothic'
plt.rc('axes', unicode_minus=False)

def format_currency(value):
    if value >= 100000000:
        return f"{round(value/100000000, 1)} 억"
    elif value >= 10000000:
        return f"{round(value/10000):,} 만"
    elif value >= 1000:
        return f"{round(value):,} 원"
    else:
        return f"{int(value)} 원"

def simulate(seed_money, monthly_invest, annual_invest_increase,
             annual_return, annual_dividend_yield, dividend_growth,
             capital_growth, reinvest_dividend, tax_rate, years):

    result = []
    total_principal = seed_money

    if reinvest_dividend:

        price_per_share = 10000
        shares = seed_money / price_per_share

        for year in range(1, years+1):
            yearly_invest = monthly_invest * 12
            shares += yearly_invest / price_per_share
            total_principal += yearly_invest

            price_per_share *= (1 + capital_growth/100)

            dividend_per_share = price_per_share * (annual_dividend_yield/100)
            dividend = shares * dividend_per_share
            dividend_after_tax = dividend * (1 - tax_rate/100)
            monthly_dividend_after_tax = dividend_after_tax/12

            shares += dividend_after_tax / price_per_share

            annual_dividend_yield *= (1 + dividend_growth/100)

            asset = shares * price_per_share

            result.append({
                "연도": year,
                "월 투자금": monthly_invest,
                "누적 원금": total_principal,
                "총 자산": asset,
                "연 배당금(세후)": dividend_after_tax,
                "월 배당금(세후)": monthly_dividend_after_tax,
                "연 인출액(4%)": asset * 0.04,
                "월 인출액(4%)": asset * 0.04 / 12
            })

            monthly_invest += annual_invest_increase

    else:
        asset = seed_money
        invest = monthly_invest

        for year in range(1, years+1):
            yearly_invest = invest * 12
            asset += yearly_invest
            total_principal += yearly_invest

            asset *= (1 + annual_return/100)

            result.append({
                "연도": year,
                "월 투자금": invest,
                "누적 원금": total_principal,
                "총 자산": asset,
                "연 배당금(세후)": 0,
                "월 배당금(세후)": 0,
                "연 인출액(4%)": asset * 0.04,
                "월 인출액(4%)": asset * 0.04 / 12,
            })
            invest += annual_invest_increase

    return pd.DataFrame(result)


st.title("🔥은퇴 자금/배당 재투자 시뮬레이터")

col1, col2 = st.columns(2)

with col1:
    seed_money = st.number_input("현재 순자산 (원)", min_value=0, value=50000000, step=1000000)
    monthly_invest = st.number_input("월 투자금 (원)", min_value=0, value=2000000, step=100000)
    years = st.slider("시뮬레이션 기간 (년)", 1, 50, 20)
with col2:
    annual_return = st.slider("목표 수익률 (%)", 0.0, 20.0, 10.0, step=0.1)
    annual_invest_increase = st.number_input("매년 월 투자금 증가액 (원)", min_value=0, value=100000, step=100000)
    reinvest_dividend = st.checkbox("배당 재투자", value=True)


if reinvest_dividend:
    st.markdown("### 📈 배당 관련 설정")
    st.caption("👉 배당금 전액 재투자로 가정합니다")
    st.caption("👉 본 계산기는 물가 상승률을 반영하지 않습니다")

    initial_price = st.number_input("초기 주가 (원)", min_value=0.0, value= 50000.0, step=100.0)
    annual_dividend_yield = st.number_input("연 배당률 (%)", min_value=0.0, max_value=20.0, value=5.0, step=0.1)
    dividend_growth = st.number_input("배당 성장률 (%)", min_value=0.0, max_value=20.0, value=5.0, step=0.1)
    capital_growth = st.number_input("배당주 시가 성장률 (%)", min_value=0.0, max_value=20.0, value=5.0, step=0.1)
    tax_rate = st.number_input("배당 과세율 (%)", min_value=0.0, max_value=50.0, value=15.4, step=0.1)
else:
    initial_price = 50000
    annual_dividend_yield = 0
    dividend_growth = 0
    capital_growth = annual_return
    tax_rate = 0


df = simulate(seed_money, monthly_invest, annual_invest_increase,
              annual_return, annual_dividend_yield, dividend_growth,
              capital_growth, reinvest_dividend, tax_rate, years)

df_fmt = df.copy()
for col in ["누적 원금", "총 자산", "연 배당금(세후)", "월 배당금(세후)", "연 인출액(4%)", "월 인출액(4%)"]:
    df_fmt[col] = df[col].apply(format_currency)

st.subheader("📊 연도별 시뮬레이션 결과")
st.dataframe(df_fmt)

st.download_button(
    label="결과 다운로드 (CSV)",
    data=df.to_csv(index=False).encode("utf-8-sig"),
    file_name="retirement_simulation.csv",
    mime="text/csv"
)


fig, ax = plt.subplots(figsize=(10, 5))
bar_width = 0.35
x = df["연도"]

ax.bar(x - 0.2, df["총 자산"], width=bar_width, label="Total Asset")
ax.bar(x + 0.2, df["연 인출액(4%)"], width=bar_width, label="Annual withdrawal of 4%")

ax.set_xlabel("Year")

def won_formatter(x, pos):
    if x >= 1e9:
        return f"{x/1e9:.1f} B"
    elif x >= 1e6:
        return f"{int(x/1e6)} M"
    else:
        return f"{int(x)}"

ax.yaxis.set_major_formatter(mticker.FuncFormatter(won_formatter))
ax.set_ylabel("Won")
ax.legend()
st.pyplot(fig)

st.markdown("---"*10)
st.markdown("출처: https://github.com/rhuegahyun")
st.markdown("Linkedin: https://www.linkedin.com/in/gahyeon-ryu-3613a6225")
