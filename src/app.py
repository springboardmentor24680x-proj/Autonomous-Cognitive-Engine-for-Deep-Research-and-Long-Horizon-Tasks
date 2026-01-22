import streamlit as st
from vfs import VirtualFileSystem

# Initialize VFS in session (IMPORTANT)
if "vfs" not in st.session_state:
    st.session_state.vfs = VirtualFileSystem()

vfs = st.session_state.vfs

st.set_page_config(page_title="VFS Memory Agent", layout="wide")
st.title(" Virtual File System – Memory Agent")

# Sidebar: File list
st.sidebar.header("Files in Memory")
files = vfs.ls()
if files:
    for f in files:
        st.sidebar.write(f)
else:
    st.sidebar.write("No files yet")

# Main UI
st.subheader("Write / Edit File")
filename = st.text_input("Filename")
content = st.text_area("File Content", height=150)

col1, col2 = st.columns(2)

with col1:
    if st.button("Write File"):
        if filename and content:
            msg = vfs.write_file(filename, content)
            st.success(msg)

with col2:
    if st.button("Edit File"):
        if filename and content:
            msg = vfs.edit_file(filename, content)
            st.success(msg)

st.divider()

st.subheader("Read File")
read_filename = st.text_input("Filename to read")

if st.button("Read File"):
    result = vfs.read_file(read_filename)
    st.text_area("File Output", result, height=150)

