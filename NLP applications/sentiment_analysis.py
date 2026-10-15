
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob

TEXT_COLUMN = "reviews.text"
RATING_COLUMN = "reviews.rating"
MODEL_NAME = "en_core_web_md"
DATASET_FILENAME = (
    "Datafiniti_Amazon_Consumer_Reviews_of_Amazon_Products_May19"
    ".csv"
)
NEGATION_WORDS = {"no", "not", "never", "none", "nor", "n't"}


def load_nlp_model() -> Any:
    try:
        nlp = spacy.load(MODEL_NAME)
    except OSError as error:
        message = (
            f"The required spaCy model '{MODEL_NAME}' is not installed.\n"
            f"Install it with: python -m spacy download {MODEL_NAME}"
        )
        raise RuntimeError(message) from error

    if "spacytextblob" not in nlp.pipe_names:
        try:
            nlp.add_pipe("spacytextblob")
        except ValueError as error:
            message = (
                "spacytextblob is not installed. Install it with: "
                "python -m pip install spacytextblob textblob"
            )
            raise RuntimeError(message) from error
    return nlp


def find_default_dataset() -> Path:
    script_folder = Path(__file__).resolve().parent
    possible_paths = (
        script_folder / DATASET_FILENAME,
        script_folder / DATASET_FILENAME / DATASET_FILENAME,
    )
    for path in possible_paths:
        if path.is_file():
            return path
    return possible_paths[0]


def load_reviews(csv_path: Path) -> pd.DataFrame:
    if not csv_path.is_file():
        raise FileNotFoundError(f"Dataset not found: {csv_path}")

    dataframe = pd.read_csv(csv_path, low_memory=False)
    if TEXT_COLUMN not in dataframe.columns:
        raise KeyError(
            f"Expected column '{TEXT_COLUMN}' was not found. "
            f"Available columns: {', '.join(dataframe.columns)}"
        )

    clean_data = dataframe.dropna(subset=[TEXT_COLUMN]).copy()
    clean_data[TEXT_COLUMN] = clean_data[TEXT_COLUMN].astype(str)
    clean_data = clean_data[clean_data[TEXT_COLUMN].str.strip().ne("")]
    return clean_data


def preprocess_review(review: str, nlp: Any) -> str:
    normalised_review = str(review).lower().strip()
    document = nlp(normalised_review)
    useful_tokens = [
        token.text
        for token in document
        if token.is_alpha
        and not token.is_space
        and (not token.is_stop or token.lower_ in NEGATION_WORDS)
    ]
    return " ".join(useful_tokens)


def label_polarity(polarity: float) -> str:
    if polarity > 0.05:
        return "Positive"
    if polarity < -0.05:
        return "Negative"
    return "Neutral"


def analyse_sentiment(review: str, nlp: Any) -> dict[str, Any]:
    cleaned_review = preprocess_review(review, nlp)
    if not cleaned_review:
        return {
            "cleaned_review": "",
            "polarity": 0.0,
            "sentiment": "Neutral",
        }

    document = nlp(cleaned_review)
    polarity = float(document._.blob.polarity)
    return {
        "cleaned_review": cleaned_review,
        "polarity": polarity,
        "sentiment": label_polarity(polarity),
    }


def compare_reviews(first_review: str, second_review: str, nlp: Any) -> float:
    first_cleaned = preprocess_review(first_review, nlp)
    second_cleaned = preprocess_review(second_review, nlp)
    if not first_cleaned or not second_cleaned:
        return 0.0
    return float(nlp(first_cleaned).similarity(nlp(second_cleaned)))


def rating_to_sentiment(rating: Any) -> str | None:
    if pd.isna(rating):
        return None
    rating_value = float(rating)
    if rating_value <= 2:
        return "Negative"
    if rating_value == 3:
        return "Neutral"
    if rating_value >= 4:
        return "Positive"
    return None


def evaluate_predictions(
    dataframe: pd.DataFrame, nlp: Any, sample_size: int
) -> pd.DataFrame:
    if RATING_COLUMN not in dataframe.columns:
        return pd.DataFrame()

    labelled_data = dataframe.dropna(subset=[RATING_COLUMN]).copy()
    evaluation_data = labelled_data.head(sample_size).copy()
    evaluation_data["expected_sentiment"] = evaluation_data[RATING_COLUMN].map(
        rating_to_sentiment
    )
    evaluation_data = evaluation_data.dropna(subset=["expected_sentiment"])
    evaluation_data["predicted_sentiment"] = evaluation_data[TEXT_COLUMN].map(
        lambda review: analyse_sentiment(review, nlp)["sentiment"]
    )
    return evaluation_data


def print_sample_results(dataframe: pd.DataFrame, nlp: Any) -> None:
    sample_reviews = dataframe[TEXT_COLUMN].head(3).tolist()
    print("\nSAMPLE SENTIMENT ANALYSIS")
    for number, review in enumerate(sample_reviews, start=1):
        result = analyse_sentiment(review, nlp)
        print(f"\nReview {number}: {review}")
        print(f"Cleaned review: {result['cleaned_review']}")
        print(f"Polarity score: {result['polarity']:.3f}")
        print(f"Predicted sentiment: {result['sentiment']}")

    if len(sample_reviews) >= 2:
        similarity = compare_reviews(sample_reviews[0], sample_reviews[1], nlp)
        print("\nREVIEW SIMILARITY")
        print(f"Reviews 1 and 2 similarity score: {similarity:.3f}")


def print_evaluation(evaluation_data: pd.DataFrame) -> None:
    if evaluation_data.empty:
        print("\nEVALUATION")
        print("No ratings were available, so proxy evaluation was skipped.")
        return

    accuracy = (
        evaluation_data["predicted_sentiment"]
        == evaluation_data["expected_sentiment"]
    ).mean()
    print("\nEVALUATION AGAINST STAR-RATING CLASSES")
    print(f"Reviews evaluated: {len(evaluation_data)}")
    print(f"Proxy accuracy: {accuracy:.1%}")
    print("\nPredicted sentiment counts:")
    print(evaluation_data["predicted_sentiment"].value_counts().to_string())


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--csv",
        type=Path,
        default=find_default_dataset(),
        help="Path to the Datafiniti CSV (found automatically when omitted).",
    )
    parser.add_argument(
        "--evaluate",
        type=int,
        default=100,
        help="Number of labelled reviews to evaluate (default: 100).",
    )
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    if arguments.evaluate < 1:
        raise ValueError("evaluate must be at least 1.")

    nlp = load_nlp_model()
    reviews = load_reviews(arguments.csv)
    print("DATASET SUMMARY")
    print(f"Dataset path: {arguments.csv}")
    print(f"Usable reviews after removing missing text: {len(reviews):,}")
    print_sample_results(reviews, nlp)
    evaluation = evaluate_predictions(reviews, nlp, arguments.evaluate)
    print_evaluation(evaluation)


if __name__ == "__main__":
    main()
