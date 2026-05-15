import re
import math
import random
from collections import Counter
from typing import List, Dict, Tuple

import numpy as np
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "than", "to", "of", "in",
    "on", "for", "with", "as", "by", "from", "at", "is", "are", "was", "were",
    "be", "been", "being", "this", "that", "these", "those", "it", "its", "into",
    "can", "may", "might", "will", "would", "should", "could", "about", "between",
    "using", "used", "use", "such", "also", "each", "their", "there", "which",
    "when", "where", "what", "who", "how", "why", "not", "no", "yes", "do",
    "does", "did", "done", "has", "have", "had", "we", "you", "they", "he",
    "she", "i", "our", "your", "his", "her", "them", "more", "most", "some",
    "any", "many", "much", "one", "two", "first", "second", "new"
}


def extract_pdf_text(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    pages = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)

    clean_text = "\n".join(pages)
    clean_text = clean_text.replace("\x00", " ")
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    return clean_text


def split_sentences(text: str) -> List[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 35]
    return sentences


def get_keywords(text: str, top_n: int = 15) -> List[str]:
    words = re.findall(r"\b[A-Za-z][A-Za-z\-]{3,}\b", text.lower())
    words = [w for w in words if w not in STOPWORDS]

    counts = Counter(words)

    common = []
    for word, _ in counts.most_common(top_n * 3):
        if len(word) >= 4 and word not in common:
            common.append(word)
        if len(common) >= top_n:
            break

    return common


def generate_summary(text: str, max_sentences: int = 6) -> str:
    sentences = split_sentences(text)

    if not sentences:
        return "No readable lecture text was found. Try uploading a text-based PDF instead of a scanned image PDF."

    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(sentences)

    sentence_scores = np.asarray(matrix.sum(axis=1)).ravel()

    ranked_indices = sentence_scores.argsort()[::-1][:max_sentences]
    ranked_indices = sorted(ranked_indices)

    selected = [sentences[i] for i in ranked_indices]

    return " ".join(selected)


def extract_definition_candidates(text: str, max_items: int = 12) -> List[Dict[str, str]]:
    sentences = split_sentences(text)
    cards = []

    patterns = [
        r"(?P<term>[A-Z][A-Za-z\s\-]{2,40})\s+is\s+(?P<definition>[^.]{20,220})",
        r"(?P<term>[A-Z][A-Za-z\s\-]{2,40})\s+refers to\s+(?P<definition>[^.]{20,220})",
        r"(?P<term>[A-Z][A-Za-z\s\-]{2,40})\s+means\s+(?P<definition>[^.]{20,220})",
        r"(?P<term>[A-Z][A-Za-z\s\-]{2,40})\s+can be defined as\s+(?P<definition>[^.]{20,220})",
    ]

    seen = set()

    for sentence in sentences:
        for pattern in patterns:
            match = re.search(pattern, sentence)
            if match:
                term = match.group("term").strip()
                definition = match.group("definition").strip()

                term = re.sub(r"\s+", " ", term)
                definition = re.sub(r"\s+", " ", definition)

                if len(term.split()) > 6:
                    continue

                key = term.lower()
                if key not in seen:
                    seen.add(key)
                    cards.append(
                        {
                            "front": f"What is {term}?",
                            "back": definition.capitalize() + ".",
                            "topic": term.title()
                        }
                    )

        if len(cards) >= max_items:
            break

    return cards


def generate_flashcards(text: str, max_cards: int = 10) -> List[Dict[str, str]]:
    cards = extract_definition_candidates(text, max_items=max_cards)

    if len(cards) >= max_cards:
        return cards[:max_cards]

    keywords = get_keywords(text, top_n=max_cards)
    sentences = split_sentences(text)

    used_fronts = {card["front"].lower() for card in cards}

    for keyword in keywords:
        related_sentence = ""

        for sentence in sentences:
            if keyword.lower() in sentence.lower():
                related_sentence = sentence
                break

        if not related_sentence:
            continue

        front = f"What is the importance of {keyword.title()}?"
        if front.lower() in used_fronts:
            continue

        cards.append(
            {
                "front": front,
                "back": related_sentence[:280],
                "topic": keyword.title()
            }
        )

        used_fronts.add(front.lower())

        if len(cards) >= max_cards:
            break

    return cards


def generate_key_points(text: str, max_points: int = 7) -> List[str]:
    sentences = split_sentences(text)

    if not sentences:
        return ["No readable text found."]

    keywords = get_keywords(text, top_n=20)

    scored = []
    for sentence in sentences:
        score = 0
        lower_sentence = sentence.lower()

        for keyword in keywords:
            if keyword in lower_sentence:
                score += 1

        if any(marker in lower_sentence for marker in ["important", "main", "key", "therefore", "because", "defined", "means"]):
            score += 2

        scored.append((score, sentence))

    scored.sort(reverse=True, key=lambda x: x[0])
    points = [sentence for score, sentence in scored[:max_points]]

    return points


def generate_quiz(text: str, max_questions: int = 6) -> List[Dict]:
    keywords = get_keywords(text, top_n=30)
    sentences = split_sentences(text)

    questions = []
    used_answers = set()

    for keyword in keywords:
        if keyword in used_answers:
            continue

        source_sentence = None

        for sentence in sentences:
            if keyword.lower() in sentence.lower() and len(sentence.split()) >= 8:
                source_sentence = sentence
                break

        if not source_sentence:
            continue

        answer = keyword.title()
        used_answers.add(keyword)

        distractor_pool = [k.title() for k in keywords if k != keyword]
        random.shuffle(distractor_pool)

        options = [answer] + distractor_pool[:3]
        random.shuffle(options)

        blanked_sentence = re.sub(
            re.escape(keyword),
            "_____",
            source_sentence,
            flags=re.IGNORECASE
        )

        if "_____" not in blanked_sentence:
            continue

        question_text = f"Fill in the blank: {blanked_sentence}"

        questions.append(
            {
                "question": question_text,
                "options": options,
                "answer": answer,
                "topic": answer,
                "explanation": source_sentence
            }
        )

        if len(questions) >= max_questions:
            break

    return questions


def estimate_readiness(
    uploaded: bool,
    quiz_score: int | None,
    weak_topics_count: int,
    completed_topics: int,
    total_topics: int
) -> int:
    upload_score = 20 if uploaded else 0

    progress_score = 0
    if total_topics > 0:
        progress_score = int((completed_topics / total_topics) * 35)

    quiz_component = 20
    if quiz_score is not None:
        quiz_component = int((quiz_score / 100) * 35)

    weakness_penalty = min(weak_topics_count * 4, 20)

    readiness = upload_score + progress_score + quiz_component - weakness_penalty

    return max(0, min(100, readiness))


def answer_from_lecture(question: str, text: str, top_k: int = 3) -> str:
    sentences = split_sentences(text)

    if not text or not sentences:
        return (
            "I do not have lecture text yet. Upload a readable PDF first, then ask me questions from it."
        )

    corpus = sentences + [question]

    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(corpus)

    question_vector = matrix[-1]
    sentence_vectors = matrix[:-1]

    similarities = cosine_similarity(question_vector, sentence_vectors).ravel()
    top_indices = similarities.argsort()[::-1][:top_k]

    selected = []
    for idx in top_indices:
        if similarities[idx] > 0:
            selected.append(sentences[idx])

    if not selected:
        return (
            "I could not find a strong match in the uploaded lecture. Try asking using terms from the lecture."
        )

    answer = "Based on your uploaded lecture:\n\n"
    for sentence in selected:
        answer += f"- {sentence}\n"

    return answer


def build_study_plan(topics: List[str], days_left: int, hours_per_day: float) -> pd.DataFrame:
    if not topics:
        topics = ["Review uploaded lecture"]

    days = max(days_left, 1)
    total_slots = max(int(days * max(hours_per_day, 1)), 1)

    rows = []

    for day in range(1, days + 1):
        topic = topics[(day - 1) % len(topics)]

        if days_left <= 3:
            task = f"Crash review: focus on {topic}, flashcards, and quiz mistakes."
        else:
            task = f"Study {topic}, review summary, then test yourself."

        rows.append(
            {
                "Day": f"Day {day}",
                "Focus Topic": topic,
                "Recommended Task": task,
                "Study Time": f"{hours_per_day:g} hours"
            }
        )

    return pd.DataFrame(rows)


def detect_topics_from_text(text: str, max_topics: int = 6) -> List[str]:
    keywords = get_keywords(text, top_n=max_topics)
    topics = [keyword.title() for keyword in keywords]
    return topics if topics else ["General Review"]
