import streamlit as st
import pandas as pd
import plotly.express as px

1. 페이지 기본 설정

st.set_page_config(
page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
page_icon="🎬",
layout="wide"
)

2. 데이터 로드 및 전처리 함수

@st.cache_data
def load_data():
url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
df = pd.read_csv(url)

# genre 열에서 세로막대 기호(|)로 분리되어 있는 경우 첫 번째 장르만 사용
df['genre'] = df['genre'].astype(str).apply(lambda x: x.split('|')[0].strip() if pd.notna(x) and x != 'nan' else '기타')

# 수치형 데이터 형변환 (결측치 처리)
numeric_cols = ['first_scrn', 'first_show', 'first_week_audi', 'total_audi', 'days_in_top10']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
return df


df = load_data()

3. 헤더 및 데이터 소개

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown("박스오피스 상위권 영화 216편의 데이터를 바탕으로 장르별 분포, 흥행 관객 수, 그리고 스크린 수 및 상영 기간과의 관계를 시각적으로 탐색합니다.")

st.divider()

데이터 요약 정보 확장 영역

with st.expander("📄 원본 데이터 요약표 보기"):
st.dataframe(df, use_container_width=True)
st.caption(f"총 {len(df)}개 영화 데이터 로드 완료")

st.markdown("## 📊 데이터 분포와 관계 분석")

-------------------------------------------------------------------

그래프 1: 장르별 영화 편수 (도넛 차트)

-------------------------------------------------------------------

st.subheader("1. 장르별 영화 편수 분포 (도넛 그래프)")

genre_counts = df['genre'].value_counts().reset_index()
genre_counts.columns = ['장르', '편수']

fig1 = px.pie(
genre_counts,
names='장르',
values='편수',
hole=0.4,
color_discrete_sequence=px.colors.qualitative.Pastel
)

fig1.update_traces(
textinfo='percent+label',
hovertemplate="장르: %{label}



영화 편수: %{value}편



점유율: %{percent}"
)

fig1.update_layout(
margin=dict(t=30, b=30, l=10, r=10),
legend_title_text="장르 목록"
)

st.plotly_chart(fig1, use_container_width=True)

st.info("💡 이 그래프로 알 수 있는 것: 드라마, 애니메이션, 액션 장르가 전체 개봉작의 과반수를 차지하며 박스오피스 상위권 시장을 주도하고 있음을 알 수 있습니다.")

st.divider()

-------------------------------------------------------------------

그래프 2: 장르별 영화 흥행 규모 (트리맵)

-------------------------------------------------------------------

st.subheader("2. 장르 및 영화별 총 관객 수 (트리맵)")

fig2 = px.treemap(
df,
path=[px.Constant("전체 영화"), 'genre', 'movieNm'],
values='total_audi',
color='genre',
color_discrete_sequence=px.colors.qualitative.Pastel
)

fig2.update_traces(
hovertemplate="%{label}



총 관객 수: %{value:,.0f}명"
)

fig2.update_layout(
margin=dict(t=30, b=30, l=10, r=10)
)

st.plotly_chart(fig2, use_container_width=True)

st.info("💡 이 그래프로 알 수 있는 것: 동일한 장르 내에서도 특정 메가 히트 영화가 장르 전체의 총 관객 수 지표를 크게 견인하고 있음을 확인할 수 있습니다.")

st.divider()

-------------------------------------------------------------------

그래프 3: 총 관객 수 분포 (히스토그램)

-------------------------------------------------------------------

st.subheader("3. 총 관객 수 분포 (히스토그램)")

fig3 = px.histogram(
df,
x="total_audi",
nbins=30,
color_discrete_sequence=['#4B8BF5'],
labels={'total_audi': '총 관객 수 (명)'}
)

fig3.update_traces(
hovertemplate="관객 수 구간: %{x:,.0f}명



영화 수: %{y}편"
)

fig3.update_layout(
yaxis_title="영화 수 (편)",
bargap=0.1,
margin=dict(t=30, b=30, l=10, r=10)
)

st.plotly_chart(fig3, use_container_width=True)

데이터 탐색: 최고 관객 영화 및 집중 구간 계산

max_movie = df.loc[df['total_audi'].idxmax()]
top_movie_name = max_movie['movieNm']
top_movie_audi = int(max_movie['total_audi'])

under_2m_count = (df['total_audi'] <= 2000000).sum()
under_2m_pct = (under_2m_count / len(df)) * 100

st.info(
f"💡 이 그래프로 알 수 있는 것: 대부분의 영화(전체의 약 {under_2m_pct:.1f}%, {under_2m_count}편)가 총 관객 수 200만 명 이하 구간에 집중되어 있으며, "
f"가장 많은 관객을 동원한 영화는 '{top_movie_name}'(총 {top_movie_audi:,.0f}명)입니다."
)

st.divider()

-------------------------------------------------------------------

그래프 4: 개봉일 스크린 수 vs 총 관객 수 (산점도)

-------------------------------------------------------------------

st.subheader("4. 개봉일 스크린 수와 총 관객 수의 관계 (산점도)")

fig4 = px.scatter(
df,
x="first_scrn",
y="total_audi",
color="genre",
hover_name="movieNm",
labels={
"first_scrn": "개봉일 스크린 수 (개)",
"total_audi": "총 관객 수 (명)",
"genre": "장르"
},
color_discrete_sequence=px.colors.qualitative.Set2
)

fig4.update_traces(
marker=dict(size=10, opacity=0.8),
hovertemplate="%{hovertext}



개봉일 스크린 수: %{x:,.0f}개



총 관객 수: %{y:,.0f}명"
)

fig4.update_layout(
margin=dict(t=30, b=30, l=10, r=10),
legend_title_text="장르"
)

st.plotly_chart(fig4, use_container_width=True)

st.info("💡 이 그래프로 알 수 있는 것: 개봉일 스크린 수가 많을수록 총 관객 수도 전반적으로 증가하는 양의 상관관계를 나타내며, 초기 상영관 확보가 최종 흥행 규모에 중요한 역할을 함을 알 수 있습니다.")

st.divider()

-------------------------------------------------------------------

그래프 5: 주요 장르별 총 관객 수 분포 (박스플롯)

-------------------------------------------------------------------

st.subheader("5. 주요 장르별 총 관객 수 분포 (상자 그림)")

영화 수 10편 이상인 장르 필터링

genre_counts_series = df['genre'].value_counts()
major_genres = genre_counts_series[genre_counts_series >= 10].index
df_major = df[df['genre'].isin(major_genres)]

fig5 = px.box(
df_major,
x="genre",
y="total_audi",
color="genre",
hover_name="movieNm",
points="outliers",
labels={
"genre": "장르",
"total_audi": "총 관객 수 (명)"
},
color_discrete_sequence=px.colors.qualitative.Pastel
)

fig5.update_traces(
hovertemplate="%{hovertext}



장르: %{x}



총 관객 수: %{y:,.0f}명"
)

fig5.update_layout(
margin=dict(t=30, b=30, l=10, r=10),
showlegend=False
)

st.plotly_chart(fig5, use_container_width=True)

st.info("💡 이 그래프로 알 수 있는 것: 영화 편수가 10편 이상인 주요 장르 중에서도, 상자 밖의 이상치 점(대형 흥행작)의 유무에 따라 장르 내 흥행 편차가 매우 크다는 것을 확인할 수 있습니다.")
