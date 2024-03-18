import os
import base64
import requests
from PIL import Image, ImageEnhance
from dotenv import load_dotenv

load_dotenv()

# ...
class Image_gen:

    # ...
    def add_watermark(self, input_image_path, output_image_path, watermark_image_path, transparency=25):
        if watermark_image_path is None or not os.path.exists(watermark_image_path):
            original_image = Image.open(input_image_path)
            original_image.save(output_image_path)
            return

        # ...
        try:
            original_image = Image.open(input_image_path)
            watermark = Image.open(watermark_image_path)
            min_dimension = min(original_image.width, original_image.height)
            watermark_size = (int(min_dimension * 0.14), int(min_dimension * 0.14))
            watermark = watermark.resize(watermark_size)
            if watermark.mode != 'RGBA':
                watermark = watermark.convert('RGBA')
            image_with_watermark = original_image.copy()
            position = (0, original_image.size[1] - watermark.size[1])
            image_with_watermark.paste(watermark, position, watermark)
            alpha = watermark.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(transparency / 100.0)
            watermark.putalpha(alpha)
            image_with_watermark.save(output_image_path)
        # ...
        except Exception as e:
            print(f"Error adding watermark: {e}")
            original_image.save(output_image_path)

    # Method to generate an image based on a prompt using an AI model
    def generate_image(self, prompt):
        api_key = os.getenv('STABILITY_API_KEY')
        common_params = {
            "samples": 1,
            "steps": 50,
            "cfg_scale": 15.5,
            "clip_guidance_preset": "FAST_GREEN",
            "height": 1024,
            "width": 1024,
            "text_prompts": [
                {
                    "text"  : prompt, 
                    "weight": 1
                },
                {
                    "text": "The artwork showcases excellent anatomical accuracy, portraying a clear, complete, and aesthetically pleasing depiction. It meticulously renders well-proportioned and meticulously polished details, resulting in a unique and harmoniously balanced composition. The high-resolution image is devoid of any damage and flawlessly crafted, conveying a vibrant and lifelike appearance, free from any abnormalities or imperfections. The mastery of the artist is evident in the skillful framing and lifelike portrayal of features, including finely drawn facial expressions and hands. The absence of signatures enhances its seamless and authentic quality, while the precise depiction of straight fingers further enhances its overall allure.",
                    "weight": 0.4
                },
                {
                    "text": "The artwork features two faces and two heads, exhibiting poor anatomical accuracy and a blurry, cloned appearance. It suffers from a cropped image, resulting in cut-off and deformed limbs, including disconnected limbs and disturbingly disfigured hands. The presence of duplicated artifacts and extra fingers or limbs detracts from its visual appeal. Additionally, floating limbs and irregular proportions contribute to its unappealing appearance. The artwork is marred by low resolution, mangled details, and mutated or mutilated features, such as twisted fingers and malformed hands. The inclusion of multiple heads and the absence of proper framing and signatures further diminish its quality, giving it a surreal and unsettling quality.",
                    "weight": -1
                }
            ],
        }

        # ...
        try:
            response = requests.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                json=common_params,
            )

            # ...
            if response.status_code != 200:
                raise Exception("Non-200 response: " + str(response.text))
            data = response.json()            
            artifacts = data.get("artifacts", [])
            if not artifacts:
                raise Exception("No artifacts returned by the API")   

            # ...
            output_directory = "./web/static/image"
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
            file_name = f'{data["artifacts"][0]["seed"]}.png'
            generated_image_path = f'{output_directory}/{file_name}'
            with open(generated_image_path, "wb") as f:
                f.write(base64.b64decode(data["artifacts"][0]["base64"]))

            # Method to generate an image based on a prompt using an AI model
            watermark_image_path = './web/static/logo.png' 
            output_with_watermark_path = generated_image_path
            self.add_watermark(generated_image_path, output_with_watermark_path, watermark_image_path, transparency=25)
            return file_name
        # ...
        except Exception as e:
            print(f"Error in generate_image: {e}")
            return None

image_gen = Image_gen()
