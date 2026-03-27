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
    "星星 (The Star)": {"正位": "希望、宁静", "逆位": "失望、迷茫"},
    "月亮 (The Moon)": {"正位": "不安、潜意识", "逆位": "释怀、看清"},
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
        
        # 整理牌阵信息传给 AI
        prompt_cards = ""
        for c in cards_list:
            prompt_cards += f"{c['pos']}: {c['name']} ({c['status']})\n"
        
        system_msg = "你是一位毒舌犀利、拒绝套话的塔罗师。直接说本质和阻碍，给具体建议，禁止废话，200字左右。"
        user_msg = f"问题：【{question}】\n牌阵：\n{prompt_cards}\n请解读。"

        with st.spinner('看透真相中...'):
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
                temperature=0.8
            )
        st.markdown(response.choices[0].message.content)
    except Exception as e:
        st.error(f"失败：请确认 Streamlit Secrets 里配置了 DEEPSEEK_API_KEY。具体错误：{e}")

# 4. 页面交互
user_question = st.text_input("输入你的困惑：")

if st.button("✨ 开启真相之门 ✨"):
    if not user_question:
        st.warning("请先输入问题。")
    else:
        with st.spinner('正在洗牌...'):
            time.sleep(1)
        
        # 抽取三张牌
        drawn_names = random.sample(list(MAJOR_ARCANA.keys()), 3)
        spread_labels = ["【过去/根源】", "【现状/阻碍】", "【建议/指引】"]
        
        final_cards_for_ai = []
        cols = st.columns(3)
        
        for i in range(3):
            with cols[i]:
                name = drawn_names[i]
                status = random.choice(["正位", "逆位"])
                meaning = MAJOR_ARCANA[name][status]
                
                # 存入列表传给 AI
                final_cards_for_ai.append({
                    "pos": spread_labels[i],
                    "name": name,
                    "status": status
                })
                
                # 界面显示
                st.markdown(f"**{spread_labels[i]}**")
                st.markdown(f"### {name}")
                st.write(f"{'**正位** ⬆️' if status == '正位' else '**逆位** ⬇️'}")
                st.markdown(f"<p style='color:#d4af37; font-style:italic;'>{meaning}</p>", unsafe_allow_html=True)
        
        # 调用解读
        get_deepseek_interpretation(user_question, final_cards_for_ai)
        st.balloons()
