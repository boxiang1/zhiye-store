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

# ==================== 2. 长记忆加载与保存函数 ====================
def load_memory():
    """加载瓷器类目专属的长记忆文件"""
    if MEMORY_FILE.exists():
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ [记忆读取提示] 读取记忆文件出现小异常: {e}")
            return []
    return []

def save_memory(product_name, summary):
    """保存本次瓷器新品的摘要到长记忆文件"""
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
        print("🧠 [长记忆] 已成功沉淀本次瓷器新品美学档案！")
    except Exception as e:
        print(f"⚠️ [记忆保存提示] 写入记忆文件失败: {e}")

# ==================== 3. 瓷器 Agent 核心执行主程序 ====================
def run_porcelain_agent():
    print("=" * 60)
    print("🏺 执冶（ZHIYE）- 瓷器艺术出海专家 Agent 启动...")
    print("=" * 60)

    # 校验 API Key
    if not API_KEY:
        print("❌ 错误：未检测到 GEMINI_API_KEY 环境变量！")
        print("👉 请先在命令行黑窗口中运行：set GEMINI_API_KEY=你的密钥")
        print("=" * 60)
        return

    # 初始化 Google Gemini 客户端
    client = genai.Client(api_key=API_KEY)

    # 读取同类历史记忆
    history = load_memory()
    print(f"🧠 [瓷器记忆库] 已加载 {len(history)} 条瓷器艺术历史档案。")

    # 优先查找 input/porcelain/test_item.jpg，其次查找根目录下的 test_item.jpg
    input_img = INPUT_DIR / "test_item.jpg"
    if not input_img.exists():
        input_img = CURRENT_DIR / "test_item.jpg"

    if not input_img.exists():
        print(f"❌ 错误：未找到测试图片！")
        print(f"👉 请在目录：{CURRENT_DIR} 下放入一张名为 test_item.jpg 的商品原图。")
        print("=" * 60)
        return

    # 本次处理的商品名称（可以随时修改引号里的中文）
    product_name = "手作柴烧青花瓷杯"
    print(f"📦 正在处理瓷器商品: 【{product_name}】...")

    # 创建带有时间戳的专属输出文件夹
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_folder = CURRENT_DIR / f"output_porcelain_{timestamp}"
    output_folder.mkdir(exist_ok=True)

    # ------------------- 步骤 A：生成极简高级感场景图 -------------------
    print("\n🎨 [视觉模块] 正在生成符合极简高级感与瓷器窑变润泽质感的场景图...")
    orig_img = Image.open(input_img)
    saved_img_path = output_folder / "product_image.png"

    try:
        image_response = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=f"Studio photograph of artisan hand-made ceramic product {product_name}, wood-fired glaze texture, placed on natural dark wood table, soft window sunlight, quiet luxury interior atmosphere, 8k resolution.",
            config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio="1:1")
        )
        for img in image_response.generated_images:
            img.image.save(saved_img_path)
        print("✅ 瓷器美学场景图生成成功！")
    except Exception as e:
        print(f"⚠️ [场景图生成提示] 调用生图 API 遇到波动，开启原图备份模式: {e}")
        orig_img.save(saved_img_path)
        print("✅ 已成功将原图备份归档为 product_image.png！")

    # ------------------- 步骤 B：撰写瓷器专属跨文化 B2B 文案 -------------------
    print("\n✍️ [文案与翻译模块] 正在撰写瓷器专属的欧美高端买手 B2B 英文文案...")
    img_for_text = Image.open(saved_img_path)

    prompt = f"""
    You are an expert porcelain buyer and ceramics historian for luxury home galleries in Europe and North America.
    Product: {product_name}
    Category: Fine Ceramics / Kiln-altered Porcelain

    Write a conversion-optimized English B2B product listing (with Chinese reference) strictly as follows:
    # [Title]
    ## Executive Summary / 一句话核心卖点 (EN/ZH)
    ## Artisan Story & Craftsmanship / 工艺与文化叙事 (EN/ZH)
    ## Key Features & Specifications / 核心规格与细节 (EN/ZH)
    ## High-Performance SEO Keywords / 欧美独立站高权重搜索标签 (10 keywords)
    """

    try:
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=[img_for_text, prompt]
        )
        doc_content = response.text
        doc_path = output_folder / "description.md"
        
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(doc_content)
        
        print("✅ 瓷器 B2B 英文买手文案生成成功！")
        
        # 归档长记忆
        save_memory(product_name, doc_content[:150])
        
        print("\n" + "=" * 60)
        print(f"🎉 瓷器出海文案与图片全部搞定！结果已存入文件夹：\n👉 {output_folder}")
        print("=" * 60)
    except Exception as e:
        print(f"❌ [文案生成错误] 生成文案失败，错误信息: {e}")
        print("=" * 60)

# ==================== 4. 主程序入口（保证脚本被调用时必定执行） ====================
if __name__ == "__main__":
    run_porcelain_agent()