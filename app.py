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
        "🦸‍♂️ 英雄與車身疊加計算",
        "🧮 配兵推薦與 What-If 模擬",
        "💡 AI 深度診斷與戰術卡匯出",
        "📖 戰術名詞小百科",
    ]
)

# ---------------------------------------------------------
# 1. Session State 預設值初始化 (預設歸零/預設值)
# ---------------------------------------------------------
defaults = {
    "a_name": "攻擊方玩家",
    "d_name": "防守方玩家",
    "a_i_fc6": 0, "a_i_fc7": 0, "a_l_fc7": 0, "a_m_fc7": 0,
    "d_i_fc8": 0, "d_i_fc7": 0, "d_l_fc7": 0, "d_m_fc7": 0,
    "a_i_a": 0.0, "a_i_d": 0.0, "a_i_l": 0.0, "a_i_h": 0.0,
    "a_l_a": 0.0, "a_l_d": 0.0, "a_l_l": 0.0, "a_l_h": 0.0,
    "a_m_a": 0.0, "a_m_d": 0.0, "a_m_l": 0.0, "a_m_h": 0.0,
    "d_i_a": 0.0, "d_i_d": 0.0, "d_i_l": 0.0, "d_i_h": 0.0,
    "d_l_a": 0.0, "d_l_d": 0.0, "d_l_l": 0.0, "d_l_h": 0.0,
    "d_m_a": 0.0, "d_m_d": 0.0, "d_m_l": 0.0, "d_m_h": 0.0,
    "a_leader": "赫羅尼莫 / 傑西 / 納塔莉",
    "a_joiner_hero": "傑西 (Jessie) - 傷害 +25%",
    "a_joiner_count": 4,
    "d_leader": "赫羅尼莫 / 派翠克 / 謝爾蓋",
    "d_joiner_hero": "派翠克 (Patrick) - 生命恢復與生命提升",
    "d_joiner_count": 4,
    "a_pet_snow": False, "a_pet_tiger": False,
    "d_pet_snow": False, "d_pet_hyena": False,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------------------------------------------------
# TAB 1: 圖片上傳、OCR 辨識與基礎面板
# ---------------------------------------------------------
with tab_input:
    # 🧹 一鍵清空 / 重置按鈕 (安全還原)
    if st.button("🧹 一鍵清空所有數值"):
        for key in defaults.keys():
            st.session_state[key] = defaults[key]
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
            if st.button("🚀 啟動 AI 辨識並自動帶入面板數據", type="primary"):
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
    st.subheader("✏️ 2. 面板與兵種數量手動微調")

    col_a, col_d = st.columns(2)
    with col_a:
        st.header("⚔️ 攻擊方 (Attacker)")
        st.text_input("玩家名稱", key="a_name")
        with st.expander("🛡️ 盾兵與火晶數量", expanded=True):
            st.number_input(
                "FC6 (Lv 10.0)", min_value=0, step=1000, key="a_i_fc6"
            )
            st.number_input(
                "FC7 (Lv 10.1~10.3)", min_value=0, step=1000, key="a_i_fc7"
            )
        with st.expander("🗡️ 矛兵數量", expanded=False):
            st.number_input(
                "FC7 (Lv 10.1~10.3)", min_value=0, step=1000, key="a_l_fc7"
            )
        with st.expander("🏹 射手數量", expanded=False):
            st.number_input(
                "FC7 (Lv 10.1~10.3)", min_value=0, step=1000, key="a_m_fc7"
            )

        a_inf_total = st.session_state.a_i_fc6 + st.session_state.a_i_fc7
        a_lan_total = st.session_state.a_l_fc7
        a_mar_total = st.session_state.a_m_fc7
        a_total = a_inf_total + a_lan_total + a_mar_total
        st.info(f"⚔️ 攻擊總兵力：**{a_total:,}**")

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
        with st.expander("🛡️ 盾兵與火晶數量", expanded=True):
            st.number_input(
                "FC7 (Lv 10.1~10.3)", min_value=0, step=1000, key="d_i_fc7"
            )
            st.number_input(
                "FC8 (Lv 10.4~10.8)", min_value=0, step=1000, key="d_i_fc8"
            )
        with st.expander("🗡️ 矛兵數量", expanded=False):
            st.number_input(
                "FC7 (Lv 10.1~10.3)", min_value=0, step=1000, key="d_l_fc7"
            )
        with st.expander("🏹 射手數量", expanded=False):
            st.number_input(
                "FC7 (Lv 10.1~10.3)", min_value=0, step=1000, key="d_m_fc7"
            )

        d_inf_total = st.session_state.d_i_fc7 + st.session_state.d_i_fc8
        d_lan_total = st.session_state.d_l_fc7
        d_mar_total = st.session_state.d_m_fc7
        d_total = d_inf_total + d_lan_total + d_mar_total
        st.info(f"🏰 防守總兵力：**{d_total:,}**")

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
# TAB 3: 🦸‍♂️ 英雄與車身遠征技能自動疊加計算器
# ---------------------------------------------------------
with tab_heroes:
    st.header("🦸‍♂️ 車頭/車身英雄選擇與被動技能自動疊加")
    st.markdown(
        "根據遊戲機制：**集結/駐守的前 4 位車身玩家**，其主要英雄的第一個遠征技能會自動生效並疊加。"
    )

    col_h_a, col_h_d = st.columns(2)

    with col_h_a:
        st.subheader("⚔️ 攻擊方車頭與車身配置")
        st.text_input("集結車頭 3 隻主將名稱", key="a_leader")

        st.selectbox(
            "選擇車身第一英雄 (Joiner Hero)",
            options=[
                "傑西 (Jessie) - 傷害 +25%",
                "赫羅尼莫 (Jeronimo) - 傷害 +15%",
                "金恩尚 (Shin Eun-seong) - 傷害 +20%",
                "無 / 其他普通英雄 - 無加成",
            ],
            key="a_joiner_hero",
        )
        st.slider(
            "有效車身數量 (上限 4 人)",
            min_value=0,
            max_value=4,
            value=4,
            key="a_joiner_count",
        )

        # 計算增益
        atk_buff_pct = 0
        if "傑西" in st.session_state.a_joiner_hero:
            atk_buff_pct = 25 * st.session_state.a_joiner_count
        elif "赫羅尼莫" in st.session_state.a_joiner_hero:
            atk_buff_pct = 15 * st.session_state.a_joiner_count
        elif "金恩尚" in st.session_state.a_joiner_hero:
            atk_buff_pct = 20 * st.session_state.a_joiner_count

        st.success(
            f"🔥 攻擊車身總傷害加成：**+{atk_buff_pct}% 傷害提升**"
        )

    with col_h_d:
        st.subheader("🏰 防守方駐守隊長與車身配置")
        st.text_input("駐守隊長 3 隻主將名稱", key="d_leader")

        st.selectbox(
            "選擇駐守車身核心英雄",
            options=[
                "派翠克 (Patrick) - 生命恢復與生命提升",
                "謝爾蓋 (Sergey) - 受傷降低 20%",
                "阿蒙森 (Amundsen) - 受傷降低 15%",
                "無 / 其他普通英雄",
            ],
            key="d_joiner_hero",
        )
        st.slider(
            "有效駐守車身數量 (上限 4 人)",
            min_value=0,
            max_value=4,
            value=4,
            key="d_joiner_count",
        )

        def_red_pct = 0
        if "謝爾蓋" in st.session_state.d_joiner_hero:
            def_red_pct = 20
        elif "阿蒙森" in st.session_state.d_joiner_hero:
            def_red_pct = 15

        st.success(f"🛡️ 防守車身減傷防禦加成：**-{def_red_pct}% 受到傷害**")

    st.markdown("---")
    st.subheader("🐾 寵物主動技能與戰術影響增益")
    cp1, cp2 = st.columns(2)
    with cp1:
        st.checkbox("⚔️ 攻擊方啟用【雪豹】(爆發殺傷提升)", key="a_pet_snow")
        st.checkbox("⚔️ 攻擊方啟用【劍齒虎】(穿透敵方防禦)", key="a_pet_tiger")
    with cp2:
        st.checkbox("🏰 防守方啟用【巨鬣狗】(降低敵方攻擊)", key="d_pet_hyena")
        st.checkbox("🏰 防守方啟用【雪豹】(駐守反傷加成)", key="d_pet_snow")

# ---------------------------------------------------------
# TAB 4: ⚔️ 最佳配兵推薦與 What-If 模擬器
# ---------------------------------------------------------
with tab_whatif:
    st.header("🧮 最佳配兵試算與 What-If 屬性模擬器")

    # 1. 配兵比例推薦 logic
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

    # 2. What-If 模擬
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

    base_ehp = (st.session_state.a_i_fc6 * 1.08 + st.session_state.a_i_fc7 * 1.18) * (
        1 + st.session_state.a_i_h / 100
    ) * (1 + st.session_state.a_i_d / 100)
    sim_ehp = (st.session_state.a_i_fc6 * 1.08 + st.session_state.a_i_fc7 * 1.18) * (
        1 + (st.session_state.a_i_h + sim_add_h) / 100
    ) * (1 + (st.session_state.a_i_d + sim_add_d) / 100)

    m_b1, m_b2, m_b3 = st.columns(3)
    m_b1.metric("當前實際 EHP", f"{base_ehp:,.0f}")
    m_b2.metric(
        "模擬增益後 EHP",
        f"{sim_ehp:,.0f}",
        delta=f"+{sim_ehp - base_ehp:,.0f}",
    )
    m_b3.metric("EHP 成長幅度", f"+{((sim_ehp/base_ehp)-1)*100:.1f}%")

# ---------------------------------------------------------
# TAB 5: AI 戰術大師診斷與報告匯出
# ---------------------------------------------------------
with tab_advice:
    st.header("💡 AI 戰況總覽與戰術摘要卡")

    # EHP 計算
    a_w_inf = (st.session_state.a_i_fc6 * 1.08) + (
        st.session_state.a_i_fc7 * 1.18
    )
    d_w_inf = (st.session_state.d_i_fc7 * 1.18) + (
        st.session_state.d_i_fc8 * 1.32
    )

    a_ehp = (
        a_w_inf
        * (1 + st.session_state.a_i_h / 100)
        * (1 + st.session_state.a_i_d / 100)
    )
    d_ehp = (
        d_w_inf
        * (1 + st.session_state.d_i_h / 100)
        * (1 + st.session_state.d_i_d / 100)
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
你是一位《寒霜啟示錄 (Whiteout Survival)》頂級指揮官。請根據以下完整的數據、車身疊加與寵物配置，產出極具操作性的戰術報告：

【攻擊方】: {st.session_state.a_name}
- 車頭/車身英雄: {st.session_state.a_leader} | 車身: {st.session_state.a_joiner_hero} x{st.session_state.a_joiner_count}
- 寵物加成: 雪豹({st.session_state.a_pet_snow}), 劍齒虎({st.session_state.a_pet_tiger})
- 總兵力: {a_total:,} (盾: {a_inf_total}, 矛: {a_lan_total}, 射: {a_mar_total})
- 面板 (攻/防/殺/命): 盾({st.session_state.a_i_a}%,{st.session_state.a_i_d}%,{st.session_state.a_i_l}%,{st.session_state.a_i_h}%) | 射({st.session_state.a_m_a}%,{st.session_state.a_m_d}%,{st.session_state.a_m_l}%,{st.session_state.a_m_h}%)
- 盾兵 EHP: {a_ehp:,.0f}

【防守方】: {st.session_state.d_name}
- 隊長/車身英雄: {st.session_state.d_leader} | 車身: {st.session_state.d_joiner_hero} x{st.session_state.d_joiner_count}
- 寵物加成: 巨鬣狗({st.session_state.d_pet_hyena}), 雪豹({st.session_state.d_pet_snow})
- 總兵力: {d_total:,} (盾: {d_inf_total}, 矛: {d_lan_total}, 射: {d_mar_total})
- 面板 (攻/防/殺/命): 盾({st.session_state.d_i_a}%,{st.session_state.d_i_d}%,{st.session_state.d_i_l}%,{st.session_state.d_i_h}%) | 射({st.session_state.d_m_a}%,{st.session_state.d_m_d}%,{st.session_state.d_m_l}%,{st.session_state.d_m_h}%)
- 盾兵 EHP: {d_ehp:,.0f}

【AI 配兵建議】: {recommend_str}

請包含：
1. **勝敗核心分析** (結合 EHP 與車身加成)
2. **⚔️ 車頭與車身改進方向**
3. **🏰 防守駐守補強建議**
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
            "EHP 代表真實戰場上的總承傷上限，綜合考量火晶加權兵量、防禦 % 與生命 %。"
        )

    with st.expander("⚔️ 2. 車身 (Joiner) 技能疊加機制"):
        st.markdown(
            "集結/駐守的前 4 位車身英雄，其第一項遠征技能（如傑西 +25% 傷害）可重複疊加最高 4 層 (+100%)。"
        )
