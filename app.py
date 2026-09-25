import streamlit as st

# 페이지 설정 (토스 스타일을 위해 레이아웃을 중앙으로 좁게 유지)
st.set_page_config(page_title="양성화 대상 판별기", page_icon="🏠", layout="centered")

# --- 커스텀 CSS (토스 느낌의 카드 디자인 및 폰트 스타일링) ---
st.markdown("""
<style>
    /* 전체 배경을 아주 연한 회색으로 */
    .stApp {
        background-color: #F9FAFB;
    }
    
    /* 카드형 컨테이너 스타일 */
    .toss-card {
        background-color: white;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 24px;
    }
    
    /* 제목 스타일 */
    .toss-title {
        font-size: 28px;
        font-weight: 800;
        color: #191F28;
        margin-bottom: 8px;
    }
    
    /* 소제목/질문 스타일 */
    .toss-question {
        font-size: 18px;
        font-weight: 700;
        color: #333D4B;
        margin-bottom: 12px;
    }
    
    /* 안내 문구 스타일 */
    .toss-desc {
        font-size: 15px;
        color: #8B95A1;
        line-height: 1.5;
    }
    
    /* Streamlit 기본 요소 미세 조정 */
    div[data-testid="stRadio"] > div {flex-direction: row;} /* 라디오 버튼 가로 정렬 */
</style>
""", unsafe_allow_html=True)


# --- 헤더 영역 ---
st.markdown('<div class="toss-title">특정건축물 양성화 대상 확인</div>', unsafe_allow_html=True)
st.markdown('<div class="toss-desc">보유하신 건축물이 양성화 대상인지 1분 만에 확인해보세요.</div>', unsafe_allow_html=True)
st.write("") # 여백

# --- 법령 및 주의사항 (Expander) ---
with st.expander("📖 양성화 심사 조건 및 과태료 안내 (클릭)", expanded=False):
    st.markdown("""
    **[시행 2026. 12. 17.] 특정건축물 정리에 관한 특별조치법**
    
    ✅ **기본 필수 요건**
    * 2023년 12월 31일 이전 완공
    * 주거용 면적 50% 이상
    * 개발제한구역, 보전산지 등 특정 구역 제외
    
    💰 **비용 및 기한**
    * **과태료:** 이행강제금의 5회분 부과 (기납부액 차감)
    * **기한:** 법 시행 후 단 **18개월**간만 유효합니다.
    * **주의:** 본 결과는 참고용이며, 최종 신고는 건축사가 작성한 설계도서가 필요합니다.
    """)

# --- [1] 기본 요건 카드 ---
st.markdown('<div class="toss-card">', unsafe_allow_html=True)
st.markdown('<div class="toss-question">1. 기본 요건을 확인해주세요</div>', unsafe_allow_html=True)

st.write("**2023년 12월 31일 이전에 사실상 완공되었나요?**")
is_completed = st.radio("완공여부", ("예", "아니오"), index=1, label_visibility="collapsed")
st.write("")

st.write("**전체 면적 중 주거용 비율이 50% 이상인가요?**")
is_residential = st.radio("주거용비율", ("예", "아니오"), index=1, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)


# --- [2] 규모 요건 카드 ---
st.markdown('<div class="toss-card">', unsafe_allow_html=True)
st.markdown('<div class="toss-question">2. 건축물 유형과 면적을 알려주세요</div>', unsafe_allow_html=True)

building_type = st.selectbox("건축물 유형", ["선택해주세요", "다세대주택", "단독주택", "다가구주택", "근린생활시설 (주택 사용)"])

area = 0.0
if building_type == "다세대주택":
    area = st.number_input("세대당 전용면적 (㎡)", min_value=0.0, step=1.0)
elif building_type in ["단독주택", "다가구주택", "근린생활시설 (주택 사용)"]:
    area = st.number_input("전체 연면적 (㎡)", min_value=0.0, step=1.0)
st.markdown('</div>', unsafe_allow_html=True)


# --- [3] 제외 구역 카드 ---
st.markdown('<div class="toss-card">', unsafe_allow_html=True)
st.markdown('<div class="toss-question">3. 적용 제외 구역에 해당하나요?</div>', unsafe_allow_html=True)
st.markdown('<div class="toss-desc">보전산지, 개발제한구역, 정비구역 등에 포함되는지 확인합니다.</div>', unsafe_allow_html=True)
is_restricted_area = st.radio("제외구역여부", ("해당 없음 (안전함)", "제외 구역 포함됨"), index=0, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)


st.write("")

# --- 판별 로직 버튼 ---
if st.button("결과 확인하기", type="primary", use_container_width=True):
    st.markdown("---")
    if is_completed == "아니오":
        st.error("불가: 2023년 12월 31일 이전 완공 건물만 대상입니다.")
    elif is_residential == "아니오":
        st.error("불가: 주거용 면적이 50% 이상이어야 합니다.")
    elif is_restricted_area == "제외 구역 포함됨":
        st.error("불가: 적용 제외 구역에 위치하고 있습니다.")
    elif building_type == "선택해주세요":
        st.warning("건축물 유형을 선택해주세요.")
    elif area <= 0:
        st.warning("면적을 정확히 입력해주세요.")
    else:
        is_pass = False
        reason = ""

        if building_type == "다세대주택":
            if area <= 85: is_pass = True
            else: reason = "다세대주택은 세대당 전용면적 85㎡ 이하여야 합니다."
        elif building_type == "단독주택":
            if area <= 165: is_pass = True
            else: reason = "단독주택은 연면적 165㎡ 이하여야 합니다."
        elif building_type == "다가구주택":
            if area <= 660: is_pass = True
            else: reason = "다가구주택은 연면적 660㎡ 이하여야 합니다."
        elif building_type == "근린생활시설 (주택 사용)":
            if area <= 165: is_pass = True
            else: reason = "면적 기준 초과"

        if is_pass:
            st.success("양성화 대상일 가능성이 높습니다!")
            st.info("다음 단계: 건축사를 통해 현장 조사를 진행하고, 기한(18개월) 내에 관할 구청에 신고하세요.")
        else:
            st.error(f"대상 아님: {reason}")