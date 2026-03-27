import streamlit as st
import random
import time
from openai import OpenAI

# 1. 界面与配置
st.set_page_config(page_title="AI 塔罗神殿", page_icon="🔮")
# --- 注入 CSS 样式开始 ---
st.markdown(
    """
    <style>
    /* 1. 整个背景变深紫色 */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* 2. 所有文字颜色变成淡紫色/白色 */
    h1, h2, h3, p, span, div {
        color: #e0e0e0 !important;
    }

    /* 3. 修改输入框和卡片样式 */
    .stTextInput>div>div>input {
        background-color: #0f3460;
        color: white;
        border: 1px solid #d69dfb;
    }

    /* 4. 修改那个闪亮的抽牌按钮 */
    .stButton>button {
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 25px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 15px #6a11cb;
    }

    /* 5. 让抽出的牌更像卡片 */
    .stInfo {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid #d69dfb;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# --- 注入 CSS 样式结束 ---
st.title("🔮 AI 塔罗神殿：智慧之眼")
st.markdown("""
<div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px;'>
    <strong>仪式指南：</strong><br>
    1. 在下方写下你心中的疑惑，越具体越好。<br>
    2. 点击抽牌，AI 占卜师将为你进行深度解读。<br>
    <em>(基于 DeepSeek 大模型提供解读)</em>
</div>
""", unsafe_allow_html=True)
st.write("")

# 2. 核心牌库 (保持不变，省略部分以节省空间，记得用你之前的完整字典替换这里)
MAJOR_ARCANA = {
    "愚者 (The Fool)": {"正位": "新的开始、自发性、信念的飞跃", "逆位": "鲁莽、停滞、糟糕的决定"},
    "魔术师 (The Magician)": {"正位": "显化、资源充足、力量", "逆位": "操控、规划不周、未开发的潜力"},
    "女祭司 (The High Priestess)": {"正位": "直觉、潜意识、神秘", "逆位": "直觉被封锁、秘密、肤浅"},
    "命运之轮 (Wheel of Fortune)": {"正位": "转折、业力、生命的循环", "逆位": "运气不好、抗拒改变、打破循环"},
    "世界 (The World)": {"正位": "完成、整合、圆满", "逆位": "缺乏完成、不完整的循环、未实现的潜能"}
    # ... 请确保这里把你之前那 22 张牌的字典完整粘贴过来 ...
}

# 3. 连接 DeepSeek 大脑 (从云端读取密钥)
def get_deepseek_interpretation(question, drawn_cards_info):
    st.write("---")
    st.subheader("💡 DeepSeek 占卜师的深度指引")
    
    # 尝试从 Streamlit 的云端秘密环境变量中获取 API Key
    try:
        api_key = st.secrets["DEEPSEEK_API_KEY"]
    except Exception:
        st.error("⚠️ 占卜师失联：系统未配置 API Key。请联系开发者在云端后台设置 Secrets。")
        return

    cards_text = ""
    for card in drawn_cards_info:
        cards_text += f"- {card['pos']}：{card['name']} ({card['orientation']})，核心释义：{card['keywords']}\n"
    
    system_prompt = """
    你是一位富有洞察力、富有同理心的专业塔罗占卜师。
    请根据用户的问题和抽到的三张牌（包含正逆位），进行深度且充满启发的解读。
    你的语言风格应该是优雅、神秘且具有疗愈感的。
    请分析牌阵中的能量流动，并为用户提供切实可行的生活建议。
    解读字数在 500 字左右，排版请清晰美观。
    """
    
    user_prompt = f"我的问题是：【{question}】\n我抽到的牌阵如下：\n{cards_text}\n请为我进行深度解读。"

    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        with st.spinner('DeepSeek 正在解析星象与数据洪流...'):
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7 
            )
        st.markdown(response.choices[0].message.content)
    except Exception as e:
        st.error(f"沟通宇宙接口时出现干扰：{e}")

# 4. 交互逻辑
user_question = st.text_input("你想问什么问题？（例：我的毕业论文进展会顺利吗？）")

if st.button("✨ 确认问题，点击抽牌 ✨"):
    if user_question == "":
        st.warning("牌阵需要感应你的具体问题，请先输入问题哦！")
    else:
        with st.spinner('正在洗牌，连结宇宙能量...'):
            time.sleep(1.5) 
            
        st.success(f"关于【{user_question}】，这是属于你的三张牌：")
        st.write("")
        
        spread_info = ["【过去 / 基础】", "【现在 / 挑战】", "【未来 / 指引】"]
        drawn_cards_data = []
        drawn_card_names = random.sample(list(MAJOR_ARCANA.keys()), 3)
        
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]
        
        for i, col in enumerate(cols):
            with col:
                card_name = drawn_card_names[i]
                orientation = random.choice(["正位", "逆位"])
                keywords = MAJOR_ARCANA[card_name][orientation]
                
                drawn_cards_data.append({
                    "pos": spread_info[i],
                    "name": card_name,
                    "orientation": orientation,
                    "keywords": keywords
                })
                
                orient_text = f"**{orientation}** ⬆️" if orientation == "正位" else f"**{orientation}** ⬇️"
                
                st.subheader(f"{spread_info[i]}")
                st.markdown(f"**{card_name}**")
                st.markdown(f"状态：{orient_text}")
                st.info(f"💡 关键词：{keywords}")
                time.sleep(0.3)
                
        # 调用 AI 分析
        get_deepseek_interpretation(user_question, drawn_cards_data)
        
        st.balloons() 
        st.write("---")
        st.write("✨ 愿星辰指引你的方向 ✨")
