import re
import numpy as np
import pandas as pd
from PIL import Image
import streamlit as st

# 嘗試載入 EasyOCR 模組
try:
    import easyocr

    ocr_available = True
except ImportError:
    ocr_available = False

st.set_page_config(
    page_title="寒霜啟示錄 - 全功能戰術指揮系統",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# 全局 UI / 字體大小 / 樣式注入 (CSS 優化)
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    /* 全局字體大小與行高優化 */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang TC", "Microsoft JhengHei", sans-serif;
        font-size: 17px !important;
    }
    
    /* TAB 頁籤標題放大 */
    button[data-baseweb="tab"] div p {
        font-size: 1.15rem !important;
        font-weight: 700 !important;
    }
    
    /* st.metric 數據指標放大與加粗 */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #424242 !important;
    }
    
    /* 輸入框與 Selectbox 字體放大 */
    .stNumberInput input, .stSelectbox div, .stTextInput input {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    
    /* Dataframe / Table 字體加大與間距優化 */
    div[data-testid="stDataFrame"] {
        font-size: 1.15rem !important;
    }
    div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {
        padding: 10px !important;
    }
    
    /* 按鈕字體放大 */
    .stButton button {
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("❄️ 寒霜啟示錄 - 戰報分析與模擬診斷系統")

# ---------------------------------------------------------
# 選單常數設定
# ---------------------------------------------------------
HERO_LIST = [
    "【1代-盾】赫羅尼莫 (Jeronimo)",
    "【1代-盾】娜塔莉亞 (Natalia)",
    "【1代-矛】茉莉 (Molly)",
    "【1代-射】津曼 (Zinman)",
    "【2代-盾】弗林特 (Flint)",
    "【2代-射】阿隆索 (Alonso)",
    "【2代-矛】菲蘭德 (Philly)",
    "【3代-矛】米婭 (Mia)",
    "【3代-射】格雷格 (Greg)",
    "【3代-盾】羅根 (Logan)",
    "【4代-盾】阿赫摩斯 (Ahmose)",
    "【4代-矛】玲奈 (Reina)",
    "【4代-射】琳恩 (Lynn)",
    "【5代-盾】赫克托 (Hector)",
    "【5代-矛】芮妮 (Renee)",
    "【5代-射】格溫 (Gwen)",
    "【6代-盾】無名 (Wu Ming)",
    "【6代-射】韋恩 (Wayne)",
    "【6代-矛】諾拉 (Norah)",
    "【7代-射】布拉德利 (Bradley)",
    "【7代-矛】艾迪絲 (Edith)",
    "【7代-射】哥頓 (Gordon)",
    "【紫卡-盾】謝爾蓋 (Sergey)",
    "【紫卡-矛】杰西 (Jessie) - 傷害+",
    "【紫卡-矛】派翠克 (Patrick) - 生命/恢復+",
    "【紫卡-射】巴希提 (Bahiti)",
    "【紫卡-射】書允 (Seo-yoon)",
    "無 / 其他普通英雄",
]

STAR_OPTIONS = [
    "5 星 (100% 技能效果)",
    "4 星 (80% 技能效果)",
    "3 星 (60% 技能效果)",
    "2 星 (40% 技能效果)",
    "1 星 (20% 技能效果)",
]

# ---------------------------------------------------------
# Session State 預設值與初始化
# ---------------------------------------------------------
# ---------------------------------------------------------
# Session State 預設值與初始化 (全清空/歸零版本)
# ---------------------------------------------------------
defaults = {
    "a_name": "",
    "d_name": "",
    # 攻方 兵量 / 平均階級 / 平均火晶
    "a_inf_cnt": 0,
    "a_inf_tier": 10.0,
    "a_inf_fc": 0.0,
    "a_lan_cnt": 0,
    "a_lan_tier": 10.0,
    "a_lan_fc": 0.0,
    "a_mar_cnt": 0,
    "a_mar_tier": 10.0,
    "a_mar_fc": 0.0,
    # 守方 兵量 / 平均階級 / 平均火晶
    "d_inf_cnt": 0,
    "d_inf_tier": 10.0,
    "d_inf_fc": 0.0,
    "d_lan_cnt": 0,
    "d_lan_tier": 10.0,
    "d_lan_fc": 0.0,
    "d_mar_cnt": 0,
    "d_mar_tier": 10.0,
    "d_mar_fc": 0.0,
    # 12 大屬性 (%) 歸零
    "a_i_a": 0.0,
    "a_i_d": 0.0,
    "a_i_l": 0.0,
    "a_i_h": 0.0,
    "a_l_a": 0.0,
    "a_l_d": 0.0,
    "a_l_l": 0.0,
    "a_l_h": 0.0,
    "a_m_a": 0.0,
    "a_m_d": 0.0,
    "a_m_l": 0.0,
    "a_m_h": 0.0,
    "d_i_a": 0.0,
    "d_i_d": 0.0,
    "d_i_l": 0.0,
    "d_i_h": 0.0,
    "d_l_a": 0.0,
    "d_l_d": 0.0,
    "d_l_l": 0.0,
    "d_l_h": 0.0,
    "d_m_a": 0.0,
    "d_m_d": 0.0,
    "d_m_l": 0.0,
    "d_m_h": 0.0,
    # 特殊加成 - 歸零
    "a_sp_def_eff": 0.0,
    "a_sp_rally_atk": 0.0,
    "a_sp_rally_sth": 0.0,
    "a_sp_pet_atk": 0.0,
    "a_sp_pet_def": 0.0,
    "a_sp_pet_sth": 0.0,
    "a_sp_pet_hp": 0.0,
    "a_sp_pet_de_def": 0.0,
    "a_sp_pet_de_sth": 0.0,
    "a_sp_pet_de_hp": 0.0,
    "a_sp_exp_de_sth": 0.0,
    "d_sp_def_eff": 0.0,
    "d_sp_city_atk": 0.0,
    "d_sp_city_def": 0.0,
    "d_sp_city_sth": 0.0,
    "d_sp_pet_atk": 0.0,
    "d_sp_pet_def": 0.0,
    "d_sp_pet_sth": 0.0,
    "d_sp_pet_hp": 0.0,
    "d_sp_pet_de_def": 0.0,
    "d_sp_pet_de_sth": 0.0,
    "d_sp_pet_de_hp": 0.0,
    "d_sp_exp_de_sth": 0.0,
}

# 補全英雄與專武設定預設值
for i in range(1, 4):
    defaults[f"a_l{i}_hero"] = HERO_LIST[0]
    defaults[f"a_l{i}_stars"] = STAR_OPTIONS[0]
    defaults[f"a_l{i}_wp"] = 5
    defaults[f"d_l{i}_hero"] = HERO_LIST[0]
    defaults[f"d_l{i}_stars"] = STAR_OPTIONS[0]
    defaults[f"d_l{i}_wp"] = 5

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# 一鍵清空/重置 回呼函數
def reset_all_inputs():
    for key, default_val in defaults.items():
        st.session_state[key] = default_val


# ---------------------------------------------------------
# 快取載入 EasyOCR 模型
# ---------------------------------------------------------
@st.cache_resource
def load_ocr_reader():
    if ocr_available:
        return easyocr.Reader(["ch_tra", "en"], gpu=False)
    return None


tab_input, tab_special, tab_compare, tab_heroes, tab_whatif, tab_advice, tab_dict = st.tabs(
    [
        "📸 截圖辨識與基礎面板",
        "🌟 特殊加成區 (寵物/集結/守城)",
        "📊 12大屬性與 Delta",
        "🦸‍♂️ 1~7代英雄/專武與寵物系統",
        "🧮 配兵推薦與 What-If 模擬",
        "💡 本地 AI 戰術診斷報告",
        "📖 戰術名詞小百科",
    ]
)


def calc_troop_weight(avg_tier: float, avg_fc: float) -> float:
    fc_points = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    fc_weights = [0.60, 0.68, 0.76, 0.84, 0.92, 1.00, 1.08, 1.18, 1.32]
    base_fc_w = float(np.interp(avg_fc, fc_points, fc_weights))

    if avg_tier >= 10.0:
        tier_mult = 1.0 + (avg_tier - 10.0) * 0.15
    else:
        tier_mult = max(0.1, 1.0 - (10.0 - avg_tier) * 0.10)

    return base_fc_w * tier_mult


# ---------------------------------------------------------
# TAB 1: 截圖辨識與面板
# ---------------------------------------------------------
with tab_input:
    st.button("🧹 一鍵清空/重置所有數值", on_click=reset_all_inputs)

    st.subheader("🖼️ 1. 上傳戰報與面板截圖")
    uploaded_files = st.file_uploader(
        "請上傳戰報或特殊加成截圖 (PNG/JPG)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        files_to_show = uploaded_files[:6]
        cols = st.columns(min(len(files_to_show), 4))
        for idx, file in enumerate(files_to_show):
            image = Image.open(file)
            with cols[idx % 4]:
                st.image(image, caption=f"截圖 {idx + 1}", width="stretch")

        st.markdown("---")
        if not ocr_available:
            st.warning("⚠️ 系統尚未加載 EasyOCR 套件，請檢查環境。")
        else:
            if st.button("🚀 啟動 AI 辨識基礎屬性", type="primary"):
                with st.spinner("AI 解析中..."):
                    try:
                        reader = load_ocr_reader()
                        extracted_text = []

                        for file in files_to_show:
                            img = Image.open(file).convert("RGB")
                            img.thumbnail((1200, 1200))
                            img_np = np.array(img)

                            results = reader.readtext(img_np, detail=0)
                            extracted_text.extend(results)

                        pct_numbers = []
                        for t in extracted_text:
                            found = re.findall(
                                r"([+-]?\d+[\.\,]\d+|[+-]?\d+)\%", t
                            )
                            for f in found:
                                try:
                                    pct_numbers.append(
                                        float(f.replace(",", "."))
                                    )
                                except ValueError:
                                    pass

                        keys_all = [
                            "a_i_a",
                            "a_i_d",
                            "a_i_l",
                            "a_i_h",
                            "a_l_a",
                            "a_l_d",
                            "a_l_l",
                            "a_l_h",
                            "a_m_a",
                            "a_m_d",
                            "a_m_l",
                            "a_m_h",
                            "d_i_a",
                            "d_i_d",
                            "d_i_l",
                            "d_i_h",
                            "d_l_a",
                            "d_l_d",
                            "d_l_l",
                            "d_l_h",
                            "d_m_a",
                            "d_m_d",
                            "d_m_l",
                            "d_m_h",
                        ]
                        for idx, k in enumerate(keys_all):
                            if idx < len(pct_numbers):
                                st.session_state[k] = abs(pct_numbers[idx])

                        st.success(
                            "✅ 已完成 12 大基礎屬性解析！若有誤差請於下方手動修正。"
                        )
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ OCR 辨識失敗：{e}")

    st.markdown("---")
    st.subheader("✏️ 2. 玩家資訊與三兵種兵量/火晶/階級獨立設定")

    col_a, col_d = st.columns(2)

    with col_a:
        st.header("⚔️ 攻擊方 (Attacker)")
        st.text_input("玩家名稱", key="a_name")

        st.markdown("**🛡️ 盾兵獨立設定**")
        ca_i1, ca_i2, ca_i3 = st.columns(3)
        with ca_i1:
            st.number_input(
                "🛡️ 數量", min_value=0, step=10000, key="a_inf_cnt"
            )
        with ca_i2:
            st.number_input(
                "階級 (ex:10.6)",
                min_value=1.0,
                max_value=11.0,
                step=0.1,
                key="a_inf_tier",
            )
        with ca_i3:
            st.number_input(
                "火晶 (ex:6.8)",
                min_value=0.0,
                max_value=8.0,
                step=0.1,
                key="a_inf_fc",
            )

        st.markdown("**🗡️ 矛兵獨立設定**")
        ca_l1, ca_l2, ca_l3 = st.columns(3)
        with ca_l1:
            st.number_input(
                "🗡️ 數量", min_value=0, step=10000, key="a_lan_cnt"
            )
        with ca_l2:
            st.number_input(
                "階級 (ex:10.6)",
                min_value=1.0,
                max_value=11.0,
                step=0.1,
                key="a_lan_tier",
            )
        with ca_l3:
            st.number_input(
                "火晶 (ex:6.8)",
                min_value=0.0,
                max_value=8.0,
                step=0.1,
                key="a_lan_fc",
            )

        st.markdown("**🏹 射手獨立設定**")
        ca_m1, ca_m2, ca_m3 = st.columns(3)
        with ca_m1:
            st.number_input(
                "🏹 數量", min_value=0, step=10000, key="a_mar_cnt"
            )
        with ca_m2:
            st.number_input(
                "階級 (ex:10.6)",
                min_value=1.0,
                max_value=11.0,
                step=0.1,
                key="a_mar_tier",
            )
        with ca_m3:
            st.number_input(
                "火晶 (ex:6.8)",
                min_value=0.0,
                max_value=8.0,
                step=0.1,
                key="a_mar_fc",
            )

        a_w_inf = st.session_state.a_inf_cnt * calc_troop_weight(
            st.session_state.a_inf_tier, st.session_state.a_inf_fc
        )
        a_w_lan = st.session_state.a_lan_cnt * calc_troop_weight(
            st.session_state.a_lan_tier, st.session_state.a_lan_fc
        )
        a_w_mar = st.session_state.a_mar_cnt * calc_troop_weight(
            st.session_state.a_mar_tier, st.session_state.a_mar_fc
        )
        a_total_cnt = (
            st.session_state.a_inf_cnt
            + st.session_state.a_lan_cnt
            + st.session_state.a_mar_cnt
        )
        a_total_w_cnt = a_w_inf + a_w_lan + a_w_mar

        st.info(
            f"⚔️ **攻擊方加權戰力**：**{a_total_w_cnt:,.0f}** | 總兵力：**{a_total_cnt:,}**"
        )

        st.caption("📈 攻擊方 12 大屬性 (%)")
        ca1, ca2 = st.columns(2)
        with ca1:
            st.number_input("盾兵攻擊%", key="a_i_a")
            st.number_input("盾兵防禦%", key="a_i_d")
            st.number_input("盾兵殺傷%", key="a_i_l")
            st.number_input("盾兵生命%", key="a_i_h")
            st.number_input("矛兵攻擊%", key="a_l_a")
            st.number_input("矛兵防禦%", key="a_l_d")
        with ca2:
            st.number_input("矛兵殺傷%", key="a_l_l")
            st.number_input("矛兵生命%", key="a_l_h")
            st.number_input("射手攻擊%", key="a_m_a")
            st.number_input("射手防禦%", key="a_m_d")
            st.number_input("射手殺傷%", key="a_m_l")
            st.number_input("射手生命%", key="a_m_h")

    with col_d:
        st.header("🏰 防守方 (Defender)")
        st.text_input("玩家名稱", key="d_name")

        st.markdown("**🛡️ 盾兵獨立設定**")
        cd_i1, cd_i2, cd_i3 = st.columns(3)
        with cd_i1:
            st.number_input(
                "🛡️ 數量", min_value=0, step=10000, key="d_inf_cnt"
            )
        with cd_i2:
            st.number_input(
                "階級 (ex:10.6)",
                min_value=1.0,
                max_value=11.0,
                step=0.1,
                key="d_inf_tier",
            )
        with cd_i3:
            st.number_input(
                "火晶 (ex:6.8)",
                min_value=0.0,
                max_value=8.0,
                step=0.1,
                key="d_inf_fc",
            )

        st.markdown("**🗡️ 矛兵獨立設定**")
        cd_l1, cd_l2, cd_l3 = st.columns(3)
        with cd_l1:
            st.number_input(
                "🗡️ 數量", min_value=0, step=10000, key="d_lan_cnt"
            )
        with cd_l2:
            st.number_input(
                "階級 (ex:10.6)",
                min_value=1.0,
                max_value=11.0,
                step=0.1,
                key="d_lan_tier",
            )
        with cd_l3:
            st.number_input(
                "火晶 (ex:6.8)",
                min_value=0.0,
                max_value=8.0,
                step=0.1,
                key="d_lan_fc",
            )

        st.markdown("**🏹 射手獨立設定**")
        cd_m1, cd_m2, cd_m3 = st.columns(3)
        with cd_m1:
            st.number_input(
                "🏹 數量", min_value=0, step=10000, key="d_mar_cnt"
            )
        with cd_m2:
            st.number_input(
                "階級 (ex:10.6)",
                min_value=1.0,
                max_value=11.0,
                step=0.1,
                key="d_mar_tier",
            )
        with cd_m3:
            st.number_input(
                "火晶 (ex:6.8)",
                min_value=0.0,
                max_value=8.0,
                step=0.1,
                key="d_mar_fc",
            )

        d_w_inf = st.session_state.d_inf_cnt * calc_troop_weight(
            st.session_state.d_inf_tier, st.session_state.d_inf_fc
        )
        d_w_lan = st.session_state.d_lan_cnt * calc_troop_weight(
            st.session_state.d_lan_tier, st.session_state.d_lan_fc
        )
        d_w_mar = st.session_state.d_mar_cnt * calc_troop_weight(
            st.session_state.d_mar_tier, st.session_state.d_mar_fc
        )
        d_total_cnt = (
            st.session_state.d_inf_cnt
            + st.session_state.d_lan_cnt
            + st.session_state.d_mar_cnt
        )
        d_total_w_cnt = d_w_inf + d_w_lan + d_w_mar

        st.info(
            f"🏰 **防守方加權戰力**：**{d_total_w_cnt:,.0f}** | 總兵力：**{d_total_cnt:,}**"
        )

        st.caption("📈 防守方 12 大屬性 (%)")
        cd1, cd2 = st.columns(2)
        with cd1:
            st.number_input("盾兵攻擊%", key="d_i_a")
            st.number_input("盾兵防禦%", key="d_i_d")
            st.number_input("盾兵殺傷%", key="d_i_l")
            st.number_input("盾兵生命%", key="d_i_h")
            st.number_input("矛兵攻擊%", key="d_l_a")
            st.number_input("矛兵防禦%", key="d_l_d")
        with cd2:
            st.number_input("矛兵殺傷%", key="d_l_l")
            st.number_input("矛兵生命%", key="d_l_h")
            st.number_input("射手攻擊%", key="d_m_a")
            st.number_input("射手防禦%", key="d_m_d")
            st.number_input("射手殺傷%", key="d_m_l")
            st.number_input("射手生命%", key="d_m_h")

# ---------------------------------------------------------
# TAB 2: 特殊加成區
# ---------------------------------------------------------
with tab_special:
    st.header("🌟 特殊加成說明區")
    col_sp_a, col_sp_d = st.columns(2)

    with col_sp_a:
        st.subheader("⚔️ 攻擊方 (左欄/紅字)")
        st.number_input("集結部隊攻擊力 (%)", key="a_sp_rally_atk")
        st.number_input("集結部隊殺傷力 (%)", key="a_sp_rally_sth")
        st.number_input("部隊防禦力增益效果 (%)", key="a_sp_def_eff")

        st.markdown("**🐾 寵物技能加成 (攻方)**")
        st.number_input("攻擊力增益 (寵物技能) %", key="a_sp_pet_atk")
        st.number_input("防禦力增益 (寵物技能) %", key="a_sp_pet_def")
        st.number_input("殺傷力增益 (寵物技能) %", key="a_sp_pet_sth")
        st.number_input("生命值增益 (寵物技能) %", key="a_sp_pet_hp")

        st.markdown("**📉 敵方減益效果 (攻方對守方施加)**")
        st.number_input("敵方防禦力減益 (寵物技能) %", key="a_sp_pet_de_def")
        st.number_input("敵方殺傷力減益 (寵物技能) %", key="a_sp_pet_de_sth")
        st.number_input("敵方生命值減益 (寵物技能) %", key="a_sp_pet_de_hp")
        st.number_input("敵方殺傷力減益 (專家技能) %", key="a_sp_exp_de_sth")

    with col_sp_d:
        st.subheader("🏰 防守方 (右欄/綠字)")
        st.number_input("守城部隊攻擊力 (%)", key="d_sp_city_atk")
        st.number_input("守城部隊防禦力 (%)", key="d_sp_city_def")
        st.number_input("守城部隊殺傷力 (%)", key="d_sp_city_sth")
        st.number_input("部隊防禦力增益效果 (%)", key="d_sp_def_eff")

        st.markdown("**🐾 寵物技能加成 (守方)**")
        st.number_input("攻擊力增益 (寵物技能) %", key="d_sp_pet_atk")
        st.number_input("防禦力增益 (寵物技能) %", key="d_sp_pet_def")
        st.number_input("殺傷力增益 (寵物技能) %", key="d_sp_pet_sth")
        st.number_input("生命值增益 (寵物技能) %", key="d_sp_pet_hp")

        st.markdown("**📉 敵方減益效果 (守方對攻方施加)**")
        st.number_input("敵方防禦力減益 (寵物技能) %", key="d_sp_pet_de_def")
        st.number_input("敵方殺傷力減益 (寵物技能) %", key="d_sp_pet_de_sth")
        st.number_input("敵方生命值減益 (寵物技能) %", key="d_sp_pet_de_hp")
        st.number_input("敵方殺傷力減益 (專家技能) %", key="d_sp_exp_de_sth")

# ---------------------------------------------------------
# TAB 3: 動態 12 大屬性對比表
# ---------------------------------------------------------
with tab_compare:
    st.header("📊 12 大屬性動態 Delta 對比表")

    stats_list = [
        "盾兵-攻擊",
        "盾兵-防禦",
        "盾兵-殺傷",
        "盾兵-生命",
        "矛兵-攻擊",
        "矛兵-防禦",
        "矛兵-殺傷",
        "矛兵-生命",
        "射手-攻擊",
        "射手-防禦",
        "射手-殺傷",
        "射手-生命",
    ]
    a_keys = [
        "a_i_a",
        "a_i_d",
        "a_i_l",
        "a_i_h",
        "a_l_a",
        "a_l_d",
        "a_l_l",
        "a_l_h",
        "a_m_a",
        "a_m_d",
        "a_m_l",
        "a_m_h",
    ]
    d_keys = [
        "d_i_a",
        "d_i_d",
        "d_i_l",
        "d_i_h",
        "d_l_a",
        "d_l_d",
        "d_l_l",
        "d_l_h",
        "d_m_a",
        "d_m_d",
        "d_m_l",
        "d_m_h",
    ]

    a_vals = [st.session_state[k] for k in a_keys]
    d_vals = [st.session_state[k] for k in d_keys]
    diffs = [round(a - d, 1) for a, d in zip(a_vals, d_vals)]

    col_a_head = f"{st.session_state.a_name} (%)"
    col_d_head = f"{st.session_state.d_name} (%)"
    col_diff_head = "屬性差距 (攻 - 守)"

    df_compare = pd.DataFrame({
        "屬性項目": stats_list,
        col_a_head: a_vals,
        col_d_head: d_vals,
        col_diff_head: diffs,
    }).set_index("屬性項目")

    def style_delta(val):
        if val > 0:
            return "color: #2e7d32; font-weight: bold; font-size: 1.15rem;"
        elif val < 0:
            return "color: #d32f2f; font-weight: bold; font-size: 1.15rem;"
        return "color: #616161; font-size: 1.15rem;"

    styled_df = (
        df_compare.style.map(style_delta, subset=[col_diff_head])
        .format("{:+.1f}%", subset=[col_diff_head])
        .format("{:.1f}%", subset=[col_a_head, col_d_head])
    )

    st.dataframe(styled_df, width="stretch", height=500)

# ---------------------------------------------------------
# HEROES & PETS
# ---------------------------------------------------------
with tab_heroes:
    st.header("🦸‍♂️ 車頭英雄與專武獨立配置")
    col_h_a, col_h_d = st.columns(2)

    with col_h_a:
        st.subheader("⚔️ 攻擊方車頭英雄")
        a_lead_wp_sum = 0
        for i in range(1, 4):
            with st.expander(f"車頭英雄 {i} 配置", expanded=(i == 1)):
                st.selectbox(f"選擇英雄", HERO_LIST, key=f"a_l{i}_hero")
                st.selectbox(f"星數", STAR_OPTIONS, key=f"a_l{i}_stars")
                wp = st.slider(
                    f"專武等級 (Lv.0 ~ Lv.10)", 0, 10, key=f"a_l{i}_wp"
                )
                a_lead_wp_sum += wp

    with col_h_d:
        st.subheader("🏰 防守方隊長英雄")
        d_lead_wp_sum = 0
        for i in range(1, 4):
            with st.expander(f"隊長英雄 {i} 配置", expanded=(i == 1)):
                st.selectbox(f"選擇英雄", HERO_LIST, key=f"d_l{i}_hero")
                st.selectbox(f"星數", STAR_OPTIONS, key=f"d_l{i}_stars")
                wp = st.slider(
                    f"專武等級 (Lv.0 ~ Lv.10)", 0, 10, key=f"d_l{i}_wp"
                )
                d_lead_wp_sum += wp

    a_weapon_buff = (a_lead_wp_sum / 3.0) * 2.5
    d_weapon_buff = (d_lead_wp_sum / 3.0) * 2.5

# ---------------------------------------------------------
# 全局 盾兵 EHP 計算
# ---------------------------------------------------------
a_eff_def = (
    st.session_state.a_i_d
    + a_weapon_buff
    + st.session_state.a_sp_pet_def
    + st.session_state.d_sp_pet_de_def
)
a_eff_hp = (
    st.session_state.a_i_h
    + st.session_state.a_sp_pet_hp
    + st.session_state.d_sp_pet_de_hp
)

d_eff_def = (
    st.session_state.d_i_d
    + d_weapon_buff
    + st.session_state.d_sp_pet_def
    + st.session_state.d_sp_city_def
    + st.session_state.a_sp_pet_de_def
)
d_eff_hp = (
    st.session_state.d_i_h
    + st.session_state.d_sp_pet_hp
    + st.session_state.a_sp_pet_de_hp
)

a_ehp = a_w_inf * (1 + max(0, a_eff_hp) / 100) * (1 + max(0, a_eff_def) / 100)
d_ehp = d_w_inf * (1 + max(0, d_eff_hp) / 100) * (1 + max(0, d_eff_def) / 100)

# ---------------------------------------------------------
# TAB 4: What-If 模擬器
# ---------------------------------------------------------
with tab_whatif:
    st.header("🧮 配兵推薦與 What-If 模擬器")

    recommend_str = ""
    if st.session_state.d_m_l > 1200:
        recommend_str = "建議採用 **【高盾比 60% 盾 / 15% 矛 / 25% 射】**。敵方射手殺傷極高，必須大幅提高前排盾兵儲備避免崩盤。"
    elif st.session_state.d_i_d > 1500:
        recommend_str = "建議採用 **【破防型 40% 盾 / 20% 矛 / 40% 射】**。敵方盾兵防禦極高，需要拉高射手比例進行破防。"
    else:
        recommend_str = "建議採用 **【標準平衡型 50% 盾 / 20% 矛 / 30% 射】**。"

    st.info(f"🎯 AI 推薦最佳配兵方案：\n\n{recommend_str}")

    st.markdown("---")
    sim_add_h = st.slider(
        "假設【攻擊方盾兵生命】額外增加 (%)",
        min_value=0,
        max_value=300,
        value=0,
        step=10,
    )
    sim_add_d = st.slider(
        "假設【攻擊方盾兵防禦】額外增加 (%)",
        min_value=0,
        max_value=300,
        value=0,
        step=10,
    )

    sim_ehp = (
        a_w_inf
        * (1 + (a_eff_hp + sim_add_h) / 100)
        * (1 + (a_eff_def + sim_add_d) / 100)
    )

    m_b1, m_b2, m_b3 = st.columns(3)
    m_b1.metric("當前實際 EHP (含特殊加成)", f"{a_ehp:,.0f}")
    m_b2.metric(
        "模擬增益後 EHP",
        f"{sim_ehp:,.0f}",
        delta=f"+{sim_ehp - a_ehp:,.0f}",
    )

    ehp_growth = (
        f"+{((sim_ehp / a_ehp) - 1) * 100:.1f}%" if a_ehp > 0 else "0.0%"
    )
    m_b3.metric("EHP 成長幅度", ehp_growth)

# ---------------------------------------------------------
# TAB 5: AI 戰術診斷報告
# ---------------------------------------------------------
with tab_advice:
    st.header("💡 AI 戰術大師診斷與戰果歸因報告")

    troop_ratio = a_total_cnt / d_total_cnt if d_total_cnt > 0 else 1.0
    ehp_ratio = a_ehp / d_ehp if d_ehp > 0 else 1.0

    st.subheader("📋 戰局核心數據總覽")
    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("兵量壓制比", f"{troop_ratio:.2f} 倍")
    mc2.metric(f"{st.session_state.a_name} 盾兵 EHP", f"{a_ehp:,.0f}")
    mc3.metric(f"{st.session_state.d_name} 盾兵 EHP", f"{d_ehp:,.0f}")

    st.markdown("---")

    if st.button("🚀 生成戰勝 / 戰敗歸因診斷報告", type="primary"):
        with st.spinner("AI 深度分析戰術數據中..."):
            score_a = a_total_w_cnt * (a_ehp**0.35)
            score_d = d_total_w_cnt * (d_ehp**0.35)
            win_rate_a = (
                (score_a / (score_a + score_d)) * 100
                if (score_a + score_d) > 0
                else 50.0
            )

            status_color = "green" if win_rate_a >= 55 else (
                "red" if win_rate_a <= 45 else "orange"
            )
            status_text = "【大幅領先 / 預估勝仗】" if win_rate_a >= 55 else (
                "【嚴肅告急 / 預估戰敗】" if win_rate_a <= 45 else "【拉鋸膠著 / 勢均力敵】"
            )

            st.markdown(
                f"### 🎯 預估攻方勝率：:{status_color}[{win_rate_a:.1f}%] - {status_text}"
            )

            st.markdown("---")
            st.markdown("### 🔍 戰局勝敗可能原因深度剖析 (Root Cause Analysis)")

            losses_reasons = []
            win_reasons = []

            # 1. 前排坦度 (EHP) 差距
            if ehp_ratio < 0.75:
                losses_reasons.append(
                    f"**前排盾兵坦度 (EHP) 嚴重潰敗**：攻方 EHP 為 **{a_ehp:,.0f}**，僅為守方的 **{ehp_ratio*100:.1f}%**。盾兵防禦 (`{st.session_state.a_i_d}%` vs `{st.session_state.d_i_d}%`) 與生命 (`{st.session_state.a_i_h}%` vs `{st.session_state.d_i_h}%`) 差距過大，盾兵會被極速融化。"
                )
            elif ehp_ratio > 1.25:
                win_reasons.append(
                    f"**前排盾兵 (EHP) 具備壓制性優勢**：攻方 EHP 高達守方的 **{ehp_ratio:.2f} 倍**，盾兵能穩健抗住敵方第一波與續航傷害。"
                )

            # 2. 射手與破防/殺傷差距
            m_sth_diff = st.session_state.a_m_l - st.session_state.d_m_l
            if m_sth_diff < -300:
                losses_reasons.append(
                    f"**射手殺傷力落後過多 ({m_sth_diff:+.1f}%)**：敵方射手殺傷高達 `{st.session_state.d_m_l}%`（攻方僅 `{st.session_state.a_m_l}%`），對方能對我方盾兵造成毀滅性穿透傷害。"
                )
            elif m_sth_diff > 200:
                win_reasons.append(
                    f"**後排火力殺傷優異 ({m_sth_diff:+.1f}%)**：攻方射手殺傷力表現出色，能有效穿透敵方防守前排。"
                )

            # 3. 火晶/階級壓制
            fc_diff = st.session_state.a_inf_fc - st.session_state.d_inf_fc
            if fc_diff <= -1.0:
                losses_reasons.append(
                    f"**火晶等級被壓制 (落後 {abs(fc_diff):.1f} 級)**：基礎兵種屬性差距過大，直接影響每回合戰鬥機率基礎。"
                )
            elif fc_diff >= 1.0:
                win_reasons.append(
                    f"**火晶等級領先 (+{fc_diff:.1f} 級)**：擁有基礎科技兵階與加權戰力的底層壓制。"
                )

            # 4. 守城與寵物/特殊加成
            d_pet_sum = (
                st.session_state.d_sp_pet_atk
                + st.session_state.d_sp_pet_def
                + st.session_state.d_sp_city_atk
            )
            a_pet_sum = (
                st.session_state.a_sp_pet_atk
                + st.session_state.a_sp_pet_def
                + st.session_state.a_sp_rally_atk
            )
            if d_pet_sum > a_pet_sum + 20:
                losses_reasons.append(
                    f"**守方建築與寵物加成過高**：守方享有守城攻擊 `+{st.session_state.d_sp_city_atk}%` 與寵物加成，抵消了攻方的進攻優勢。"
                )

            if losses_reasons:
                st.markdown("#### 🚨 戰敗致命要因 (Why You Might Lose)")
                for r in losses_reasons:
                    st.markdown(f"* {r}")

            if win_reasons:
                st.markdown("#### 🟢 戰勝核心優勢 (Why You Might Win)")
                for r in win_reasons:
                    st.markdown(f"* {r}")

            if not losses_reasons and not win_reasons:
                st.markdown(
                    "* 雙方基礎屬性差距均在伯仲之間，勝負主要取決於戰場隨機暴擊與微小兵量波動。"
                )

            st.markdown("---")
            st.markdown("### 💡 戰術調配與改善建議")
            st.markdown(f"* **🎯 配兵調整**：{recommend_str}")
            if ehp_ratio < 1.0:
                st.markdown(
                    "* **🛡️ 優先補強方向**：重點提升【盾兵生命%】與【盾兵防禦%】，並於車頭選擇帶有生命加成（如派翠克）或傷害減免（如謝爾蓋/阿赫摩斯）的英雄以拉高 EHP。"
                )
            if m_sth_diff < 0:
                st.markdown(
                    "* **🏹 火力補強方向**：提升【射手殺傷%】與寵物技能，強化後排輸出能力。"
                )

# ---------------------------------------------------------
# TAB 6: 戰術名詞小百科
# ---------------------------------------------------------
with tab_dict:
    st.header("📖 戰術名詞與計算邏輯百科")

    with st.expander("🛡️ 1. EHP (Effective Health Points)", expanded=True):
        st.markdown(
            "EHP 代表前排盾兵真實戰場上的總承傷上限，綜合考量盾兵專屬火晶等級加權、平均兵階加權、專武屬性加成、寵物/守城特殊加成與敵方減益效果。"
        )
