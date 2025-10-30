import streamlit as st
from io import StringIO
import os
from datetime import datetime
import pytz  # requirements.txt に pytz を追加してください

# ==== ログ関連のユーティリティ ====

def write_log(event_text: str):
    """
    logs/ ディレクトリと app_log.txt を用意し、
    event_text を1行追記する。
    """
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)

    log_path = os.path.join(logs_dir, "app_log.txt")

    # タイムゾーンは日本時間(Asia/Tokyo)で記録
    tz = pytz.timezone("Asia/Tokyo")
    now_str = datetime.now(tz).isoformat(timespec="seconds")

    line = f"{now_str}, {event_text}\n"

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line)
        #st.download_button("ログをダウンロード", data=f.read())


# ==== アプリ本体 ====

st.title("Javaコード表示アプリ（ログ付きテスト）")

# アプリにアクセスしたタイミングでログを残す
# Streamlitは何度も再実行されるので、同じユーザーが
# 何度もアクセスログを残すことになります。これは仕様としてOKとします。
write_log("accessed app")

uploaded_file = st.file_uploader('Javaファイルをアップロード', type='java')

if st.button('コードを表示'):
    if uploaded_file is not None:
        # ファイル名をログ
        write_log(f"uploaded: {uploaded_file.name}")

        # 中身を表示
        stringio = StringIO(uploaded_file.getvalue().decode('utf-8'))
        string_data = stringio.read()
        st.code(string_data, language='java')
    else:
        st.warning("ファイルが選択されていません。")

if os.path.exists(log_path):
    st.subheader("現在のログ（このインスタンス上）")
    with open(log_path, "r", encoding="utf-8") as f:
        log_text = f.read()

    st.download_button(
        "ログをダウンロード",
        data=log_text,
        file_name="app_log.txt",
        mime="text/plain",
    )
else:
    st.info("まだローカルログはありません。")
