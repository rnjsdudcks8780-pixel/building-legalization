import streamlit as st

# 페이지 설정
st.set_page_config(page_title="특정건축물 양성화 판별기", page_icon="🏠", layout="centered")

st.title("🏠 특정건축물 양성화 대상 판별기")

# --- 주의사항 및 면책 조항 (크고 강조되게) ---
st.warning("""
**🚨 주의사항:** 본 판별기의 결과는 단순 참고용입니다. 
최종적인 양성화 가능 여부는 반드시 관할 지자체 특정건축물 지원센터 상담 및 **건축사**를 통한 정확한 현장 조사를 거쳐야 합니다.
""")

# --- 법령 안내문 (접었다 펴기) ---
with st.expander("📖 양성화 대상 필수 조건 (클릭해서 읽어보세요)", expanded=False):
    st.markdown("""
    **[시행 2026. 12. 17.] 특정건축물 정리에 관한 특별조치법 기준**
    
    다음 조건을 **모두** 만족해야 양성화 심사 대상이 될 수 있습니다.
    * **시점:** 2023년 12월 31일 당시에 사실상 완공된 건축물이어야 합니다.
    * **용도:** 전체 연면적 중 **주거용 비율이 50% 이상**이어야 합니다.
    * **규모:** 
        - 다세대주택: 세대당 전용면적 85㎡ 이하
        - 단독주택: 연면적 165㎡ 이하 (지자체 조례에 따라 최대 330㎡)
        - 다가구주택: 연면적 660㎡ 이하
    * **제외 구역:** 개발제한구역, 보전산지, 도시개발구역, 군사기지, 접도구역 등에는 해당하지 않아야 합니다. (단, 구역 지정 전 건축된 경우 등 일부 예외 있음)
    * **필수 절차:** 건축사가 작성한 설계도서와 현장조사서를 첨부하여 관할 구청에 신고해야 합니다.
    """)

st.divider()

# --- [1단계] 기본 요건 입력 (글씨 크기 확대) ---
st.markdown("### <span style='color:#2C3E50'>1. 기본 요건 확인</span>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("<p style='font-size: 18px; font-weight: bold;'>📅 2023년 12월 31일 이전에 사실상 완공되었습니까?</p>", unsafe_allow_html=True)
    is_completed = st.radio(
        "완공 여부", 
        ("예", "아니오"), 
        index=1,
        label_visibility="collapsed"
    )
with col2:
    st.markdown("<p style='font-size: 18px; font-weight: bold;'>🏠 전체 연면적 중 주거용 비율이 50% 이상입니까?</p>", unsafe_allow_html=True)
    is_residential = st.radio(
        "주거용 비율", 
        ("예", "아니오"), 
        index=1,
        label_visibility="collapsed"
    )

st.write("") # 여백 추가

# --- [2단계] 규모 및 면적 요건 입력 ---
st.markdown("### <span style='color:#2C3E50'>2. 건축물 유형 및 규모 확인</span>", unsafe_allow_html=True)

st.markdown("<p style='font-size: 18px; font-weight: bold;'>🏢 건축물 유형을 선택해주세요</p>", unsafe_allow_html=True)
building_type = st.selectbox(
    "건축물 유형",
    ["선택하세요", "다세대주택", "단독주택", "다가구주택", "근린생활시설 (사실상 주택 사용)"],
    label_visibility="collapsed"
)

area = 0.0
if building_type == "다세대주택":
    st.markdown("<p style='font-size: 18px; font-weight: bold;'>📏 세대당 전용면적을 입력하세요 (㎡)</p>", unsafe_allow_html=True)
    area = st.number_input("면적입력1", min_value=0.0, step=1.0, label_visibility="collapsed")
elif building_type in ["단독주택", "다가구주택", "근린생활시설 (사실상 주택 사용)"]:
    st.markdown("<p style='font-size: 18px; font-weight: bold;'>📏 건축물 전체 연면적을 입력하세요 (㎡)</p>", unsafe_allow_html=True)
    area = st.number_input("면적입력2", min_value=0.0, step=1.0, label_visibility="collapsed")

# --- [3단계] 적용 제외 구역 확인 ---
st.subheader("3. 적용 제외 구역 해당 여부")
st.markdown("건축물이 다음 구역에 포함되어 있습니까? (보전산지, 개발제한구역, 도시개발구역, 정비구역, 접도구역 등)")
is_restricted_area = st.radio("제외 구역 포함 여부", ("포함 안 됨 (해당 없음)", "포함됨"), index=0)

st.divider()

# --- 판별 로직 및 결과 출력 ---
if st.button("🔍 양성화 대상 여부 결과 보기", type="primary", use_container_width=True):
    
    # 1. 탈락 조건 먼저 검사
    if is_completed == "아니오":
        st.error("❌ 대상 아님: 2023년 12월 31일 이전 완공된 건축물만 대상입니다.")
    elif is_residential == "아니오":
        st.error("❌ 대상 아님: 연면적의 50% 이상이 주거용이어야 합니다.")
    elif is_restricted_area == "포함됨":
        st.error("❌ 대상 아님: 개발제한구역, 보전산지 등 적용 제외 구역에 위치하고 있습니다. (단, 구역 지정 전 건축된 경우 예외 심사 가능)")
    elif building_type == "선택하세요":
        st.warning("⚠️ 건축물 유형을 선택해주세요.")
    elif area <= 0:
        st.warning("⚠️ 면적을 정확히 입력해주세요.")
    
    # 2. 통과 시 면적 조건 검사
    else:
        is_pass = False
        reason = ""

        if building_type == "다세대주택":
            if area <= 85:
                is_pass = True
            else:
                reason = "다세대주택은 세대당 전용면적 85㎡ 이하여야 합니다."
                
        elif building_type == "단독주택":
            if area <= 165:
                is_pass = True
            else:
                reason = "단독주택은 연면적 165㎡ 이하여야 합니다. (지자체 조례에 따라 최대 330㎡까지 가능할 수 있음)"
                
        elif building_type == "다가구주택":
            if area <= 660:
                is_pass = True
            else:
                reason = "다가구주택은 연면적 660㎡ 이하여야 합니다."
                
        elif building_type == "근린생활시설 (사실상 주택 사용)":
            if area <= 165: # 단독주택 기준 차용 (실제 법령 해석에 따라 다세대/단독 기준 적용)
                is_pass = True
                st.info("💡 근린생활시설의 경우, 2023년 12월 31일 이전부터 주택으로 사용된 경우에만 한정됩니다.")
            else:
                reason = "면적 기준(예: 165㎡)을 초과하였습니다."

        # 최종 결과 출력
        if is_pass:
            st.success("🎉 축하합니다! 입력하신 정보에 따르면 특정건축물 양성화 **대상일 가능성이 높습니다.**")
            st.markdown("""
            **다음 단계 안내:**
            * 관할 구청(시장·군수·구청장) 특정건축물 지원센터에 방문하여 상담을 진행하세요.
            * 건축사가 작성한 설계도서와 현장조사서를 첨부하여 신고해야 합니다.
            * 이행강제금 체납이 없어야 사용승인서가 발급됩니다. (단, 1년 내 모두 납부 조건으로 승인 가능)
            """)
        else:
            st.error(f"❌ 대상 아님: {reason}")