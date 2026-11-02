import os
import json
import time
from pathlib import Path
from PIL import Image
from google import genai
from google.genai import types

API_KEY = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=API_KEY)

CURRENT_DIR = Path(__file__).parent
MEMORY_FILE = CURRENT_DIR / "memory_beads.json"
INPUT_DIR = CURRENT_DIR / "input" / "beads"

def load_memory():
    if MEMORY_FILE.exists():
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_memory(product_name, summary):
    memories = load_memory()
    memories.append({
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "product_name": product_name,
        "category": "珠串类",
        "summary": summary
    })
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memories, f, ensure_ascii=False, indent=4)

def run_beads_agent():
    print("📿 执冶（ZHIYE）- 禅意珠串与冥想文创出海专家 Agent 启动...")
    history = load_memory()
    print(f"🧠 [珠串记忆库] 已加载 {len(history)} 条同类产品档案")

    input_img = INPUT_DIR / "test_item.jpg"
    if not input_img.exists():
        input_img = CURRENT_DIR / "test_item.jpg"

    if not input_img.exists():
        print("❌ 错误：请在 input/beads/ 放入 test_item.jpg")
        return

    product_name = "小叶紫檀禅意手串"
    print(f"📦 处理商品: {product_name} (品类: 珠串类)...")

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_folder = CURRENT_DIR / f"output_beads_{timestamp}"
    output_folder.mkdir(exist_ok=True)

    print("🎨 正在生成符合冥想与自然材质风格的场景图...")
    orig_img = Image.open(input_img)
    try:
        image_response = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=f"Macro e-commerce studio photography of {product_name}, polished natural wooden beads, peaceful meditation atmosphere, incense smoke in background, warm soft lighting, high-end wellness jewelry style, 8k.",
            config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio="1:1")
        )
        saved_img_path = output_folder / "product_image.png"
        for img in image_response.generated_images:
            img.image.save(saved_img_path)
        print("✅ 珠串美学场景图生成成功！")
    except Exception as e:
        print(f"⚠️ 使用原图备份: {e}")
        saved_img_path = output_folder / "product_image.png"
        orig_img.save(saved_img_path)

    print("✍️ 正在撰写珠串与正念冥想专属英文文案...")
    img_for_text = Image.open(saved_img_path)
    
    prompt = f"""
    You are a luxury wellness & holistic jewelry branding consultant for Western buyers.
    Product: {product_name}
    Category: Mindful Prayer Beads & Artisan Wooden Jewelry
    
    Write a B2B product listing emphasizing:
    - Natural rare timber origin, tactile grounding sensation, mindfulness and meditation aesthetic.
    - Patina aging process (how hand contact enhances color over time), material authenticity.
    
    Structure: Title, Executive Summary (EN/ZH), Material Story (EN/ZH), Specs & Maintenance (EN/ZH), 10 SEO Tags.
    """
    
    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=[img_for_text, prompt]
    )
    
    doc_path = output_folder / "description.md"
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(response.text)
    
    save_memory(product_name, response.text[:150])
    print(f"🎉 结果已归档至：{output_folder}")

if __name__ == "__main__":
    run_beads_agent()