import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide")
st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    # 1년간 박스오피스 10위권에 든 영화 216편의 요약표를 불러옵니다
    df = pd.read_csv(DATA_URL)
    # 장르가 세로막대 기호(|)로 여러 개 적힌 영화는 첫 번째 장르만 씁니다
    df["장르"] = df["genre"].str.split("|").str[0]
    return df


df = load_data()

# ── 그래프 1. 장르별 영화 편수 도넛 ──
st.header("1. 장르별 영화 편수 (도넛)")
genre_count = df["장르"].value_counts().reset_index()
genre_count.columns = ["장르", "편수"]

fig = px.pie(
    genre_count,
    names="장르",
    values="편수",
    hole=0.45,  # 가운데 구멍을 뚫어 도넛 모양으로
)
# 조각에 마우스를 올리면 편수와 비율이 보이게 합니다
fig.update_traces(hovertemplate="%{label}<br>%{value}편 (%{percent})<extra></extra>")
st.plotly_chart(fig, width="stretch")

# '이 그래프로 알 수 있는 것' 한 문장을 적는 자리
st.text_input("이 그래프로 알 수 있는 것", key="note1")

st.divider()
# 앞으로 그래프를 계속 추가할 구역
st.header("2. (다음 그래프를 여기에 추가)")

# ── 그래프 2. 장르 안의 영화 (트리맵) ──
st.header("2. 장르 안의 영화 (트리맵)")
fig2 = px.treemap(df, path=["장르", "movieNm"], values="total_audi",
                  hover_data=["total_audi"])
st.plotly_chart(fig2, width="stretch")
st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")

# ── 그래프 3. 총 관객의 분포 (히스토그램) ──
st.header("3. 총 관객의 분포 (히스토그램)")
fig3 = px.histogram(df, x="total_audi", nbins=40)
st.plotly_chart(fig3, width="stretch")
under_1m = (df["total_audi"] < 1_000_000).sum()
best = df.loc[df["total_audi"].idxmax()]
st.write(f"216편 가운데 {under_1m}편이 100만 명 미만입니다. "
         f"가장 많이 본 영화는 {best['movieNm']}({best['total_audi']:,}명)입니다.")
st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")

# ── 그래프 4. 스크린 수와 총 관객 (산점도) ──
st.header("4. 개봉일 스크린 수와 총 관객 (산점도)")
fig4 = px.scatter(df, x="first_scrn", y="total_audi", color="장르",
                  hover_name="movieNm")
st.plotly_chart(fig4, width="stretch")
st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")

# ── 그래프 5. 장르별 총 관객 (박스플롯) ──
st.header("5. 장르별 총 관객 (박스플롯)")
big = df["장르"].value_counts()
big = big[big >= 10].index
fig5 = px.box(df[df["장르"].isin(big)], x="장르", y="total_audi", points="outliers",
              hover_name="movieNm")
st.plotly_chart(fig5, width="stretch")
st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")

# ── 그래프 6. 첫 주 관객을 점 크기로 (버블) ──
st.header("6. 첫 주 관객을 점 크기로 (버블)")
fig6 = px.scatter(df, x="first_scrn", y="total_audi", color="장르",
                  size="first_week_audi", size_max=40, hover_name="movieNm")
st.plotly_chart(fig6, width="stretch")
st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")

# ── 그래프 7. 국가에서 장르로 (선버스트) ──
st.header("7. 국가에서 장르로 (선버스트)")
df["대표국가"] = df["nation"].str.split("|").str[0]
counted = (df.groupby(["대표국가", "장르"], as_index=False)
             .agg(편수=("movieNm", "count")))
fig7 = px.sunburst(counted, path=["대표국가", "장르"], values="편수")
st.plotly_chart(fig7, width="stretch")
st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")
