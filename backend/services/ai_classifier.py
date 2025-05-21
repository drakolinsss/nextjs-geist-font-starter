from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from langchain.llms import HuggingFacePipeline
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import torch
import logging
from typing import Dict, List, Optional
import os
from ..config import AI_MODEL_PATH, AI_MODEL_CACHE_DIR

logger = logging.getLogger(__name__)

class AIClassifier:
    def __init__(self):
        self.initialize_models()
        self.setup_langchain()

    def initialize_models(self):
        """Initialize the classification model"""
        try:
            # Product category classifier
            self.category_classifier = pipeline(
                "text-classification",
                model=AI_MODEL_PATH,
                cache_dir=AI_MODEL_CACHE_DIR
            )

            # Content moderation classifier
            self.content_classifier = pipeline(
                "text-classification",
                model="facebook/roberta-hate-speech-dynabench-r4-target",
                cache_dir=AI_MODEL_CACHE_DIR
            )
        except Exception as e:
            logger.error(f"Error initializing AI models: {e}")
            # Fallback to simpler classification if needed
            self.category_classifier = None
            self.content_classifier = None

    def setup_langchain(self):
        """Setup LangChain for advanced content analysis"""
        try:
            # Initialize LangChain with our model
            model = HuggingFacePipeline(
                pipeline=pipeline(
                    "text-generation",
                    model="gpt2",
                    cache_dir=AI_MODEL_CACHE_DIR
                )
            )

            # Create content analysis prompt
            self.content_prompt = PromptTemplate(
                input_variables=["text"],
                template="Analyze this marketplace listing for potential issues:\n{text}\nPotential issues:"
            )

            # Create the chain
            self.content_chain = LLMChain(
                llm=model,
                prompt=self.content_prompt
            )
        except Exception as e:
            logger.error(f"Error setting up LangChain: {e}")
            self.content_chain = None

    def classify_product(self, description: str) -> Dict:
        """
        Classify product description into categories and check for potential issues
        """
        try:
            results = {
                "category": "unknown",
                "confidence": 0.0,
                "flags": [],
                "is_safe": True
            }

            # Perform category classification
            if self.category_classifier:
                category_result = self.category_classifier(description)
                if category_result:
                    results["category"] = category_result[0]["label"]
                    results["confidence"] = category_result[0]["score"]

            # Check content safety
            if self.content_classifier:
                safety_result = self.content_classifier(description)
                if safety_result:
                    results["is_safe"] = safety_result[0]["label"] == "LABEL_0"
                    if not results["is_safe"]:
                        results["flags"].append("potentially_unsafe_content")

            # Perform deeper content analysis with LangChain
            if self.content_chain:
                analysis = self.content_chain.run(description)
                if "suspicious" in analysis.lower() or "scam" in analysis.lower():
                    results["flags"].append("potential_fraud")

            return results
        except Exception as e:
            logger.error(f"Error in product classification: {e}")
            return {
                "category": "unknown",
                "confidence": 0.0,
                "flags": ["classification_error"],
                "is_safe": False
            }

    def detect_fraud(self, data: Dict) -> List[str]:
        """
        Analyze various data points for potential fraud
        """
        flags = []
        try:
            # Price analysis
            if data.get("price", 0) <= 0:
                flags.append("invalid_price")
            elif data.get("price", 0) > 10000:  # Arbitrary threshold
                flags.append("suspicious_price")

            # Description analysis
            description = data.get("description", "").lower()
            suspicious_terms = ["free money", "guaranteed profit", "100% success"]
            if any(term in description for term in suspicious_terms):
                flags.append("suspicious_description")

            # Additional checks can be added here

        except Exception as e:
            logger.error(f"Error in fraud detection: {e}")
            flags.append("fraud_check_error")

        return flags

# Create a global instance
classifier = AIClassifier()
