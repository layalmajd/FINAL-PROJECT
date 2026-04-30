from app.models.assignment import AssignmentGroup, EvaluationCriterion
from app.utils.prompt_policy import build_grading_rules


def build_evaluation_prompt(
    *,
    group: AssignmentGroup,
    criteria: list[EvaluationCriterion],
    submission_text: str,
    response_language: str = "en",
) -> str:
    language_label = "Arabic" if response_language == "ar" else "English"
    grading_rules = build_grading_rules(language_label=language_label, grade_scale=group.grade_scale)
    submission_word_count = len(submission_text.split())
    criteria_lines = []
    for criterion in criteria:
        criteria_lines.append(
            "\n".join(
                [
                    f"- Criterion: {criterion.name}",
                    f"  Weight / final points: {float(criterion.weight):.2f}",
                    f"  Manual only: {'yes' if criterion.is_manual else 'no'}",
                    f"  Description: {criterion.description or 'No description provided.'}",
                ]
            )
        )

    return f"""
You are a neutral, precise academic evaluator. Evaluate only the provided submission against the listed criteria.

Assignment group:
- Name: {group.name}
- Description: {group.description or 'No description provided.'}
- Grade scale: {group.grade_scale}

Scoring requirements:
{grading_rules}

JSON shape:
{{
  "total_score": number | null,
  "summary_feedback": "string",
  "criterion_scores": [
    {{
      "criterion_name": "string",
      "ai_score": number | null,
      "feedback": "string"
    }}
  ]
}}

Criteria:
{chr(10).join(criteria_lines)}

Submission size:
- Word count: {submission_word_count}
- Use word count only as context. Do not deduct for length itself; deduct only when the criterion's required evidence is missing or weak.

Submission content:
{submission_text}
""".strip()
