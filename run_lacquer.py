import os
import json
import time
from pathlib import Path
from PIL import Image
from google import genai
from google.genai import types

API_KEY = os.environ.get(GEMINI_API_KEY, )
client = genai.Client(api_key=API_KEY)

CURRENT_DIR = Path(__file__).parent
MEMORY_FILE = CURRENT_DIR  memory_lacquer.json
INPUT_DIR = CURRENT_DIR  input  lacquer

def load_memory()
    if MEMORY_FILE.exists()
        try
            with open(MEMORY_FILE, r, encoding=utf-8) as f
                return json.load(f)
        except Exception
            return []
    return []

def save_memory(product_name, summary)
    memories = load_memory()
    memories.append({
        time time.strftime(%Y-%m-%d %H%M%S),
        product_name product_name,
        category 大漆金缮类,
        summary summary
    })
    with open(MEMORY_FILE, w, encoding=utf-8) as f
        json.dump(memories, f, ensure_ascii=False, indent=4)

def run_lacquer_agent()
    print(🌿 执冶（ZHIYE）- 大漆与金缮文化出海专家 Agent 启动...)
    history = load_memory()
    print(f🧠 [大漆记忆库] 已加载 {len(history)} 条同类历史产品美学档案)

    input_img = INPUT_DIR  test_item.jpg
    if not input_img.exists()
        input_img = CURRENT_DIR  test_item.jpg # 兼容根目录
    
    if not input_img.exists()
        print(❌ 错误：未找到测试图片，请在 inputlacquer 放入 test_item.jpg)
        return

    product_name = 手作大漆金缮茶盏
    print(f📦 处理商品 {product_name} (品类 大漆金缮类)...)

    timestamp = time.strftime(%Y%m%d_%H%M%S)
    output_folder = CURRENT_DIR  foutput_lacquer_{timestamp}
    output_folder.mkdir(exist_ok=True)

    print(🎨 正在生成符合 Wabi-sabi 与天然漆艺质感的场景图...)
    orig_img = Image.open(input_img)
    try
        image_response = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=fHigh-end minimalist e-commerce photograph of {product_name}, natural raw lacquer surface with subtle gold kintsugi joinery, dark warm slate stone background, museum spot lighting, zen and wabi-sabi aesthetic, 8k resolution.,
            config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio=11)
        )
        saved_img_path = output_folder  product_image.png
        for img in image_response.generated_images
            img.image.save(saved_img_path)
        print(✅ 大漆美学场景图生成成功！)
    except Exception as e
        print(f⚠️ 使用原图备份 {e})
        saved_img_path = output_folder  product_image.png
        orig_img.save(saved_img_path)

    print(✍️ 正在撰写大漆金缮专属的欧美买手跨文化叙事...)
    img_for_text = Image.open(saved_img_path)
    
    prompt = f
    You are an expert curator specializing in Oriental Lacquerware (Urushi) and Kintsugi art for high-end EuropeanNorth American interior design boutiques.
    Product {product_name}
    Category Lacquerware & Kintsugi Art
    
    Write a compelling B2B listing focusing on
    - Kintsugi philosophy (finding beauty in brokenness, sustainable heirloom).
    - Natural Urushi lacquer heritage, eco-friendly durability, and food-safe organic resin craftsmanship.
    
    Structure Title, Executive Summary (ENZH), Artisan Story (ENZH), Specs & Maintenance (ENZH), 10 SEO Tags.
    
    
    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=[img_for_text, prompt]
    )
    
    doc_path = output_folder  description.md
    with open(doc_path, w, encoding=utf-8) as f
        f.write(response.text)
    
    save_memory(product_name, response.text[150])
    print(f🎉 结果已归档至：{output_folder})

if __name__ == __main__
    run_lacquer_agent()