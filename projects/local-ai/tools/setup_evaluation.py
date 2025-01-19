#!/usr/bin/env python3
"""
Setup script for model evaluation suite.
This tool helps evaluate and compare different models across various metrics.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict

def check_requirements():
    """Check if required packages are installed."""
    required = ['torch', 'evaluate', 'nltk', 'rouge-score', 'sacrebleu', 'python-dotenv', 'pandas']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Installing missing packages: {', '.join(missing)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)

def setup_env():
    """Setup environment configuration."""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("Creating .env file...")
        with open(env_path, "w") as f:
            f.write("""# Evaluation Settings
MODELS=["codellama", "llama2", "mistral"]
EVAL_DATA_PATH=./data/evaluation
RESULTS_PATH=./data/results
METRICS=["rouge", "bleu", "exact_match", "semantic_sim"]
BATCH_SIZE=4
NUM_SAMPLES=100
""")
        print("Created .env file with default settings")
    else:
        print(".env file already exists")

def setup_evaluation():
    """Setup the evaluation system files."""
    # Create necessary directories
    for dir_path in ["data/evaluation", "data/results", "scripts"]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Create evaluation script
    with open("scripts/evaluate_models.py", "w") as f:
        f.write("""#!/usr/bin/env python3
import json
import os
from pathlib import Path
from typing import List, Dict
import torch
import evaluate
import nltk
import pandas as pd
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class ModelEvaluator:
    def __init__(self):
        self.models = eval(os.getenv("MODELS"))
        self.metrics = eval(os.getenv("METRICS"))
        self.batch_size = int(os.getenv("BATCH_SIZE"))
        self.results_path = Path(os.getenv("RESULTS_PATH"))
        
        # Initialize metrics
        self.rouge = evaluate.load('rouge')
        self.bleu = evaluate.load('sacrebleu')
        nltk.download('punkt')
    
    def evaluate_model(self, model_name: str, test_data: List[Dict]) -> Dict:
        \"\"\"Evaluate a single model on test data.\"\"\"
        print(f"Evaluating {model_name}...")
        results = {metric: [] for metric in self.metrics}
        
        for batch_start in range(0, len(test_data), self.batch_size):
            batch = test_data[batch_start:batch_start + self.batch_size]
            
            # Get model predictions
            predictions = self._get_predictions(model_name, batch)
            
            # Calculate metrics
            for metric in self.metrics:
                if metric == "rouge":
                    scores = self.rouge.compute(
                        predictions=predictions,
                        references=[item["output"] for item in batch]
                    )
                    results[metric].extend([scores["rouge1"]] * len(batch))
                
                elif metric == "bleu":
                    scores = self.bleu.compute(
                        predictions=predictions,
                        references=[[item["output"]] for item in batch]
                    )
                    results[metric].extend([scores["score"]] * len(batch))
                
                elif metric == "exact_match":
                    for pred, ref in zip(predictions, [item["output"] for item in batch]):
                        results[metric].append(1.0 if pred.strip() == ref.strip() else 0.0)
                
                elif metric == "semantic_sim":
                    # Use model to calculate semantic similarity
                    for pred, ref in zip(predictions, [item["output"] for item in batch]):
                        similarity = self._calculate_semantic_similarity(pred, ref)
                        results[metric].append(similarity)
        
        # Average results
        return {metric: sum(scores)/len(scores) for metric, scores in results.items()}
    
    def _get_predictions(self, model_name: str, batch: List[Dict]) -> List[str]:
        \"\"\"Get model predictions for a batch of inputs.\"\"\"
        predictions = []
        
        for item in batch:
            # Format prompt
            prompt = f"### Instruction: {item['instruction']}\\n"
            if item.get('input'):
                prompt += f"### Input: {item['input']}\\n"
            prompt += "### Response:"
            
            # Query model
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt
                }
            )
            
            predictions.append(response.json()["response"])
        
        return predictions
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        \"\"\"Calculate semantic similarity between two texts.\"\"\"
        # Use model embeddings to calculate similarity
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            json={
                "model": "codellama",
                "prompt": text1
            }
        )
        emb1 = torch.tensor(response.json()["embedding"])
        
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            json={
                "model": "codellama",
                "prompt": text2
            }
        )
        emb2 = torch.tensor(response.json()["embedding"])
        
        return float(torch.nn.functional.cosine_similarity(emb1, emb2, dim=0))

def main():
    # Load test data
    eval_data_path = Path(os.getenv("EVAL_DATA_PATH"))
    test_data = []
    for json_file in eval_data_path.glob("*.json"):
        with open(json_file) as f:
            data = json.load(f)
            if isinstance(data, list):
                test_data.extend(data)
            else:
                test_data.append(data)
    
    # Limit samples if specified
    num_samples = int(os.getenv("NUM_SAMPLES"))
    if num_samples > 0:
        test_data = test_data[:num_samples]
    
    # Initialize evaluator
    evaluator = ModelEvaluator()
    
    # Evaluate each model
    results = {}
    for model in evaluator.models:
        results[model] = evaluator.evaluate_model(model, test_data)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = evaluator.results_path / f"eval_results_{timestamp}.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    # Generate report
    df = pd.DataFrame(results).round(4)
    print("\\nEvaluation Results:\\n")
    print(df)
    
    # Save report
    report_file = evaluator.results_path / f"eval_report_{timestamp}.md"
    with open(report_file, "w") as f:
        f.write("# Model Evaluation Report\\n\\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")
        f.write("## Results\\n\\n")
        f.write(df.to_markdown())
        f.write("\\n\\n## Metrics Description\\n\\n")
        f.write("- ROUGE: Measures overlap of n-grams between prediction and reference\\n")
        f.write("- BLEU: Measures translation quality between prediction and reference\\n")
        f.write("- Exact Match: Percentage of predictions that exactly match references\\n")
        f.write("- Semantic Similarity: Cosine similarity between prediction and reference embeddings\\n")

if __name__ == "__main__":
    main()
""")

    # Create example test data
    example_data = [
        {
            "instruction": "What is the capital of France?",
            "output": "The capital of France is Paris."
        },
        {
            "instruction": "Write a function to check if a number is prime.",
            "input": "n = 17",
            "output": "def is_prime(n):\\n    if n < 2:\\n        return False\\n    for i in range(2, int(n ** 0.5) + 1):\\n        if n % i == 0:\\n            return False\\n    return True"
        }
    ]
    
    with open("data/evaluation/example_test.json", "w") as f:
        json.dump(example_data, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Setup model evaluation suite")
    parser.add_argument("--models", nargs="+", default=["codellama", "llama2", "mistral"],
                      help="Models to evaluate (default: codellama llama2 mistral)")
    args = parser.parse_args()
    
    print("Setting up model evaluation suite...")
    
    # Check and install requirements
    check_requirements()
    
    # Setup environment
    setup_env()
    
    # Setup evaluation system
    setup_evaluation()
    
    print(f"""
Setup complete! To evaluate models:

1. Prepare your test data:
   - Add JSON files to data/evaluation/
   - Format: {{"instruction": "task", "input": "optional input", "output": "expected output"}}
   - See example_test.json for reference

2. Start the models you want to evaluate:
   {' && '.join(f'ollama run {model}' for model in args.models)}

3. Run evaluation:
   python scripts/evaluate_models.py

The system will:
- Load your test dataset
- Evaluate each model using multiple metrics:
  * ROUGE (text overlap)
  * BLEU (translation quality)
  * Exact Match
  * Semantic Similarity
- Generate detailed reports in data/results/

Tips:
- Adjust settings in .env file
- Use NUM_SAMPLES to limit test size
- Add custom metrics in evaluate_models.py
- Compare results across different model versions
""")

if __name__ == "__main__":
    main() 