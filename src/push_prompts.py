"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

DICAS DE IMPLEMENTAÇÃO:

- O push é feito pelo cliente do LangSmith:

      from langsmith import Client
      from langchain_core.prompts import ChatPromptTemplate

      client = Client()
      prompt = ChatPromptTemplate.from_messages([
          ("system", system_prompt),
          ("user", user_prompt),
      ])
      url = client.push_prompt(
          f"{username}/bug_to_user_story_v2",
          object=prompt,
          is_public=True,
          description="...",
          tags=[...],
      )

- `username` vem de USERNAME_LANGSMITH_HUB no .env e precisa ser o seu handle
  do Hub. Se você ainda não tem um handle, veja as instruções no .env.example.

- A variável do template precisa ser {bug_report}, que é a chave de entrada
  usada no dataset de avaliação.

- Use `load_yaml` de utils.py para ler o arquivo .yml.
"""

import os
import sys
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


PROMPT_FILE = "prompts/bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome completo no Hub ({handle}/{nome})
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_data["system_prompt"]),
            ("user", prompt_data.get("user_prompt", "{bug_report}")),
        ])

        techniques = ", ".join(prompt_data.get("techniques_applied", []))
        description = prompt_data.get("description", "")
        if techniques:
            description = f"{description} Técnicas: {techniques}."

        url = Client().push_prompt(
            prompt_name,
            object=prompt,
            is_public=True,
            description=description,
            tags=prompt_data.get("tags", []),
        )
        print(f"✓ Push realizado: {prompt_name}")
        print(f"  {url}")
        return True
    except Exception as e:
        print(f"❌ Erro ao fazer push de '{prompt_name}': {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    for field in ("description", "system_prompt", "user_prompt", "version"):
        if not str(prompt_data.get(field, "")).strip():
            errors.append(f"Campo obrigatório faltando ou vazio: {field}")

    for field in ("system_prompt", "user_prompt"):
        if "[TODO]" in str(prompt_data.get(field, "")):
            errors.append(f"{field} ainda contém [TODO]")

    if "{bug_report}" not in str(prompt_data.get("user_prompt", "")):
        errors.append("user_prompt deve conter a variável {bug_report}")

    if len(prompt_data.get("techniques_applied", [])) < 2:
        errors.append("Liste pelo menos 2 técnicas em techniques_applied")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS PARA O LANGSMITH")

    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    data = load_yaml(PROMPT_FILE)
    if not data or PROMPT_KEY not in data:
        print(f"❌ Chave '{PROMPT_KEY}' não encontrada em {PROMPT_FILE}")
        return 1

    prompt_data = data[PROMPT_KEY]
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Prompt inválido:")
        for error in errors:
            print(f"   - {error}")
        return 1

    prompt_name = f"{os.getenv('USERNAME_LANGSMITH_HUB')}/{PROMPT_KEY}"
    return 0 if push_prompt_to_langsmith(prompt_name, prompt_data) else 1


if __name__ == "__main__":
    sys.exit(main())
