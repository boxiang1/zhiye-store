import os
import json
import time
from pathlib import Path
from PIL import Image
from duckduckgo_search import DDGS
from google import genai
from google.genai import types

# ==================== 1. 初始化与配置 ====================
API_KEY = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=API_KEY)

CURRENT_DIR = Path(__file__).parent
MEMORY_FILE = CURRENT_DIR / "master_memory.json"
CHAT_LOG_FILE = CURRENT_DIR / "chat_history.log"
INPUT_DIR = CURRENT_DIR / "input"

# ==================== 2. 长记忆与对话日志模块 ====================
def load_memory():
    """读取本地沉淀的知识与历史案例"""
    if MEMORY_FILE.exists():
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"brand_style": "执冶 (ZHIYE) 极简禅意/匠人叙事", "insights": [], "products": []}
    return {"brand_style": "执冶 (ZHIYE) 极简禅意/匠人叙事", "insights": [], "products": []}

def save_memory(memory_data):
    """保存更新后的长记忆"""
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory_data, f, ensure_ascii=False, indent=4)

def log_chat(user_input, agent_response):
    """追加写入本地对话日志，确保每次沟通均可追溯"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(CHAT_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] USER: {user_input}\n")
        f.write(f"[{timestamp}] AGENT: {agent_response}\n")
        f.write("-" * 60 + "\n")

# ==================== 3. 实时搜索与市场分析工具 ====================
def web_search(query, max_results=5):
    """网络搜索工具：抓取欧美最新市场趋势或竞品信息"""
    print(f"🔍 [网络搜索] 正在检索关键词: '{query}'...")
    results_text = ""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            for idx, r in enumerate(results, 1):
                results_text += f"{idx}. {r['title']}: {r['body']}\n"
    except Exception as e:
        results_text = f"搜索遇到限制: {e}"
    return results_text

# ==================== 4. Agent 核心决策逻辑 ====================
def run_cultural_export_agent(user_prompt, category="瓷器", image_filename="test_item.jpg"):
    print("=" * 65)
    print("🚀 执冶 (ZHIYE) 智能出海 Master Agent 启动...")
    print("=" * 65)

    if not API_KEY:
        print("❌ 错误: 未找到 GEMINI_API_KEY 环境变量！")
        return

    # 1. 加载长记忆
    memory = load_memory()
    print(f"🧠 [长记忆] 已加载 {len(memory['products'])} 个历史案例及 {len(memory['insights'])} 条市场洞察。")

    # 2. 执行网络实时搜索（针对出海趋势与 SEO 关键词）
    search_query = f"luxury Chinese ceramic handcrafted design trend Europe US {category}"
    search_data = web_search(search_query)

    # 3. 提取图像与路径准备
    input_img_path = INPUT_DIR / category / image_filename
    if not input_img_path.exists():
        input_img_path = CURRENT_DIR / image_filename

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_folder = CURRENT_DIR / f"output_{category}_{timestamp}"
    output_folder.mkdir(exist_ok=True)

    # 4. 融合记忆 + 搜索结果 + 用户输入的全局 Prompt
    system_prompt = f"""
    You are the Chief Brand Officer & B2B Export Strategist for 'ZHIYE (执冶)', a luxury Chinese artisanal brand.
    
    [LONG-TERM BRAND MEMORY]
    - Brand Tone: {memory['brand_style']}
    - Historical Lessons Learned: {json.dumps(memory['insights'][-3:], ensure_ascii=False)}
    
    [REAL-TIME MARKET SEARCH INSIGHTS]
    {search_data}
    
    [USER REQUEST]
    Category: {category}
    User Instruction: {user_prompt}
    
    [TASK]
    Generate a comprehensive B2B Overseas Expansion Package:
    1. Market Positioning & Buyer Persona Analysis (Targeting EU/US gallery buyers)
    2. English B2B Product Listing (Title, Executive Summary, Craftsmanship Story, Specifications)
    3. High-Converting SEO Tag Cloud (10 keywords based on live market research)
    4. Continuous Learning Note: Key takeaways to update the brand's long-term memory.
    """

    # 5. 调用 Gemini 进行分析与文案生成
    print("✍️ [深度分析与创作] 结合长记忆与实时搜索数据中...")
    contents = [system_prompt]
    if input_img_path.exists():
        contents.append(Image.open(input_img_path))

    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=contents
    )
    output_text = response.text

    # 6. 保存生成结果
    doc_path = output_folder / "strategy_and_listing.md"
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(output_text)

    # 7. 记忆沉淀与日志持久化
    new_product_record = {
        "timestamp": timestamp,
        "category": category,
        "prompt": user_prompt,
        "output_path": str(doc_path)
    }
    memory["products"].append(new_product_record)
    # 自动提炼一条洞察入库
    memory["insights"].append(f"Used live trends for {category} on {timestamp}")
    save_memory(memory)
    
    log_chat(user_prompt, f"生成方案并保存至 {doc_path}")

    print("=" * 65)
    print(f"🎉 方案生成完毕！已成功保存至:\n👉 {doc_path}")
    print("🧠 [记忆沉淀] 沟通记录已同步写入 chat_history.log 与 master_memory.json")
    print("=" * 65)

if __name__ == "__main__":
    # 测试运行：只需修改这句话即可完成一次全流程调用
    run_cultural_export_agent(
        user_prompt="为最新手作柴烧青花瓷杯设计一套面向北美画廊买手的出海方案",
        category="porcelain",
        image_filename="test_item.jpg"
    )