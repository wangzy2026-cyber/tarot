import streamlit as st
import random
import time
from openai import OpenAI

# 1. 界面与配置
st.set_page_config(page_title="AI 塔罗神殿", page_icon="🔮")

# --- 注入 CSS 样式 (保留爱豆开屏逻辑) ---
st.markdown(
    """
    <style>
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
    .stApp { background-color: #0e1117 !important; }
    div[data-baseweb="input"], .stTextInput>div>div {
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
    header, footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# --- 图片显示逻辑 (确保链接准确) ---
st.markdown(
    """
    <div id="splash-screen">
        <div class="content">
            <img src="https://raw.githubusercontent.com/W-Ziyuan/tarot/main/10abb0d1c3f7bf9dcbae406c91ef9645.jpeg" onerror="this.style.display='none'">
            <p style="color: #d4af37; margin-top: 20px; font-weight: bold;">✨ 能量加载中... ✨</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("🔮 AI 塔罗神殿：逻辑与智慧")

# 2. 核心牌库
MAJOR_ARCANA = {
    "愚者 (The Fool)": {"正位": "新的开始、纯粹、冒险", "逆位": "鲁莽、缺乏计划、停滞"},
    "魔术师 (The Magician)": {"正位": "创造力、掌控资源、行动", "逆位": "沟通不畅、能力错配"},
    "女祭司 (The High Priestess)": {"正位": "直觉、潜意识、等待", "逆位": "表象迷惑、忽视内心"},
    "女皇 (The Empress)": {"正位": "丰饶、生命力、感性", "逆位": "过度控制、缺乏安全感"},
    "皇帝 (The Emperor)": {"正位": "秩序、权威、理性", "逆位": "专制、死板、失控"},
    "教皇 (The Hierophant)": {"正位": "传统、导师、共识", "逆位": "打破常规、不信任"},
    "恋人 (The Lovers)": {"正位": "选择、和谐、吸引", "逆位": "价值观冲突、失衡"},
    "战车 (The Chariot)": {"正位": "意志胜利、自律、前进", "逆位": "方向模糊、攻击性、失控"},
    "力量 (Strength)": {"正位": "内在勇气、柔韧、自控", "逆位": "自我怀疑、软弱、急躁"},
    "隐士 (The Hermit)": {"get_deepseek_interpretation": "内省、真理、孤独", "逆位": "孤立、逃避现实"},
    "命运之轮 (Wheel of Fortune)": {"正位": "周期、契机、不可抗力", "逆位": "时机未到、抗拒变化"},
    "正义 (Justice)": {"正位": "公平、因果、真相", "逆位": "失衡、不负责、偏见"},
    "倒吊人 (The Hanged Man)": {"正位": "牺牲、换位思考、暂停", "逆位": "无谓挣扎、拖延"},
    "死神 (Death)": {"正位": "彻底终结、蜕变、新生", "逆位": "抗拒改变、勉强维持"},
    "节制 (Temperance)": {"正位": "平衡、融合、适度", "逆位": "失调、极端、冲突"},
    "恶魔 (The Devil)": {"正位": "束缚、物质欲望、执念", "逆位": "觉醒、解脱、意识到真相"},
    "高塔 (The Tower)": {"正位": "剧变、幻象破灭、冲击", "逆位": "延迟的崩溃、恐惧变化"},
    "星星 (The Star)": {"正位": "希望、疗愈、灵感", "逆位": "失望、迷茫、悲观"},
    "月亮 (The Moon)": {"正位": "不安、潜意识、幻觉", "逆位": "看清真相、恐惧消除"},
    "太阳 (The Sun)": {"正位": "明亮、成功、活力", "逆位": "暂时阴云、过度乐观"},
    "审判 (Judgement)": {"正位": "觉醒、反省、因果裁决", "逆位": "自我怀疑、逃避审视"},
    "世界 (The World)": {"正位": "圆满、整合、终点", "逆位": "未竟之志、停滞不前"}
}

# 3. 核心解读函数（客观深刻版）
def get_deepseek_interpretation(question, cards_list):
    st.write("---")
    st.subheader("💡 牌面深度解析")
    try:
        api_key = st.secrets["DEEPSEEK_API_KEY"]
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        
        cards_info = "\n".join([f"{c['pos']}：{c['name']}（{c['status']}）" for c in cards_list])
        
        # 强制性 Prompt：追求逻辑深度，屏蔽网络干扰
        system_msg = """你是一位严谨、深刻且客观的塔罗逻辑分析师。
        你的原则：
        1. 【绝对切断网络】：严禁根据现实中的人物名（如明星）、事件名去联网检索。你的所有判断必须源于牌阵本身。
        2. 【深度关联】：将牌面的经典意象与用户的问题进行本质上的链接。
        3. 【拒绝平庸】：不要给出“一切都会好起来”这种废话，要指出事物运行的底层逻辑。
        4. 【输出结构】：
           - 【牌阵逻辑分析】：解析三张牌之间的内在因果联系。
           - 【核心矛盾点】：指出当前问题最深刻的阻碍点。
           - 【策略性建议】：给出基于理性推导的应对方案。
        字数250字左右，语气稳重、透彻。"""
        
        user_msg = f"用户问题：【{question}】\n当前抽取的牌阵：\n{cards_info}\n请基于牌面逻辑，给出深刻且客观的闭环分析。"

        with st.spinner('正在分析牌面因果链...'):
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
                temperature=0.7 # 降低随机性，增加逻辑稳定性
            )
        st.markdown(response.choices[0].message.content)
    except Exception as e:
        st.error(f"解读连接失败。")

# 4. 交互逻辑
user_question = st.text_input("描述你的困惑：", placeholder="例如：某项具体计划的前景，或者当下的心态局势...")

if st.button("✨ 开启逻辑之门 ✨"):
    if not user_question:
        st.warning("请输入问题以开启解析。")
    else:
        with st.spinner('正在构建牌阵...'):
            time.sleep(1)
        
        drawn_names = random.sample(list(MAJOR_ARCANA.keys()), 3)
        spread_labels = ["【过去/根源】", "【现状/阻碍】", "【建议/指引】"]
        
        final_cards = []
        cols = st.columns(3)
        
        for i in range(3):
            with cols[i]:
                name = drawn_names[i]
                status = random.choice(["正位", "逆位"])
                meaning = MAJOR_ARCANA[name][status]
                
                final_cards.append({"pos": spread_labels[i], "name": name, "status": status})
                
                st.markdown(f"**{spread_labels[i]}**")
                st.markdown(f"### {name}")
                st.write(f"{'**正位** ⬆️' if status == '正位' else '**逆位** ⬇️'}")
                st.markdown(f"<p style='color:#d4af37; font-size:0.85em; font-style:italic;'>{meaning}</p>", unsafe_allow_html=True)
        
        get_deepseek_interpretation(user_question, final_cards)
        st.balloons()
