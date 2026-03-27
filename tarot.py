import streamlit as st
import random
import time
from openai import OpenAI

# 1. 界面与配置
st.set_page_config(page_title="AI 塔罗神殿", page_icon="🔮")

# --- 注入 CSS 样式 ---
st.markdown(
    """
    <style>
    /* 开屏闪现层 */
    #splash-screen {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: #0e1117;
        display: flex; justify-content: center; align-items: center;
        z-index: 99999;
        animation: fadeOut 3.5s forwards;
        pointer-events: none;
    }
    .content { text-align: center; }
    .content img { 
        max-width: 85vw; max-height: 70vh; 
        border-radius: 20px; 
        border: 2px solid #d4af37;
        box-shadow: 0 0 30px rgba(212, 175, 55, 0.5);
    }
    
    @keyframes fadeOut {
        0% { opacity: 1; }
        80% { opacity: 1; }
        100% { opacity: 0; visibility: hidden; }
    }

    /* 基础界面样式 */
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
    }
    .stButton>button:hover {
        background-color: #d4af37 !important;
        color: #0e1117 !important;
        box-shadow: 0 0 15px #6a11cb;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# --- 爱豆开屏照片 (根据你的仓库路径动态生成) ---
st.markdown(
    """
    <div id="splash-screen">
        <div class="content">
            <img src="https://raw.githubusercontent.com/W-Ziyuan/tarot/main/10abb0d1c3f7bf9dcbae406c91ef9645.jpeg?v=1" onerror="this.style.display='none'">
            <p style="color: #d4af37; margin-top: 20px; font-weight: bold;">✨ 正在链接宇宙能量... ✨</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("🔮 AI 塔罗神殿：智慧之眼")

# 2. 核心牌库
MAJOR_ARCANA = {
    "愚者 (The Fool)": {"正位": "新的开始、信念、冒险", "逆位": "鲁莽、停滞、盲目"},
    "魔术师 (The Magician)": {"正位": "显化、力量、行动", "逆位": "操控、怀才不遇"},
    "女祭司 (The High Priestess)": {"正位": "直觉、潜意识", "逆位": "肤浅、忽略内心"},
    "女皇 (The Empress)": {"正位": "丰饶、母性", "逆位": "缺乏安全感、过度依赖"},
    "皇帝 (The Emperor)": {"正位": "权威、稳固", "逆位": "暴政、死板"},
    "教皇 (The Hierophant)": {"正位": "传统、引导", "逆位": "叛逆、新观念"},
    "恋人 (The Lovers)": {"正位": "爱、和谐", "逆位": "失衡、错误选择"},
    "战车 (The Chariot)": {"正位": "胜利、意志", "逆位": "失控、攻击性"},
    "力量 (Strength)": {"正位": "勇气、耐心", "逆位": "自我怀疑、软弱"},
    "隐士 (The Hermit)": {"正位": "内省、真理", "逆位": "孤立、逃避"},
    "命运之轮 (Wheel of Fortune)": {"正位": "转折、好运", "逆位": "时运不济、抗拒"},
    "正义 (Justice)": {"正位": "公平、责任", "逆位": "不公、逃避"},
    "倒吊人 (The Hanged Man)": {"正位": "换位思考、牺牲", "逆位": "拖延、无谓付出"},
    "死神 (Death)": {"正位": "终结、新生", "逆位": "抗拒、停滞"},
    "节制 (Temperance)": {"正位": "平衡、适度", "逆位": "失衡、极端"},
    "恶魔 (The Devil)": {"正位": "束缚、欲望", "逆位": "释放、觉醒"},
    "高塔 (The Tower)": {"正位": "剧变、真相", "逆位": "延迟灾难、害怕"},
    "星星 (The Star)": {"正位": "希望、灵感、宁静", "逆位": "失望、迷茫"},
    "月亮 (The Moon)": {"正位": "不安、幻觉、潜意识", "逆位": "释怀、看清真相"},
    "太阳 (The Sun)": {"正位": "快乐、成功", "逆位": "暂时受挫、乐观过度"},
    "审判 (Judgement)": {"正位": "觉醒、重生", "逆位": "怀疑、拒绝召唤"},
    "世界 (The World)": {"正位": "圆满、整合", "逆位": "未竟之志、停滞"}
}

# 3. 解读函数
def get_deepseek_interpretation(question, cards_list):
    st.write("---")
    st.subheader("💡 占卜师直言")
    try:
        api_key = st.secrets["DEEPSEEK_API_KEY"]
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        
        prompt_cards = ""
        for c in cards_list:
            prompt_cards += f"{c['pos']}: {c['name']} ({c['status']})\n"
        
        # 核心指令：切断网络联想，只看牌面
        system_msg = """你是一位完全中立、冷酷、拒绝废话的塔罗分析师。
        你的原则是：
        1. 严禁联网查询或引用任何关于现实人物（如明星、艺人、公众人物）的网络八卦、生平或评价。
        2. 你的解读必须完全、唯一、仅仅来源于当前抽到的【牌面意义】及其【正逆位】。
        3. 不要说“可能、大概、似乎”，直接点破死穴，给出硬核建议。
        4. 拒绝使用“星辰、能量、宇宙、灵性”等玄学套话。
        5. 总字数控制在200字内，排版清晰。"""
        
        user_msg = f"问题：【{question}】\n牌阵：\n{prompt_cards}\n请完全基于以上牌义，不要联想任何网络已知信息，给出最纯粹的解读。"

        with st.spinner('切断外部干扰，深入牌阵...'):
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
                temperature=0.8
            )
        st.markdown(response.choices[0].message.content)
    except Exception as e:
        st.error(f"解读中断，请检查设置。")

# 4. 页面交互
user_question = st.text_input("输入你的困惑：")

if st.button("✨ 开启真相之门 ✨"):
    if not user_question:
        st.warning("请先输入问题。")
    else:
        with st.spinner('正在洗牌...'):
            time.sleep(1)
        
        drawn_names = random.sample(list(MAJOR_ARCANA.keys()), 3)
        spread_labels = ["【过去/根源】", "【现状/阻碍】", "【建议/指引】"]
        
        final_cards_for_ai = []
        cols = st.columns(3)
        
        for i in range(3):
            with cols[i]:
                name = drawn_names[i]
                status = random.choice(["正位", "逆位"])
                meaning = MAJOR_ARCANA[name][status]
                
                final_cards_for_ai.append({
                    "pos": spread_labels[i],
                    "name": name,
                    "status": status
                })
                
                st.markdown(f"**{spread_labels[i]}**")
                st.markdown(f"### {name}")
                st.write(f"{'**正位** ⬆️' if status == '正位' else '**逆位** ⬇️'}")
                st.markdown(f"<p style='color:#d4af37; font-style:italic;'>{meaning}</p>", unsafe_allow_html=True)
        
        get_deepseek_interpretation(user_question, final_cards_for_ai)
        st.balloons()
