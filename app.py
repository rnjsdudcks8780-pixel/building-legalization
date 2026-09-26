import streamlit as st
import math

# 페이지 설정
st.set_page_config(page_title="특정건축물 양성화 서비스", page_icon="🏛️", layout="centered")

# --- 커스텀 CSS (숫자 입력칸 +/- 스핀 버튼 원천 제거) ---
st.markdown("""
<style>
    .stApp { background-color: #F9FAFB; }
    .toss-card {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 16px;
    }
    .toss-question { font-size: 17px; font-weight: 700; color: #2C3E50; margin-bottom: 10px; }
    .toss-desc { font-size: 14px; color: #7F8C8D; line-height: 1.5; margin-bottom: 12px; }
    input[type="number"]::-webkit-inner-spin-button, 
    input[type="number"]::-webkit-outer-spin-button { -webkit-appearance: none; margin: 0; }
    input[type="text"] { font-size: 18px !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 위치지수 계산 함수 (실무 지수표 완벽 반영) ---
def get_loc_index(price):
    p = price / 1000  # 천원 단위로 환산
    if p <= 10: return 0.80
    elif p <= 30: return 0.82
    elif p <= 50: return 0.84
    elif p <= 100: return 0.86
    elif p <= 150: return 0.88
    elif p <= 200: return 0.90
    elif p <= 350: return 0.92
    elif p <= 500: return 0.94
    elif p <= 650: return 0.96
    elif p <= 800: return 0.98
    elif p <= 1000: return 1.00
    elif p <= 1200: return 1.03
    elif p <= 1600: return 1.06
    elif p <= 2000: return 1.09
    elif p <= 2500: return 1.12
    elif p <= 3000: return 1.15
    elif p <= 4000: return 1.18
    elif p <= 5000: return 1.21
    elif p <= 6000: return 1.24
    elif p <= 7000: return 1.27
    elif p <= 8000: return 1.30
    elif p <= 9000: return 1.33
    elif p <= 10000: return 1.36
    elif p <= 20000: return 1.40
    elif p <= 30000: return 1.45
    elif p <= 40000: return 1.50
    elif p <= 50000: return 1.55
    elif p <= 60000: return 1.60
    elif p <= 70000: return 1.63
    elif p <= 80000: return 1.66
    else: return 1.69

# --- 팝업 다이얼로그 1: 자가진단 결과 ---
@st.dialog("📋 자가진단 결과 안내")
def show_diagnostic_result(completed, residential, restricted, b_type, b_area):
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
            1. **상담 및 접수:** 관할 구청 민원실 또는 특정건축물 지원센터에 방문해 주십시오.
            2. **필수 서류:** 건축사가 작성한 설계도서 및 현장조사서가 반드시 첨부되어야 합니다.
            3. **유의 사항:** 본 특별조치법은 시행 후 18개월간만 한시적으로 운영되므로 기한 내 접수를 완료하셔야 합니다.
            """)
        else:
            st.error(f"❌ 진단 결과: 양성화 대상에 해당하지 않습니다. (사유: {reason})")
            
    if st.button("닫기", use_container_width=True):
        st.rerun()

# --- 팝업 다이얼로그 2: 과태료 산출 결과 ---
@st.dialog("💰 예상 과태료 산출 결과")
def show_fine_result(land_price, violation_area, structure, violation_year, ordinance_ratio):
    base_price = 860000 
    use_index = 0.91 # 주거용 공통 용도지수 적용
    
    # 구조 지수 및 감가상각률(매년) 맵핑
    str_map = {
        "철근콘크리트조": (1.0, 0.0225),
        "시멘트벽돌조": (0.9, 0.03),
        "경량철골조": (0.65, 0.045),
        "조립식패널조": (0.55, 0.045),
        "철파이프조 (샤시 등)": (0.3, 0.090)
    }
    str_index, dep_rate_per_year = str_map[structure]
    
    # 위치 지수 추출
    loc_index = get_loc_index(land_price)
    
    # 잔가율 계산 (하한선 0.1)
    age = max(0, 2026 - violation_year)
    depreciation_rate = max(0.1, 1.0 - (age * dep_rate_per_year))
    
    # 1. 1㎡당 시가표준액 산출 (천원 미만 절사)
    raw_unit_price = base_price * str_index * use_index * loc_index * depreciation_rate
    unit_price = math.floor(raw_unit_price / 1000) * 1000
    
    # 2. 1회분 이행강제금 계산 (천원 미만 절사)
    # 수식: 시가표준액 * 위반면적 * 0.5(법80조) * 0.85(기초공사X 증축) * 조례감경비율
    raw_one_time_fine = unit_price * violation_area * 0.5 * 0.85 * ordinance_ratio
    one_time_fine = math.floor(raw_one_time_fine / 1000) * 1000
    
    # 3. 최종 과태료 (5회분)
    total_fine = one_time_fine * 5

    st.markdown(f"**추정 1㎡당 시가표준액:** {int(unit_price):,} 원")
    st.markdown(f"**1회분 이행강제금 예상액:** {int(one_time_fine):,} 원")
    
    st.markdown('<div style="background-color: #F2F4F6; padding: 16px; border-radius: 8px; margin-top: 16px;">', unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; color: #3182F6;'>최종 예상 과태료(5회분)</h3>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center; color: #191F28;'>약 {int(total_fine):,} 원</h2>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("닫기", use_container_width=True):
        st.rerun()

# ==========================================
# 최상단 공공기관용 공식 안내문 (고정 노출)
# ==========================================
st.markdown("<h2 style='text-align: center; color: #2C3E50; margin-bottom: 20px;'>🏛️ 특정건축물 양성화 서비스</h2>", unsafe_allow_html=True)
st.markdown("""
<div style='background-color: #EBF5FB; padding: 20px; border-radius: 10px; border-left: 5px solid #2980B9; margin-bottom: 24px;'>
    <h4 style='margin-top: 0; color: #2980B9;'>안내말씀</h4>
    <p style='font-size: 15px; color: #34495E; line-height: 1.6; margin-bottom: 0;'>
        본 서비스는 <strong>「특정건축물 정리에 관한 특별조치법」</strong>(시행 2026. 12. 17.)에 따른 양성화 대상 여부 및 예상 과태료를 사전에 가늠해 보실 수 있도록 마련된 자가진단입니다.<br><br>
        정확한 <strong>건축물 유형</strong> 및 <strong>면적(㎡)</strong> 확인이 필요하신 경우, <strong>정부24(www.gov.kr)</strong>에서 건축물대장을 무료로 발급받아 확인하시거나 <strong>관할구청 민원여권과</strong>로 문의하여 주시기 바랍니다.<br><br>
        <span style='color: #C0392B; font-weight: bold;'>※ 주의사항:</span> 과태료(이행강제금 5회분 상당) 부과 및 기한(법 시행 후 18개월) 요건이 존재하므로, 최종 접수는 반드시 관할 지자체 담당 부서 및 건축사와 협의해 주십시오.
    </p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 탭(Tabs) 분할
# ==========================================
tab1, tab2 = st.tabs(["🏛️ 양성화 대상 자가진단", "💰 예상 과태료(이행강제금) 계산"])

# ------------------------------------------
# 탭 1: 양성화 대상 판별
# ------------------------------------------
with tab1:
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
    if building_type == "다세대주택":
        st.markdown("<p style='font-size: 15px; font-weight: bold; margin-bottom: 5px; margin-top: 10px;'>해당 면적 직접 입력 <span style='color:#C0392B;'>(※ 위반부분의 면적을 포함한 세대당 전용면적, ㎡)</span></p>", unsafe_allow_html=True)
        area_str = st.text_input("면적 입력 (다세대)", value="0", label_visibility="collapsed")
        try: area = float(area_str)
        except ValueError: area = 0.0
    elif building_type in ["단독주택", "다가구주택", "근린생활시설 (사실상 주택 사용)"]:
        st.markdown("<p style='font-size: 15px; font-weight: bold; margin-bottom: 5px; margin-top: 10px;'>해당 면적 직접 입력 <span style='color:#C0392B;'>(※ 위반부분의 면적을 포함한 전체 연면적, ㎡)</span></p>", unsafe_allow_html=True)
        area_str = st.text_input("면적 입력 (기타)", value="0", label_visibility="collapsed")
        try: area = float(area_str)
        except ValueError: area = 0.0
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="toss-card">', unsafe_allow_html=True)
    st.markdown('<div class="toss-question">3. 적용 제외 구역 위치 여부</div>', unsafe_allow_html=True)
    st.markdown('<div class="toss-desc">해당 건축물이 보전산지, 개발제한구역, 정비구역 등에 포함되어 있습니까?</div>', unsafe_allow_html=True)
    is_restricted_area = st.radio("제외구역여부", ("해당 없음 (미포함)", "해당됨 (포함)"), index=0, horizontal=True, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("진단 결과 확인하기", type="primary", use_container_width=True):
        show_diagnostic_result(is_completed, is_residential, is_restricted_area, building_type, area)

# ------------------------------------------
# 탭 2: 과태료(이행강제금) 계산
# ------------------------------------------
with tab2:
    st.warning("""
    **💡 [예상 과태료 및 행정 처분 안내]**
    * **본 산출액은 개략적인 예상 금액입니다:** 관할 지자체의 정밀한 현장 조사 및 공식적인 시가표준액 산정 결과에 따라 최종 금액은 달라질 수 있습니다.
    * **사용승인 전 완납 조건:** 양성화(사용승인)를 받으시기 위해서는 해당 과태료가 필수적으로 부과되며, 사용승인 전까지 체납 없이 완납하셔야 합니다. (단, 1년 이내 모두 납부하는 조건으로 우선 발급 가능)
    * **기납부액 차감:** 과거 해당 위반 사항으로 이미 납부하신 이행강제금이 있다면, 부과 시 그 금액만큼 차감됩니다.
    """)

    st.markdown('<div class="toss-card">', unsafe_allow_html=True)
    st.markdown('<div class="toss-question">건축물 위반 정보 입력</div>', unsafe_allow_html=True)
    
    st.markdown("[👉 내 토지 개별공시지가 확인하기 (부동산공시가격알리미)](https://www.realtyprice.kr/)")
    st.markdown("<p style='font-size: 15px; font-weight: bold; margin-bottom: 5px;'>토지 ㎡당 개별공시지가 (원)</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; color: #7F8C8D; margin-bottom: 5px;'>숫자만 입력하시면 콤마(,)는 알아서 인식됩니다. (예: 2,500,000)</p>", unsafe_allow_html=True)
    
    land_price_str = st.text_input("공시지가", value="2,500,000", label_visibility="collapsed")
    try: land_price = int(land_price_str.replace(",", "").strip())
    except ValueError: land_price = 0
        
    st.markdown("<p style='font-size: 15px; font-weight: bold; margin-bottom: 5px; margin-top: 15px;'>위반 면적 (㎡)</p>", unsafe_allow_html=True)
    violation_area_str = st.text_input("위반 면적", value="15", label_visibility="collapsed")
    try: violation_area = float(violation_area_str)
    except ValueError: violation_area = 0.0
    
    st.markdown("<p style='font-size: 15px; font-weight: bold; margin-bottom: 5px; margin-top: 15px;'>건축물 주요 구조</p>", unsafe_allow_html=True)
    structure = st.selectbox("구조", ["철근콘크리트조", "시멘트벽돌조", "경량철골조", "조립식패널조", "철파이프조 (샤시 등)"], index=4, label_visibility="collapsed")
    
    st.markdown("<p style='font-size: 15px; font-weight: bold; margin-bottom: 5px; margin-top: 15px;'>위반(발생) 연도</p>", unsafe_allow_html=True)
    violation_year_str = st.text_input("위반 연도", value="2015", label_visibility="collapsed")
    try: violation_year = int(violation_year_str)
    except ValueError: violation_year = 2015
    
    st.markdown("<p style='font-size: 15px; font-weight: bold; margin-bottom: 5px; margin-top: 15px;'>지자체 조례 감경 비율</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; color: #7F8C8D; margin-bottom: 5px;'>지역별 조례에 따른 미신고/무허가 감경 비율을 선택해 주세요. (예: 부산 미신고 0.6)</p>", unsafe_allow_html=True)
    ordinance_ratio = st.selectbox("조례비율", [0.5, 0.6, 0.7, 0.8, 0.9, 1.0], index=1, label_visibility="collapsed")
    
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("💰 예상 과태료(5회분) 계산하기", type="primary", use_container_width=True):
        if violation_area <= 0 or land_price <= 0:
            st.warning("⚠️ 위반 면적과 공시지가를 정확히 숫자로 입력해 주십시오.")
        else:
            show_fine_result(land_price, violation_area, structure, violation_year, ordinance_ratio)