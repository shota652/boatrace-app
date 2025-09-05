import streamlit as st
import json
import os

SCENARIO_TYPES = [
    "イン逃げ",
    "2捲り", "2差し",
    "3捲り", "3捲り差し",
    "4捲り", "4捲り差し", "4差し",
    "5捲り", "5捲り差し",
    "6捲り"
]

FILE_PATH = "scenarios.json"


def load_scenarios():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {t: [] for t in SCENARIO_TYPES}


def save_scenarios(data):
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    st.title("展開パターン辞書")

    scenarios = load_scenarios()
    selected_type = st.selectbox("展開を選択してください", SCENARIO_TYPES)

    st.subheader(f"【{selected_type}】の登録パターン")

    if selected_type not in st.session_state:
        st.session_state[selected_type] = [False] * len(scenarios[selected_type])

    if scenarios[selected_type]:
        for idx, pattern in enumerate(scenarios[selected_type], start=1):
            edit_key = f"{selected_type}_{idx}_edit"
            if edit_key not in st.session_state:
                st.session_state[edit_key] = False

            # expanderでカード風表示
            with st.expander(f"{idx}. {pattern['pattern']}", expanded=False):
                st.markdown(f"### {pattern['pattern']}")
                st.markdown(f"📝 <span style='color:blue'>要因:</span> {pattern['factor']}", unsafe_allow_html=True)
                st.markdown(f"🎯 <span style='color:green'>出目:</span> {pattern['result']}", unsafe_allow_html=True)


                if st.session_state[edit_key]:
                    # 編集モード
                    p_input = st.text_input("パターン", value=pattern['pattern'], key=f"{edit_key}_pattern")
                    f_input = st.text_input("要因", value=pattern['factor'], key=f"{edit_key}_factor")
                    r_input = st.text_input("出目", value=pattern['result'], key=f"{edit_key}_result")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("保存", key=f"{edit_key}_save"):
                            pattern['pattern'], pattern['factor'], pattern['result'] = p_input, f_input, r_input
                            save_scenarios(scenarios)
                            st.session_state[edit_key] = False
                            st.rerun()
                    with col2:
                        if st.button("キャンセル", key=f"{edit_key}_cancel"):
                            st.session_state[edit_key] = False
                            st.rerun()
                else:
                    # 編集ボタン
                    if st.button("編集", key=f"{edit_key}_btn"):
                        st.session_state[edit_key] = True
                        st.rerun()
    else:
        st.info("まだ登録されていません。")

    st.markdown("---")
    st.subheader("新しいパターンを追加")
    with st.form("add_pattern"):
        pattern = st.text_input("パターン（例: ジカマ成功）", key="pattern")
        factor = st.text_input("要因（例: 1号艇スタート遅れ）", key="factor")
        result = st.text_input("出目（例: 2-1,2-3,2-4）", key="result")

        submitted = st.form_submit_button("追加")
        if submitted:
            if pattern and result:
                new_entry = {
                    "pattern": pattern,
                    "factor": factor,
                    "result": result
                }
                scenarios[selected_type].append(new_entry)
                save_scenarios(scenarios)

                # 入力欄をリセット
                st.session_state.pattern = ""
                st.session_state.factor = ""
                st.session_state.result = ""

                st.success("追加しました！")
                st.rerun()
            else:
                st.error("パターンと出目は必須です。")


if __name__ == "__main__":
    main()