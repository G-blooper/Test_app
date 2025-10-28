import streamlit as st
from io import StringIO

###(テスト)アップロードされたJavaのソースコードを、streamlit上で表示できるようにするプログラム
# Input
uploaded_file = st.file_uploader('Javaファイルをアップロード', type='java')

# Process
if st.button('コードを表示'):
  if uploaded_file is not None:
    stringio = StringIO(uploaded_file.getvalue().decode('utf-8'))
    string_data = stringio.read()
# Output
    st.code(string_data, language='java')
