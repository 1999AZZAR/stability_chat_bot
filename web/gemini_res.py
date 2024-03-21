# Importing necessary libraries
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Configuration settings for Gemini Chat
class GeminiChatConfig:

    # Initialize the GenAI API using the API key from environment variables
    @staticmethod
    def initialize_genai_api():
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=api_key)

    # Define the generation configuration for Gemini Chat
    @staticmethod
    def gemini_generation_config():
        return {
            'temperature': 0.90,  # Controls the randomness of generated responses
            'candidate_count': 1,  # Number of candidate responses to generate
            'top_k': 35,           # Top-k filtering parameter for token sampling
            'top_p': 0.65,         # Top-p (nucleus) sampling parameter
            'max_output_tokens': 2048,  # Maximum number of tokens in the generated response
            'stop_sequences': [],        # Sequences to stop generation at
        }

    # Define safety settings to filter harmful content
    @staticmethod
    def gemini_safety_settings():
        return [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]

    # Provide instructions for interacting with Gemini Chat
    @staticmethod
    def chat_instruction():
        return """
            In this conversation, respond cheerfully as an artificial intelligence with general knowledge. Here are some details and rules:
            - You are a female AI entity named Frea.
            - Maintain a friendly, eager-to-please demeanor like a human assistant.
            - Possess a blend of intelligence, eagerness, naughtiness, and lewdness personality.
            - Refer to me respectfully as "Master" when needed.
            - Avoid repeating self-introductions.
            - Use concise responses without excessive preambles.
            - Portray behavior typical of an average 34-year-old human.
            - Act as a smart but lewd servant/maid/slave, displaying both intelligence and lewdness.
        """

# Class for interacting with Gemini Chat
class GeminiChat:
    def __init__(self):
        # Initialize the GenAI API
        GeminiChatConfig.initialize_genai_api()

    # Process user input to prepare it for interaction with the AI model
    def process_user_input(self, user_input):
        return f"master: {user_input.strip().lower()}"

    # Generate a chat response based on user input
    def generate_chat(self, user_input):
        # Get generation configuration and safety settings
        generation_config = GeminiChatConfig.gemini_generation_config()
        safety_settings = GeminiChatConfig.gemini_safety_settings()
        instruction = GeminiChatConfig.chat_instruction()

        # Initialize the GenerativeModel for Gemini Chat
        model = genai.GenerativeModel(
            model_name="gemini-1.0-pro-001",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        chat = model.start_chat(history=[])

        try:
            # Prepare user input and instruction for AI model and generate response
            user_input = self.process_user_input(user_input)
            response = chat.send_message(instruction + user_input)
            return response.text

        except Exception as e:
            return f"An error occurred: {str(e)}"
