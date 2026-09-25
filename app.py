import streamlit as st

# 페이지 설정
st.set_page_config(page_title="양성화 판별기", page_icon="🏠", layout="centered")

# --- 커스텀 CSS (모바일 압축, 숫자 입력칸 +/- 숨기기) ---
st.markdown("""
<style>
    .stApp { background-color: #F9FAFB; }
    
    /* 모바일 스크롤 압축을 위해 패딩 및 마진 최소화 */
    .toss-card {
        background-color: white;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }
    .toss-question { font-size: 16px; font-weight: 700; color: #333D4B; margin-bottom: 8px; }
    .toss-desc { font-size: 14px; color: #8B95A1; line-height: 1.4; margin-bottom: 8px; }
    
    /* 숫자 입력칸 +/- 스핀 버튼 원천 제거 및 폰트 크기 확대 */
    input[type="number"]::-webkit-inner-spin-button, 
    input[type="number"]::-webkit-outer-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }
    input[type="number"] { font-size: 18px !important; font-weight: bold; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 팝업 다이얼로그 (결과를 화면 중앙에 크게 띄움) ---
@st.dialog("🔍 판별 결과")
def show_result_dialog(completed, residential, restricted, b_type, b_area):
    if completed == "아니오":
        st.error("❌ 불가: 2023년 12월 31일 이전 완공 건물만 대상입니다.")
    elif residential == "아니오":
        st.error("❌ 불가: 주거용 면적이 50% 이상이어야 합니다.")
    elif restricted == "포함됨":
        st.error("❌ 불가: 적용 제외 구역에 위치하고 있습니다.")
    elif b_type == "선택해주세요":
        st.warning("⚠️ 건축물 유형을 선택해주세요.")
    elif b_area <= 0:
        st.warning("⚠️ 면적을 정확히 입력해주세요.")
    else:
        is_pass = False
        reason = ""

        if b_type == "다세대주택":
            if b_area <= 85: is_pass = True
            else: reason = "세대당 전용면적 85㎡ 이하여야 합니다."
        elif b_type == "단독주택":
            if b_area <= 165: is_pass = True
            else: reason = "연면적 165㎡ 이하여야 합니다."
        elif b_type == "다가구주택":
            if b_area <= 660: is_pass = True
            else: reason = "연면적 660㎡ 이하여야 합니다."
        elif b_type == "근린생활시설 (주택 사용)":
            if b_area <= 165: is_pass = True
            else: reason = "면적 기준 초과"

        if is_pass:
            st.success("🎉 양성화 대상일 가능성이 높습니다!")
            st.info("""
            **다음 단계 안내:**
            * 관할 구청에 방문하여 사전 상담을 진행하세요.
            * 건축사를 통한 현장조사서가 반드시 필요합니다.
            """)
        else:
            st.error(f"❌ 대상 아님: {reason}")
            
    if st.button("닫기", use_container_width=True):
        st.rerun()

# --- 화면 렌더링 ---
st.markdown('### 특정건축물 양성화 판별기')
st.markdown('<div class="toss-desc">보유하신 건축물이 양성화 대상인지 1분 만에 확인해보세요.</div>', unsafe_allow_html=True)

# 1. 기본 요건 (가로 배치로 압축)
st.markdown('<div class="toss-card">', unsafe_allow_html=True)
st.markdown('<div class="toss-question">1. 기본 요건</div>', unsafe_allow_html=True)
is_completed = st.radio("2023.12.31 이전 사실상 완공?", ("예", "아니오"), index=1, horizontal=True)
is_residential = st.radio("전체 면적 중 주거용 50% 이상?", ("예", "아니오"), index=1, horizontal=True)
st.markdown('</div>', unsafe_allow_html=True)

# 2. 건축물 유형 및 면적
st.markdown('<div class="toss-card">', unsafe_allow_html=True)
st.markdown('<div class="toss-question">2. 유형 및 면적 (㎡)</div>', unsafe_allow_html=True)
building_type = st.selectbox("건축물 유형", ["선택해주세요", "다세대주택", "단독주택", "다가구주택", "근린생활시설 (주택 사용)"], label_visibility="collapsed")

area = 0.0
if building_type != "선택해주세요":
    area = st.number_input("면적 입력", min_value=0.0, step=1.0, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# 3. 제외 구역
st.markdown('<div class="toss-card">', unsafe_allow_html=True)
st.markdown('<div class="toss-question">3. 적용 제외 구역 확인</div>', unsafe_allow_html=True)
st.markdown('<div class="toss-desc">보전산지, 개발제한구역, 정비구역 등 포함 여부</div>', unsafe_allow_html=True)
is_restricted_area = st.radio("제외구역여부", ("포함 안 됨", "포함됨"), index=0, horizontal=True, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# 결과 팝업 실행 버튼
if st.button("결과 확인하기", type="primary", use_container_width=True):
    show_result_dialog(is_completed, is_residential, is_restricted_area, building_type, area)