# app.py
# ---------------------------------------------
# Streamlit: 성과보수 중심 계산기 (안정화 버전)
# - 초기화 on_click 콜백
# - 인용비율 프리셋 → 입력 위젯 순서 유지
# - 성과보수 억/천만 가로 입력 + 단위 라벨
# - 결과: 역산 결과만 카드형 지표
# ---------------------------------------------
import streamlit as st

st.set_page_config(page_title="성과보수 중심 계산기", layout="centered")
st.title("💰 성과보수 중심 계산기")

# -----------------------------
# 세션 상태 기본값
# -----------------------------
defaults = {
    "fee_eok": 0,
    "fee_chunman": 0,
    "ratio_y": 0.0,
    "calculated": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -----------------------------
# 콜백
# -----------------------------
def reset_all():
    st.session_state.fee_eok = 0
    st.session_state.fee_chunman = 0
    st.session_state.ratio_y = 0.0
    st.session_state.calculated = False
    st.rerun()

def set_ratio(v: float):
    st.session_state.ratio_y = float(v)

# -----------------------------
# 상단 바: 초기화 버튼
# -----------------------------
hdr1, hdr2 = st.columns([5, 1])
with hdr2:
    st.button("↺ 초기화", type="secondary", use_container_width=True, on_click=reset_all)

# -----------------------------
# 성과보수 입력(가로 + 단위)
# -----------------------------
st.markdown("#### 📥 성과보수 입력")
c1, c2, c3, c4 = st.columns([1.2, 0.6, 1.2, 0.6])
with c1:
    st.number_input(" ", min_value=0, max_value=5, step=1, key="fee_eok")
with c2:
    st.markdown("#### 억")
with c3:
    st.number_input("  ", min_value=0, max_value=9, step=1, key="fee_chunman")
with c4:
    st.markdown("#### 천만")
st.caption("예: 3억 5천만 원 → 왼쪽 3, 오른쪽 5 (성과보수 최대 5억)")

# -----------------------------
# 인용비율 프리셋 → 입력 위젯
# -----------------------------
st.markdown("#### 📊 원고 인용비율")
pb = st.columns(6)
for col, v in zip(pb, [0, 10, 20, 30, 40, 50]):
    with col:
        st.button(f"{v}%", on_click=set_ratio, args=(float(v),), key=f"preset_{v}")

st.number_input("원고 인용비율 (%)", min_value=0.0, max_value=100.0, step=0.1, key="ratio_y")

# -----------------------------
# 금액 합산 및 제약
# -----------------------------
fee_input = (st.session_state.fee_eok * 100_000_000) + (st.session_state.fee_chunman * 10_000_000)
if fee_input > 500_000_000:
    st.warning("성과보수는 5억 이하여야 합니다.")
fee_label = f"{st.session_state.fee_eok}억 {st.session_state.fee_chunman}천만 원"
st.caption(f"입력된 성과보수: {fee_label}  (= {fee_input/100_000_000:.1f}억 원)")

# -----------------------------
# 계산 버튼
# -----------------------------
if st.button("💡 계산하기"):
    st.session_state.calculated = True

# -----------------------------
# 역산 결과(카드형 지표)
# -----------------------------
if st.session_state.calculated:
    if 0 < fee_input <= 500_000_000 and 0 <= st.session_state.ratio_y < 100:
        fee = fee_input
        z = fee / 0.03                             # 피고 경제적 이익
        x = z / (1 - st.session_state.ratio_y/100) # 총 금액
        y = x * (st.session_state.ratio_y/100)     # 판결 인용액
        ratio_zx = (z / x) * 100
        condition_met = ratio_zx >= 60

        st.markdown("### 📈 역산 결과")
        m1, m2 = st.columns(2)
        with m1:
            st.metric("총 금액 (x)", f"{x/100_000_000:.1f} 억 원")
        with m2:
            st.metric("판결 인용액 (y)", f"{y/100_000_000:.1f} 억 원")

        m3, m4 = st.columns(2)
        with m3:
            st.metric("피고 경제적 이익 (z)", f"{z/100_000_000:.1f} 억 원")
        with m4:
            st.metric("피고 경제적 이익 비율 (z/x)", f"{ratio_zx:.1f} %")

        if condition_met:
            st.success("성과보수 기준 충족: z/x ≥ 60%")
        else:
            st.error("성과보수 기준 미충족: z/x < 60%")

        st.caption(f"입력 기준 · 성과보수: {fee/100_000_000:.1f}억 원 · 인용비율: {st.session_state.ratio_y:.1f}%")
    else:
        st.warning("입력 오류: 성과보수는 5억 이하여야 하며, 인용비율은 100% 미만이어야 합니다.")

