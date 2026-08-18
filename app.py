import re
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
    page_title="寒霜啟示錄 - 全功能戰術指揮系統", layout="wide"
)
st.title("❄️ 寒霜啟示錄 - 全功能 AI 戰術指揮與模擬診斷系統")

tab_input, tab_compare, tab_heroes, tab_whatif, tab_advice, tab_dict = st.tabs(
    [
        "📸 截圖辨識與面板",
        "📊 12大屬性與 Delta",
        "🦸‍♂️ 1~7代英雄/專武與寵物系統",
        "🧮 配兵推薦與 What-If 模擬",
        "💡 AI 深度診斷與戰法匯出",
        "📖 戰術名詞小百科",
    ]
)

# ---------------------------------------------------------
# 1~7 代英雄資料庫 (含常用史詩紫卡)
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
    "5 星 (100% 技能加成)",
    "4 星 (80% 技能加成)",
    "3 星 (60% 技能加成)",
    "2 星 (40% 技能加成)",
    "1 星 (20% 技能加成)",
]

STAR_RATIO = {
    "5 星 (100% 技能加成)": 1.00,
    "4 星 (80% 技能加成)": 0.80,
    "3 星 (60% 技能加成)": 0.60,
    "2 星 (40% 技能加成)": 0.40,
    "1 星 (20% 技能加成)": 0.20,
}

# ---------------------------------------------------------
# Session State 預設值初始化
# ---------------------------------------------------------
defaults = {
    "a_name": "攻擊方玩家",
    "d_name": "防守方玩家",
    # 面板預設 (%)
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
    # 寵物設定預設
    "a_pet_snow_enable": False,
    "a_pet_snow_lvl": 5,
    "a_pet_tiger_enable": False,
    "a_pet_tiger_lvl": 5,
    "d_pet_hyena_enable": False,
    "d_pet_hyena_lvl": 5,
    "d_pet_snow_enable": False,
    "d_pet_snow_lvl": 5,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

default_a_df = pd.DataFrame([
    {"兵種": "🛡️ 盾兵", "階級": "T10", "火晶等級": "FC7", "數量": 0},
    {"兵種": "🗡️ 矛兵", "階級": "T10", "火晶等級": "FC7", "數量": 0},
    {"兵種": "🏹 射手", "階級": "T10", "火晶等級": "FC7", "數量": 0},
])

default_d_df = pd.DataFrame([
    {"兵種": "🛡️ 盾兵", "階級": "T10", "火晶等級": "FC7", "數量": 0},
    {"兵種": "🗡️ 矛兵", "階級": "T10", "火晶等級": "FC7", "數量": 0},
    {"兵種": "🏹 射手", "階級": "T10", "火晶等級": "FC7", "數量": 0},
])

if "a_troops_df" not in st.session_state:
    st.session_state["a_troops_df"] = default_a_df.copy()
if "d_troops_df" not in st.session_state:
    st.session_state["d_troops_df"] = default_d_df.copy()

WEIGHT_MAP = {
    ("FC5", "T10"): 1.00,
    ("FC5", "T11 (太陽神)"): 1.15,
    ("FC6", "T10"): 1.08,
    ("FC6", "T11 (太陽神)"): 1.25,
    ("FC7", "T10"): 1.18,
    ("FC7", "T11 (太陽神)"): 1.35,
    ("FC8", "T10"): 1.32,
    ("FC8", "T11 (太陽神)"): 1.50,
}

# ---------------------------------------------------------
# TAB 1: 圖片上傳、OCR 辨識與兵種輸入
# ---------------------------------------------------------
with tab_input:
    if st.button("🧹 一鍵清空所有數值"):
        for key in list(st.session_state.keys()):
            if key in defaults:
                st.session_state[key] = defaults[key]
            else:
                del st.session_state[key]
        st.session_state["a_troops_df"] = default_a_df.copy()
        st.session_state["d_troops_df"] = default_d_df.copy()
        st.rerun()

    st.subheader("🖼️ 1. 上傳戰報截圖 (自動辨識 12 大屬性)")
    uploaded_files = st.file_uploader(
        "請上傳戰報截圖 (PNG/JPG)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        files_to_show = uploaded_files[:6]
        cols = st.columns(min(len(files_to_show), 4))
        for idx, file in enumerate(files_to_show):
            image = Image.open(file)
            with cols[idx % 4]:
                st.image(
                    image, caption=f"截圖 {idx + 1}", use_container_width=True
                )

        st.markdown("---")
        if not ocr_available:
            st.warning("⚠️ 系統尚未加載 EasyOCR，請確認套件已安裝。")
        else:
            if st.button("🚀 啟動 AI 辨識並帶入數據", type="primary"):
                with st.spinner("AI 解析中..."):
                    reader = easyocr.Reader(["ch_tra", "en"], gpu=False)
                    extracted_text = []

                    for file in files_to_show:
                        img = Image.open(file)
                        img.save("temp_ocr.png")
                        results = reader.readtext("temp_ocr.png", detail=0)
                        extracted_text.extend(results)

                    pct_numbers = []
                    for t in extracted_text:
                        found = re.findall(r"(\d+[\.\,]\d+|\d+)\%", t)
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
                            st.session_state[k] = pct_numbers[idx]

                    st.success("✅ 辨識完成！數據已更新。")
                    st.rerun()

    st.markdown("---")
    st.subheader("✏️ 2. 面板與兵種數量 (支援 T10/T11、FC5~FC8 自由新增)")

    col_a, col_d = st.columns(2)

    column_config_spec = {
        "兵種": st.column_config.SelectboxColumn(
            "兵種",
            options=["🛡️ 盾兵", "🗡️ 矛兵", "🏹 射手"],
            required=True,
        ),
        "階級": st.column_config.SelectboxColumn(
            "階級",
            options=["T10", "T11 (太陽神)"],
            required=True,
        ),
        "火晶等級": st.column_config.SelectboxColumn(
            "火晶等級",
            options=["FC5", "FC6", "FC7", "FC8"],
            required=True,
        ),
        "數量": st.column_config.NumberColumn(
            "兵量", min_value=0, step=1000, default=0, required=True
        ),
    }

    # ---------------- 攻擊方 ----------------
    with col_a:
        st.header("⚔️ 攻擊方 (Attacker)")
        st.text_input("玩家名稱", key="a_name")

        st.caption("📋 兵種組合表")
        edited_a_df = st.data_editor(
            st.session_state["a_troops_df"],
            num_rows="dynamic",
            column_config=column_config_spec,
            use_container_width=True,
            key="a_editor",
        )
        st.session_state["a_troops_df"] = edited_a_df

        a_inf_total, a_lan_total, a_mar_total, a_w_inf = 0, 0, 0, 0.0
        for _, row in edited_a_df.iterrows():
            b_type = str(row.get("兵種", ""))
            tier = str(row.get("階級", "T10"))
            fc = str(row.get("火晶等級", "FC7"))
            try:
                cnt = int(row.get("數量", 0))
            except (ValueError, TypeError):
                cnt = 0

            if "盾" in b_type:
                a_inf_total += cnt
                w = WEIGHT_MAP.get((fc, tier), 1.18)
                a_w_inf += cnt * w
            elif "矛" in b_type:
                a_lan_total += cnt
            elif "射" in b_type:
                a_mar_total += cnt

        a_total = a_inf_total + a_lan_total + a_mar_total
        st.info(
            f"⚔️ 攻擊總兵力：**{a_total:,}** (🛡️ 盾: {a_inf_total:,} | 🗡️ 矛: {a_lan_total:,} | 🏹 射: {a_mar_total:,})"
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

    # ---------------- 防守方 ----------------
    with col_d:
        st.header("🏰 防守方 (Defender)")
        st.text_input("玩家名稱", key="d_name")

        st.caption("📋 兵種組合表")
        edited_d_df = st.data_editor(
            st.session_state["d_troops_df"],
            num_rows="dynamic",
            column_config=column_config_spec,
            use_container_width=True,
            key="d_editor",
        )
        st.session_state["d_troops_df"] = edited_d_df

        d_inf_total, d_lan_total, d_mar_total, d_w_inf = 0, 0, 0, 0.0
        for _, row in edited_d_df.iterrows():
            b_type = str(row.get("兵種", ""))
            tier = str(row.get("階級", "T10"))
            fc = str(row.get("火晶等級", "FC7"))
            try:
                cnt = int(row.get("數量", 0))
            except (ValueError, TypeError):
                cnt = 0

            if "盾" in b_type:
                d_inf_total += cnt
                w = WEIGHT_MAP.get((fc, tier), 1.18)
                d_w_inf += cnt * w
            elif "矛" in b_type:
                d_lan_total += cnt
            elif "射" in b_type:
                d_mar_total += cnt

        d_total = d_inf_total + d_lan_total + d_mar_total
        st.info(
            f"🏰 防守總兵力：**{d_total:,}** (🛡️ 盾: {d_inf_total:,} | 🗡️ 矛: {d_lan_total:,} | 🏹 射: {d_mar_total:,})"
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
# TAB 2: 動態 12 大屬性對比表
# ---------------------------------------------------------
with tab_compare:
    st.header("📊 12 大屬性動態 Delta 對比")
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
    a_vals = [
        st.session_state[k]
        for k in [
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
    ]
    d_vals = [
        st.session_state[k]
        for k in [
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
    ]
    diffs = [round(a - d, 1) for a, d in zip(a_vals, d_vals)]

    df_compare = pd.DataFrame({
        "屬性項目": stats_list,
        f"{st.session_state.a_name} (%)": a_vals,
        f"{st.session_state.d_name} (%)": d_vals,
        "屬性差距 (攻 - 守)": diffs,
    }).set_index("屬性項目")

    st.dataframe(df_compare, use_container_width=True)
    st.bar_chart(
        df_compare[[
            f"{st.session_state.a_name} (%)", f"{st.session_state.d_name} (%)"
        ]]
    )

# ---------------------------------------------------------
# TAB 3: 🦸‍♂️ 1~7 代英雄/專武與寵物系統
# ---------------------------------------------------------
with tab_heroes:
    st.header("🦸‍♂️ 1~7 代英雄個體獨立配置 (車頭/車身分開選擇)")

    col_h_a, col_h_d = st.columns(2)

    # ---------------- 攻擊方英雄配置 ----------------
    with col_h_a:
        st.subheader("⚔️ 攻擊方 (車頭 3 主將 + 車身 4 隊友)")

        st.markdown("##### 👑 車頭 3 隻主將 (帶領全隊)")
        a_lead_weapons_sum = 0

        for i in range(1, 4):
            with st.expander(f"主將 {i} 配置", expanded=(i == 1)):
                st.selectbox(f"選擇英雄 (1~7代)", HERO_LIST, key=f"a_l{i}_hero")
                st.selectbox(f"星數 (技能)", STAR_OPTIONS, key=f"a_l{i}_stars")
                wp = st.slider(
                    f"專屬武器等級 (+0 ~ +20)",
                    0,
                    20,
                    value=10,
                    key=f"a_l{i}_wp",
                )
                a_lead_weapons_sum += wp

        st.markdown("---")
        st.markdown("##### 👥 車身 4 位隊友 (第一技能疊加加成)")

        a_joiner_buff_sum = 0.0
        for j in range(1, 5):
            with st.expander(f"車身隊友 {j} 配置", expanded=(j == 1)):
                hero = st.selectbox(
                    f"選擇英雄", HERO_LIST, index=23, key=f"a_j{j}_hero"
                )  # 預設傑西
                stars = st.selectbox(
                    f"星數", STAR_OPTIONS, index=0, key=f"a_j{j}_stars"
                )

                s_ratio = STAR_RATIO.get(stars, 1.0)
                base_val = 0
                if "傑西" in hero:
                    base_val = 25.0
                elif "赫羅尼莫" in hero:
                    base_val = 15.0
                elif "莫莉" in hero:
                    base_val = 10.0
                elif "金恩尚" in hero:
                    base_val = 20.0

                a_joiner_buff_sum += base_val * s_ratio

        a_weapon_buff = (
            a_lead_weapons_sum / 3.0
        ) * 1.5  # 3 位主將專武平均攻防加成

        st.success(
            f"🔥 攻擊車身總傷害疊加加成：**+{a_joiner_buff_sum:.1f}%**\n\n"
            f"⚔️ 車頭專武全軍屬性加成：**+{a_weapon_buff:.1f}% 攻防**"
        )

    # ---------------- 防守方英雄配置 ----------------
    with col_h_d:
        st.subheader("🏰 防守方 (駐守 3 隊長 + 駐守 4 車身)")

        st.markdown("##### 👑 駐守 3 隻隊長")
        d_lead_weapons_sum = 0

        for i in range(1, 4):
            with st.expander(f"隊長 {i} 配置", expanded=(i == 1)):
                st.selectbox(f"選擇英雄 (1~7代)", HERO_LIST, key=f"d_l{i}_hero")
                st.selectbox(f"星數 (技能)", STAR_OPTIONS, key=f"d_l{i}_stars")
                wp = st.slider(
                    f"專屬武器等級 (+0 ~ +20)",
                    0,
                    20,
                    value=10,
                    key=f"d_l{i}_wp",
                )
                d_lead_weapons_sum += wp

        st.markdown("---")
        st.markdown("##### 👥 駐守車身 4 位隊友")

        d_joiner_buff_sum = 0.0
        for j in range(1, 5):
            with st.expander(f"駐守車身 {j} 配置", expanded=(j == 1)):
                hero = st.selectbox(
                    f"選擇英雄", HERO_LIST, index=24, key=f"d_j{j}_hero"
                )  # 預設派翠克
                stars = st.selectbox(
                    f"星數", STAR_OPTIONS, index=0, key=f"d_j{j}_stars"
                )

                s_ratio = STAR_RATIO.get(stars, 1.0)
                base_val = 0
                if "派翠克" in hero:
                    base_val = 25.0  # 生命/恢復加成
                elif "謝爾蓋" in hero:
                    base_val = 20.0  # 受傷降低
                elif "阿赫摩斯" in hero:
                    base_val = 15.0

                d_joiner_buff_sum += base_val * s_ratio

        d_weapon_buff = (d_lead_weapons_sum / 3.0) * 1.5

        st.success(
            f"🛡️ 防守車身減傷/生命總疊加：**+{d_joiner_buff_sum:.1f}%**\n\n"
            f"🏰 隊長專武全軍屬性加成：**+{d_weapon_buff:.1f}% 攻防**"
        )

    st.markdown("---")

    # ------------ 寵物主動技能與等級 ------------
    st.subheader("🐾 寵物主動技能開關與技能等級 (Pet Active Skills)")

    cp1, cp2 = st.columns(2)
    with cp1:
        st.markdown("##### ⚔️ 攻擊方寵物")
        c11, c12 = st.columns([2, 3])
        with c11:
            st.checkbox("啟用【雪豹】(爆發殺傷)", key="a_pet_snow_enable")
        with c12:
            st.slider("雪豹技能等級", 1, 10, key="a_pet_snow_lvl")

        c21, c22 = st.columns([2, 3])
        with c21:
            st.checkbox(
                "啟用【劍齒虎】(穿透防禦)", key="a_pet_tiger_enable"
            )
        with c22:
            st.slider("劍齒虎技能等級", 1, 10, key="a_pet_tiger_lvl")

    with cp2:
        st.markdown("##### 🏰 防守方寵物")
        c31, c32 = st.columns([2, 3])
        with c31:
            st.checkbox(
                "啟用【巨鬣狗】(降低敵方攻擊)", key="d_pet_hyena_enable"
            )
        with c32:
            st.slider("巨鬣狗技能等級", 1, 10, key="d_pet_hyena_lvl")

        c41, c42 = st.columns([2, 3])
        with c41:
            st.checkbox(
                "啟用【雪豹】(駐守反傷加成)", key="d_pet_snow_enable"
            )
        with c42:
            st.slider("雪豹技能等級", 1, 10, key="d_pet_snow_lvl")

# ---------------------------------------------------------
# TAB 4: ⚔️ 最佳配兵推薦與 What-If 模擬器
# ---------------------------------------------------------
with tab_whatif:
    st.header("🧮 最佳配兵試算與 What-If 屬性模擬器")

    st.subheader("💡 AI 戰術最佳集結配兵推薦 (Troop Optimizer)")

    d_mar_leth = st.session_state.d_m_l
    recommend_str = ""

    if d_mar_leth > 1200:
        recommend_str = "建議採用 **【高盾比 60% 盾 / 15% 矛 / 25% 射】**。敵方射手殺傷極高，必須提高盾兵儲備吸收大量穿透傷害。"
    elif st.session_state.d_i_d > 1500:
        recommend_str = "建議採用 **【破防型 40% 盾 / 20% 矛 / 40% 射】**。敵方盾兵鐵壁極高，拉高我方射手比例進行前排破防。"
    else:
        recommend_str = "建議採用 **【標準平衡型 50% 盾 / 20% 矛 / 30% 射】**。"

    st.info(f"🎯 針對目前敵方面板，AI 推薦配兵指示：\n\n{recommend_str}")

    st.markdown("---")

    st.subheader("🧪 What-If 邊際效益試算 (假設性增益測試)")
    st.caption("調整下方滑桿，測試「若提升特定屬性，盾兵 EHP 與對比優勢會如何改變」：")

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

    base_ehp = (
        a_w_inf
        * (1 + (st.session_state.a_i_h + a_weapon_buff) / 100)
        * (1 + (st.session_state.a_i_d + a_weapon_buff) / 100)
    )
    sim_ehp = (
        a_w_inf
        * (1 + (st.session_state.a_i_h + a_weapon_buff + sim_add_h) / 100)
        * (1 + (st.session_state.a_i_d + a_weapon_buff + sim_add_d) / 100)
    )

    m_b1, m_b2, m_b3 = st.columns(3)
    m_b1.metric("當前實際 EHP (含專武)", f"{base_ehp:,.0f}")
    m_b2.metric(
        "模擬增益後 EHP",
        f"{sim_ehp:,.0f}",
        delta=f"+{sim_ehp - base_ehp:,.0f}",
    )
    m_b3.metric(
        "EHP 成長幅度",
        f"+{((sim_ehp/base_ehp)-1)*100:.1f}%" if base_ehp > 0 else "0%",
    )

# ---------------------------------------------------------
# TAB 5: AI 戰術大師診斷與報告匯出
# ---------------------------------------------------------
with tab_advice:
    st.header("💡 AI 戰況總覽與戰術摘要卡")

    a_ehp = (
        a_w_inf
        * (1 + (st.session_state.a_i_h + a_weapon_buff) / 100)
        * (1 + (st.session_state.a_i_d + a_weapon_buff) / 100)
    )
    d_ehp = (
        d_w_inf
        * (1 + (st.session_state.d_i_h + d_weapon_buff) / 100)
        * (1 + (st.session_state.d_i_d + d_weapon_buff) / 100)
    )
    troop_ratio = a_total / d_total if d_total > 0 else 0

    st.subheader("📋 戰局速覽與 EHP 對比")
    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("兵量壓制比", f"{troop_ratio:.2f} 倍")
    mc2.metric(f"{st.session_state.a_name} 盾兵 EHP", f"{a_ehp:,.0f}")
    mc3.metric(f"{st.session_state.d_name} 盾兵 EHP", f"{d_ehp:,.0f}")

    st.markdown("---")
    st.subheader("🤖 AI 大模型深度戰術診斷 (需 API Key)")

    api_key = st.text_input(
        "輸入 OpenAI API Key 啟用深度剖析", type="password"
    )

    if st.button("🧠 生成全方位戰術診斷報告", type="primary"):
        if not api_key:
            st.warning("請先輸入 OpenAI API Key。")
        else:
            try:
                import openai

                client = openai.OpenAI(api_key=api_key)

                prompt_content = f"""
你是一位《寒霜啟示錄 (Whiteout Survival)》頂級指揮官。請根據以下精確的個體英雄配置與數據產出深度報告：

【攻擊方】: {st.session_state.a_name}
- 車頭專武平均加成: +{a_weapon_buff:.1f}% 攻防
- 車身 4 隊友傷害總疊加: +{a_joiner_buff_sum:.1f}%
- 寵物: 雪豹(開:{st.session_state.a_pet_snow_enable}, Lv.{st.session_state.a_pet_snow_lvl}), 劍齒虎(開:{st.session_state.a_pet_tiger_enable}, Lv.{st.session_state.a_pet_tiger_lvl})
- 總兵力: {a_total:,} (盾: {a_inf_total}, 矛: {a_lan_total}, 射: {a_mar_total})
- 綜合 EHP (含專武): {a_ehp:,.0f}

【防守方】: {st.session_state.d_name}
- 隊長專武平均加成: +{d_weapon_buff:.1f}% 攻防
- 駐守車身減傷/生命總疊加: +{d_joiner_buff_sum:.1f}%
- 寵物: 巨鬣狗(開:{st.session_state.d_pet_hyena_enable}, Lv.{st.session_state.d_pet_hyena_lvl}), 雪豹(開:{st.session_state.d_pet_snow_enable}, Lv.{st.session_state.d_pet_snow_lvl})
- 總兵力: {d_total:,} (盾: {d_inf_total}, 矛: {d_lan_total}, 射: {d_mar_total})
- 綜合 EHP (含專武): {d_ehp:,.0f}

【AI 配兵建議】: {recommend_str}

請針對 1~7 代英雄差距與專武配備，提供關鍵調配優化建議與勝敗解析。
"""

                with st.spinner("AI 分析中..."):
                    res = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt_content}],
                    )
                    st.markdown(res.choices[0].message.content)

            except Exception as e:
                st.error(f"解析失敗：{e}")

# ---------------------------------------------------------
# TAB 6: 戰術專有名詞小百科
# ---------------------------------------------------------
with tab_dict:
    st.header("📖 戰術名詞與計算邏輯百科")

    with st.expander("🛡️ 1. EHP (Effective Health Points)", expanded=True):
        st.markdown(
            "EHP 代表真實戰場上的總承傷上限，綜合考量火晶等級加權、T10/T11 兵階加權、專武屬性加成、防禦 % 與生命 %。"
        )

    with st.expander("⚔️ 2. 車身 (Joiner) 星數與技能疊加機制"):
        st.markdown(
            "集結/駐守的前 4 位車身英雄，其第一項遠征技能可重複疊加最高 4 層。技能數值受車身英雄星數影響（5星提供 100% 技能數值，1星僅提供 20%）。"
        )
