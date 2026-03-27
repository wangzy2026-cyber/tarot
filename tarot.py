import streamlit as st
import random
import time
from openai import OpenAI

# 1. 界面与配置
st.set_page_config(page_title="AI 塔罗神殿", page_icon="🔮")

# --- 统一注入 CSS 样式 ---
st.markdown(
    """
    <style>
    .stApp { background-color: #0e1117 !important; }
    div[data-baseweb="input"], div[data-baseweb="base-input"], .stTextInput>div>div {
        background-color: #1a1c24 !important;
        border: 1px solid #d4af37 !important;
    }
    input { color: #d4af37 !important; }
    h1, h2, h3, p, label, .stMarkdown { color: #f0f0f0 !important; }
    .stButton>button {
        background-color: #1a1c24 !important;
        color: #d4af37 !important;
        border: 2px solid #d4af37 !important;
        width: 100%;
        border-radius: 5px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #d4af37 !important;
        color: #0e1117 !important;
        transform: scale(1.02);
        box-shadow: 0 0 15px #6a11cb;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🔮 AI 塔罗神殿：智慧之眼")
st.markdown("""
<div style='background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; border-left: 5px solid #d4af37;'>
    <strong style='color: #d4af37;'>仪式指南：</strong><br>
    1. 写下具体疑惑 -> 2. 点击抽牌 -> 3. 听大白话解读。
</div>
""", unsafe_allow_html=True)

# 2. 核心牌库
MAJOR_ARCANA = {
    "愚者 (The Fool)": {"正位": "新的开始、信念、冒险", "逆位": "鲁
