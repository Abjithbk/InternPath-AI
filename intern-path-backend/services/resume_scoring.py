import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Strong verbs list
STRONG_VERBS = {
    "develop", "design", "implement", "engineer",
    "optimize", "build", "lead", "automate",
    "create", "reduce", "increase", "improve"
}

def normalize(value, min_val, max_val):
    if max_val == min_val:
        return 0
    return max(0, min((value - min_val) / (max_val - min_val), 1))


def process_text(text: str):
    return nlp(text)


def extract_linguistic_features(doc):

    tokens = [t for t in doc if not t.is_punct and not t.is_space]
    total_tokens = len(tokens)

    sentences = list(doc.sents)
    total_sentences = len(sentences)

    noun_count = 0
    verb_count = 0
    strong_verb_count = 0
    passive_count = 0
    impact_sentences = 0
    unique_lemmas = set()

    for sent in sentences:
        has_number = False
        has_strong_verb = False

        for token in sent:
            if token.pos_ == "NOUN":
                noun_count += 1

            if token.pos_ == "VERB":
                verb_count += 1
                if token.lemma_.lower() in STRONG_VERBS:
                    strong_verb_count += 1
                    has_strong_verb = True

            if token.dep_ == "auxpass":
                passive_count += 1

            if token.like_num or "%" in token.text:
                has_number = True

            if not token.is_stop:
                unique_lemmas.add(token.lemma_.lower())

        if has_number and has_strong_verb:
            impact_sentences += 1

    noun_ratio = noun_count / total_tokens if total_tokens else 0
    verb_ratio = verb_count / total_tokens if total_tokens else 0
    strong_verb_ratio = strong_verb_count / verb_count if verb_count else 0
    passive_ratio = passive_count / total_sentences if total_sentences else 0
    impact_density = impact_sentences / total_sentences if total_sentences else 0
    unique_lemma_ratio = len(unique_lemmas) / total_tokens if total_tokens else 0
    avg_sentence_length = total_tokens / total_sentences if total_sentences else 0
    entity_density = len(doc.ents) / total_tokens if total_tokens else 0

    return {
        "noun_ratio": noun_ratio,
        "verb_ratio": verb_ratio,
        "strong_verb_ratio": strong_verb_ratio,
        "passive_ratio": passive_ratio,
        "impact_density": impact_density,
        "unique_lemma_ratio": unique_lemma_ratio,
        "avg_sentence_length": avg_sentence_length,
        "entity_density": entity_density
    }


def analyze_resume_text(text: str):

    doc = process_text(text)
    features = extract_linguistic_features(doc)

    # Normalize features
    noun_ratio = normalize(features["noun_ratio"], 0.05, 0.30)
    verb_ratio = normalize(features["verb_ratio"], 0.05, 0.20)
    strong_verb_ratio = normalize(features["strong_verb_ratio"], 0.10, 0.60)
    impact_density = normalize(features["impact_density"], 0.0, 0.50)
    unique_lemma_ratio = normalize(features["unique_lemma_ratio"], 0.20, 0.70)
    entity_density = normalize(features["entity_density"], 0.01, 0.15)
    avg_sentence_length = normalize(features["avg_sentence_length"], 10, 25)
    passive_ratio = 1 - normalize(features["passive_ratio"], 0.0, 0.30)

    # Section scores
    skills_score = (
        0.40 * noun_ratio +
        0.35 * unique_lemma_ratio +
        0.25 * entity_density
    ) * 100

    projects_score = (
        0.30 * impact_density +
        0.40 * strong_verb_ratio +
        0.30 * verb_ratio
    ) * 100

    education_score = (
        0.60 * entity_density +
        0.40 * noun_ratio
    ) * 100

    ats_score = (
        0.40 * avg_sentence_length +
        0.35 * passive_ratio +
        0.25 * unique_lemma_ratio
    ) * 100

    # Overall weighted score
    overall_score = (
        0.30 * skills_score +
        0.30 * projects_score +
        0.20 * education_score +
        0.20 * ats_score
    )

    overall_score = round(overall_score)
    grade = "A" if overall_score >= 85 else "B" if overall_score >= 70 else "C"

    return {
        "overall_score": overall_score,
        "grade": grade,
        "section_scores": {
            "skills": round(skills_score),
            "projects": round(projects_score),
            "education": round(education_score),
            "ats_formatting": round(ats_score)
        },
        "linguistic_features": {k: round(v, 3) for k, v in features.items()}
    }