"""
Multi-Model Manager - Switch between Claude, GLM-4.6, and other LLMs
"""

import os
from typing import Optional, Dict, Any, Literal
from dotenv import load_dotenv

load_dotenv()


class LLMManager:
    """
    Unified interface for multiple LLM providers:
    - Claude (Anthropic)
    - GLM-4.6 (Zhipu AI)
    - OpenAI GPT models
    """

    def __init__(
        self,
        default_model: Literal["claude", "glm", "gpt"] = "claude"
    ):
        """
        Initialize LLM Manager

        Args:
            default_model: Which model to use by default
        """
        self.default_model = default_model
        self.clients = {}

        # Initialize clients based on available API keys
        self._init_claude()
        self._init_glm()
        self._init_openai()

    def _init_claude(self):
        """Initialize Claude (Anthropic) client"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            try:
                from anthropic import Anthropic
                self.clients["claude"] = Anthropic(api_key=api_key)
                print("✅ Claude client initialized")
            except ImportError:
                print("⚠️  anthropic package not installed. Run: pip install anthropic")
            except Exception as e:
                print(f"❌ Claude initialization failed: {e}")

    def _init_glm(self):
        """Initialize GLM-4.6 (Zhipu AI) client"""
        api_key = os.getenv("ZHIPUAI_API_KEY")
        if api_key:
            try:
                from zhipuai import ZhipuAI
                self.clients["glm"] = ZhipuAI(api_key=api_key)
                print("✅ GLM-4.6 client initialized")
            except ImportError:
                print("⚠️  zhipuai package not installed. Run: pip install zhipuai")
            except Exception as e:
                print(f"❌ GLM initialization failed: {e}")

    def _init_openai(self):
        """Initialize OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                from openai import OpenAI
                self.clients["gpt"] = OpenAI(api_key=api_key)
                print("✅ OpenAI client initialized")
            except ImportError:
                print("⚠️  openai package not installed. Run: pip install openai")
            except Exception as e:
                print(f"❌ OpenAI initialization failed: {e}")

    def classify_text(
        self,
        text: str,
        categories: list,
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Classify text into categories using specified model

        Args:
            text: Text to classify
            categories: List of possible categories
            model: Which model to use (claude, glm, gpt). Defaults to default_model

        Returns:
            dict with classification results
        """
        model = model or self.default_model

        prompt = f"""Classify the following text into one of these categories: {', '.join(categories)}

Text: {text}

Return only the category name, nothing else."""

        if model == "claude":
            return self._classify_claude(prompt, **kwargs)
        elif model == "glm":
            return self._classify_glm(prompt, **kwargs)
        elif model == "gpt":
            return self._classify_openai(prompt, **kwargs)
        else:
            raise ValueError(f"Unknown model: {model}")

    def _classify_claude(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Classify using Claude"""
        if "claude" not in self.clients:
            raise RuntimeError("Claude client not initialized")

        response = self.clients["claude"].messages.create(
            model=kwargs.get("model_version", "claude-3-5-sonnet-20241022"),
            max_tokens=kwargs.get("max_tokens", 100),
            messages=[{"role": "user", "content": prompt}]
        )

        return {
            "model": "claude",
            "result": response.content[0].text.strip(),
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        }

    def _classify_glm(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Classify using GLM-4.6"""
        if "glm" not in self.clients:
            raise RuntimeError("GLM client not initialized")

        response = self.clients["glm"].chat.completions.create(
            model=kwargs.get("model_version", "glm-4-plus"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=kwargs.get("max_tokens", 100),
            temperature=kwargs.get("temperature", 0.1)
        )

        return {
            "model": "glm",
            "result": response.choices[0].message.content.strip(),
            "usage": {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens
            }
        }

    def _classify_openai(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Classify using OpenAI"""
        if "gpt" not in self.clients:
            raise RuntimeError("OpenAI client not initialized")

        response = self.clients["gpt"].chat.completions.create(
            model=kwargs.get("model_version", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=kwargs.get("max_tokens", 100),
            temperature=kwargs.get("temperature", 0.1)
        )

        return {
            "model": "gpt",
            "result": response.choices[0].message.content.strip(),
            "usage": {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens
            }
        }

    def summarize(
        self,
        text: str,
        max_length: int = 200,
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Summarize text using specified model

        Args:
            text: Text to summarize
            max_length: Maximum summary length
            model: Which model to use

        Returns:
            dict with summary and metadata
        """
        model = model or self.default_model

        prompt = f"""Summarize the following legal case in {max_length} words or less:

{text}

Summary:"""

        if model == "claude":
            return self._classify_claude(prompt, max_tokens=max_length * 2, **kwargs)
        elif model == "glm":
            return self._classify_glm(prompt, max_tokens=max_length * 2, **kwargs)
        elif model == "gpt":
            return self._classify_openai(prompt, max_tokens=max_length * 2, **kwargs)

    def extract_entities(
        self,
        text: str,
        entity_types: list,
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Extract named entities from text

        Args:
            text: Text to analyze
            entity_types: Types of entities to extract (e.g., ["person", "organization", "date"])
            model: Which model to use

        Returns:
            dict with extracted entities
        """
        model = model or self.default_model

        prompt = f"""Extract the following entities from the legal text: {', '.join(entity_types)}

Text: {text}

Return as JSON format: {{"person": [...], "organization": [...], "date": [...]}}"""

        if model == "claude":
            return self._classify_claude(prompt, max_tokens=500, **kwargs)
        elif model == "glm":
            return self._classify_glm(prompt, max_tokens=500, **kwargs)
        elif model == "gpt":
            return self._classify_openai(prompt, max_tokens=500, **kwargs)

    def compare_models(
        self,
        text: str,
        task: str = "classify",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run the same task on all available models and compare results

        Args:
            text: Input text
            task: Task type (classify, summarize, extract)

        Returns:
            dict with results from all models
        """
        results = {}

        for model_name in self.clients.keys():
            try:
                if task == "classify":
                    results[model_name] = self.classify_text(
                        text,
                        categories=kwargs.get("categories", ["CRIMINAL", "CIVIL", "TAX"]),
                        model=model_name
                    )
                elif task == "summarize":
                    results[model_name] = self.summarize(text, model=model_name)
                elif task == "extract":
                    results[model_name] = self.extract_entities(
                        text,
                        entity_types=kwargs.get("entity_types", ["person", "date"]),
                        model=model_name
                    )
            except Exception as e:
                results[model_name] = {"error": str(e)}

        return results

    def switch_default(self, model: Literal["claude", "glm", "gpt"]):
        """
        Switch the default model

        Args:
            model: Model to use as default
        """
        if model not in ["claude", "glm", "gpt"]:
            raise ValueError(f"Unknown model: {model}")

        self.default_model = model
        print(f"✅ Default model switched to: {model}")


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_usage():
    """Example usage of LLMManager"""

    # Initialize with Claude as default
    llm = LLMManager(default_model="claude")

    # Example 1: Classify using default model (Claude)
    result = llm.classify_text(
        "This case involves murder and robbery",
        categories=["CRIMINAL", "CIVIL", "TAX", "CONSTITUTIONAL"]
    )
    print(f"Classification (Claude): {result['result']}")

    # Example 2: Classify using GLM-4.6
    result_glm = llm.classify_text(
        "This case involves murder and robbery",
        categories=["CRIMINAL", "CIVIL", "TAX", "CONSTITUTIONAL"],
        model="glm"
    )
    print(f"Classification (GLM): {result_glm['result']}")

    # Example 3: Compare all models
    comparison = llm.compare_models(
        "Contract dispute between two companies",
        task="classify",
        categories=["CRIMINAL", "CIVIL", "TAX"]
    )

    for model, result in comparison.items():
        print(f"{model}: {result.get('result', result.get('error'))}")

    # Example 4: Switch default model to GLM
    llm.switch_default("glm")

    # Now this will use GLM by default
    result = llm.classify_text(
        "Tax evasion case",
        categories=["CRIMINAL", "CIVIL", "TAX"]
    )
    print(f"Classification (now using GLM as default): {result['result']}")


if __name__ == "__main__":
    example_usage()
