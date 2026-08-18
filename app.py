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
    page_title="寒霜啟示錄 - AI 自動辨識與英雄戰術診斷系統", layout="wide"
)
st.title("❄️ 寒霜啟示錄 - AI 截圖辨識、英雄隊容與雙向戰術診斷系統")

tab_input, tab_compare, tab_advice, tab_dict = st.tabs([
    "📸 截圖上傳與 AI 自動填寫",
    "📊 12大屬性與兵量對比",
    "💡 戰鬥診斷與改善建議",
    "📖 戰術專有名詞小百科",
])

# ---------------------------------------------------------
# 1. 初始化 Session State 預設值
# ---------------------------------------------------------
defaults = {
    "a_name": "[UWD]香腸",
    "d_name": "[NRG]ODYESSUS",
    "a_hero_main": "赫羅尼莫 / 傑西 / 納塔莉",
    "d_hero_main": "赫羅尼莫 / 派翠克 / 謝爾蓋",
    "a_i_fc6": 403170,
    "a_i_fc7": 86885,
    "a_l_fc7": 116285,
    "a_m_fc7": 200000,
    "d_i_fc8": 132369,
    "d_i_fc7": 11456,
    "d_l_fc7": 100000,
    "d_m_fc7": 98160,
    "a_i_a": 1354.4,
    "a_i_d": 1091.1,
    "a_i_l": 834.5,
    "a_i_h": 857.7,
    "a_l_a": 1062.4,
    "a_l_d": 852.4,
    "a_l_l": 794.5,
    "a_l_h": 500.7,
    "a_m_a": 1291.0,
    "a_m_d": 1038.6,
    "a_m_l": 1049.2,
    "a_m_h": 675.3,
    "d_i_a": 1599.4,
    "d_i_d": 1636.8,
    "d_i_l": 1220.7,
    "d_i_h": 1150.0,
    "d_l_a": 1312.1,
    "d_l_d": 1295.3,
    "d_l_l": 871.4,
    "d_l_h": 525.4,
    "d_m_a": 1752.3,
    "d_m_d": 1655.6,
    "d_m_l": 1403.9,
    "d_m_h": 1030.7,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------------------------------------------------
# TAB 1: 圖片上傳、OCR 自動填寫與手動微調
# ---------------------------------------------------------
with tab_input:
    st.subheader("🖼️ 1. 上傳戰報截圖 (最多 6 張，包含車頭/車身駐防英雄截圖)")
    uploaded_files = st.file_uploader(
        "請上傳戰報截圖：包含總覽、12大屬性、兵種明細與【車身/駐防英雄隊容】截圖 (PNG/JPG)",
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
        st.subheader("🤖 2. AI 自動辨識")

        if not ocr_available:
            st.warning(
                "⚠️ 未檢測到 EasyOCR 套件，請在 CMD 執行：`py -m pip install easyocr torch` 以啟用辨識。"
            )
        else:
            if st.button("🚀 讀取截圖數據並同步所有欄位", type="primary"):
                with st.spinner("AI 正在解析數據並更新全站表格中..."):
                    reader = easyocr.Reader(["ch_tra", "en"], gpu=False)
                    extracted_text = []

                    for file in files_to_show:
                        img = Image.open(file)
                        img.save("temp_ocr.png")
                        results = reader.readtext("temp_ocr.png", detail=0)
                        extracted_text.extend(results)

                    # 抓取包含 % 的數字
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

                    st.success("✅ 辨識完成！正在更新全站數據...")
                    st.rerun()

    st.markdown("---")
    st.subheader("✏️ 3. 數據與英雄隊容微調")

    col_atk_ui, col_def_ui = st.columns(2)

    # ⚔️ 攻擊方
    with col_atk_ui:
        st.header("⚔️ 攻擊方 (Attacker)")
        st.text_input("攻擊者名稱", key="a_name")
        st.text_input(
            "🦸‍♂️ 集結車頭 / 車身英雄",
            key="a_hero_main",
            help="例：傑西 (車身第一技能可疊加傷害增益 25%)",
        )

        with st.expander("🛡️ 盾兵明細", expanded=True):
            st.number_input(
                "FC6 (Lv 10.0)", min_value=0, step=1000, key="a_i_fc6"
            )
            st.number_input(
                "FC7 (Lv 10.1~10.3)", min_value=0, step=1000, key="a_i_fc7"
            )

        with st.expander("🗡️ 矛兵明細", expanded=False):
            st.number_input(
                "FC7 (Lv 10.1~10.3)", min_value=0, step=1000, key="a_l_fc7"
            )

        with st.expander("🏹 射手明細", expanded=False):
            st.number_input(
                "FC7 (Lv 10.1~10.3)", min_value=0, step=1000, key="a_m_fc7"
            )

        a_inf_total = st.session_state.a_i_fc6 + st.session_state.a_i_fc7
        a_lan_total = st.session_state.a_l_fc7
        a_mar_total = st.session_state.a_m_fc7
        a_total = a_inf_total + a_lan_total + a_mar_total
        st.success(f"⚔️ 攻擊方總兵力：**{a_total:,}**")

        st.caption("📈 面板 12 大屬性 (%)")
        ca1, ca2 = st.columns(2)
        with ca1:
            st.number_input("盾兵攻擊 %", key="a_i_a")
            st.number_input("盾兵防禦 %", key="a_i_d")
            st.number_input("盾兵殺傷 %", key="a_i_l")
            st.number_input("盾兵生命 %", key="a_i_h")
            st.number_input("矛兵攻擊 %", key="a_l_a")
            st.number_input("矛兵防禦 %", key="a_l_d")
        with ca2:
            st.number_input("矛兵殺傷 %", key="a_l_l")
            st.number_input("矛兵生命 %", key="a_l_h")
            st.number_input("射手攻擊 %", key="a_m_a")
            st.number_input("射手防禦 %", key="a_m_d")
            st.number_input("射手殺傷 %", key="a_m_l")
            st.number_input("射手生命 %", key="a_m_h")

    # 🏰 防守方
    with col_def_ui:
        st.header("🏰 防守方 (Defender)")
        st.text_input("防守者名稱", key="d_name")
        st.text_input(
            "🛡️ 駐守隊長 / 駐守車身英雄",
            key="d_hero_main",
            help="例：派翠克 / 謝爾蓋 / 阿蒙森 (影響駐守減傷與生命復原)",
        )

        with st.expander("🛡️ 盾兵明細", expanded=True):
            st.number_input(
                "FC7 (Lv 10.1~10.3)", min_value=0, step=1000, key="d_i_fc7"
            )
            st.number_input(
                "FC8 (Lv 10.4~10.8)", min_value=0, step=1000, key="d_i_fc8"
            )

        with st.expander("🗡️ 矛兵明細", expanded=False):
            st.number_input(
                "FC7 (Lv 10.1~10.3)", min_value=0, step=1000, key="d_l_fc7"
            )

        with st.expander("🏹 射手明細", expanded=False):
            st.number_input(
                "FC7 (Lv 10.1~10.3)", min_value=0, step=1000, key="d_m_fc7"
            )

        d_inf_total = st.session_state.d_i_fc7 + st.session_state.d_i_fc8
        d_lan_total = st.session_state.d_l_fc7
        d_mar_total = st.session_state.d_m_fc7
        d_total = d_inf_total + d_lan_total + d_mar_total
        st.success(f"🏰 防守方總兵力：**{d_total:,}**")

        st.caption("📈 面板 12 大屬性 (%)")
        cd1, cd2 = st.columns(2)
        with cd1:
            st.number_input("盾兵攻擊 %", key="d_i_a")
            st.number_input("盾兵防禦 %", key="d_i_d")
            st.number_input("盾兵殺傷 %", key="d_i_l")
            st.number_input("盾兵生命 %", key="d_i_h")
            st.number_input("矛兵攻擊 %", key="d_l_a")
            st.number_input("矛兵防禦 %", key="d_l_d")
        with cd2:
            st.number_input("矛兵殺傷 %", key="d_l_l")
            st.number_input("矛兵生命 %", key="d_l_h")
            st.number_input("射手攻擊 %", key="d_m_a")
            st.number_input("射手防禦 %", key="d_m_d")
            st.number_input("射手殺傷 %", key="d_m_l")
            st.number_input("射手生命 %", key="d_m_h")

# ---------------------------------------------------------
# TAB 2: 動態 12 大屬性對比數據表
# ---------------------------------------------------------
with tab_compare:
    st.header("📊 12 大屬性動態對比表 (Delta)")
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
# TAB 3: AI 戰術大師診斷與英雄搭配建議
# ---------------------------------------------------------
with tab_advice:
    st.header("💡 AI 戰力診斷與車頭/車身英雄搭配建議")

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

    m1, m2, m3 = st.columns(3)
    m1.metric("兵量比 (攻 / 守)", f"{troop_ratio:.2f} 倍")
    m2.metric(f"{st.session_state.a_name} 盾兵 EHP", f"{a_ehp:,.0f}")
    m3.metric(f"{st.session_state.d_name} 盾兵 EHP", f"{d_ehp:,.0f}")

    st.markdown("---")
    st.subheader("🤖 AI 戰術大師 - 深度英雄與面板診斷")

    api_key = st.text_input(
        "輸入 OpenAI API Key 啟用 AI 英雄與戰術深度診斷 (選填)",
        type="password",
    )

    if st.button("🧠 啟動 AI 戰術與英雄技能深度分析", type="primary"):
        if not api_key:
            st.info("💡 請輸入 OpenAI API Key 以取得 AI 生成的高階英雄搭配與專武解析報告。")
        else:
            try:
                import openai

                client = openai.OpenAI(api_key=api_key)

                prompt_content = f"""
你是一位《寒霜啟示錄 (Whiteout Survival)》頂級玩家與戰術指揮官。請根據以下數據進行深度的戰術與【英雄隊容/車身技能】剖析：

【攻擊方】: {st.session_state.a_name}
- 英雄隊容: {st.session_state.a_hero_main}
- 總兵力: {a_total:,} (盾兵: {a_inf_total}, 矛兵: {a_lan_total}, 射手: {a_mar_total})
- 面板 (盾/矛/射 攻防殺命): 
  盾({st.session_state.a_i_a}%, {st.session_state.a_i_d}%, {st.session_state.a_i_l}%, {st.session_state.a_i_h}%)
  矛({st.session_state.a_l_a}%, {st.session_state.a_l_d}%, {st.session_state.a_l_l}%, {st.session_state.a_l_h}%)
  射({st.session_state.a_m_a}%, {st.session_state.a_m_d}%, {st.session_state.a_m_l}%, {st.session_state.a_m_h}%)
- 盾兵 EHP: {a_ehp:,.0f}

【防守方】: {st.session_state.d_name}
- 英雄隊容: {st.session_state.d_hero_main}
- 總兵力: {d_total:,} (盾兵: {d_inf_total}, 矛兵: {d_lan_total}, 射手: {d_mar_total})
- 面板 (盾/矛/射 攻防殺命): 
  盾({st.session_state.d_i_a}%, {st.session_state.d_i_d}%, {st.session_state.d_i_l}%, {st.session_state.d_i_h}%)
  矛({st.session_state.d_l_a}%, {st.session_state.d_l_d}%, {st.session_state.d_l_l}%, {st.session_state.d_l_h}%)
  射({st.session_state.d_m_a}%, {st.session_state.d_m_d}%, {st.session_state.d_m_l}%, {st.session_state.d_m_h}%)
- 盾兵 EHP: {d_ehp:,.0f}

【兵量與 EHP 比例】: 兵量比 {troop_ratio:.2f} 倍。

請產出包含以下要點的精準報告：
1. **勝負核心評析**：結合屬性差與 EHP 分析戰損主因。
2. **⚔️ 車頭與車身 (Joiner) 英雄優化建議**：點評目前攻擊方的英雄搭配，是否發揮車身第一技能（如傑西/赫羅尼莫的增傷/減傷疊加）。
3. **🏰 防守與駐守 (Garrison) 英雄應對**：點評防守方的英雄選擇（如派翠克/謝爾蓋/阿蒙森）與駐守補兵策略。
"""

                with st.spinner("AI 正在研讀英雄技能與 12 大屬性中..."):
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt_content}],
                        temperature=0.7,
                    )
                    st.markdown(response.choices[0].message.content)

            except Exception as e:
                st.error(f"❌ 解析失敗：{e}")

# ---------------------------------------------------------
# TAB 4: 戰術專有名詞小百科
# ---------------------------------------------------------
with tab_dict:
    st.header("📖 寒霜啟示錄 - 戰術專有名詞與計算公式小百科")

    with st.expander("🛡️ 1. 什麼是 EHP (Effective Health Points 有效承傷值)？", expanded=True):
        st.markdown("""
        * **定義**：EHP 代表一個兵種在實戰中**真正能承受的總傷害上限**。
        * **為什麼重要**：單看「盾兵數量」或單看「防禦 %」都不準確。一位擁有 10 萬 FC8 盾兵且生命/防禦 1500% 的玩家，其總承傷能力可能遠高於擁有 30 萬普通 T10 盾兵但屬性僅 500% 的玩家。
        * **計算公式**：
          $$\\text{盾兵 EHP} = \\text{火晶加權兵量} \\times \\left(1 + \\frac{\\text{生命 \\%}}{100}\\right) \\times \\left(1 + \\frac{\\text{防禦 \\%}}{100}\\right)$$
        """)

    with st.expander("⚔️ 2. 車頭 (Rally Leader) 與 車身 (Rally Joiner) 機制"):
        st.markdown("""
        * **車頭 (集結發起者)**：車頭的 **12 大屬性**、**領主裝備**、**火晶階級** 與 **主要英雄面板** 決定了整個集結部隊的基礎戰力。
        * **車身 (參戰車廂)**：加入集結的隊友稱為車身。車身**不會**提供個人的 12 大屬性面板，但車身前四名玩家的**英雄第一遠征技能 (被動技能)** 會生效並疊加！
        * **熱門車身英雄**：
          * **傑西 (Jessie)**：第一技能提供 **+25% 傷害輸出** (4 位車身疊滿可達 +100%)。
          * **赫羅尼莫 (Jeronimo)**：第一技能提供 **+15% 傷害輸出**。
        """)

    with st.expander("🏰 3. 駐守隊長 (Garrison Leader) 與 駐守車身"):
        st.markdown("""
        * **駐守隊长**：守護建築或盟友城市的負責人，其 12 大屬性為全體駐守部隊的基底。
        * **熱門駐守英雄**：
          * **派翠克 (Patrick)**：提供全隊生命值恢復與生命加成。
          * **謝爾蓋 (Sergey)**：提供全隊受到的傷害降低 (減傷)。
        """)

    with st.expander("🎯 4. 殺傷 (Lethality) vs 防禦 (Defense) / 生命 (Health)"):
        st.markdown("""
        * **攻擊 vs 防禦**：決定基礎戰損的攻防互抵。
        * **殺傷 vs 生命**：殺傷屬於**高階穿透屬性**。當射手的殺傷 % 高於敵方盾兵的生命 % 時，能大幅加快敵方前排盾兵的蒸發速度。
        """)