from langchain.chains import RetrievalQA
from dotenv import load_dotenv
import os
from transformers import MarianMTModel, MarianTokenizer
import torch
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {device}")

load_dotenv("config.env")
google_api_key = os.getenv("GOOGLE_API_KEY")

try:
    model_name = "Helsinki-NLP/opus-mt-en-ar"
    logger.info(f"Loading tokenizer for {model_name}")
    tokenizer = MarianTokenizer.from_pretrained(model_name)

    logger.info(f"Loading model for {model_name}")
    translation_model = MarianMTModel.from_pretrained(model_name).to(device)
    logger.info("Model loaded successfully")

except Exception as e:
    logger.error(f"Model loading failed: {str(e)}")
    raise


def translate(text: str) -> str:
    """Translate English to Arabic"""
    try:
        if not text.strip():
            return ""

        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(
            translation_model.device)

        with torch.no_grad():
            outputs = translation_model.generate(**inputs)

        return tokenizer.decode(outputs[0], skip_special_token=True)
    except Exception as ex:
        logger.error(f"Translation Failed {str(ex)}")
        return f"Translation Error {str(ex)}"
