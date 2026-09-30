# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

Projeto do MBA Full Cycle (IA): puxa um prompt de baixa qualidade do LangSmith Prompt Hub, otimiza com técnicas de Prompt Engineering, publica de volta e mede a qualidade com 5 métricas (Helpfulness, Correctness, F1-Score, Clarity, Precision), exigindo **todas >= 0.8**.

## Técnicas Aplicadas (Fase 2)

O prompt otimizado está em [`prompts/bug_to_user_story_v2.yml`](prompts/bug_to_user_story_v2.yml).

| Técnica | Por que escolhi | Como apliquei |
|---|---|---|
| **Few-shot Learning** (obrigatória) | As referências do dataset têm formatos bem específicos por complexidade. Exemplos ensinam o formato melhor que descrições. | 4 exemplos `<entrada>/<saida>`: simples (validação), médio com segurança e dois perfis, médio com contexto técnico, e complexo (vários problemas). |
| **Role Prompting** | Uma persona define tom e nível de detalhe. | "Product Manager sênior com forte base técnica", que escreve histórias testáveis. |
| **Chain of Thought** | O modelo precisa classificar a complexidade e levantar os fatos antes de escrever. | 5 passos de raciocínio feitos mentalmente, sem aparecer na resposta (evita poluir a saída e prejudicar Clarity/Precision). |
| **Skeleton of Thought** | Bugs complexos exigem estrutura fixa para cobrir todos os problemas. | Esqueleto por complexidade: simples, médio (`Contexto Técnico`) e complexo (`=== USER STORY PRINCIPAL ===`, critérios A/B/C, técnicos, contexto, tasks). |

Outras decisões: regras explícitas (fidelidade aos fatos, sem inventar métricas, critérios mensuráveis), tratamento de edge cases (relato vago, em inglês, sem usuário, não-bug) e separação **System** (persona, regras, exemplos) vs **User** (apenas o relato em `{bug_report}`, sem duplicar como no v1).

## Resultados Finais

> Preencher após a avaliação (ver seção "Como Executar").

- Dataset público (com experimentos): _link do `share_dataset`_
- Screenshots: _adicionar em `docs/`_

### v1 vs v2

| | v1 | v2 |
|---|---|---|
| Persona | genérica ("assistente") | Product Manager sênior |
| Exemplos | nenhum | 4 few-shot |
| Formato | não definido | Como/Quero/Para que + Dado/Quando/Então por complexidade |
| Regras / edge cases | nenhuma | regras explícitas e tratamento de casos limite |
| `{bug_report}` | duplicado no system e no user | apenas no user prompt |

## Como Executar

**Pré-requisitos:** Python 3.10+, conta no [LangSmith](https://smith.langchain.com) (com handle público criado, ver `.env.example`) e uma API key da OpenAI ou do Google Gemini.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # preencha as chaves, USERNAME_LANGSMITH_HUB, LLM_PROVIDER, LLM_MODEL e EVAL_MODEL
```

1. Pull do prompt inicial (v1): `python src/pull_prompts.py`
2. Edite `prompts/bug_to_user_story_v2.yml`
3. Push do v2 (público): `python src/push_prompts.py`
4. Avaliação: `python src/evaluate.py`
5. Testes: `pytest tests/test_prompts.py`
6. Link público do dataset:

```bash
python -c "from langsmith import Client; print(Client().share_dataset(dataset_name='<LANGSMITH_PROJECT>-eval')['url'])"
```
