import os
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify
from response import GeminiChat
from iresponse import ImageGenerator
import sqlite3

# global initialization
app = Flask(__name__)
chat_app = GeminiChat() 
image_generator = ImageGenerator() 
IMAGE_LOG = './web/datalog/image_log.db'

# Initialize database connection
conn = sqlite3.connect(IMAGE_LOG)
c = conn.cursor()

# Create table to store image log
c.execute('''
        CREATE TABLE IF NOT EXISTS images(
        filename TEXT,
        creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    ''')
conn.commit()
conn.close()

# index
@app.route('/')
def index():
    return render_template('index.html')

# Function to delete old images from database and filesystem
def delete_old_images():
    conn = sqlite3.connect(IMAGE_LOG)
    c = conn.cursor()
    image_dir = "./web/static/image"
    if os.path.exists(image_dir):
        # Get the current time
        now = time.time()
        # Calculate the time threshold (30 minutes ago)
        threshold = now - 1800
        # Iterate through the images in the database
        for row in c.execute("SELECT filename, creation_time FROM images"):
            filename, creation_time = row
            creation_time = time.mktime(time.strptime(creation_time, "%Y-%m-%d %H:%M:%S"))
            file_path = os.path.join(image_dir, filename)
            if os.path.isfile(file_path):
                # Check if the creation time is older than the threshold
                if creation_time < threshold:
                    # Delete the image file
                    os.remove(file_path)
                    # Remove the entry from the database
                    c.execute("DELETE FROM images WHERE filename=?", (filename,))
                    conn.commit()
    conn.close()

# Route to handle user input
@app.route('/user_input', methods=['POST'])
def handle_user_input():
    honeypot_value = request.form.get('honeypot', '')
    if honeypot_value:
        return 'Bot activity detected. Access denied.'

    user_input = request.get_json().get('user_input', '').lower()
    if user_input.startswith('imagine'):
        prompt = user_input[len('imagine'):].strip()
        prompt_text = prompt if prompt else 'Your prompt here'
        image_path = image_generator.generate_image(prompt_text)
        if image_path:
            # Delete old images before returning response
            delete_old_images()
            # Insert metadata into database with current timestamp
            conn = sqlite3.connect(IMAGE_LOG)
            c = conn.cursor()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO images (filename, creation_time) VALUES (?, ?)", (image_path, current_time))
            conn.commit()
            conn.close()
            return jsonify({'image_path': image_path})
        else:
            return jsonify({'bot_response': 'Error generating image'})
    else:
        response = chat_app.generate_chat(user_input)
        return jsonify({'bot_response': response})


# Main function to run the app
if __name__ == '__main__':
    app.run(debug=True, port=2500)
