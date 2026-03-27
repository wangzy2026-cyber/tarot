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
    /* 1. 全局深色背景 */
    .stApp {
        background-color: #0e1117 !important;
    }
    
    /* 2. 输入框样式 */
    div[data-baseweb="input"], 
    div[data-baseweb="base-input"],
    .stTextInput>div>div {
        background-color: #1a1c24 !important;
        border: 1px solid #d4af37 !important;
    }

    /* 3. 文字颜色 */
    input {
        color: #d4af37 !important;
    }
    h1, h2, h3, p, label, .stMarkdown {
        color: #f0f0f0 !important;
    }

    /* 4. 按钮样式：黑底金边 */
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

    /* 5. 隐藏页眉页脚 */
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
    1. 在下方写下你心中的疑惑，越具体越好。<br>
    2. 点击抽牌，AI 占卜师将为你进行深度解读。<br>
    <span style='font-size: 0.8em; opacity: 0.7;'> (基于 DeepSeek 大模型提供解读) </span>
</div>
""", unsafe_allow_html=True)
st.write("")

# 2. 核心牌库
MAJOR_ARCANA = {
    "愚者 (The Fool)": {"正位": "新的开始、自发性、信念的飞跃", "逆位": "鲁莽、停滞、糟糕的决定"},
    "魔术师 (The Magician)": {"正位": "显化、资源充足、力量", "逆位": "操控、规划不周、未开发的潜力"},
    "女祭司 (The High Priestess)": {"正位": "直觉、潜意识、神秘", "逆位": "直觉被封锁、秘密、肤浅"},
    "女皇 (The Empress)": {"正位": "丰饶、母性、自然", "逆位": "创造力受阻、过度依赖"},
    "皇帝 (The Emperor)": {"正位": "权威、结构、稳固", "逆位": "暴政、缺乏自律、控制欲强"},
    "教皇 (The Hierophant)": {"正位": "传统、精神智慧、规范", "逆位": "叛逆、打破常规、新观念"},
    "恋人 (The Lovers)": {"正位": "爱、和谐、选择", "逆位": "失衡、自我爱怜、关系不合"},
    "战车 (The Chariot)": {"正位": "意志力、胜利、行动力", "逆位": "失去控制、方向不明、攻击性"},
    "力量 (Strength)": {"正位": "勇气、耐心、内心力量", "逆位": "自我怀疑、软弱、情绪失控"},
    "隐士 (The Hermit)": {"正位": "内省、孤独、寻求真理", "逆位": "孤立、偏执、逃避"},
    "命运之轮 (Wheel of Fortune)": {"正位": "转折、业力、生命的循环", "逆位": "运气不好、抗拒改变、打破循环"},
    "正义 (Justice)": {"正位": "公平、真理、法律因果", "逆位": "不公、逃避责任、偏见"},
    "倒吊人 (The Hanged Man)": {"正位": "换位思考、释放、牺牲", "逆位": "拖延、无谓的牺牲、停滞"},
    "死神 (Death)": {"正位": "终结、转变、新生", "逆位": "抗拒改变、恐惧、停滞不前"},
    "节制 (Temperance)": {"正位": "平衡、适度、目标明确", "逆位": "失衡、极端、缺乏目标"},
    "恶魔 (The Devil)": {"正位": "束缚、成瘾、物质欲望", "逆位": "释放、自我觉醒、斩断束缚"},
    "高塔 (The Tower)": {"正位": "剧变、灾难、真相大白", "逆位": "延迟的灾难、害怕改变、逃过一劫"},
    "星星 (The Star)": {"正位": "希望、灵感、宁静", "逆位": "失望、缺乏信仰、迷茫"},
    "月亮 (The Moon)": {"正位": "不安、幻觉、潜意识", "逆位": "释怀、看清真相、克服恐惧"},
    "太阳 (The Sun)": {"正位": "快乐、成功、生命力", "逆位": "暂时受挫、过度乐观、虚假繁荣"},
    "审判 (Judgement)": {"正位": "觉醒、重生、使命感", "逆位": "自我怀疑、拒绝召唤、优柔寡断"},
    "世界 (The World)": {"正位": "完成、整合、圆满", "逆位": "缺乏完成、不完整的循环、未实现的潜能"}
}

# 3. 连接 DeepSeek 大脑
def get_deepseek_interpretation(question, drawn_cards_info):
    st.write("---")
    st.subheader("💡 占卜师直言")
    
    try:
        api_key = st.secrets["DEEPSEEK_API_KEY"]
    except Exception:
        st.error("⚠️ 密钥未配置，请在 Streamlit Secrets 中设置 DEEPSEEK_API_KEY")
        return

    cards_text = ""
    for card in drawn_cards_info:
        cards_text += f"- {card['pos']}：{card['name']} ({card['orientation']})\n"
    
    # 修改后的提示词：拒绝废话版本
    system_prompt = """
    你是一位言辞犀利、一针见血的职业塔罗占卜师。
    你的解读要求：
    1. 拒绝任何“宇宙、星辰、能量”等虚无缥缈的废话套话。
    2. 直接点出问题的核心本质和当前的阻碍。
    3. 给出1-2条具体的、可执行的行动建议。
    4. 语气要像个睿智的朋友在说大白话。
    5. 总字数控制在 250 字左右，排版清晰。
    """
    user_prompt = f"问题：【{question}】\n牌阵：\n{cards_text}\n请直接给出最干货的解读。"

    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        with st.spinner('正在看透真相...'):
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.
