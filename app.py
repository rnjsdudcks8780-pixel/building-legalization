import streamlit as st
import datetime

# --- 페이지 설정 ---
st.set_page_config(page_title="양성화 대상 판별 & 과태료 계산기", page_icon="🏠", layout="centered")

# --- 커스텀 CSS ---
st.markdown("""
<style>
    .stApp { background-color: #F9FAFB; }
    .toss-card {
        background-color: white; padding: 24px; border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 24px;
    }
    .toss-title { font-size: 26px; font-weight: 800; color: #191F28; margin-bottom: 8px; }
    .toss-subtitle { font-size: 20px; font-weight: 700; color: #333D4B; margin-bottom: 12px; }
    .toss-desc { font-size: 15px; color: #8B95A1; line-height: 1.5; }
    .highlight-box { background-color: #F2F4F6; padding: 16px; border-radius: 8px; margin-top: 16px;}
</style>
""", unsafe_allow_html=True)

# --- 상단 타이틀 ---
st.markdown('<div class="toss-title">특정건축물 양성화 판별 & 과태료 계산기</div>', unsafe_allow_html=True)
st.markdown('<div class="toss-desc">대상 여부 확인부터 예상 과태료(이행강제금 5회분) 계산까지 한 번에 해보세요.</div>', unsafe_allow_html=True)
st.write("")

# ==========================================
# 탭(Tab) 구성: 1. 대상 판별 / 2. 과태료 계산
# ==========================================
tab1, tab2 = st.tabs(["✅ 양성화 대상 판별", "💰 예상 과태료 계산"])

# ------------------------------------------
# 탭 1: 양성화 대상 판별 로직
# ------------------------------------------
with tab1:
    st.markdown('<div class="toss-card">', unsafe_allow_html=True)
    st.markdown('<div class="toss-subtitle">1. 기본 요건 확인</div>', unsafe_allow_html=True)
    is_completed = st.radio("**2023년 12월 31일 이전에 사실상 완공되었나요?**", ("예", "아니오"), index=1)
    is_residential = st.radio("**전체 면적 중 주거용 비율이 50% 이상인가요?**", ("예", "아니오"), index=1)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="toss-card">', unsafe_allow_html=True)
    st.markdown('<div class="toss-subtitle">2. 건축물 유형 및 규모 확인</div>', unsafe_allow_html=True)
    building_type = st.selectbox("건축물 유형", ["선택해주세요", "다세대주택", "단독주택", "다가구주택", "근린생활시설 (주택 사용)"])
    area = 0.0
    if building_type == "다세대주택":
        area = st.number_input("세대당 전용면적 (㎡)", min_value=0.0, step=1.0)
    elif building_type in ["단독주택", "다가구주택", "근린생활시설 (주택 사용)"]:
        area = st.number_input("전체 연면적 (㎡)", min_value=0.0, step=1.0)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="toss-card">', unsafe_allow_html=True)
    st.markdown('<div class="toss-subtitle">3. 제외 구역 해당 여부</div>', unsafe_allow_html=True)
    is_restricted_area = st.radio("**보전산지, 개발제한구역, 정비구역 등에 포함되나요?**", ("해당 없음 (안전함)", "제외 구역 포함됨"), index=0)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("대상 여부 결과 확인", type="primary", use_container_width=True):
        if is_completed == "아니오": st.error("불가: 2023년 12월 31일 이전 완공 건물만 대상입니다.")
        elif is_residential == "아니오": st.error("불가: 주거용 면적이 50% 이상이어야 합니다.")
        elif is_restricted_area == "제외 구역 포함됨": st.error("불가: 적용 제외 구역에 위치하고 있습니다.")
        elif building_type == "선택해주세요": st.warning("건축물 유형을 선택해주세요.")
        elif area <= 0: st.warning("면적을 정확히 입력해주세요.")
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
                st.success("🎉 양성화 대상일 가능성이 높습니다!")
                st.info("오른쪽 [예상 과태료 계산] 탭으로 이동하여 납부 예상 금액을 확인해 보세요.")
            else:
                st.error(f"❌ 대상 아님: {reason}")


# ------------------------------------------
# 탭 2: 이행강제금(과태료) 계산 로직
# ------------------------------------------
with tab2:
    st.warning("""
    **💡 [예상 과태료 및 행정 처분 안내]**
    * **본 산출액은 개략적인 예상 금액입니다:** 입력하신 정보를 바탕으로 산출된 '추정치'이며, 인허가 과정에서 관할 지자체의 정밀한 현장 조사 및 공식적인 시가표준액 산정 결과에 따라 최종 금액은 달라질 수 있습니다.
    * **사용승인 전 완납 조건:** 합법적인 건축물로 양성화(사용승인)를 받으시기 위해서는 해당 과태료가 필수적으로 부과되며, 사용승인 전까지 체납 없이 완납하셔야 합니다. (단, 1년 이내 모두 납부하는 조건으로 사용승인서 우선 발급 가능)
    * **기납부액 차감:** 과거 해당 위반 사항으로 이미 납부하신 이행강제금이 있다면, 부과 시 그 금액만큼 차감됩니다.
    """)

    st.markdown('<div class="toss-card">', unsafe_allow_html=True)
    st.markdown('<div class="toss-subtitle">건축물 위반 정보 입력</div>', unsafe_allow_html=True)
    
    st.markdown("[👉 내 토지 개별공시지가 확인하기 (부동산공시가격알리미)](https://www.realtyprice.kr/)")
    land_price = st.number_input("토지 ㎡당 개별공시지가 (원)", min_value=0, step=10000, value=1000000)
    
    violation_area = st.number_input("위반 면적 (㎡)", min_value=0.0, step=1.0, value=15.0)
    
    structure = st.selectbox("건축물 주요 구조", ["철근콘크리트조", "시멘트벽돌조", "경량철골조", "조립식패널조"])
    
    violation_year = st.number_input("위반(발생) 연도", min_value=1980, max_value=2023, value=2015)
    
    violation_type = st.radio("위반 유형 (택 1)", ["건축 미신고 (소규모)", "건축 무허가 (대규모)"])
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("💰 예상 과태료(5회분) 계산하기", type="primary", use_container_width=True):
        if violation_area == 0 or land_price == 0:
            st.warning("면적과 공시지가를 정확히 입력해주세요.")
        else:
            # 1. 신축가격기준액 (2026년 주거/상업 860,000원 기준)
            base_price = 860000 
            
            # 2. 구조지수 매핑 (단순화)
            if structure == "철근콘크리트조": str_index = 1.0
            elif structure == "시멘트벽돌조": str_index = 0.9
            elif structure == "경량철골조": str_index = 0.65
            elif structure == "조립식패널조": str_index = 0.55
            else: str_index = 1.0
            
            # 3. 위치지수 매핑 (공시지가 기반 러프한 표준 구간 설정)
            if land_price < 500000: loc_index = 0.94
            elif land_price < 1000000: loc_index = 1.00
            elif land_price < 3000000: loc_index = 1.15
            elif land_price < 7000000: loc_index = 1.27
            else: loc_index = 1.40
            
            # 4. 잔가율 계산 (단순 정액법 감가 상각 가정 - 매년 2% 감가, 최저 20%)
            age = 2026 - violation_year
            depreciation_rate = max(0.2, 1.0 - (age * 0.02))
            
            # 5. 시가표준액 산출 (1㎡당)
            # 수식: 신축가격기준액 * 구조지수 * 용도지수(1.0가정) * 위치지수 * 잔가율
            unit_price = base_price * str_index * 1.0 * loc_index * depreciation_rate
            
            # 6. 1회분 이행강제금 계산 (사용자 제공 로직)
            # 수식: 시가표준액 * 위반면적 * 0.5 * 무단증축가중(0.85) * 조례비율(미신고 0.7 or 무허가 0.9)
            penalty_ratio = 0.7 if violation_type == "건축 미신고 (소규모)" else 0.9
            one_time_fine = unit_price * violation_area * 0.5 * 0.85 * penalty_ratio
            
            # 7. 양성화 과태료 (5회분)
            total_fine = one_time_fine * 5

            # 결과 출력
            st.markdown('<div class="toss-card">', unsafe_allow_html=True)
            st.markdown('<div class="toss-title">📊 계산 결과</div>', unsafe_allow_html=True)
            st.markdown(f"**추정 1㎡당 시가표준액:** 약 {int(unit_price):,} 원")
            st.markdown(f"**1회분 이행강제금 예상액:** 약 {int(one_time_fine):,} 원")
            
            st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center; color: #3182F6;'>최종 예상 과태료(5회분)</h3>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='text-align: center; color: #191F28;'>약 {int(total_fine):,} 원</h2>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)