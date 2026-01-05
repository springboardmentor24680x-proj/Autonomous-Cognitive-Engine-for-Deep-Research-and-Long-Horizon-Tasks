import streamlit as st
from vfs import VirtualFileSystem

# Keep VFS alive across UI actions
if "vfs" not in st.session_state:
    st.session_state.vfs = VirtualFileSystem()

vfs = st.session_state.vfs

st.set_page_config(page_title="Virtual File System UI", layout="wide")
st.title(" Virtual File System (External Memory UI)")

# Sidebar: list files
st.sidebar.header(" Files in Memory")
files = vfs.list_files()
if files:
    for f in files:
        st.sidebar.write(f)
else:
    st.sidebar.write("No files created yet")

st.divider()

# Write / Edit section
st.subheader("Write / Edit File")

filename = st.text_input("Filename")
content = st.text_area("Content", height=150)

col1, col2 = st.columns(2)

with col1:
    if st.button("Write File"):
        if filename and content:
            st.success(vfs.write_file(filename, content))
        else:
            st.warning("Filename and content required")

with col2:
    if st.button("Edit File"):
        if filename and content:
            st.success(vfs.edit_file(filename, content))
        else:
            st.warning("Filename and content required")

st.divider()

# Read section
st.subheader("Read File")
read_filename = st.text_input("Filename to read", key="read")

if st.button("Read File"):
    st.text_area("File Content", vfs.read_file(read_filename), height=150)

