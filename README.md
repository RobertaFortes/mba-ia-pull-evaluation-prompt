# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

Projeto do MBA Full Cycle (IA): puxa um prompt de baixa qualidade do LangSmith Prompt Hub, otimiza com técnicas de Prompt Engineering, publica de volta e mede a qualidade com 5 métricas (Helpfulness, Correctness, F1-Score, Clarity, Precision), exigindo **todas >= 0.8**.

- Prompt semente (v1): `leonanluppi/bug_to_user_story_v1`
- Prompt otimizado (v2, público): `roberta-fortes/bug_to_user_story_v2`
- Modelos (OpenAI): `gpt-5.4-mini` responde, `gpt-5.4` avalia

## Técnicas Aplicadas (Fase 2)

O prompt otimizado está em [`prompts/bug_to_user_story_v2.yml`](prompts/bug_to_user_story_v2.yml).

| Técnica | Por que escolhi | Como apliquei |
|---|---|---|
| **Few-shot Learning** (obrigatória) | As referências do dataset têm formatos bem específicos por complexidade (5 critérios nos simples; seções extras nos médios; blocos A/B/C e tasks nos complexos). Exemplos ensinam o formato melhor que descrições. | 7 exemplos `<entrada>/<saida>` originais: simples (exportar PDF), médio de segurança com dois perfis, médio de performance, médio de UI com acessibilidade, médio com cálculo, médio com concorrência/prevenção e um complexo com 3 problemas. |
| **Role Prompting** | Uma persona define tom e nível de detalhe. | "Product Manager sênior com forte base técnica e mais de 10 anos em times ágeis". |
| **Chain of Thought** | O modelo precisa classificar a complexidade e levantar fatos antes de escrever. | 6 passos de raciocínio feitos mentalmente, sem aparecer na resposta (para não poluir a saída e prejudicar Clarity/Precision). |
| **Skeleton of Thought** | Cada complexidade pede uma estrutura fixa. | Esqueleto por complexidade: simples (história + 5 critérios), médio (+ seções conforme o tipo: `Contexto Técnico`, `Critérios de Acessibilidade`, `Exemplo de Cálculo`, `Critérios de Prevenção`, `Contexto de Segurança`) e complexo (`=== USER STORY PRINCIPAL ===`, critérios A/B/C, técnicos, contexto do bug e tasks em fases). |

**Exemplos práticos de aplicação (trechos do prompt):**

- *Role Prompting:* "Você é um Product Manager sênior, com forte base técnica e mais de 10 anos de experiência em times ágeis."
- *Chain of Thought:* "RACIOCÍNIO (faça mentalmente, passo a passo, e NÃO mostre na resposta): 1. Identifique quem é afetado... 4. Classifique a complexidade..."
- *Skeleton of Thought:* "SIMPLES: frase da história + 'Critérios de Aceitação:' com exatamente 5 itens: 1 Dado, 1 Quando, 1 Então e 2 E."
- *Few-shot:* blocos `<entrada>…</entrada><saida>…</saida>` cobrindo cada complexidade.

Outras decisões: regras explícitas (fidelidade aos fatos, vocabulário do relato, critérios mensuráveis), tratamento de edge cases (relato vago, em inglês, sem usuário, não-bug), e separação **System** (persona, regras, exemplos) vs **User** (apenas o relato em `{bug_report}`, sem duplicar como no v1).

## Resultados Finais

### Evidências no LangSmith

- **Dataset público (15 exemplos + experimentos):** https://smith.langchain.com/public/b2dd3b9b-29f5-47d9-8806-3a67da31b2f8/d
- Screenshots das avaliações e dos traces (3 exemplos): pasta [`docs/`](docs/) — _adicionar_ (ver "Como Executar").

### Notas finais do v2 (todas >= 0.8)

```
Prompt: roberta-fortes/bug_to_user_story_v2

Métricas Derivadas:
  - Helpfulness: 0.85 ✓
  - Correctness: 0.83 ✓

Métricas Base:
  - F1-Score: 0.82 ✓
  - Clarity: 0.87 ✓
  - Precision: 0.83 ✓

📊 MÉDIA GERAL: 0.8401
✅ STATUS: APROVADO - Todas as métricas >= 0.8
```

### Processo de otimização (4 iterações)

| # | Mudança | Helpfulness | Correctness | F1 | Clarity | Precision | Status |
|---|---|---|---|---|---|---|---|
| v1 | Prompt semente (baseline) | ~0.80 ✗ | 0.73 ✗ | 0.68 ✗ | 0.82 | 0.77 ✗ | Reprovado (média 0.76) |
| 1 | Primeira versão do v2 (few-shot + persona + CoT + esqueleto) | 0.83 | 0.81 | 0.81 | 0.86 | 0.80 | Aprovado, **mas inflado** (ver abaixo) |
| 2 | Exemplos few-shot trocados por exemplos originais | 0.83 | 0.79 ✗ | 0.79 ✗ | 0.86 | 0.80 | Reprovado |
| 3 | História orientada à capacidade (sem repetir o bug), 5 critérios nos simples, complexo mais rico | 0.84 | 0.79 ✗ | 0.78 ✗ | 0.87 | 0.80 | Reprovado |
| 4 | Regras dos médios (contexto sempre presente, cálculo, prevenção), vocabulário do relato, +2 exemplos | **0.85** | **0.83** | **0.82** | **0.87** | **0.83** | **Aprovado** |

**O que aprendi em cada passo:**

- **Iteração 1 → 2 (vazamento de dados).** Percebi que 3 dos meus exemplos few-shot tinham sido copiados de itens do próprio dataset de avaliação. Isso infla a nota, porque o modelo "já viu" a resposta. Troquei por exemplos novos, com o mesmo estilo, e a nota caiu: a medição honesta é a da iteração 2 em diante.
- **Iteração 2 → 3.** Comparando as respostas geradas com as referências dos exemplos mais fracos, vi que o modelo repetia o bug na história ("não deve exibir 50") enquanto as referências descrevem a *capacidade desejada* com expectativas complementares (confirmação visual, contador atualizado, mesma qualidade entre navegadores). Também vazou um token em outro alfabeto numa resposta, então adicionei a regra "somente português com alfabeto latino".
- **Iteração 3 → 4.** Os exemplos médios caíram (F1 de 0,53 e 0,55): o modelo os tratava como simples, sem `Exemplo de Cálculo`, sem `Critérios de Prevenção` e inventando o status "pago" quando o relato dizia "aprovado". Reforcei a regra ("médio sempre traz uma seção de contexto"), adicionei a regra de vocabulário e dois exemplos (cálculo e prevenção).

### Comparação v1 x v2: o que mudou e por quê

| | v1 | v2 |
|---|---|---|
| Persona | genérica ("assistente") | Product Manager sênior |
| Exemplos | nenhum | 7 few-shot originais |
| Formato | não definido | Como/Quero/Para que + Dado/Quando/Então, adaptado à complexidade |
| Regras / edge cases | nenhuma | regras explícitas (fidelidade, vocabulário, verificabilidade) e casos limite |
| System vs User | `{bug_report}` duplicado nos dois | system com instruções; user só com o relato |
| Resultado | média 0.76 (reprovado) | média 0.84 (aprovado) |

O ganho maior foi em **F1 (0.68 → 0.82)** e **Correctness (0.73 → 0.83)**: o v1 gera histórias genéricas e omite a estrutura e as seções que as referências esperam; o v2 força a estrutura por complexidade e as expectativas complementares.

**Limitações e observações honestas:**

- As margens são pequenas (a menor nota é 0.82). O avaliador é um LLM: rodar de novo pode variar alguns centésimos.
- Com `gpt-5.4-mini` o v1 já parte de ~0.76, bem acima dos "0.45" do exemplo ilustrativo do enunciado.
- Há exemplos individuais abaixo de 0.8 (por exemplo o [5], com F1 0.65): as notas oficiais são as médias por métrica.

## Como Executar

**Pré-requisitos:** Python 3.10+, conta no [LangSmith](https://smith.langchain.com) (com handle público criado, ver `.env.example`) e uma API key da OpenAI ou do Google Gemini (com crédito/cota).

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # preencha LANGSMITH_API_KEY, USERNAME_LANGSMITH_HUB, a chave do provider, LLM_PROVIDER, LLM_MODEL e EVAL_MODEL
```

1. Pull do prompt inicial (v1): `python src/pull_prompts.py`
2. Edite `prompts/bug_to_user_story_v2.yml`
3. Push do v2 (público): `python src/push_prompts.py`
4. Avaliação: `python src/evaluate.py`
5. Testes: `pytest tests/test_prompts.py`
6. (Opcional) Nota do baseline v1 no mesmo dataset: `python scripts/evaluate_baseline.py`
7. Link público do dataset (rode uma vez só: a cada chamada o link muda):

```bash
python -c "from langsmith import Client; print(Client().share_dataset(dataset_name='<LANGSMITH_PROJECT>-eval')['url'])"
```

**Screenshots:** no LangSmith, abra o dataset `<LANGSMITH_PROJECT>-eval` → aba Experiments e capture (1) a comparação com as notas do v2 aprovado e (2) o trace detalhado de pelo menos 3 exemplos. Salve em `docs/`.

### Estrutura

```
prompts/   bug_to_user_story_v1.yml (pull) e bug_to_user_story_v2.yml (otimizado)
src/       pull_prompts.py, push_prompts.py (implementados); evaluate.py, metrics.py, utils.py (base)
tests/     test_prompts.py (6 testes de validação do prompt)
scripts/   evaluate_baseline.py (avalia o v1 para comparação)
datasets/  bug_to_user_story.jsonl (15 exemplos, não alterado)
```
