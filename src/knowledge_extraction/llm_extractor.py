import os
import json
from openai import OpenAI
from typing import Dict, Any

# --- IMPORTANT ---
# The user has provided a DeepSeek API key.
# We will use the OpenAI library to connect to the DeepSeek API,
# as they share a compatible API structure.
DEEPSEEK_API_KEY = "sk-af3e7e69cc3848669167549d79318d94"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

class LLMExtractor:
    def __init__(self, ontology_path: str, prompt_template_path: str):
        if not os.path.exists(ontology_path):
            raise FileNotFoundError(f"Ontology file not found at: {ontology_path}")
        if not os.path.exists(prompt_template_path):
            raise FileNotFoundError(f"Prompt template file not found at: {prompt_template_path}")

        with open(ontology_path, 'r', encoding='utf-8') as f:
            self.ontology = f.read()

        with open(prompt_template_path, 'r', encoding='utf-8') as f:
            self.prompt_template = f.read()

        # Initialize the client for the DeepSeek API
        self.client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

    def _create_prompt(self, text_chunk: str) -> str:
        """Fills the prompt template with the ontology and text chunk."""
        prompt = self.prompt_template.replace('{{ontology}}', self.ontology)
        prompt = prompt.replace('{{text_chunk}}', text_chunk)
        return prompt

    def _chunk_text(self, text: str, chunk_size: int = 2000, overlap: int = 200) -> list[str]:
        """Splits text into overlapping chunks."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap
        return chunks

    def extract(self, text: str, model: str = 'deepseek-chat') -> Dict[str, Any]:
        """
        Extracts knowledge from text using the DeepSeek API.

        Args:
            text: The text to extract knowledge from.
            model: The name of the DeepSeek model to use.

        Returns:
            A dictionary containing the extracted entities and relationships.
        """
        chunks = self._chunk_text(text)
        all_extractions = {"entities": [], "relationships": []}

        print(f"Processing text in {len(chunks)} chunks using DeepSeek API...")

        for i, chunk in enumerate(chunks):
            print(f"  - Processing chunk {i+1}/{len(chunks)}...")
            prompt = self._create_prompt(chunk)

            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{'role': 'user', 'content': prompt}],
                    response_format={"type": "json_object"} # Request JSON output
                )

                content_str = response.choices[0].message.content
                chunk_extraction = json.loads(content_str)

                if chunk_extraction.get("entities"):
                    all_extractions["entities"].extend(chunk_extraction["entities"])
                if chunk_extraction.get("relationships"):
                    all_extractions["relationships"].extend(chunk_extraction["relationships"])

            except json.JSONDecodeError:
                print(f"    - Warning: API returned invalid JSON for chunk {i+1}. Skipping.")
                continue
            except Exception as e:
                print(f"    - Error processing chunk {i+1}: {e}")
                continue

        return all_extractions

if __name__ == '__main__':
    ontology_file = 'config/ontology.yaml'
    prompt_file = 'config/extraction_prompt.txt'
    input_text_file = 'data/extracted_text_ocr.txt'

    if not os.path.exists(input_text_file):
        print(f"Error: Input text file not found at {input_text_file}")
    else:
        with open(input_text_file, 'r', encoding='utf-8') as f:
            full_text = f.read()

        extractor = LLMExtractor(ontology_path=ontology_file, prompt_template_path=prompt_file)

        print("Starting LLM extraction process with DeepSeek API...")
        extracted_data = extractor.extract(full_text)

        output_json_path = 'data/extracted_knowledge.json'
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=2)

        print(f"Extraction complete. Results saved to {output_json_path}")
        print(f"Extracted {len(extracted_data.get('entities', []))} entities and {len(extracted_data.get('relationships', []))} relationships.")
