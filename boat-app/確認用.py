import streamlit as st

st.write("【デバッグ】df_move の中身（先頭5件）")
st.write(df_move.head())

st.write("【デバッグ】df_move のカラム一覧")
st.write(df_move.columns.tolist())

st.write("【デバッグ】ST評価 列の値一覧（欠損含む）")
st.write(df_move["ST評価"].unique())

st.write("【デバッグ】ST評価の件数カウント")
st.write(df_move["ST評価"].value_counts(dropna=False))