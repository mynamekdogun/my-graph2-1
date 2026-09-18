import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide"
)

# 제목 설정
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown("---")


# 데이터 로드 및 강화된 전처리 함수
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)

    # 문자열 공백 제거 및 장르 추출
    df["genre"] = (
        df["genre"].astype(str).str.split("|").str[0].str.strip()
    )
    df["movieNm"] = df["movieNm"].astype(str).str.strip()
    df["nation"] = df["nation"].astype(str).str.strip()

    # 결측치 및 문자열 'nan' 제거
    df = df[~df["genre"].isin(["nan", "None", ""])]
    df = df[~df["movieNm"].isin(["nan", "None", ""])]

    # 수치형 컬럼 변환 및 결측치 처리
    num_cols = ["total_audi", "first_scrn", "first_week_audi", "days_in_top10"]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


# 데이터 불러오기
try:
    df = load_data()

    # 1. 장르별 영화 편수 (Plotly 도넛 그래프)
    st.subheader("1. 장르별 영화 편수 분포")

    genre_counts = df["genre"].value_counts().reset_index()
    genre_counts.columns = ["genre", "count"]

    fig_donut = px.pie(
        genre_counts,
        values="count",
        names="genre",
        title="장르별 영화 편수 비중",
        hole=0.4,
        hover_data=["count"],
    )

    fig_donut.update_traces(
        hovertemplate="<b>장르: %{label}</b><br>영화 편수: %{value}편<br>비율: %{percent}"
    )

    st.plotly_chart(fig_donut, use_container_width=True)

    st.info(
        "💡 **이 그래프로 알 수 있는 것:** "
        "박스오피스 상위권 영화 중 특정 장르가 차지하는 편수 비중을 한눈에 파악할 수 있으며, 시장을 주도하는 대표 장르를 확인할 수 있습니다."
    )

    st.markdown("---")

    # 2. 장르 및 영화별 총 관객수 (Plotly 트리맵)
    st.subheader("2. 장르 및 영화별 총 관객수 분포 (트리맵)")

    # 관객수가 0보다 큰 데이터만 추출 후 장르-영화명 중복 집계 정제
    df_treemap = (
        df[df["total_audi"] > 0]
        .groupby(["genre", "movieNm"], as_index=False)["total_audi"]
        .sum()
    )

    fig_treemap = px.treemap(
        df_treemap,
        path=["genre", "movieNm"],
        values="total_audi",
        color="genre",
        title="장르 및 영화별 총 관객수 비중",
    )

    fig_treemap.update_traces(
        hovertemplate="<b>%{label}</b><br>총 관객수: %{value:,}명"
    )

    st.plotly_chart(fig_treemap, use_container_width=True)

    st.info(
        "💡 **이 그래프로 알 수 있는 것:** "
        "전체 관객수에서 각 장르가 차지하는 면적 크기를 비교할 수 있고, 장르 내에서 흥행을 견인한 개별 영화와 관객 집중도를 바로 파악할 수 있습니다."
    )

    st.markdown("---")

    # 3. 총 관객수 분포 (Plotly 히스토그램)
    st.subheader("3. 총 관객수 분포 (히스토그램)")

    fig_hist = px.histogram(
        df,
        x="total_audi",
        nbins=20,
        title="영화별 총 관객수 분포",
        labels={"total_audi": "총 관객수"},
    )

    fig_hist.update_traces(
        hovertemplate="<b>관객수 구간: %{x}명</b><br>영화 수: %{y}편"
    )
    fig_hist.update_layout(yaxis_title="영화 수")

    st.plotly_chart(fig_hist, use_container_width=True)

    max_movie_row = df.loc[df["total_audi"].idxmax()]
    max_movie_name = max_movie_row["movieNm"]
    max_movie_audi = int(max_movie_row["total_audi"])

    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** "
        f"대부분의 영화가 하위 관객수 구간에 집중되어 있는 비대칭 분포를 보이며, "
        f"가장 관객 수가 많은 영화는 **'{max_movie_name}'**(총 {max_movie_audi:,}명)입니다."
    )

    st.markdown("---")

    # 4. 개봉일 스크린수와 총 관객수의 관계 (Plotly 산점도)
    st.subheader("4. 개봉일 스크린수 vs 총 관객수 (산점도)")

    fig_scatter = px.scatter(
        df,
        x="first_scrn",
        y="total_audi",
        color="genre",
        hover_name="movieNm",
        title="개봉일 스크린수와 총 관객수의 상관관계",
        labels={
            "first_scrn": "개봉일 스크린수(개)",
            "total_audi": "총 관객수(명)",
            "genre": "장르",
        },
    )

    fig_scatter.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린수: %{x:,}개<br>총 관객수: %{y:,}명"
    )

    st.plotly_chart(fig_scatter, use_container_width=True)

    st.info(
        "💡 **이 그래프로 알 수 있는 것:** "
        "개봉일 스크린수가 많을수록 대체로 총 관객수도 증가하는 양의 상관관계를 보이며, "
        "적은 스크린수 대비 효율적인 흥행 성과를 거둔 영화나 장르별 초기 배급 규모의 차이를 확인할 수 있습니다."
    )

    st.markdown("---")

    # 5. 주요 장르별 총 관객수 분포 (Plotly 상자 그림)
    st.subheader("5. 주요 장르별 총 관객수 분포 (상자 그림)")

    genre_counts_series = df["genre"].value_counts()
    major_genres = genre_counts_series[genre_counts_series >= 10].index
    df_filtered = df[df["genre"].isin(major_genres)]

    fig_box = px.box(
        df_filtered,
        x="genre",
        y="total_audi",
        color="genre",
        hover_name="movieNm",
        points="outliers",
        title="영화 10편 이상 장르의 총 관객수 분포 비교",
        labels={"genre": "장르", "total_audi": "총 관객수(명)"},
    )

    fig_box.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>총 관객수: %{y:,}명"
    )

    st.plotly_chart(fig_box, use_container_width=True)

    st.info(
        "💡 **이 그래프로 알 수 있는 것:** "
        "주요 장르별 관객수의 중앙값과 편차를 비교할 수 있으며, 이상치(상자 밖 점)로 돌출된 초대형 흥행작들의 관객수를 확인할 수 있습니다."
    )

    st.markdown("---")

    # 6. 개봉일 스크린수, 총 관객수, 첫 주 관객수의 관계 (Plotly 버블 차트)
    st.subheader("6. 개봉일 스크린수 vs 총 관객수 vs 첫 주 관객수 (버블 차트)")

    fig_bubble = px.scatter(
        df,
        x="first_scrn",
        y="total_audi",
        size="first_week_audi",
        color="genre",
        hover_name="movieNm",
        size_max=40,
        title="개봉일 스크린수와 총 관객수의 관계 (버블 크기: 첫 주 관객수)",
        labels={
            "first_scrn": "개봉일 스크린수(개)",
            "total_audi": "총 관객수(명)",
            "first_week_audi": "첫 주 관객수(명)",
            "genre": "장르",
        },
        custom_data=["first_week_audi"],
    )

    fig_bubble.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린수: %{x:,}개<br>총 관객수: %{y:,}명<br>첫 주 관객수: %{customdata[0]:,}명"
    )

    st.plotly_chart(fig_bubble, use_container_width=True)

    st.info(
        "💡 **이 그래프로 알 수 있는 것:** "
        "초기 개봉 스크린수 및 첫 주 관객수(버블 크기)가 최종 총 관객수에 미치는 영향을 동시에 비교할 수 있으며, "
        "초반 흥행 화력과 장기 흥행 여부의 관계를 입체적으로 파악할 수 있습니다."
    )

    st.markdown("---")

    # 7. 제작 국가 및 장르별 영화 편수 (Plotly 선버스트 차트)
    st.subheader("7. 제작 국가 및 장르별 영화 편수 (선버스트 차트)")

    nation_genre_counts = (
        df.groupby(["nation", "genre"], as_index=False)
        .size()
        .rename(columns={"size": "movie_count"})
    )
    nation_genre_counts = nation_genre_counts[
        nation_genre_counts["movie_count"] > 0
    ]

    fig_sunburst = px.sunburst(
        nation_genre_counts,
        path=["nation", "genre"],
        values="movie_count",
        title="제작 국가 → 장르 계층별 영화 편수 비중",
    )

    fig_sunburst.update_traces(
        hovertemplate="<b>%{label}</b><br>영화 편수: %{value}편<br>비율: %{percentParent:.1%}"
    )

    st.plotly_chart(fig_sunburst, use_container_width=True)

    st.info(
        "💡 **이 그래프로 알 수 있는 것:** "
        "제작 국가별 영화 수 비중과 함께, 각 국가 내부에서 주로 제작·개봉된 대표 장르의 구성비를 한눈에 파악할 수 있습니다."
    )

    st.markdown("---")

    # 8. 10위권 체류 일수 분포 (히스토그램 + 상자 그림 결합)
    st.subheader("8. 10위권 체류 일수 분포 (히스토그램 & 상자 그림)")

    fig_top10 = px.histogram(
        df,
        x="days_in_top10",
        marginal="box",
        hover_data=["movieNm"],
        title="박스오피스 10위권 체류 일수 분포",
        labels={"days_in_top10": "10위권 체류 일수(일)"},
        nbins=20,
    )

    fig_top10.update_layout(yaxis_title="영화 수")

    st.plotly_chart(fig_top10, use_container_width=True)

    median_days = df["days_in_top10"].median()
    max_stay_row = df.loc[df["days_in_top10"].idxmax()]

    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** "
        f"영화들이 10위권에 머무는 기간의 중앙값은 **약 {median_days:.0f}일**로 대개 2~3주 내외에 몰려 있으며, "
        f"가장 오랫동안 10위권을 지킨 영화는 **'{max_stay_row['movieNm']}'**(총 {int(max_stay_row['days_in_top10'])}일)임을 알 수 있습니다."
    )

    st.markdown("---")

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
