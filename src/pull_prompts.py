"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull do prompt semente do desafio
3. Salva localmente em prompts/bug_to_user_story_v1.yml

DICAS DE IMPLEMENTAÇÃO:

- O pull é feito pelo cliente do LangSmith:

      from langsmith import Client
      client = Client()
      prompt = client.pull_prompt(
          "leonanluppi/bug_to_user_story_v1",
          dangerously_pull_public_prompt=True,
      )

- O parâmetro `dangerously_pull_public_prompt=True` é obrigatório sempre que o
  identificador tem dono explícito ("owner/nome"). O LangSmith bloqueia esse pull
  por padrão porque um prompt do Hub é um objeto LangChain serializado, que pode
  vir de terceiros. Aqui o prompt é o do desafio, então o risco é conhecido.

- O retorno é um ChatPromptTemplate. Para extrair o conteúdo das mensagens,
  use a serialização nativa do LangChain (`prompt.messages`, e o atributo
  `.prompt.template` de cada mensagem).

- Use `save_yaml` de utils.py para gravar o resultado no arquivo .yml.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


SEED_PROMPT = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = "prompts/bug_to_user_story_v1.yml"


def _message_parts(prompt) -> dict:
    """Extrai o texto das mensagens system/user de um ChatPromptTemplate."""
    parts = {}
    for message in prompt.messages:
        class_name = type(message).__name__
        if class_name == "SystemMessagePromptTemplate":
            parts["system_prompt"] = message.prompt.template
        elif class_name == "HumanMessagePromptTemplate":
            parts["user_prompt"] = message.prompt.template
    return parts


def pull_prompts_from_langsmith() -> bool:
    """Faz pull do prompt semente e salva em prompts/bug_to_user_story_v1.yml."""
    print(f"Fazendo pull de: {SEED_PROMPT}")

    try:
        client = Client()
        # Obrigatório para prompts "owner/nome": o Hub bloqueia por padrão o pull de terceiros.
        prompt = client.pull_prompt(SEED_PROMPT, dangerously_pull_public_prompt=True)
    except Exception as e:
        print(f"❌ Erro ao fazer pull do prompt: {e}")
        return False

    parts = _message_parts(prompt)
    if "system_prompt" not in parts:
        print("❌ O prompt retornado não possui mensagem de system")
        return False

    data = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": parts["system_prompt"],
            "user_prompt": parts.get("user_prompt", "{bug_report}"),
            "version": "v1",
            "source": SEED_PROMPT,
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }

    if not save_yaml(data, OUTPUT_PATH):
        return False

    print(f"✓ Prompt salvo em {OUTPUT_PATH}")
    return True


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    return 0 if pull_prompts_from_langsmith() else 1


if __name__ == "__main__":
    sys.exit(main())
