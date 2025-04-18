import os
import openai
import base64
import json

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
image_folder = "data"
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_caption(image_path):
    base64_image = encode_image(image_path)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    { "type": "text", "text": "Generate a 3-5 sentence caption for this image." },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=100
    )

    return response.choices[0].message.content

image_extensions = (".jpg", ".jpeg", ".png")

def main():
    captions = {}
    for filename in os.listdir(image_folder):
        if filename.lower().endswith(image_extensions):
            image_path = os.path.join(image_folder, filename)
            try:
                caption = generate_caption(image_path)
                captions[filename] = caption
                print(f"{filename}: {caption}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    output_path = "data/image_captions.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(captions, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()