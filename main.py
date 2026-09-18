
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------------------------
# 페이지 설정
# --------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.write(
    "1년간 박스오피스 10위권에 든 영화 가운데 "
    "이 기간에 개봉한 영화 216편의 데이터를 살펴봅니다."
)

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/"
    "modudata/main/data/kobis_movies.csv"
)


@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(DATA_URL)

    # 열 이름 앞뒤 공백 제거
    df.columns = df.columns.str.strip()

    # 날짜를 실제 날짜 형식으로 변환
    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str).str.replace(r"\.0$", "", regex=True),
        format="%Y%m%d",
        errors="coerce"
    )

    # 숫자 열 변환
    numeric_cols = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 장르가 여러 개면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("기타")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
        .replace("", "기타")
    )

    # 국가 결측값 처리
    df["nation"] = (
        df["nation"]
        .fillna("기타")
        .astype(str)
        .str.strip()
        .replace("", "기타")
    )

    # 영화명 결측값 처리
    df["movieNm"] = df["movieNm"].fillna("이름 없음")

    return df


try:
    df = load_data()

    required_cols = [
        "movieCd",
        "movieNm",
        "openDt",
        "genre",
        "nation",
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    missing_cols = [
        col for col in required_cols
        if col not in df.columns
    ]

    if missing_cols:
        st.error(
            "데이터에 필요한 열이 없습니다: "
            + ", ".join(missing_cols)
        )
        st.stop()

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# --------------------------------------------------
# 데이터 확인
# --------------------------------------------------
st.subheader("📋 데이터 미리보기")

st.caption(f"전체 영화 수: {len(df):,}편")

with st.expander("원본 데이터 보기"):
    st.dataframe(df, use_container_width=True)


# --------------------------------------------------
# 공통 함수
# --------------------------------------------------
def explanation_space(section_number):
    """그래프 아래에 사용자가 직접 설명을 적을 공간"""
    st.markdown("**이 그래프로 알 수 있는 것**")

    st.text_area(
        "설명 입력",
        value="",
        placeholder="이 그래프를 보고 알 수 있는 점을 직접 적어 보세요.",
        key=f"explanation_{section_number}",
        label_visibility="collapsed"
    )


def section_title(number, title):
    st.divider()
    st.header(f"그래프 {number}. {title}")


# --------------------------------------------------
# 그래프 1
# 장르별 영화 편수 - 도넛 그래프
# --------------------------------------------------
section_title(1, "장르별 영화 편수")

genre_counts = (
    df.groupby("genre")
    .size()
    .reset_index(name="영화 편수")
    .sort_values("영화 편수", ascending=False)
)

fig1 = px.pie(
    genre_counts,
    names="genre",
    values="영화 편수",
    hole=0.45,
    title="장르별 영화 편수",
    color="genre"
)

fig1.update_traces(
    textposition="inside",
    textinfo="label+percent",
    hovertemplate=(
        "장르: %{label}<br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}"
        "<extra></extra>"
    )
)

fig1.update_layout(
    height=550,
    legend_title_text="장르"
)

st.plotly_chart(fig1, use_container_width=True)

explanation_space(1)


# --------------------------------------------------
# 그래프 2
# 장르 안에 영화가 들어 있는 트리맵
# 칸의 크기 = 총 관객
# --------------------------------------------------
section_title(2, "장르별 영화와 총 관객")

treemap_df = df[
    df["total_audi"].notna()
    & (df["total_audi"] > 0)
].copy()

if not treemap_df.empty:
    fig2 = px.treemap(
        treemap_df,
        path=["genre", "movieNm"],
        values="total_audi",
        color="genre",
        title="장르별 영화 총 관객 트리맵",
        custom_data=["movieNm", "total_audi"]
    )

    fig2.update_traces(
        hovertemplate=(
            "영화명: %{customdata[0]}<br>"
            "총 관객: %{customdata[1]:,.0f}명"
            "<extra></extra>"
        ),
        textinfo="label"
    )

    fig2.update_layout(height=650)

    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("트리맵을 그릴 수 있는 관객 데이터가 없습니다.")

explanation_space(2)


# --------------------------------------------------
# 그래프 3
# 총 관객 히스토그램
# --------------------------------------------------
section_title(3, "총 관객 분포")

hist_df = df[
    df["total_audi"].notna()
    & (df["total_audi"] >= 0)
].copy()

if not hist_df.empty:
    fig3 = px.histogram(
        hist_df,
        x="total_audi",
        nbins=30,
        title="영화별 총 관객 분포",
        labels={
            "total_audi": "총 관객 수(명)",
            "count": "영화 편수"
        },
        hover_data=["movieNm"]
    )

    fig3.update_layout(
        height=500,
        xaxis_title="총 관객 수(명)",
        yaxis_title="영화 편수"
    )

    st.plotly_chart(fig3, use_container_width=True)

    # 가장 관객이 많은 영화
    max_row = hist_df.loc[hist_df["total_audi"].idxmax()]

       # 대부분의 영화가 몰린 구간 계산
    import numpy as np

    hist_counts, hist_edges = np.histogram(
        hist_df["total_audi"],
        bins=30
    )

    max_bin_idx = hist_counts.argmax()

    lower = hist_edges[max_bin_idx]
    upper = hist_edges[max_bin_idx + 1]

    st.info(
        f"📊 가장 많은 영화가 몰린 구간: "
        f"{lower:,.0f}명 ~ {upper:,.0f}명 "
        f"({hist_counts[max_bin_idx]}편)"
    )

    # 가장 관객이 많은 영화
    max_row = hist_df.loc[hist_df["total_audi"].idxmax()]

    st.info(
        f"🏆 가장 관객이 많은 영화: "
        f"{max_row['movieNm']} "
        f"({max_row['total_audi']:,.0f}명)"
    )

    # 히스토그램과 동일한 방식으로 구간 계산
    hist_counts, hist_edges = __import__("numpy").histogram(
        hist_df["total_audi"],
        bins=30
    )

    max_bin_idx = hist_counts.argmax()

    lower = hist_edges[max_bin_idx]
    upper = hist_edges[max_bin_idx + 1]

    st.info(
        f"📊 가장 많은 영화가 몰린 구간: "
        f"{lower:,.0f}명 ~ {upper:,.0f}명 "
        f"({hist_counts[max_bin_idx]}편)"
    )

    st.info(
        f"🏆 가장 관객이 많은 영화: "
        f"{max_row['movieNm']} "
        f"({max_row['total_audi']:,.0f}명)"
    )

else:
    st.warning("총 관객 데이터가 없습니다.")

explanation_space(3)


# --------------------------------------------------
# 그래프 4
# 개봉일 스크린 수와 총 관객 산점도
# 장르별 색상 구분
# --------------------------------------------------
section_title(4, "개봉일 스크린 수와 총 관객의 관계")

scatter_df = df[
    df["first_scrn"].notna()
    & df["total_audi"].notna()
].copy()

if not scatter_df.empty:
    fig4 = px.scatter(
        scatter_df,
        x="first_scrn",
        y="total_audi",
        color="genre",
        hover_name="movieNm",
        hover_data={
            "first_scrn": ":,.0f",
            "total_audi": ":,.0f",
            "genre": True
        },
        title="개봉일 스크린 수와 총 관객",
        labels={
            "first_scrn": "개봉일 스크린 수",
            "total_audi": "총 관객 수(명)",
            "genre": "장르"
        }
    )

    fig4.update_layout(height=600)

    st.plotly_chart(fig4, use_container_width=True)
else:
    st.warning("산점도를 그릴 데이터가 없습니다.")

explanation_space(4)


# --------------------------------------------------
# 그래프 5
# 영화가 10편 이상인 장르의 총 관객 박스플롯
# --------------------------------------------------
section_title(5, "장르별 총 관객 분포 비교")

box_df = df[
    df["total_audi"].notna()
].copy()

# 영화가 10편 이상인 장르만 선택
genre_movie_counts = box_df["genre"].value_counts()

valid_genres = genre_movie_counts[
    genre_movie_counts >= 10
].index

box_df = box_df[
    box_df["genre"].isin(valid_genres)
].copy()

if not box_df.empty:
    fig5 = px.box(
        box_df,
        x="genre",
        y="total_audi",
        color="genre",
        points="outliers",
        hover_name="movieNm",
        hover_data={
            "total_audi": ":,.0f",
            "genre": True
        },
        title="장르별 총 관객 박스플롯",
        labels={
            "genre": "장르",
            "total_audi": "총 관객 수(명)"
        }
    )

    fig5.update_layout(
        height=600,
        showlegend=False
    )

    st.plotly_chart(fig5, use_container_width=True)

    st.caption(
        "상자 밖의 점은 해당 장르의 관객 분포에서 "
        "이상치로 표시된 영화입니다. 점에 마우스를 올리면 "
        "영화명을 확인할 수 있습니다."
    )
else:
    st.warning("영화가 10편 이상인 장르가 없습니다.")

explanation_space(5)


# --------------------------------------------------
# 그래프 6
# 개봉일 스크린 수와 총 관객의 버블 그래프
# 버블 크기 = 첫 주 관객
# --------------------------------------------------
section_title(6, "첫 주 관객을 포함한 버블 그래프")

bubble_df = df[
    df["first_scrn"].notna()
    & df["total_audi"].notna()
    & df["first_week_audi"].notna()
].copy()

# 버블 크기 음수 방지
bubble_df = bubble_df[
    bubble_df["first_week_audi"] >= 0
].copy()

if not bubble_df.empty:
    fig6 = px.scatter(
        bubble_df,
        x="first_scrn",
        y="total_audi",
        size="first_week_audi",
        color="genre",
        hover_name="movieNm",
        hover_data={
            "first_scrn": ":,.0f",
            "total_audi": ":,.0f",
            "first_week_audi": ":,.0f",
            "genre": True
        },
        size_max=60,
        title="개봉일 스크린 수 · 첫 주 관객 · 총 관객",
        labels={
            "first_scrn": "개봉일 스크린 수",
            "total_audi": "총 관객 수(명)",
            "first_week_audi": "첫 주 관객 수",
            "genre": "장르"
        }
    )

    fig6.update_layout(height=650)

    st.plotly_chart(fig6, use_container_width=True)
else:
    st.warning("버블 그래프를 그릴 데이터가 없습니다.")

explanation_space(6)


# --------------------------------------------------
# 그래프 7
# 제작 국가 → 장르 선버스트 그래프
# 칸의 크기 = 영화 편수
# --------------------------------------------------
section_title(7, "제작 국가에서 장르로 내려가는 선버스트")

sunburst_df = (
    df.groupby(["nation", "genre"])
    .size()
    .reset_index(name="영화 편수")
)

if not sunburst_df.empty:
    fig7 = px.sunburst(
        sunburst_df,
        path=["nation", "genre"],
        values="영화 편수",
        color="nation",
        title="제작 국가 → 장르별 영화 편수",
        hover_data={
            "영화 편수": True
        }
    )

    fig7.update_traces(
        hovertemplate=(
            "분류: %{label}<br>"
            "영화 편수: %{value}편"
            "<extra></extra>"
        ),
        insidetextorientation="radial"
    )

    fig7.update_layout(height=700)

    st.plotly_chart(fig7, use_container_width=True)

    st.caption(
        "가운데에서 바깥쪽으로 제작 국가와 장르를 확인할 수 있습니다. "
        "각 칸의 크기는 해당 분류에 속한 영화 편수를 나타냅니다."
    )
else:
    st.warning("선버스트 그래프를 그릴 데이터가 없습니다.")

explanation_space(7)


# --------------------------------------------------
# 마지막 안내
# --------------------------------------------------
st.divider()
st.caption(
    "영화 데이터 그래프 도감 2 - 분포와 관계 | "
    "데이터 출처: KOBIS 영화 데이터"
)
# --------------------------------------------------
# 그래프 8
# 총 관객 수가 많아질수록 첫 주 관객 비율은 어떻게 달라질까?
# --------------------------------------------------
section_title(
    8,
    "총 관객 수가 많아질수록 첫 주 관객 비율은 어떻게 달라질까?"
)

ratio_df = df[
    df["first_week_audi"].notna()
    & df["total_audi"].notna()
    & (df["total_audi"] > 0)
    & (df["first_week_audi"] >= 0)
    & (df["first_week_audi"] <= df["total_audi"])
].copy()

if not ratio_df.empty:

    # 첫 주 관객이 전체 관객에서 차지하는 비율
    ratio_df["first_week_ratio"] = (
        ratio_df["first_week_audi"]
        / ratio_df["total_audi"]
        * 100
    )

    fig8 = px.scatter(
        ratio_df,
        x="total_audi",
        y="first_week_ratio",
        color="genre",
        hover_name="movieNm",
        hover_data={
            "total_audi": ":,.0f",
            "first_week_audi": ":,.0f",
            "first_week_ratio": ":.1f",
            "genre": True
        },
        title="총 관객 수와 첫 주 관객 비율의 관계",
        labels={
            "total_audi": "총 관객 수(명)",
            "first_week_ratio": "첫 주 관객 비율(%)",
            "genre": "장르"
        }
    )

    fig8.update_layout(
        height=650,
        xaxis_title="총 관객 수(명)",
        yaxis_title="첫 주 관객 비율(%)"
    )

    fig8.update_yaxes(
        range=[0, 100]
    )

    st.plotly_chart(
        fig8,
        use_container_width=True
    )

    st.caption(
        "점 하나가 영화 한 편을 나타냅니다. "
        "위쪽에 있을수록 전체 관객 중 첫 주에 관람한 관객의 비율이 높고, "
        "아래쪽에 있을수록 첫 주 이후에 관객이 더 많이 유입된 영화입니다. "
        "영화명은 점에 마우스를 올리면 확인할 수 있습니다."
    )

else:
    st.warning(
        "첫 주 관객과 총 관객 데이터를 모두 확인할 수 있는 "
        "영화가 없습니다."
    )

explanation_space(8)
