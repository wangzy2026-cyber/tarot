import streamlit as st
import random
import time
from openai import OpenAI

# 1. 界面与配置
st.set_page_config(page_title="AI 塔罗神殿", page_icon="🔮")

# --- 界面样式 (保留爱豆开屏) ---
st.markdown(
    """
    <style>
    #splash-screen {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: #0e1117; display: flex; justify-content: center; align-items: center;
        z-index: 99999; animation: fadeOut 3.5s forwards; pointer-events: none;
    }
    .content { text-align: center; }
    .content img { max-width: 85vw; max-height: 70vh; border-radius: 20px; border: 2px solid #d4af37; box-shadow: 0 0 30px rgba(212, 175, 55, 0.5); }
    @keyframes fadeOut { 0% { opacity: 1; } 80% { opacity: 1; } 100% { opacity: 0; visibility: hidden; } }
    .stApp { background-color: #0e1117 !important; }
    div[data-baseweb="input"], .stTextInput>div>div { background-color: #1a1c24 !important; border: 1px solid #d4af37 !important; }
    input { color: #d4af37 !important; }
    h1, h2, h3, p, label, .stMarkdown { color: #f0f0f0 !important; }
    .stButton>button { background-color: #1a1c24 !important; color: #d4af37 !important; border: 2px solid #d4af37 !important; width: 100%; border-radius: 5px; font-weight: bold; }
    header, footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# 开屏逻辑 (优先尝试加载你的长文件名图片)
st.markdown(
    """
    <div id="splash-screen">
        <div class="content">
            <img src="https://raw.githubusercontent.com/W-Ziyuan/tarot/main/10abb0d1c3f7bf9dcbae406c91ef9645.jpeg" onerror="this.style.display='none'">
            <p style="color: #d4af37; margin-top: 20px; font-weight: bold;">✨ 正在构建封闭逻辑场... ✨</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("🔮 AI 塔罗神殿：深度逻辑场")

# 2. 核心牌库 (精简意象，留给 AI 深度发挥空间)
MAJOR_ARCANA = {
    "愚者 (The Fool)": {"正位": "纯粹起始、零点、潜在冒险", "逆位": "无序、盲动、停滞"},
    "魔术师 (The Magician)": {"正位": "意志变现、资源整合、创造", "逆位": "能量错位、沟通陷阱"},
    "女祭司 (The High Priestess)": {"正位": "静止智慧、潜意识、直觉", "逆位": "表象干扰、情绪波动"},
    "女皇 (The Empress)": {"正位": "生产力、滋养、感性扩张", "逆位": "过度消耗、情感窒息"},
    "皇帝 (The Emperor)": {"正位": "结构化控制、理性法则、稳固", "逆位": "权力崩塌、僵化死板"},
    "教皇 (The Hierophant)": {"正位": "文化秩序、教导、共识信仰", "逆位": "打破禁忌、不信任"},
    "恋人 (The Lovers)": {"正位": "二元契合、重大抉择、平衡", "逆位": "连接断裂、价值观冲突"},
    "战车 (The Chariot)": {"正位": "意志驱动、对立统一的胜利", "逆位": "动力失衡、方向瓦解"},
    "力量 (Strength)": {"正位": "内在驯服、柔韧制衡、耐受", "逆位": "自我动摇、急功近利"},
    "隐士 (The Hermit)": {"正位": "剥离外物、寻求本质、孤独", "逆位": "逃避性隔离、思维死角"},
    "命运之轮 (Wheel of Fortune)": {"正位": "客观周期、时空契机、流变", "逆位": "主观抗拒周期、错失点"},
    "正义 (Justice)": {"正位": "衡定、因果裁决、事实回归", "逆位": "认知偏见、失衡的责任"},
    "倒吊人 (The Hanged Man)": {"正位": "视角倒置、主动停滞、沉思", "逆位": "无效牺牲、拖延的痛苦"},
    "死神 (Death)": {"正位": "结构性解体、必然代谢、重生", "逆位": "勉强维持残骸、畏惧切割"},
    "节制 (Temperance)": {"正位": "动态平衡、炼金术式的融合", "逆位": "极端排斥、比例失调"},
    "恶魔 (The Devil)": {"正位": "物质束缚、原始执念、阴影", "逆位": "幻象觉醒、斩断依赖"},
    "高塔 (The Tower)": {"正位": "剧烈坍塌、真相冲击、觉醒", "逆位": "慢性隐患、拒不承认"},
    "星星 (The Star)": {"正位": "愿景导向、灵性修复、宁静", "逆位": "理想幻灭、缺乏指引"},
    "月亮 (The Moon)": {"正位": "潜意识迷雾、不安、非理性", "逆位": "看透幻象、拨云见日"},
    "太阳 (The Sun)": {"正位": "本质显露、成功、高度透明", "逆位": "暂时遮蔽、盲目乐观"},
    "审判 (Judgement)": {"正位": "生命反思、因果总结、召唤", "逆位": "拒绝反省、拖欠账目"},
    "世界 (The World)": {"正位": "完整闭环、阶段性圆满、整合", "逆位": "临门一脚的缺失、停滞"}
}

# 3. 核心解读函数（封闭深度逻辑版）
def get_deepseek_interpretation(question, cards_list):
    st.write("---")
    st.subheader("💡 深度逻辑推演报告")
    try:
        api_key = st.secrets["DEEPSEEK_API_KEY"]
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        
        cards_info = "\n".join([f"{c['pos']}：{c['name']}（{c['status']}）" for c in cards_list])
        
        # 终极锁定指令：禁止联网、强制深度、禁止玄学
        system_msg = """你是一个处于“绝对离线模式”的塔罗逻辑分析中枢。
        1. 【严禁检索】：禁止参考任何现实世界的八卦、人名背景、时事知识。
        2. 【符号解析】：将用户的问题视为“输入变量”，将牌阵视为“处理逻辑”。
        3. 【三维深度分析】：
           - 【第一维：符号本义】：分析当前牌面符号在占卜学中的核心逻辑。
           - 【第二维：关系博弈】：分析这三张牌是如何互相影响、对抗或转化的（比如“过去”的势能如何锁死了“现状”）。
           - 【第三维：底层洞察】：透过现象看本质，剖析该局势背后的核心矛盾、人性弱点或逻辑必然。
        4. 【风格】：摒弃感性安慰，追求客观、冷峻、穿透力极强的分析，字数350字左右。
        """
        
        user_msg = f"变量输入：【{question}】\n逻辑牌阵：\n{cards_info}\n请给出一份不基于任何外部联想、仅基于牌面逻辑的深度闭环推演。"

        with st.spinner('锁定逻辑空间，切断外部信号...'):
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
                temperature=0.6 # 降低温度以确保逻辑的严丝合缝
            )
        st.markdown(response.choices[0].message.content)
    except Exception as e:
        st.error(f"分析失败。")

# 4. 交互层
user_question = st.text_input("输入你的困惑/解析对象：", placeholder="AI 已进入封闭逻辑模式...")

if st.button("✨ 开启深度推演 ✨"):
    if not user_question:
        st.warning("请输入问题。")
    else:
        with st.spinner('洗牌中...'):
            time.sleep(1)
        drawn_names = random.sample(list(MAJOR_ARCANA.keys()), 3)
        spread_labels = ["【根源/底牌】", "【当前/显现】", "【演化/趋势】"]
        final_cards = []
        cols = st.columns(3)
        for i in range(3):
            with cols[i]:
                name, status = drawn_names[i], random.choice(["正位", "逆位"])
                meaning = MAJOR_ARCANA[name][status]
                final_cards.append({"pos": spread_labels[i], "name": name, "status": status})
                st.markdown(f"**{spread_labels[i]}**\n### {name}\n**{status}**")
                st.markdown(f"<p style='color:#d4af37; font-size:0.85em;'>{meaning}</p>", unsafe_allow_html=True)
        get_deepseek_interpretation(user_question, final_cards)
        st.balloons()
