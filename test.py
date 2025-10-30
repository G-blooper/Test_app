import streamlit as st
from io import StringIO
from datetime import datetime
import pytz
import base64
import requests

# ====== Secretsから読み込み ======
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_OWNER = st.secrets["REPO_OWNER"]
REPO_NAME  = st.secrets["REPO_NAME"]

GITHUB_API_BASE = "https://api.github.com"

# GitHubリポジトリ上でのログファイルのパス
REMOTE_LOG_PATH = "logs/app_log.txt"


def timestamp_jst_iso():
    """日本時間(Asia/Tokyo)の現在時刻を ISO8601 文字列で返す"""
    tz = pytz.timezone("Asia/Tokyo")
    return datetime.now(tz).isoformat(timespec="seconds")


def get_github_file(owner: str, repo: str, path: str):
    """
    GitHub上のファイルを取得し、JSON(dict)を返す。
    返り値の例:
      {
        "content": "<base64...>",
        "sha": "...",
        ...
      }
    ファイルがない場合は None を返す。
    エラー時は st.error() で通知して None を返す。
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json()
    elif r.status_code == 404:
        # まだ存在しない
        return None
    else:
        st.error(f"GitHub API error (GET {path}): {r.status_code} {r.text}")
        return None


def append_line_to_repo_log(owner: str, repo: str, path: str, event_text: str):
    """
    指定のevent_textを1行として、GitHub上の logs/app_log.txt に追記する。
    仕組み:
      1. いまのファイルをGET
      2. デコードして末尾に event_text+"\n" を足す
      3. 再エンコードして PUT でアップロード
    新規ファイルの場合は、新しく作る。
    """
    # 1行分を "timestamp, event_text" の形式で整える
    line = f"{timestamp_jst_iso()}, {event_text}"

    existing = get_github_file(owner, repo, path)

    if existing is None:
        # ファイルが存在しない場合は新規作成
        updated_text = line + "\n"
        sha = None
    else:
        # 既存ファイルあり -> もとのcontentを取り出して追記
        b64_content = existing["content"]
        decoded = base64.b64decode(b64_content).decode("utf-8")
        updated_text = decoded + line + "\n"
        sha = existing["sha"]

    # base64エンコード
    b64_updated = base64.b64encode(updated_text.encode("utf-8")).decode("utf-8")

    # PUTで更新
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "message": f"Append log at {timestamp_jst_iso()}",
        "content": b64_updated,
    }
    if sha:
        payload["sha"] = sha  # 既存ファイル更新時に必須

    r = requests.put(url, headers=headers, json=payload)

    if r.status_code not in (200, 201):
        st.error(f"GitHub API error (PUT {path}): {r.status_code} {r.text}")


# =====================================================
# Streamlitアプリ本体
# =====================================================

st.title("Javaコード表示アプリ（GitHub永続ログ版）")

# セッションごとに1回だけアクセスログを残す
if "visited_logged" not in st.session_state:
    append_line_to_repo_log(REPO_OWNER, REPO_NAME, REMOTE_LOG_PATH, "accessed app")
    st.session_state["visited_logged"] = True

uploaded_file = st.file_uploader('Javaファイルをアップロード', type='java')

if st.button('コードを表示'):
    if uploaded_file is not None:
        # --- ログを残す（アップロードされたファイル名）
        append_line_to_repo_log(
            REPO_OWNER,
            REPO_NAME,
            REMOTE_LOG_PATH,
            f"uploaded: {uploaded_file.name}"
        )

        # --- ファイル内容を表示
        string_data = uploaded_file.getvalue().decode('utf-8')
        st.code(string_data, language='java')
    else:
        st.warning("ファイルが選択されていません。")


# 参考用: GitHub側に蓄積されている最新ログを読み戻して画面に表示
# （「今、何がpushされてるのか目視したい」ための確認UI）
existing_log = get_github_file(REPO_OWNER, REPO_NAME, REMOTE_LOG_PATH)
if existing_log is not None:
    b64_content = existing_log["content"]
    decoded = base64.b64decode(b64_content).decode("utf-8")
    st.subheader("GitHubに保存されているログ")
    st.text(decoded)
else:
    st.info("GitHub側にまだログファイルがありません。")
