import os
import json
import time
from pathlib import Path
from PIL import Image
from google import genai
from google.genai import types

# ----------------- 配置区域 -----------------
# 优先从系统环境变量读取 API Key，如果没有则使用默认值，确保上传 GitHub 时安全合规
API_KEY = API_KEY = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=API_KEY)

# 记忆文件路径
CURRENT_DIR = Path(__file__).parent
MEMORY_FILE = CURRENT_DIR / "memory.json"

def load_memory():
    """读取历史长记忆，保持品牌调性延续"""
    if MEMORY_FILE.exists():
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_memory(product_name, category, summary):
    """保存新记忆到本地"""
    memories = load_memory()
    new_memory = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "product_name": product_name,
        "category": category,
        "summary": summary
    }
    memories.append(new_memory)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memories, f, ensure_ascii=False, indent=4)

def run_global_cultural_agent():
    print("🌍 执冶（ZHIYE）欧美文创出海智能 Agent 启动...")
    
    # 1. 加载历史长记忆
    history_memories = load_memory()
    print(f"🧠 [长记忆] 已加载过往 {len(history_memories)} 条出海产品档案，维持欧美高端美学调性。")

    input_img_path = CURRENT_DIR / "test_item.jpg"
    if not input_img_path.exists():
        print(f"❌ 错误：在文件夹中找不到测试图片 test_item.jpg，请放入一张商品图！")
        return

    # 本次处理的商品信息（可随时修改）
    product_name = "手作大漆金缮茶盏"
    category = "大漆类"
    target_market = "Europe & North America High-end B2B/DTC Market"
    
    print(f"📦 正在处理出海商品: {product_name} (目标市场: 欧美高端市场)...")

    # 创建输出文件夹
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_folder = CURRENT_DIR / f"output_{timestamp}"
    output_folder.mkdir(exist_ok=True)

    # 2. 图像生成与优化
    print("🎨 [视觉模块] 正在让 Gemini 优化符合欧美极简美学的电商场景图...")
    original_image = Image.open(input_img_path)
    
    try:
        image_response = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=f"A professional high-end studio e-commerce photograph of {product_name}, category {category}, minimalist dark stone or natural wood background, soft warm museum lighting, wabi-sabi aesthetic, 8k resolution, premium design style suitable for Western luxury market.",
            config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio="1:1")
        )
        saved_img_path = output_folder / "product_image.png"
        for img in image_response.generated_images:
            img.image.save(saved_img_path)
        print("✅ 视觉场景图生成成功！")
    except Exception as e:
        print(f"⚠️ 启用原图备份模式: {e}")
        saved_img_path = output_folder / "product_image.png"
        original_image.save(saved_img_path)

    # 3. 跨文化本地化文案与翻译核心模块
    print("✍️ [跨文化翻译与文案模块] 正在生成符合欧美文化的本地化 B2B 英文叙事...")
    img_for_text = Image.open(saved_img_path)

    memory_context = f"历史产品风格参考：{json.dumps(history_memories[-2:], ensure_ascii=False)}" if history_memories else "这是系列首款产品。"

    # 专门为欧美文化和买手习惯定制的 Prompt
    cultural_prompt = f"""
    You are an elite cross-border e-commerce branding expert and copywriter specializing in bringing Asian heritage crafts to Western (European and North American) high-end markets.
    
    【Brand & Market Context】
    - Brand: ZHIYE (执冶)
    - Target Audience: Western interior designers, boutique curators, mindful living enthusiasts, and high-end B2B buyers.
    - Core Narrative: Do not just translate literally. Use cultural localization. Translate traditional elements (like lacquerware and kintsugi) into concepts of "mindful living", "sustainable luxury", "wabi-sabi imperfection", and "heirloom craftsmanship".
    {memory_context}

    【Product Details】
    - Product Name: {product_name}
    - Category: {category}

    Please analyze the product image and write a conversion-optimized English B2B product description (with Chinese translation reference for the founder), structured strictly as follows (Markdown format):

    # [Catchy, Western-Market-Ready Product Title]
    
    ## Executive Summary / 一句话核心卖点 (English & 中文)
    (Focus on emotional connection and aesthetic value for Western homes)

    ## Artisan Story & Craftsmanship / 工艺与文化叙事 (English & 中文)
    (Explain the heritage, natural materials, and the philosophy behind the craft in fluent, poetic yet commercial English)

    ## Key Features & Specifications / 核心规格与细节 (English & 中文)
    - Material / 材质:
    - Dimensions & Finish / 尺寸与质感:
    - Care Instructions / 保养建议 (Crucial for Western consumers):

    ## High-Performance SEO Keywords / 欧美独立站高权重搜索标签
    (Provide 10 high-converting English SEO keywords/tags separated by commas, targeting search habits on Google/Shopify)
    """

    text_response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=[img_for_text, cultural_prompt]
    )

    doc_content = text_response.text

    # 4. 保存文案与长记忆归档
    doc_path = output_folder / "description.md"
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(doc_content)
    
    save_memory(product_name, category, doc_content[:150])
    print("🧠 [长记忆] 欧美出海文案风格已成功沉淀至 memory.json！")

    print(f"\n🎉 欧美出海文案与图片全部搞定！结果已存入：\n👉 {output_folder}\n")

if __name__ == "__main__":
    run_global_cultural_agent()