"""
Avalia o prompt v1 (baseline) no mesmo dataset e com o mesmo avaliador do v2,
para permitir a comparação v1 x v2 do README.

Não altera src/evaluate.py: reutiliza suas funções. O v1 é publicado como prompt
PRIVADO no seu handle (roberta/bug_to_user_story_v1) apenas para poder ser puxado pelo avaliador.

Uso: python scripts/evaluate_baseline.py
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client

import evaluate
from utils import load_yaml


def main():
    username = os.environ["USERNAME_LANGSMITH_HUB"]
    name = f"{username}/bug_to_user_story_v1"

    data = load_yaml(str(ROOT / "prompts" / "bug_to_user_story_v1.yml"))["bug_to_user_story_v1"]
    prompt = ChatPromptTemplate.from_messages([("system", data["system_prompt"]), ("user", data["user_prompt"])])

    client = Client()
    client.push_prompt(name, object=prompt, is_public=False, description="Baseline (v1) para comparação")

    dataset_name = f"{os.environ['LANGSMITH_PROJECT']}-eval"
    scores, url = evaluate.run_experiment(client, name, dataset_name)
    evaluate.display_results(name, scores)
    print(f"\nExperimento: {url}")


if __name__ == "__main__":
    main()
