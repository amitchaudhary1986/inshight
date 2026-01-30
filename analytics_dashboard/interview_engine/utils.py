import json

def calculate_final_score(scores, tab_switches, cheating_flagged):
    """
    Production-ready scoring formula.
    Base Score: 40% Technical, 30% Relevance, 20% Clarity, 10% Communication.
    Penalties: 20% reduction per tab switch (capped at 5 switches), 50% reduction if cheating flagged.
    """
    # Individual scores are expected to be on a scale of 1-10
    base_score = (
        0.4 * scores.get('technical_depth', 0) +
        0.3 * scores.get('relevance', 0) +
        0.2 * scores.get('clarity', 0) +
        0.1 * scores.get('communication', 0)
    )

    # Apply penalties
    penalty_multiplier = 1.0

    # Each tab switch reduces score by 20%
    penalty_multiplier -= (0.2 * min(tab_switches, 5))

    # Major cheating flag reduces score by 50%
    if cheating_flagged:
        penalty_multiplier -= 0.5

    # Ensure final score is not negative and rounded
    final_score = max(0, base_score * max(0, penalty_multiplier))
    return round(final_score, 2)

def get_evaluation_prompt(question, transcription):
    """
    Generates the prompt for the LLM evaluation.
    """
    return f"""
    You are an expert technical interviewer. Evaluate the candidate's response to the following question.

    Question: {question}
    Candidate Transcription: {transcription}

    Criteria (Score each from 1-10):
    1. Relevance: Did the candidate answer the specific question asked?
    2. Technical Depth: Did the candidate demonstrate a strong grasp of the technical concepts?
    3. Clarity: Was the answer easy to follow and well-structured?
    4. Communication: Did the candidate express themselves effectively?

    Respond ONLY with a JSON object in the following format:
    {{
        "relevance": <score>,
        "technical_depth": <score>,
        "clarity": <score>,
        "communication": <score>,
        "feedback": "<detailed feedback string>"
    }}
    """

def check_for_cheating(transcription):
    """
    Checks for scripted patterns or AI-generated markers.
    """
    suspicious_phrases = [
        "as an AI language model",
        "I am an AI assistant",
        "according to my training data",
        "here is the response to your question"
    ]

    for phrase in suspicious_phrases:
        if phrase.lower() in transcription.lower():
            return True, f"Found AI marker: {phrase}"

    # Check for robotic/scripted repetition
    words = transcription.split()
    if len(words) > 50:
        unique_word_ratio = len(set(words)) / len(words)
        if unique_word_ratio < 0.3:
            return True, "Extremely repetitive language (scripted)"

    return False, None

def process_interview_response(interview_response_obj):
    """
    Main logic to evaluate a response.
    """
    # 1. Get LLM Evaluation (Mocked here, but structure remains the same)
    # In production, you'd call an LLM API here.
    llm_results = {
        "relevance": 8.0,
        "technical_depth": 7.0,
        "clarity": 9.0,
        "communication": 8.0,
        "feedback": "Good fundamental understanding, but lacked specific implementation details."
    }

    # 2. Check for suspicious patterns (Anti-cheating)
    cheating_flagged, cheating_reason = check_for_cheating(interview_response_obj.transcription)
    if cheating_flagged:
        interview_response_obj.is_suspicious = True
        interview_response_obj.cheating_flags = cheating_reason

    # 3. Calculate final score
    final_score = calculate_final_score(
        llm_results,
        interview_response_obj.tab_switch_count,
        cheating_flagged
    )

    # 4. Save results to object
    interview_response_obj.relevance_score = llm_results['relevance']
    interview_response_obj.technical_depth_score = llm_results['technical_depth']
    interview_response_obj.clarity_score = llm_results['clarity']
    interview_response_obj.communication_score = llm_results['communication']
    interview_response_obj.ai_feedback = llm_results['feedback']
    interview_response_obj.final_score = final_score
    interview_response_obj.save()

    return interview_response_obj
