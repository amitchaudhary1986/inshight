# AI Interview Evaluation & Scoring

## Evaluation Prompt

The system uses the following prompt structure to evaluate candidate responses:

```text
You are an expert technical interviewer. Evaluate the candidate's response to the following question.

Question: {question}
Candidate Transcription: {transcription}

Criteria (Score each from 1-10):
1. Relevance: Did the candidate answer the specific question asked?
2. Technical Depth: Did the candidate demonstrate a strong grasp of the technical concepts?
3. Clarity: Was the answer easy to follow and well-structured?
4. Communication: Did the candidate express themselves effectively?

Respond ONLY with a JSON object in the following format:
{
    "relevance": <score>,
    "technical_depth": <score>,
    "clarity": <score>,
    "communication": <score>,
    "feedback": "<detailed feedback string>"
}
```

## Production-Ready Scoring Formula

The final score is calculated using a weighted average of individual criteria, followed by penalties for detected cheating behaviors.

### Base Score calculation
$S_{base} = 0.4 \cdot S_{tech} + 0.3 \cdot S_{rel} + 0.2 \cdot S_{clar} + 0.1 \cdot S_{comm}$

*   **Technical Depth (40%)**: Heaviest weight, as it represents the core competency.
*   **Relevance (30%)**: Ensures the candidate is actually answering the question.
*   **Clarity (20%)**: Important for effective collaboration.
*   **Communication (10%)**: Soft skills assessment.

### Penalties
$P = 1.0 - (0.2 \cdot \min(TabSwitches, 5)) - (0.5 \cdot CheatingFlagged)$

*   **Tab Switches**: Each switch (or window blur) reduces the final score by 20%, up to 100%.
*   **Cheating Flag**: If the AI detects scripted patterns or AI markers in the transcription, a flat 50% penalty is applied.

### Final Score
$S_{final} = \max(0, S_{base} \cdot P)$

## Anti-Cheating Logic

1.  **Client-Side**:
    *   `visibilitychange` & `window.blur`: Tracks when the candidate leaves the interview page.
    *   `paste` event prevention: Disallows pasting text into any fields.
2.  **Server-Side**:
    *   AI Marker Detection: Checks for phrases like "as an AI language model".
    *   Repetition Analysis: Flags extremely repetitive speech which often indicates scripted reading.
