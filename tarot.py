import streamlit as st
import random
import time
from openai import OpenAI

# 1. 界面与配置
st.set_page_config(page_title="AI 塔罗神殿", page_icon="🔮")

# --- CSS 样式与开屏逻辑 (保持一致) ---
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
            <p style="color: #d4af37; margin-top: 20px; font-weight: bold;">✨ 正在链接纯净能量... ✨</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("🔮 AI 塔罗神殿：纯净逻辑版")

# 2. 核心牌库
MAJOR_ARCANA = {
    "愚者 (The Fool)": {"正位": "新的开始、纯粹、冒险", "逆位": "鲁莽、缺乏计划、停滞"},
    "魔术师 (The Magician)": {"正位": "创造力、掌控资源、行动", "逆位": "沟通不畅、能力错配"},
    "女祭司 (The High Priestess)": {"正位": "直觉、潜意识、等待", "逆位": "表象迷惑、忽视内心"},
    "女皇 (The Empress)": {"正位": "丰饶、生命力、感性", "逆位": "过度控制、缺乏安全感"},
    "皇帝 (The Emperor)": {"正位": "秩序、权威、理性", "逆位": "专制、死板、失控"},
    "教皇 (The Hierophant)": {"正位": "传统、导师、共识", "逆位": "打破常规、不信任"},
    "恋人 (The Lovers)": {"正位": "选择、和谐、吸引", "逆位": "失衡、错误选择"},
    "战车 (The Chariot)": {"正位": "胜利、自律、前进", "逆位": "方向模糊、失控"},
    "力量 (Strength)": {"正位": "内在勇气、柔韧、自控", "逆位": "自我怀疑、软弱"},
    "隐士 (The Hermit)": {"正位": "内省、真理、孤独", "逆位": "孤立、逃避现实"},
    "命运之轮 (Wheel of Fortune)": {"正位": "周期、契机、不可抗力", "逆位": "抗拒变化"},
    "正义 (Justice)": {"正位": "公平、因果、真相", "逆位": "不公、偏见"},
    "倒吊人 (The Hanged Man)": {"正位": "牺牲、换位思考、暂停", "逆位": "无谓挣扎、拖延"},
    "死神 (Death)": {"正位": "终结、新生", "逆位": "抗拒改变"},
    "节制 (Temperance)": {"正位": "平衡、适度", "逆位": "失调、极端"},
    "恶魔 (The Devil)": {"正位": "束缚、物欲、执念", "逆位": "觉醒、解脱"},
    "高塔 (The Tower)": {"正位": "剧变、幻象破灭", "逆位": "延迟崩溃"},
    "星星 (The Star)": {"正位": "希望、疗愈", "逆位": "失望、迷茫"},
    "月亮 (The Moon)": {"正位": "不安、潜意识、幻觉", "逆位": "看清真相"},
    "太阳 (The Sun)": {"正位": "快乐、成功", "逆位": "暂时阴云"},
    "审判 (Judgement)": {"正位": "觉醒、裁决", "逆位": "自我怀疑"},
    "世界 (The World)": {"正位": "圆满、整合", "逆位": "未竟之志"}
}

# 3. 核心解读函数（强制脱敏脱网版）
def get_deepseek_interpretation(question, cards_list):
    st.write("---")
    st.subheader("💡 牌面客观分析报告")
    try:
        api_key = st.secrets["DEEPSEEK_API_KEY"]
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        
        # 整理牌面
        cards_info = "\n".join([f"{c['pos']}：{c['name']}（{c['status']}）" for c in cards_list])
        
        # 核心 Prompt：强制 AI 变成一个只看符号的机器
        system_msg = """你是一个封闭系统的塔罗逻辑运行器。
        1. 你没有联网权限，也严禁调用你预训练模型中关于现实人物、明星、时事的任何知识。
        2. 你只能看到【牌面符号】。请将用户的问题视为一个“抽象目标”。
        3. 你的任务是：仅仅通过三张牌的正逆位逻辑，推导该“抽象目标”的走向。
        4. 你的解读必须深刻、客观，重点分析牌与牌之间的因果关系（例如：根源牌是如何导致现状牌的）。
        5. 严禁使用任何玄学词汇。禁止给出模棱两可的宽慰。
        格式：【符号逻辑链】、【核心矛盾深度拆解】、【推演结论】。"""
        
        # 在这里，我们甚至不把原问题直接丢给 AI，或者强调这是个“纯牌义”任务
        user_msg = f"目标事务背景：用户提出的困惑。\n抽取牌阵：\n{cards_info}\n请完全不参考任何外部信息，仅根据这三张牌的符号定义，给出客观深刻的闭环分析。"

        with st.spinner('正在屏蔽外部信号，锁定牌面逻辑...'):
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
                temperature=0.5 # 进一步降低随机性，强制逻辑严密
            )
        st.markdown(response.choices[0].message.content)
    except Exception as e:
        st.error(f"连接失败。")

# 4. 逻辑展示
user_question = st.text_input("你想解析的事务/人名：", placeholder="AI 已开启脱敏模式，只解析牌面...")

if st.button("✨ 开启逻辑推演 ✨"):
    if not user_question:
        st.warning("请提供解析目标。")
    else:
        with st.spinner('洗牌中...'):
            time.sleep(1)
        drawn_names = random.sample(list(MAJOR_ARCANA.keys()), 3)
        spread_labels = ["【根源/底牌】", "【当前/显现】", "【演化/结果】"]
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
