import streamlit as st

# 페이지 설정
st.set_page_config(page_title="양성화 대상 자가진단", page_icon="🏛️", layout="centered")

# --- 커스텀 CSS (모바일 압축, 숫자 입력칸 +/- 스핀 버튼 원천 제거) ---
st.markdown("""
<style>
    .stApp { background-color: #F9FAFB; }
    
    /* 카드형 UI */
    .toss-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 16px;
    }
    .toss-question { font-size: 17px; font-weight: 700; color: #2C3E50; margin-bottom: 10px; }
    .toss-desc { font-size: 14px; color: #7F8C8D; line-height: 1.5; margin-bottom: 12px; }
    
    /* 숫자 입력칸 +/- 버튼 제거 및 폰트 확대 (직접 타이핑만 가능) */
    input[type="number"]::-webkit-inner-spin-button, 
    input[type="number"]::-webkit-outer-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }
    input[type="number"] { font-size: 18px !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 팝업 다이얼로그 (화면 중앙에 띄워 시선 집중 및 스크롤 이동 효과 대체) ---
@st.dialog("📋 자가진단 결과 안내")
def show_result_dialog(completed, residential, restricted, b_type, b_area):
    if completed == "아니오":
        st.error("❌ 진단 결과: 양성화 대상에 해당하지 않습니다. (사유: 2023년 12월 31일 이전 완공 기준 미달)")
    elif residential == "아니오":
        st.error("❌ 진단 결과: 양성화 대상에 해당하지 않습니다. (사유: 주거용 면적 비율 50% 미만)")
    elif restricted == "해당됨 (포함)":
        st.error("❌ 진단 결과: 양성화 대상에 해당하지 않습니다. (사유: 개발제한구역 등 적용 제외 구역 위치)")
    elif b_type == "선택해주십시오":
        st.warning("⚠️ 건축물 유형을 정확히 선택해 주십시오.")
    elif b_area <= 0:
        st.warning("⚠️ 건축물 면적을 정확히 입력해 주십시오.")
    else:
        is_pass = False
        reason = ""

        if b_type == "다세대주택":
            if b_area <= 85: is_pass = True
            else: reason = "세대당 전용면적 85㎡ 초과"
        elif b_type == "단독주택":
            if b_area <= 165: is_pass = True
            else: reason = "연면적 165㎡ 초과"
        elif b_type == "다가구주택":
            if b_area <= 660: is_pass = True
            else: reason = "연면적 660㎡ 초과"
        elif b_type == "근린생활시설 (사실상 주택 사용)":
            if b_area <= 165: is_pass = True
            else: reason = "면적 기준 초과"

        if is_pass:
            st.success("✅ 진단 결과: 특정건축물 양성화 **대상에 해당할 가능성이 높습니다.**")
            st.info("""
            **[향후 행정 절차 안내]**
            1. **상담 및 접수:** 관할 구청(건축과 등) 특정건축물 지원센터에 방문하여 상세 상담을 진행해 주십시오.
            2. **필수 서류:** 건축사가 작성한 설계도서 및 현장조사서가 반드시 첨부되어야 합니다.
            3. **유의 사항:** 본 특별조치법은 시행 후 18개월간만 한시적으로 운영되므로, 기한 내 접수를 완료하셔야 합니다.
            """)
        else:
            st.error(f"❌ 진단 결과: 양성화 대상에 해당하지 않습니다. (사유: {reason})")
            
    if st.button("닫기", use_container_width=True):
        st.rerun()

# --- 최상단 공공기관용 공식 안내문 (고정 노출) ---
st.markdown("<h2 style='text-align: center; color: #2C3E50; margin-bottom: 20px;'>🏛️ 특정건축물 양성화 자가진단</h2>", unsafe_allow_html=True)
st.markdown("""
<div style='background-color: #EBF5FB; padding: 20px; border-radius: 10px; border-left: 5px solid #2980B9; margin-bottom: 24px;'>
    <h4 style='margin-top: 0; color: #2980B9;'>안내말씀</h4>
    <p style='font-size: 15px; color: #34495E; line-height: 1.6; margin-bottom: 0;'>
        본 서비스는 <strong>「특정건축물 정리에 관한 특별조치법」</strong>(시행 2026. 12. 17.)에 따른 양성화 심사 대상 여부를 사전에 가늠해 보실 수 있도록 마련된 자가진단입니다.<br><br>
        정확한 <strong>건축물 유형</strong> 및 <strong>면적(㎡)</strong> 확인이 필요하신 경우, <strong>정부24(www.gov.kr)</strong>에서 건축물대장을 무료로 발급받아 확인하시거나 <strong>관할구청 민원여권과(예: 금정구청 ☎ 051-519-4000)</strong>로 문의하여 주시기 바랍니다.<br><br>
        <span style='color: #C0392B; font-weight: bold;'>※ 주의사항:</span> 과태료(이행강제금 5회분 상당) 부과 및 기한(법 시행 후 18개월) 요건이 존재하므로, 최종 접수는 반드시 관할 지자체 담당 부서 및 건축사와 협의해 주십시오.
    </p>
</div>
""", unsafe_allow_html=True)

# --- 입력 폼 (압축 및 공공기관 톤 앤 매너 적용) ---
st.markdown('<div class="toss-card">', unsafe_allow_html=True)
st.markdown('<div class="toss-question">1. 필수 기본 요건 확인</div>', unsafe_allow_html=True)
is_completed = st.radio("Q. 2023년 12월 31일 이전에 사실상 완공된 건축물입니까?", ("예", "아니오"), index=1)
is_residential = st.radio("Q. 건축물 전체 연면적 중 주거용 면적의 비율이 50% 이상입니까?", ("예", "아니오"), index=1)
st.markdown('</div>', unsafe_allow_html=True)


st.markdown('<div class="toss-card">', unsafe_allow_html=True)
st.markdown('<div class="toss-question">2. 건축물 유형 및 규모(면적) 확인</div>', unsafe_allow_html=True)
st.markdown('<div class="toss-desc">건축물대장 상의 정확한 용도와 면적을 기준으로 선택해 주십시오.</div>', unsafe_allow_html=True)
building_type = st.selectbox("건축물 유형", ["선택해주십시오", "다세대주택", "단독주택", "다가구주택", "근린생활시설 (사실상 주택 사용)"], label_visibility="collapsed")

area = 0.0
if building_type != "선택해주십시오":
    st.markdown("<p style='font-size: 15px; font-weight: bold; margin-bottom: 5px; margin-top: 10px;'>해당 면적 직접 입력 (㎡)</p>", unsafe_allow_html=True)
    area = st.number_input("면적 입력", min_value=0.0, step=1.0, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)


st.markdown('<div class="toss-card">', unsafe_allow_html=True)
st.markdown('<div class="toss-question">3. 적용 제외 구역 위치 여부</div>', unsafe_allow_html=True)
st.markdown('<div class="toss-desc">해당 건축물이 보전산지, 개발제한구역, 정비구역 등에 포함되어 있습니까?</div>', unsafe_allow_html=True)
is_restricted_area = st.radio("제외구역여부", ("해당 없음 (미포함)", "해당됨 (포함)"), index=0, horizontal=True, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# --- 결과 다이얼로그 호출 ---
if st.button("진단 결과 확인하기", type="primary", use_container_width=True):
    show_result_dialog(is_completed, is_residential, is_restricted_area, building_type, area)