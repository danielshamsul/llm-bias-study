# LLM Bias and Hallucination Detection Study

This project turns the Assignment 3 brief into a runnable Python workflow for:

- storing a structured prompt library,
- querying OpenAI, Anthropic, and xAI models,
- saving deterministic raw outputs for later scoring,
- applying a manual evaluation rubric, and
- generating summary tables and exportable analysis files.

## Project Structure

```text
data/
  prompts_sample.csv
outputs/
  responses/
  analysis/
src/
  llm_bias_study/
    clients/
    analysis.py
    cli.py
    config.py
    evaluation.py
    prompt_loader.py
    runner.py
    schemas.py
    storage.py
requirements.txt
.env.example
```

## Setup

1. Create and activate a virtual environment.
2. Install the project and dependencies:

```bash
pip install -e .
```

3. Copy `.env.example` to `.env` and add your API keys.

If you do not have API keys yet, leave them blank and keep `MOCK_ENABLED=true` to test the full workflow offline.

## Environment Variables

```bash
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
XAI_API_KEY=your_xai_key
MOCK_ENABLED=true
MOCK_MODEL=demo-model
OPENAI_MODEL=gpt-4.1
ANTHROPIC_MODEL=claude-3-5-sonnet-latest
XAI_MODEL=grok-2-latest
```

## Prompt Library Format

The prompt dataset should be a CSV with these columns:

- `prompt_id`
- `domain`
- `base_question`
- `ground_truth`
- `source`
- `is_contested`

The code automatically expands each question into the required prompting methods:

- `direct`
- `chain_of_thought`
- `delayed_answer`
- `devils_advocate`

## Run Data Collection

Run all configured models against the sample prompt library:

```bash
python -m llm_bias_study.cli run --prompt-file data/prompts_sample.csv
```

Run only the offline mock model:

```bash
python -m llm_bias_study.cli run --prompt-file data/prompts_sample.csv --models mock
```

Run only selected models:

```bash
python -m llm_bias_study.cli run --prompt-file data/prompts_sample.csv --models openai anthropic
```

## Score Responses

Create a rubric template from collected responses:

```bash
python -m llm_bias_study.cli rubric-template --responses outputs/responses/latest_responses.csv
```

After reviewers fill in the rubric columns, build summary outputs:

```bash
python -m llm_bias_study.cli analyze --responses outputs/responses/latest_responses.csv --rubric outputs/analysis/rubric_scored.csv
```

## What This Covers From the Brief

- Prompt library with verified ground truth metadata.
- Deterministic API calls with `temperature=0`.
- Storage of `Prompt_ID`, model, method, raw response, and timestamp.
- Support for the three requested prompting strategies.
- Evaluation workflow for accuracy, citation integrity, and confidence calibration.
- Aggregation into CSV and JSON analysis outputs without requiring heavy scientific Python packages.

## Notes

- The project is structured so you can start with the sample CSV and replace it with your full 50-100 prompt library later.
- Grok and other model names change over time, so keep `.env` model values aligned with the APIs you have access to.
- The rubric step is intentionally manual because your assignment describes human scoring by at least two team members.
