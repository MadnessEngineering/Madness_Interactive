#!/usr/bin/env python3.11
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
from common import setup_env  # Import the common setup_env function

def check_requirements():
    """Check if required packages are installed."""
    required = [
        'torch', 'evaluate', 'nltk', 'rouge-score', 'sacrebleu', 
        'python-dotenv', 'pandas', 'bert_score', 'checklist',
        'textattack', 'fairness-indicators', 'memory_profiler',
        'psutil', 'perspective-api', 'codebleu', 'py-spy',
        'factcheck', 'deepeval', 'promptfoo', 'triton',
        'scipy', 'scikit-learn', 'cleanlab', 'dataprofiler'
    ]
    missing = []

    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"Installing missing packages: {', '.join(missing)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)

def setup_env_evaluation():
    """Setup environment for evaluation."""
    env_string = """# Evaluation Settings
MODELS=["codellama", "llama2", "mistral"]
EVAL_DATA_PATH=./data/evaluation
RESULTS_PATH=./data/results
METRICS=[
    "rouge", "bleu", "exact_match", "semantic_sim",
    "bertscore", "behavioral", "adversarial",
    "latency", "memory", "fairness", "codebleu",
    "hallucination", "prompt_injection", "performance",
    "gpu_efficiency", "token_efficiency"
]
DATASET_METRICS=[
    "representation", "balance", "quality",
    "diversity", "statistical_validity"
]
BATCH_SIZE=4
NUM_SAMPLES=100
PERSPECTIVE_API_KEY=""  # Add your API key here
"""
    setup_env(env_string)

def setup_evaluation():
    """Setup the evaluation system files."""
    # Create necessary directories
    for dir_path in ["data/evaluation", "data/results", "scripts"]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    # Create evaluation script
    with open("scripts/evaluate_models.py", "w") as f:
        f.write("""#!/usr/bin/env python3.11
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

class DatasetEvaluator:
    """Evaluates dataset quality and characteristics."""
    
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.metrics = eval(os.getenv("DATASET_METRICS"))
        self.profiler = dataprofiler.Profiler()
        self.cleanlab = cleanlab.DataQuality()
        
    def evaluate_dataset(self, dataset: List[Dict]) -> Dict[str, float]:
        """Evaluate dataset quality across multiple dimensions."""
        results = {}
        
        # Domain representation analysis
        results["representation"] = self._analyze_representation(dataset)
        
        # Dataset balance metrics
        results["balance"] = self._analyze_balance(dataset)
        
        # Data quality assessment
        results["quality"] = self._analyze_quality(dataset)
        
        # Diversity metrics
        results["diversity"] = self._analyze_diversity(dataset)
        
        # Statistical validity
        results["statistical_validity"] = self._analyze_statistical_validity(dataset)
        
        return results
    
    def _analyze_representation(self, dataset: List[Dict]) -> float:
        """Analyze how well the dataset represents the domain."""
        try:
            # Profile dataset characteristics
            profile = self.profiler.analyze(dataset)
            
            metrics = {
                'coverage': self._calculate_domain_coverage(profile),
                'completeness': profile.get('completeness', 0),
                'consistency': profile.get('consistency', 0)
            }
            
            return sum(metrics.values()) / len(metrics)
        except Exception as e:
            print(f"Representation analysis error: {e}")
            return 0.0
    
    def _analyze_balance(self, dataset: List[Dict]) -> float:
        """Analyze dataset balance and bias."""
        try:
            # Extract features and analyze distributions
            instructions = [d['instruction'] for d in dataset]
            outputs = [d['output'] for d in dataset]
            
            metrics = {
                'length_distribution': self._analyze_length_distribution(instructions, outputs),
                'topic_distribution': self._analyze_topic_distribution(instructions),
                'complexity_distribution': self._analyze_complexity_distribution(dataset)
            }
            
            return sum(metrics.values()) / len(metrics)
        except Exception as e:
            print(f"Balance analysis error: {e}")
            return 0.0
    
    def _analyze_quality(self, dataset: List[Dict]) -> float:
        """Analyze data quality using cleanlab."""
        try:
            # Check for label quality issues
            quality_report = self.cleanlab.compute_quality_scores(dataset)
            
            metrics = {
                'label_quality': quality_report.get('label_quality', 0),
                'noise_score': 1 - quality_report.get('noise_score', 1),
                'consistency_score': quality_report.get('consistency_score', 0)
            }
            
            return sum(metrics.values()) / len(metrics)
        except Exception as e:
            print(f"Quality analysis error: {e}")
            return 0.0
    
    def _analyze_diversity(self, dataset: List[Dict]) -> float:
        """Analyze dataset diversity."""
        try:
            # Calculate various diversity metrics
            metrics = {
                'vocabulary_diversity': self._calculate_vocabulary_diversity(dataset),
                'structural_diversity': self._calculate_structural_diversity(dataset),
                'semantic_diversity': self._calculate_semantic_diversity(dataset)
            }
            
            return sum(metrics.values()) / len(metrics)
        except Exception as e:
            print(f"Diversity analysis error: {e}")
            return 0.0
    
    def _analyze_statistical_validity(self, dataset: List[Dict]) -> float:
        """Analyze statistical validity of the dataset."""
        try:
            from scipy import stats
            
            # Perform statistical tests
            metrics = {
                'sample_size': self._assess_sample_size(len(dataset)),
                'distribution_normality': self._test_distribution_normality(dataset),
                'variance_homogeneity': self._test_variance_homogeneity(dataset)
            }
            
            return sum(metrics.values()) / len(metrics)
        except Exception as e:
            print(f"Statistical validity analysis error: {e}")
            return 0.0
    
    def _calculate_domain_coverage(self, profile: Dict) -> float:
        """Calculate how well the dataset covers the intended domain."""
        # Analyze feature completeness and distribution
        features_present = len(profile.get('features', []))
        expected_features = profile.get('expected_features', features_present)
        
        coverage_ratio = features_present / max(expected_features, 1)
        distribution_score = profile.get('distribution_score', 0.5)
        
        return (coverage_ratio + distribution_score) / 2
    
    def _analyze_length_distribution(self, instructions: List[str], outputs: List[str]) -> float:
        """Analyze the distribution of lengths in the dataset."""
        from scipy import stats
        
        # Calculate length distributions
        instruction_lengths = [len(i.split()) for i in instructions]
        output_lengths = [len(o.split()) for o in outputs]
        
        # Test for uniformity of distribution
        _, p_value_i = stats.kstest(instruction_lengths, 'uniform')
        _, p_value_o = stats.kstest(output_lengths, 'uniform')
        
        return (p_value_i + p_value_o) / 2
    
    def _analyze_topic_distribution(self, texts: List[str]) -> float:
        """Analyze the distribution of topics in the dataset."""
        try:
            # Use basic topic modeling
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.decomposition import NMF
            
            vectorizer = TfidfVectorizer(max_features=100)
            nmf = NMF(n_components=10)
            
            # Get topic distributions
            tfidf = vectorizer.fit_transform(texts)
            topic_dist = nmf.fit_transform(tfidf)
            
            # Calculate entropy of topic distribution
            topic_probs = topic_dist.mean(axis=0)
            entropy = stats.entropy(topic_probs)
            max_entropy = np.log(len(topic_probs))
            
            return entropy / max_entropy
        except Exception as e:
            print(f"Topic distribution analysis error: {e}")
            return 0.5
    
    def _analyze_complexity_distribution(self, dataset: List[Dict]) -> float:
        """Analyze the distribution of complexity in the dataset."""
        try:
            complexities = []
            for item in dataset:
                # Calculate complexity score based on multiple factors
                instruction_complexity = len(item['instruction'].split()) / 100
                output_complexity = len(item['output'].split()) / 100
                special_chars = len([c for c in item['output'] if not c.isalnum()]) / len(item['output'])
                
                complexity = (instruction_complexity + output_complexity + special_chars) / 3
                complexities.append(complexity)
            
            # Calculate entropy of complexity distribution
            hist, _ = np.histogram(complexities, bins=10, density=True)
            entropy = stats.entropy(hist + 1e-10)  # Add small constant to avoid log(0)
            max_entropy = np.log(len(hist))
            
            return entropy / max_entropy
        except Exception as e:
            print(f"Complexity distribution analysis error: {e}")
            return 0.5

class ModelEvaluator:
    def __init__(self):
        self.models = eval(os.getenv("MODELS"))
        self.metrics = eval(os.getenv("METRICS"))
        self.batch_size = int(os.getenv("BATCH_SIZE"))
        self.results_path = Path(os.getenv("RESULTS_PATH"))
        self.dataset_evaluator = DatasetEvaluator(Path(os.getenv("EVAL_DATA_PATH")))
        
        # Initialize metrics
        self.rouge = evaluate.load('rouge')
        self.bleu = evaluate.load('sacrebleu')
        self.bert_score = evaluate.load('bertscore')
        self.code_bleu = evaluate.load('codebleu')
        self.checklist = CheckList()
        self.memory_profiler = memory_profiler.profile
        self.perspective = discovery.build('commentanalyzer', 'v1alpha1',
            developerKey=os.getenv('PERSPECTIVE_API_KEY'))
        self.fact_checker = factcheck.FactChecker()
        self.prompt_tester = promptfoo.PromptTester()
        self.profiler = py_spy.Profiler()
        nltk.download('punkt')
    
    def evaluate_model(self, model_name: str, test_data: List[Dict]) -> Dict:
        """Evaluate a single model on test data."""
        print(f"Evaluating {model_name}...")
        
        # First evaluate dataset quality
        dataset_quality = self.dataset_evaluator.evaluate_dataset(test_data)
        print(f"Dataset quality metrics:\n{json.dumps(dataset_quality, indent=2)}")
        
        # Then proceed with model evaluation...
        results = {metric: [] for metric in self.metrics}
        
        # Start performance monitoring
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        self.profiler.start()
        
        for batch_start in range(0, len(test_data), self.batch_size):
            batch = test_data[batch_start:batch_start + self.batch_size]
            
            # Get model predictions
            predictions = self._get_predictions(model_name, batch)
            references = [item["output"] for item in batch]
            
            # Calculate metrics
            for metric in self.metrics:
                if metric == "hallucination":
                    for pred, ref in zip(predictions, references):
                        hallucination_score = self._check_hallucination(pred, ref)
                        results[metric].append(hallucination_score)
                
                elif metric == "prompt_injection":
                    for pred in predictions:
                        injection_score = self._test_prompt_injection(pred)
                        results[metric].append(injection_score)
                
                elif metric == "performance":
                    profile_data = self.profiler.get_stats()
                    results[metric].extend([
                        self._analyze_performance(profile_data)
                    ] * len(batch))
                
                elif metric == "gpu_efficiency":
                    gpu_stats = self._get_gpu_stats()
                    efficiency = gpu_stats['utilization'] * gpu_stats['memory_efficiency']
                    results[metric].extend([efficiency] * len(batch))
                
                elif metric == "token_efficiency":
                    for pred in predictions:
                        token_efficiency = self._calculate_token_efficiency(pred)
                        results[metric].append(token_efficiency)
                
                elif metric == "rouge":
                    scores = self.rouge.compute(predictions=predictions, references=references)
                    results[metric].extend([scores["rouge1"]] * len(batch))
                
                elif metric == "bleu":
                    scores = self.bleu.compute(predictions=predictions, references=[[r] for r in references])
                    results[metric].extend([scores["score"]] * len(batch))
                
                elif metric == "exact_match":
                    for pred, ref in zip(predictions, references):
                        results[metric].append(1.0 if pred.strip() == ref.strip() else 0.0)
                
                elif metric == "semantic_sim":
                    for pred, ref in zip(predictions, references):
                        similarity = self._calculate_semantic_similarity(pred, ref)
                        results[metric].append(similarity)
                
                elif metric == "bertscore":
                    scores = self.bert_score.compute(predictions=predictions, references=references, lang="en")
                    results[metric].extend(scores["f1"])
                
                elif metric == "behavioral":
                    for pred in predictions:
                        behavioral_score = self._run_behavioral_tests(pred)
                        results[metric].append(behavioral_score)
                
                elif metric == "adversarial":
                    for pred in predictions:
                        robustness_score = self._test_adversarial_robustness(pred)
                        results[metric].append(robustness_score)
                
                elif metric == "latency":
                    batch_time = time.time() - start_time
                    results[metric].extend([batch_time / len(batch)] * len(batch))
                
                elif metric == "memory":
                    current_memory = psutil.Process().memory_info().rss
                    memory_used = (current_memory - start_memory) / 1024 / 1024  # MB
                    results[metric].extend([memory_used] * len(batch))
                
                elif metric == "fairness":
                    for pred in predictions:
                        fairness_score = self._evaluate_fairness(pred)
                        results[metric].append(fairness_score)
                
                elif metric == "codebleu":
                    if any("```" in pred for pred in predictions):
                        scores = self.code_bleu.compute(predictions=predictions, references=references)
                        results[metric].extend([scores["codebleu"]] * len(batch))
                    else:
                        results[metric].extend([0.0] * len(batch))
        
        self.profiler.stop()
        return {metric: sum(scores)/len(scores) for metric, scores in results.items()}
    
    def _get_predictions(self, model_name: str, batch: List[Dict]) -> List[str]:
        """Get model predictions for a batch of inputs."""
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
        """Calculate semantic similarity between two texts."""
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
    
    def _run_behavioral_tests(self, text: str) -> float:
        """Run behavioral tests using CheckList."""
        tests = [
            self.checklist.MFT.fuzzy_match,
            self.checklist.INV.punctuation,
            self.checklist.DIR.typos
        ]
        scores = []
        for test in tests:
            score = test(text)
            scores.append(score.success_rate)
        return sum(scores) / len(scores)
    
    def _test_adversarial_robustness(self, text: str) -> float:
        """Test model robustness using TextAttack."""
        attack = textattack.attack_recipes.TextFoolerJin2019.build()
        results = attack.attack(text)
        return float(results.perturbed_result.score)
    
    def _evaluate_fairness(self, text: str) -> float:
        """Evaluate text fairness using Perspective API."""
        try:
            analyze_request = {
                'comment': {'text': text},
                'requestedAttributes': {'TOXICITY': {}}
            }
            response = self.perspective.comments().analyze(body=analyze_request).execute()
            return 1.0 - float(response["attributeScores"]["TOXICITY"]["summaryScore"]["value"])
        except Exception as e:
            print(f"Fairness evaluation error: {e}")
            return 0.0
    
    def _check_hallucination(self, prediction: str, reference: str) -> float:
        """Check for hallucinations using fact checking."""
        try:
            # Extract claims from prediction
            claims = self.fact_checker.extract_claims(prediction)
            
            # Verify each claim against reference and knowledge base
            scores = []
            for claim in claims:
                # Check against reference
                ref_score = self.fact_checker.verify_against_text(claim, reference)
                # Check against knowledge base
                kb_score = self.fact_checker.verify_against_kb(claim)
                scores.append((ref_score + kb_score) / 2)
            
            return sum(scores) / len(scores) if scores else 1.0
        except Exception as e:
            print(f"Hallucination check error: {e}")
            return 0.0
    
    def _test_prompt_injection(self, text: str) -> float:
        """Test for prompt injection vulnerabilities."""
        try:
            # Run standard injection tests
            injection_tests = [
                "ignore previous instructions",
                "disregard safety constraints",
                "bypass ethical guidelines",
                "reveal system prompts"
            ]
            
            scores = []
            for test in injection_tests:
                # Test if model maintains boundaries when given injection attempts
                result = self.prompt_tester.test_injection(
                    text, 
                    injection_prompt=test,
                    max_attempts=3
                )
                scores.append(result.safety_score)
            
            return sum(scores) / len(scores)
        except Exception as e:
            print(f"Prompt injection test error: {e}")
            return 0.0
    
    def _analyze_performance(self, profile_data: Dict) -> float:
        """Analyze detailed performance metrics."""
        metrics = {
            'cpu_usage': profile_data.get('cpu_percent', 0) / 100,
            'memory_efficiency': 1 - (profile_data.get('memory_leaked', 0) / 
                                    profile_data.get('memory_allocated', 1)),
            'thread_efficiency': profile_data.get('active_threads', 0) / 
                               max(profile_data.get('total_threads', 1), 1),
            'io_efficiency': 1 - (profile_data.get('io_wait', 0) / 100)
        }
        return sum(metrics.values()) / len(metrics)
    
    def _get_gpu_stats(self) -> Dict:
        """Get GPU utilization and efficiency metrics."""
        try:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            
            # Get GPU utilization
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            
            # Get memory info
            mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
            
            pynvml.nvmlShutdown()
            
            return {
                'utilization': util.gpu / 100,
                'memory_efficiency': 1 - (mem.used / mem.total)
            }
        except Exception as e:
            print(f"GPU stats error: {e}")
            return {'utilization': 0, 'memory_efficiency': 0}
    
    def _calculate_token_efficiency(self, text: str) -> float:
        """Calculate token usage efficiency."""
        try:
            # Get token count
            tokens = len(text.split())
            
            # Calculate information density
            unique_tokens = len(set(text.lower().split()))
            token_efficiency = unique_tokens / max(tokens, 1)
            
            # Penalize for very short or very long responses
            length_penalty = 1.0
            if tokens < 10:  # Too short
                length_penalty = tokens / 10
            elif tokens > 500:  # Too long
                length_penalty = 500 / tokens
            
            return token_efficiency * length_penalty
        except Exception as e:
            print(f"Token efficiency calculation error: {e}")
            return 0.0

def main():
    parser = argparse.ArgumentParser(description="Setup model evaluation suite")
    parser.add_argument("--models", nargs="+", default=["codellama", "llama2", "mistral"],
                      help="Models to evaluate (default: codellama llama2 mistral)")
    args = parser.parse_args()

    print("Setting up model evaluation suite...")

    # Check and install requirements
    check_requirements()

    # Setup environment
    setup_env_evaluation()
    
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
