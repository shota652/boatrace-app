import sqlite3
import shutil

# ✅ 元のDBをバックアップ（安全策）
shutil.copy("boatrace_data.db", "boatrace_data_backup.db")
print("バックアップ作成済み")

# ✅ DB接続
conn = sqlite3.connect("boatrace_data.db")
cursor = conn.cursor()

# ✅ 新しいテーブルを作成（不要カラムを除き、カラム順を変更）
cursor.execute("""
CREATE TABLE race_data_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    venue_name TEXT,
    race_number INTEGER,
    course_in INTEGER,
    player_name TEXT,
    move TEXT,
    second_place INTEGER,
    lost_to INTEGER,
    rank INTEGER,
    flow INTEGER,
    cabi INTEGER,
    kawarizensoku INTEGER,
    attack INTEGER,
    pressure INTEGER,
    block INTEGER,
    three_hari INTEGER,
    three_makurizashi INTEGER,
    two_nokoshi INTEGER,
    four_tsubushi INTEGER,
    four_nokoshi INTEGER,
    st_eval TEXT
)
""

# ✅ 旧テーブルから必要なデータを移行（idも含めてコピー）
cursor.execute("""
INSERT INTO race_data_new (
    id, date, venue_name, race_number, course_in, player_name,
    move, second_place, lost_to, rank,
    flow, cabi, kawarizensoku, attack, pressure, block,
    three_hari, three_makurizashi, two_nokoshi,
    four_tsubushi, four_nokoshi, st_eval
)
SELECT
    id, date, venue_name, race_number, course_in, player_name,
    move, second_place, lost_to, rank,
    flow, cabi, kawarizensoku, attack, pressure, block,
    three_hari, three_makurizashi, two_nokoshi,
    four_tsubushi, four_nokoshi, st_eval
FROM race_data
""")

# ✅ 旧 race_data テーブルを削除
cursor.execute("DROP TABLE race_data")

# ✅ 新テーブルの名前を race_data に変更
cursor.execute("ALTER TABLE race_data_new RENAME TO race_data")

# ✅ コミットして完了
conn.commit()
conn.close()

print("✅ 不要カラムを削除し、race_data テーブルを再構築しました。")