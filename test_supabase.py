# 必要なモジュールをインポート
from supabase import create_client, Client
from datetime import date

# ここにあなたの Supabase のURLとAPIキーを入力してください
SUPABASE_URL = "https://dhmtiglgbmrsoovgkslg.supabase.co"  # ← 自分のURLに変えてね
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRobXRpZ2xnYm1yc29vdmdrc2xnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc0NjM0NzksImV4cCI6MjA2MzAzOTQ3OX0.nH5amkfjl4JFFgUa7ZSojlvBa_m0IpIznCIYQ3Ol8n8"             # ← 自分のKeyに変えてね

# Supabaseに接続
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ここが登録したいデータの中身（例）
data = {
    "race_date": date(2025, 5, 17).isoformat(),  # 登録日（今日の日付）
    "place": "住之江",                    # 開催場
    "race_number": 5,                       # レース番号
    "player_name": "田中太郎",              # 選手名
    "course": 3,                            # 進入コース
}

# Supabaseのテーブル名を指定してINSERT
response = supabase.table("boat_race_data").insert(data).execute()

print("=== レスポンス ===")
print(response)

if response.data:
    print("✅ データの挿入に成功しました")
else:
    print("❌ 挿入に失敗しました")