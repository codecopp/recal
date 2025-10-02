# app.py
# ---------------------------------------------
# Streamlit: 2탭 계산기 (성과보수 중심 / 총 금액 중심)
# - 각 탭 독립 세션키 사용
# - 억/천만 가로 입력
# - 프리셋 버튼 + 수동 비율 입력
# - 결과는 카드형 지표
# - 총 금액 중심 탭: 성과보수 상한 5억 적용
# ---------------------------------------------
import streamlit as st

st.set_page_config(page_title="성과보수·총금액 계산기", layout="centered")
st.title("💼 성과보수·총금액 계산기")

# -----------------------------
# 공통 유틸
# -----------------------------
def init_defaults(d: dict):
    for k, v in d.items():
        if k not in st.session_state:
            st.session_state[k] = v

def reset_keys(keys):
    for k, v in keys.items():
        st.session_state[k] = v
    st.rerun()

def amt_from_eok_chunman(eok_key: str, chun_key: str) -> int:
    return (st.session_state[eok_key] * 100_000_000) + (st.session_state[chun_key] * 10_000_000)

def label_eok_chunman(eok_key: str, chun_key: str) -> str:
    return f"{st.session_state[eok_key]}억 {st.session_state[chun_key]}천만 원"

CAP_FEE = 500_000_000  # 성과보수 상한 5억

# -----------------------------
# 탭 구성
# -----------------------------
tab1, tab2 = st.tabs(["성과보수 중심", "총 금액 중심"])

# =========================================================
# 탭 1: 성과보수 중심
# =========================================================
with tab1:
    init_defaults({
        "fee_eok": 0,          # 억
        "fee_chunman": 0,      # 천만
        "ratio_y_1": 0.0,      # 원고 인용비율 (%)
        "calculated_1": False,
    })

    # 콜백
    def _reset_tab1():
        reset_keys({
            "fee_eok": 0,
            "fee_chunman": 0,
            "ratio_y_1": 0.0,
            "calculated_1": False,
        })

    def _set_ratio_tab1(v: float):
        st.session_state["ratio_y_1"] = float(v)

    # 헤더 버튼
    h1, h2 = st.columns([5, 1])
    with h2:
        st.button("↺ 초기화", type="secondary", use_container_width=True, on_click=_reset_tab1, key="reset1")

    # 성과보수 입력
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

    # 인용비율 프리셋 + 입력
    st.markdown("#### 📊 원고 인용비율")
    pb = st.columns(6)
    for col, v in zip(pb, [0, 10, 20, 30, 40, 50]):
        with col:
            st.button(f"{v}%", on_click=_set_ratio_tab1, args=(float(v),), key=f"preset1_{v}")
    st.number_input("원고 인용비율 (%)", min_value=0.0, max_value=100.0, step=0.1, key="ratio_y_1")

    # 금액 합산 및 제약
    fee_input = amt_from_eok_chunman("fee_eok", "fee_chunman")
    if fee_input > CAP_FEE:
        st.warning("성과보수는 5억 이하여야 합니다.")
    st.caption(f"입력된 성과보수: {label_eok_chunman('fee_eok','fee_chunman')}  (= {fee_input/100_000_000:.1f}억 원)")

    # 계산 버튼
    if st.button("💡 계산하기", key="calc1"):
        st.session_state["calculated_1"] = True

    # 결과
    if st.session_state["calculated_1"]:
        if 0 < fee_input <= CAP_FEE and 0 <= st.session_state["ratio_y_1"] < 100:
            fee = fee_input
            r = st.session_state["ratio_y_1"] / 100.0
            z = fee / 0.03              # 피고 경제적 이익
            x = z / (1 - r)             # 총 금액
            y = x * r                   # 판결 인용액
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
                st.metric("경제적 이익 비율 (z/x)", f"{ratio_zx:.1f} %")

            if condition_met:
                st.success("성과보수 기준 충족: z/x ≥ 60%")
            else:
                st.error("성과보수 기준 미충족: z/x < 60%")

            st.caption(f"입력 기준 · 성과보수: {fee/100_000_000:.1f}억 원 · 인용비율: {st.session_state['ratio_y_1']:.1f}%")
        else:
            st.warning("입력 오류: 성과보수는 5억 이하여야 하며, 인용비율은 100% 미만이어야 합니다.")

# =========================================================
# 탭 2: 총 금액 중심  (성과보수 상한 5억 적용)
# =========================================================
with tab2:
    init_defaults({
        "total_eok": 0,        # 억
        "total_chunman": 0,    # 천만
        "ratio_y_2": 0.0,      # 원고 인용비율 (%)
        "calculated_2": False,
    })

    # 콜백
    def _reset_tab2():
        reset_keys({
            "total_eok": 0,
            "total_chunman": 0,
            "ratio_y_2": 0.0,
            "calculated_2": False,
        })

    def _set_ratio_tab2(v: float):
        st.session_state["ratio_y_2"] = float(v)

    # 헤더 버튼
    h1b, h2b = st.columns([5, 1])
    with h2b:
        st.button("↺ 초기화", type="secondary", use_container_width=True, on_click=_reset_tab2, key="reset2")

    # 총 금액 입력
    st.markdown("#### 📥 총 금액 입력")
    d1, d2, d3, d4 = st.columns([1.2, 0.6, 1.2, 0.6])
    with d1:
        st.number_input(" ", min_value=0, max_value=999, step=1, key="total_eok")
    with d2:
        st.markdown("#### 억")
    with d3:
        st.number_input("  ", min_value=0, max_value=9, step=1, key="total_chunman")
    with d4:
        st.markdown("#### 천만")
    st.caption("예: 12억 3천만 원 → 왼쪽 12, 오른쪽 3")

    # 인용비율 프리셋 + 입력
    st.markdown("#### 📊 원고 인용비율")
    pb2 = st.columns(6)
    for col, v in zip(pb2, [0, 10, 20, 30, 40, 50]):
        with col:
            st.button(f"{v}%", on_click=_set_ratio_tab2, args=(float(v),), key=f"preset2_{v}")
    st.number_input("원고 인용비율 (%)", min_value=0.0, max_value=100.0, step=0.1, key="ratio_y_2")

    # 총 금액 표시
    total_input = amt_from_eok_chunman("total_eok", "total_chunman")
    st.caption(f"입력된 총 금액: {label_eok_chunman('total_eok','total_chunman')}  (= {total_input/100_000_000:.1f}억 원)")

    # 계산 버튼
    if st.button("💡 계산하기", key="calc2"):
        st.session_state["calculated_2"] = True

    # 결과
    if st.session_state["calculated_2"]:
        if total_input > 0 and 0 <= st.session_state["ratio_y_2"] < 100:
            x = total_input
            r2 = st.session_state["ratio_y_2"] / 100.0
            y = x * r2                    # 판결 인용액
            z = x * (1 - r2)              # 피고 경제적 이익
            fee_raw = z * 0.03            # 이론상 성과보수
            capped = fee_raw > CAP_FEE
            fee = min(fee_raw, CAP_FEE)   # 상한 적용

            ratio_zx = (z / x) * 100 if x > 0 else 0.0
            condition_met = ratio_zx >= 60

            st.markdown("### 📈 계산 결과")
            m1b, m2b = st.columns(2)
            with m1b:
                st.metric("총 금액 (x)", f"{x/100_000_000:.1f} 억 원")
            with m2b:
                st.metric("판결 인용액 (y)", f"{y/100_000_000:.1f} 억 원")

            m3b, m4b = st.columns(2)
            with m3b:
                st.metric("피고 경제적 이익 (z)", f"{z/100_000_000:.1f} 억 원")
            with m4b:
                st.metric("성과보수 (3%·fee)", f"{fee/100_000_000:.2f} 억 원")

            if capped:
                st.warning(f"성과보수 상한 적용: 이론값 {fee_raw/100_000_000:.2f}억 → 지급가능 최대 {CAP_FEE/100_000_000:.2f}억")

            st.metric("경제적 이익 비율 (z/x)", f"{ratio_zx:.1f} %")
            if condition_met:
                st.success("성과보수 기준 충족: z/x ≥ 60%")
            else:
                st.error("성과보수 기준 미충족: z/x < 60%")

            st.caption(
                f"입력 기준 · 총 금액: {x/100_000_000:.1f}억 · 인용비율: {st.session_state['ratio_y_2']:.1f}% · "
                f"성과보수 상한: {CAP_FEE/100_000_000:.1f}억"
            )
        else:
            st.warning("입력 오류: 총 금액은 0 초과, 인용비율은 100% 미만이어야 합니다.")
