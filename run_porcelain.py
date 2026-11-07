import os
import json
import time
from pathlib import Path
from PIL import Image
from google import genai
from google.genai import types

# ==================== 1. 底层路径与环境变量配置 ====================
API_KEY = os.environ.get("GEMINI_API_KEY", "")

CURRENT_DIR = Path(__file__).parent
MEMORY_FILE = CURRENT_DIR / "memory_porcelain.json"
INPUT_DIR = CURRENT_DIR / "input" / "porcelain"

# 自动创建按类目归档的输出目录：output/porcelain/
CATEGORY_OUTPUT_DIR = CURRENT_DIR / "output" / "porcelain"
CATEGORY_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ==================== 2. 持续学习：长记忆加载与保存 ====================
def load_memory():
    """读取瓷器类目专属的长记忆库档案"""
    if MEMORY_FILE.exists():
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ [记忆读取提示] 读取记忆库异常: {e}")
            return []
    return []

def save_memory(product_name, summary):
    """把本次产品的核心美学叙事沉淀回瓷器长记忆库"""
    memories = load_memory()
    memories.append({
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "product_name": product_name,
        "category": "瓷器类",
        "summary": summary
    })
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memories, f, ensure_ascii=False, indent=4)
        print("🧠 [持续学习] 本次瓷器新品美学档案已沉淀入 memory_porcelain.json！")
    except Exception as e:
        print(f"⚠️ [记忆写入提示] 写入长记忆失败: {e}")

# ==================== 3. 瓷器 Agent 核心执行主程序 ====================
def run_porcelain_agent():
    print("=" * 65)
    print("🏺 执冶（ZHIYE）- 瓷器出海专家 Agent 启动（抗波动稳定版）...")
    print("=" * 65)

    if not API_KEY:
        print("❌ 错误：未检测到 GEMINI_API_KEY 环境变量！")
        print("👉 请先在 CMD 中运行：set GEMINI_API_KEY=你的密钥")
        print("=" * 65)
        return

    client = genai.Client(api_key=API_KEY)

    # 1. 加载历史美学记忆
    history = load_memory()
    print(f"🧠 [瓷器大脑] 已成功加载 {len(history)} 条同类历史产品美学档案。")

    # 2. 检查待处理图片
    input_img = INPUT_DIR / "test_item.jpg"
    if not input_img.exists():
        input_img = CURRENT_DIR / "test_item.jpg"

    if not input_img.exists():
        print(f"❌ 错误：未找到待处理测试图片！")
        print(f"👉 请在目录 {CURRENT_DIR} 下放入名为 test_item.jpg 的商品图片。")
        print("=" * 65)
        return

    # 本次处理的商品名称
    product_name = "金缮海捞青花古树纹品茗杯"
    print(f"📦 正在处理瓷器商品: 【{product_name}】...")

    # 自动归类到 output/porcelain/ 路径下
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_folder = CATEGORY_OUTPUT_DIR / f"porcelain_{timestamp}"
    output_folder.mkdir(exist_ok=True)

    # ------------------- 步骤 A：场景图处理 -------------------
    print("\n🎨 [视觉模块] 正在归档产品图片...")
    orig_img = Image.open(input_img)
    saved_img_path = output_folder / "product_image.png"

    try:
        # 保存原图/场景图
        orig_img.save(saved_img_path)
        print("✅ 已成功将原图规范归档为 product_image.png！")
    except Exception as e:
        print(f"⚠️ [图片保存提示] {e}")

    # ------------------- 步骤 B：构建带【历史记忆】的动态 Prompt -------------------
    print("\n✍️ [文案模块] 正在注入历史美学记忆，撰写欧美高端买手 B2B 英文文案...")
    img_for_text = Image.open(saved_img_path)

    memory_context = ""
    if history:
        memory_context = "\n--- HISTORICAL BRANDING MEMORIES (Learn from previous successful listings) ---\n"
        for idx, item in enumerate(history[-5:], 1):
            memory_context += f"Example {idx} [{item.get('product_name')}]: {item.get('summary')}\n"

    prompt = f"""
    You are an expert porcelain buyer and ceramics historian for luxury home galleries in Europe and North America, working for the Chinese artisanal export brand ZHIYE (执冶).
    Product Name: {product_name}
    Category: Fine Ceramics / Kiln-altered Porcelain / Kintsugi Restored

    {memory_context}

    CONTINUOUS LEARNING & BRAND VOICE INSTRUCTIONS:
    - Learn and inherit the refined, serene, and culturally authentic tone from the historical memories provided above.
    - Consistently incorporate core ZHIYE brand descriptors (e.g., Jingdezhen wood-fired kiln heritage, kaolin clay purity, tactile glaze depth, quiet luxury, Kintsugi philosophy, marine history).
    - Ensure a fresh narrative for this specific item without verbatim repeating sentences from past memory examples.

    Write a conversion-optimized English B2B product listing (with Chinese translation for reference) strictly formatted as:
    # [Title]
    ## Executive Summary / 一句话核心卖点 (EN/ZH)
    ## Artisan Story & Craftsmanship / 工艺与文化叙事 (EN/ZH)
    ## Key Features & Specifications / 核心规格与细节 (EN/ZH)
    ## High-Performance SEO Keywords / 欧美独立站高权重搜索标签 (10 keywords)
    """

    # ------------------- 智能多模型降级与重试机制 -------------------
    models_to_try = ['gemini-3.8-flash', 'gemini-1.5-flash']
    doc_content = None

    for model_name in models_to_try:
        print(f"🔄 尝试调用模型 [{model_name}]...")
        for attempt in range(2):  # 每个模型最多重试 2 次
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[img_for_text, prompt]
                )
                doc_content = response.text
                break
            except Exception as e:
                err_str = str(e)
                if "503" in err_str:
                    print(f"⚠️ 模型 [{model_name}] 遇到 503 高速波峰，等待 3 秒自动重试...")
                    time.sleep(3)
                else:
                    print(f"⚠️ 模型 [{model_name}] 返回提示: {err_str[:80]}...")
                    break
        if doc_content:
            break

    if doc_content:
        doc_path = output_folder / "description.md"
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(doc_content)

        print("✅ 瓷器 B2B 英文买手文案生成成功！")
        save_memory(product_name, doc_content[:200])

        print("\n" + "=" * 65)
        print(f"🎉 瓷器出海文案与图片处理完毕！已自动归档至瓷器类目目录：\n👉 {output_folder}")
        print("=" * 65)
    else:
        print("❌ [文案生成提示] 当前云端模型繁忙，请稍等 10 秒后重新敲 python run_porcelain.py 运行。")
        print("=" * 65)

if __name__ == "__main__":
    run_porcelain_agent()