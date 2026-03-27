import streamlit as st
import random
import time
from openai import OpenAI

# 1. 界面与配置
st.set_page_config(page_title="AI 塔罗：洞见", page_icon="🔮")

# --- 界面样式 (保留你的爱豆开屏) ---
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

# 开屏图
st.markdown(
    """
    <div id="splash-screen">
        <div class="content">
            <img src="https://raw.githubusercontent.com/W-Ziyuan/tarot/main/10abb0d1c3f7bf9dcbae406c91ef9645.jpeg" onerror="this.style.display='none'">
            <p style="color: #d4af37; margin-top: 20px; font-weight: bold;">✨ 正在梳理局势脉络... ✨</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("🔮 AI 塔罗：深度洞见")

# 2. 核心牌库 (回归本质，不极端，讲道理)
MAJOR_ARCANA = {
    "愚者": {"正位": "轻装上阵，不带预设的开始", "逆位": "缺乏敬畏心，准备不足的盲动"},
    "魔术师": {"正位": "万事俱备，有极强的执行力", "逆位": "有心无力，资源没整合好"},
    "女祭司": {"正位": "沉得住气，静观其变，内在清明", "逆位": "心浮气躁，被干扰了判断"},
    "女皇": {"正位": "资源充沛，身心愉悦，正向产出", "逆位": "过度消耗，情绪化决策"},
    "皇帝": {"正位": "掌控局势，建立秩序，理智当头", "逆位": "控制欲过强，陷入僵化思维"},
    "教皇": {"正位": "遵循社会契约，寻求长辈或传统支持", "逆位": "被教条束缚，缺乏独立思考"},
    "恋人": {"正位": "高度默契，面临关键的价值观选择", "逆位": "沟通错位，利益与情感失衡"},
    "战车": {"正位": "靠自律和意志硬拿下的胜利", "逆位": "方向冲突，内耗严重，难以持久"},
    "力量": {"正位": "温柔的掌控，以柔克刚，情绪自洽", "逆位": "内心虚弱，容易被环境带跑"},
    "隐士": {"正位": "剥离杂音，寻找最核心的真相", "逆位": "自我封闭，陷入思维死胡同"},
    "命运之轮": {"正位": "顺势而为，抓住周期性的机会", "逆位": "逆势而行，时机尚未成熟"},
    "正义": {"正位": "因果公平，实事求是，冷静权衡", "逆位": "认知失真，逃避应尽的责任"},
    "倒吊人": {"正位": "牺牲局部换取全局，换位思考的智慧", "逆位": "无意义的苦劳，沉没成本太高"},
    "死神": {"正位": "旧结构的终结，为新局面腾出空间", "逆位": "藕断丝连，拒绝必要的代谢"},
    "节制": {"正位": "动态平衡，各方利益的完美调和", "逆位": "沟通脱节，走极端，失稳"},
    "恶魔": {"正位": "执念太深，被欲望或现状套牢", "逆位": "看破套路，开始尝试剥离"},
    "高塔": {"正位": "突发的冲击，摧毁不切实际的幻象", "逆位": "掩盖裂痕，延迟的危机"},
    "星星": {"正位": "长线的希望，精神上的疗愈和指引", "逆位": "预期落空，缺乏长远眼光"},
    "月亮": {"正位": "局势不明，存在潜伏的风险和不安", "逆位": "看清套路，不再自我怀疑"},
    "太阳": {"正位": "结果公开透明，充满活力和确定性", "逆位": "盲目乐观，忽略了背后的阴影"},
    "审判": {"正位": "阶段性的定论，因果显现，清醒觉醒", "逆位": "拒绝反省，在老坑里徘徊"},
    "世界": {"正位": "系统性闭环，顺利达成阶段性目标", "逆位": "临门一脚，缺乏最后的整合力"}
}

# 3. 核心解读函数（深度洞见版）
def get_deepseek_interpretation(question, cards_list):
    st.write("---")
    st.subheader("💡 洞见解析报告")
    try:
        api_key = st.secrets["DEEPSEEK_API_KEY"]
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        
        cards_info = "\n".join([f"{c['pos']}：{c['name']}（{c['status']}）" for c in cards_list])
        
        # 精密平衡指令：客观、深刻、有理有据
        system_msg = """你是一位洞察力极强、稳重且透彻的分析顾问。
        你的任务是：基于牌阵，为用户提供一份逻辑严密、不偏激、不虚幻的深度分析。
        
        原则：
        1. 【绝对切断网络】：严禁根据用户提到的人名（明星等）去联网联想。把这个名字视为一个纯粹的解析对象。
        2. 【讲道理】：结合牌义，分析这件事背后的社会学逻辑或人性能量关系。
        3. 【三段式拆解】：
           - 【局势底层逻辑】：分析起因牌决定了什么样的基调。
           - 【当前矛盾核心】：分析现状牌指出了什么样的博弈或阻碍。
           - 【必然演化路径】：基于前两者的推导，说明最后会走向什么样的必然结果。
        4. 【风格】：语气要稳，结论要深。不要废话，不要玄学，不要学术。字数 250-300 字。"""
        
        user_msg = f"解析对象：【{question}】\n逻辑牌阵：\n{cards_info}\n请基于牌面，给出一份看透本质的深度分析报告。"

        with st.spinner('剥离杂音，推演逻辑...'):
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
                temperature=0.65 
            )
        st.markdown(response.choices[0].message.content)
    except Exception as e:
        st.error(f"连接失败。")

# 4. 交互层
user_question = st.text_input("你想透视什么？", placeholder="输入人名或具体的困惑...")

if st.button("✨ 开启洞察 ✨"):
    if not user_question:
        st.warning("请输入解析对象。")
    else:
        with st.spinner('正在排布牌阵...'):
            time.sleep(1)
        drawn_names = random.sample(list(MAJOR_ARCANA.keys()), 3)
        spread_labels = ["【缘起】", "【当下】", "【趋向】"]
        final_cards = []
        cols = st.columns(3)
        for i in range(3):
            with cols[i]:
                name, status = drawn_names[i], random.choice(["正位", "逆位"])
                meaning = MAJOR_ARCANA[name][status]
                final_cards.append({"pos": spread_labels[i], "name": name, "status": status})
                st.markdown(f"**{spread_labels[i]}**\n### {name}\n**{status}**")
                st.markdown(f"<p style='color:#d4af37; font-size:0.9em; font-style:italic;'>{meaning}</p>", unsafe_allow_html=True)
        get_deepseek_interpretation(user_question, final_cards)
        st.balloons()
