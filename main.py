import re

import pandas as pd
import plotly.express as px
import streamlit as st


# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")
st.write("1년간 박스오피스 10위권에 든 영화 데이터를 이용해 영화들의 분포와 관계를 살펴봅니다.")


# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜 열: 여덟 자리 숫자를 실제 날짜로 변환
    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str),
        format="%Y%m%d",
        errors="coerce",
    )

    # 숫자형 열 변환
    numeric_columns = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # genre의 여러 장르 중 첫 번째 장르만 사용
    # 실제 데이터에는 |와 /가 모두 사용된 행이 있어 둘 다 처리
    def get_first_genre(value):
        if pd.isna(value):
            return "알 수 없음"

        text = str(value).strip()
        if not text:
            return "알 수 없음"

        first_genre = re.split(r"[|/]", text)[0].strip()
        return first_genre if first_genre else "알 수 없음"

    df["first_genre"] = df["genre"].apply(get_first_genre)

    return df


try:
    df = load_data()
except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.code(str(e))
    st.stop()


# --------------------------------------------------
# 데이터 개요
# --------------------------------------------------
with st.expander("데이터 확인하기"):
    st.write(f"총 영화 수: **{len(df):,}편**")
    st.dataframe(
        df[
            [
                "movieCd",
                "movieNm",
                "openDt",
                "genre",
                "nation",
                "first_scrn",
                "first_show",
                "first_week_audi",
                "total_audi",
                "days_in_top10",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


# ==================================================
# 그래프 1. 장르별 영화 편수
# ==================================================
st.markdown("---")
st.header("그래프 1. 장르별 영화 편수")

genre_counts = (
    df["first_genre"]
    .value_counts()
    .rename_axis("장르")
    .reset_index(name="영화 편수")
)

fig = px.pie(
    genre_counts,
    names="장르",
    values="영화 편수",
    hole=0.55,
    title="장르별 영화 편수",
)

# 마우스를 올렸을 때 편수와 비율이 보이도록 설정
fig.update_traces(
    textinfo="label",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    ),
)

fig.update_layout(
    legend_title_text="장르",
    margin=dict(l=20, r=20, t=70, b=20),
)

st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# 그래프 아래 사용자 작성 공간
# --------------------------------------------------
st.markdown("### 이 그래프로 알 수 있는 것")
st.text_area(
    "설명 문장을 직접 작성하세요.",
    value="",
    placeholder="이 그래프로 알 수 있는 것을 한 문장으로 작성해 보세요.",
    height=100,
    key="graph1_explanation",
    label_visibility="collapsed",
)


# ==================================================
# 그래프 2. 장르별 영화 트리맵
# ==================================================
st.markdown("---")
st.header("그래프 2. 장르별 영화 트리맵")

st.write("각 장르 안에 영화가 들어 있으며, 영화 칸의 크기는 총 관객 수에 비례합니다.")

# 영화명이 중복되는 경우를 대비해 장르 + 영화명 기준으로 집계
treemap_data = (
    df[["first_genre", "movieNm", "total_audi"]]
    .dropna(subset=["movieNm", "total_audi"])
    .copy()
)

# 총 관객이 0 이하인 데이터는 트리맵의 크기 계산에 사용할 수 없으므로 제외
treemap_data = treemap_data[treemap_data["total_audi"] > 0]

# 같은 영화가 여러 행에 있을 경우 총 관객을 합산
treemap_data = (
    treemap_data
    .groupby(["first_genre", "movieNm"], as_index=False)["total_audi"]
    .sum()
)

fig2 = px.treemap(
    treemap_data,
    path=[
        px.Constant("전체"),
        "first_genre",
        "movieNm",
    ],
    values="total_audi",
    title="장르별 영화 총 관객 트리맵",
)

# 마우스를 올렸을 때 영화명과 총 관객이 보이도록 설정
fig2.update_traces(
    customdata=treemap_data["total_audi"],
    hovertemplate=(
        "<b>%{label}</b><br>"
        "총 관객: %{value:,.0f}명"
        "<extra></extra>"
    ),
    root_color="lightgrey",
)

fig2.update_layout(
    margin=dict(l=10, r=10, t=70, b=10),
)

st.plotly_chart(fig2, use_container_width=True)


# --------------------------------------------------
# 그래프 2 아래 사용자 작성 공간
# --------------------------------------------------
st.markdown("### 이 그래프로 알 수 있는 것")
st.text_area(
    "설명 문장을 직접 작성하세요.",
    value="",
    placeholder="이 그래프로 알 수 있는 것을 한 문장으로 작성해 보세요.",
    height=100,
    key="graph2_explanation",
    label_visibility="collapsed",
)


# ==================================================
# 다음 그래프를 추가할 공간
# ==================================================
st.markdown("---")
st.header("다음 그래프")
st.info("이 구역부터 앞으로 새로운 분포·관계 그래프를 추가하면 됩니다.")
