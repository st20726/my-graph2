import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 기본 설정
st.set_page_config(page_title="영화 데이터 그래프 도감 2", layout="wide")

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption("1년간 박스오피스 Top 10에 진입한 개봉 영화 216편 데이터 시각화")

# 데이터 불러오기 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)
    # 장르 컬럼에서 세로막대(|) 기호 기준 첫 번째 장르만 추출
    df['genre'] = df['genre'].fillna('').apply(lambda x: str(x).split('|')[0] if x else '기타')
    return df

df = load_data()

st.divider()

# ----------------------------------------------------
# 1. 장르별 영화 편수 (도넛 그래프)
# ----------------------------------------------------
st.subheader("1. 장르별 영화 편수 (도넛 차트)")
genre_counts = df['genre'].value_counts().reset_index()
genre_counts.columns = ['genre', 'count']

fig1 = px.pie(
    genre_counts,
    values='count',
    names='genre',
    hole=0.4,
    title="장르별 영화 편수 분포"
)
fig1.update_traces(
    hovertemplate="<b>장르: %{label}</b><br>영화 수: %{value}편<br>비율: %{percent}<extra></extra>"
)
st.plotly_chart(fig1, use_container_width=True)

st.info("💡 **이 그래프로 알 수 있는 것:** 특정 주요 장르(드라마, 액션 등)에 영화 편수가 집중되어 있으며, 비주류 장르의 비중은 상대적으로 낮음을 알 수 있습니다.")

st.divider()

# ----------------------------------------------------
# 2. 장르/영화별 총 관객 수 (트리맵)
# ----------------------------------------------------
st.subheader("2. 장르 및 영화별 총 관객 수 (트리맵)")
fig2 = px.treemap(
    df,
    path=['genre', 'movieNm'],
    values='total_audi',
    title="장르 및 영화별 총 관객 수 분포"
)
fig2.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객 수: %{value:,.0f}명<extra></extra>"
)
st.plotly_chart(fig2, use_container_width=True)

st.info("💡 **이 그래프로 알 수 있는 것:** 각 장르의 전체 관객 규모와 그 안에서 각 영화가 차지하는 상업적 성과 비중을 한눈에 비교할 수 있습니다.")

st.divider()

# ----------------------------------------------------
# 3. 총 관객 수 분포 (히스토그램)
# ----------------------------------------------------
st.subheader("3. 총 관객 수 분포 (히스토그램)")
top_movie = df.loc[df['total_audi'].idxmax()]
under_2m_ratio = (df['total_audi'] <= 2000000).mean() * 100

fig3 = px.histogram(
    df,
    x='total_audi',
    nbins=30,
    title="총 관객 수 분포",
    labels={'total_audi': '총 관객 수'}
)
fig3.update_traces(
    hovertemplate="관객 수 구간: %{x:,.0f}명<br>영화 수: %{y}편<extra></extra>"
)
st.plotly_chart(fig3, use_container_width=True)

st.info(f"💡 **이 그래프로 알 수 있는 것:** 대부분의 영화(약 {under_2m_ratio:.1f}%)가 관객 수 200만 명 이하 구간에 몰려 있으며, 가장 관객 수가 많은 영화는 '{top_movie['movieNm']}'({top_movie['total_audi']:,}명)입니다.")

st.divider()

# ----------------------------------------------------
# 4. 개봉일 스크린 수 vs 총 관객 수 (산점도)
# ----------------------------------------------------
st.subheader("4. 개봉일 스크린 수 vs 총 관객 수 (산점도)")
fig4 = px.scatter(
    df,
    x='first_scrn',
    y='total_audi',
    color='genre',
    hover_name='movieNm',
    title="개봉일 스크린 수와 총 관객 수의 관계",
    labels={'first_scrn': '개봉일 스크린 수', 'total_audi': '총 관객 수', 'genre': '장르'}
)
fig4.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린 수: %{x:,.0f}개<br>총 관객 수: %{y:,.0f}명<extra></extra>"
)
st.plotly_chart(fig4, use_container_width=True)

st.info("💡 **이 그래프로 알 수 있는 것:** 개봉일 스크린 수가 많을수록 대체로 총 관객 수도 증가하는 경향을 보이지만, 스크린 수 대비 높은 흥행을 기록한 효율적인 영화들도 존재합니다.")
