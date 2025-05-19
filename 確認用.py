import pandas as pd

# CSVファイルを読み込み
df = pd.read_csv("boatrace_data.csv")

# カラム名の一覧を表示
print("CSVのカラム名一覧：")
print(df.columns.tolist())

# カラム数を確認
print("カラム数：", len(df.columns))