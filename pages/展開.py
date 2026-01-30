import streamlit as st
import json
import os

SCENARIO_TYPES = [
    "イン逃げ",
    "2捲り", "2差し",
    "3捲り", "3捲り差し",
    "4捲り", "4捲り差し", "4差し",
    "5捲り", "5捲り差し",
    "6捲り", "6捲り差し"
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

    scenarios[selected_type] = sorted(
        scenarios[selected_type],
        key=lambda x: x["pattern"]
    )

    st.subheader(f"【{selected_type}】の登録パターン")

    if selected_type not in st.session_state:
        st.session_state[selected_type] = [False] * len(scenarios[selected_type])

    if scenarios[selected_type]:
        for idx, pattern in enumerate(scenarios[selected_type], start=1):
            edit_key = f"{selected_type}_{idx}_edit"
            if edit_key not in st.session_state:
                st.session_state[edit_key] = False

            # expanderでカード風表示
            with st.expander(f"{idx}. **{pattern['pattern']}**", expanded=False):
                st.markdown(f"📝 <span style='color:blue'>要因:</span> {pattern['factor']}", unsafe_allow_html=True)

                pattern["results"].sort(key=lambda x: x["count"], reverse=True)

                for r in pattern["results"]:
                    col1,col2 = st.columns([3,1])
                    with col1:
                        st.write(f"🎯 {r['kimari']}（{r['count']}）")
                    with col2:
                        if st.button("＋", key=f"plus_{selected_type}_{idx}_{r['kimari']}"):
                            r["count"] += 1
                            save_scenarios(scenarios)
                            st.rerun()


                if st.session_state[edit_key]:
                    # 編集モード
                    # --- パターン・要因 ---
                    p_input = st.text_input("パターン", value=pattern['pattern'], key=f"{edit_key}_pattern")
                    f_input = st.text_input("要因", value=pattern['factor'], key=f"{edit_key}_factor")

                    st.markdown("### 出目一覧")


                    for i, r in enumerate(pattern["results"]):
                        c1, c2, c3 = st.columns([3,2,1])

                        with c1:
                            kimari = st.text_input(
                                "出目",
                                value=r["kimari"],
                                key=f"{edit_key}_kimari_{i}"
                            )

                        with c2:
                            count = st.number_input(
                                "回数",
                                min_value=0,
                                value=r["count"],
                                key=f"{edit_key}_count_{i}"
                            )

                        with c3:
                            if st.button("❌", key=f"{edit_key}_del_{i}"):
                                pattern["results"].pop(i)
                                save_scenarios(scenarios)
                                st.rerun()

                        r["kimari"] = kimari
                        r["count"] = count

                    st.markdown("---")
                    st.markdown("### 新しい出目を追加")

                    c1,c2,c3,c4 = st.columns(4)
                    with c1:
                        n1 = st.selectbox("1着", ["1","2","3","4","5","6"], key=f"{edit_key}_n1")
                    with c2:
                        n2 = st.selectbox("2着", ["1","2","3","4","5","6"], key=f"{edit_key}_n2")
                    with c3:
                        n3 = st.selectbox("3着", ["1","2","3","4","5","6"], key=f"{edit_key}_n3")
                    with c4:
                        ncount = st.number_input("回数", min_value=1, value=1, key=f"{edit_key}_ncount")
 
                    if st.button("追加", key=f"{edit_key}_add"):
                        new_kimari = f"{n1}-{n2}-{n3}"

                        exists = False
                        for r in pattern["results"]:
                            if r["kimari"] == new_kimari:
                                r["count"] += ncount
                                exists = True

                        if not exists:
                            pattern["results"].append(
                                {"kimari": new_kimari, "count": ncount}
                            )

                        save_scenarios(scenarios)
                        st.rerun()

                    st.markdown("---")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("保存", key=f"{edit_key}_save"):
                            pattern['pattern'] = p_input
                            pattern['factor'] = f_input
                            save_scenarios(scenarios)
                            st.session_state[edit_key] = False
                            st.rerun()
                    with col2:
                        if st.button("キャンセル", key=f"{edit_key}_cancel"):
                            st.session_state[edit_key] = False
                            st.rerun()
                    st.markdown("---")
                    if st.button("🗑 このパターンを削除", key=f"{edit_key}_delete_pattern"):
                        scenarios[selected_type].pop(idx-1)
                        save_scenarios(scenarios)
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
    with st.form("add_pattern", clear_on_submit=True):
        pattern = st.text_input("パターン（例: ジカマ成功）", key="pattern")
        factor = st.text_input("要因（例: 1号艇スタート遅れ）", key="factor")
        col1,col2,col3 = st.columns(3)
        with col1:
            r1 = st.selectbox("1着", ["1","2","3","4","5","6"])
        with col2:
            r2 = st.selectbox("2着", ["1","2","3","4","5","6"])
        with col3:
            r3 = st.selectbox("3着", ["1","2","3","4","5","6"])

        results = f"{r1}-{r2}-{r3}"

        submitted = st.form_submit_button("追加")
        if submitted:
            if pattern and results:
                new_entry = {
                    "pattern": pattern.strip(),
                    "factor": factor.strip(),
                    "results": [
                      {"kimari": results, "count":1}
                    ]
                }

                # 重複チェック
                if new_entry in scenarios[selected_type]:
                    st.warning("同じパターンがすでに存在します。")
                else:
                    scenarios[selected_type].append(new_entry)
                    save_scenarios(scenarios)
                    st.success("追加しました！")
                    st.rerun()
            else:
                st.error("パターンと出目は必須です。")


if __name__ == "__main__":
    main()