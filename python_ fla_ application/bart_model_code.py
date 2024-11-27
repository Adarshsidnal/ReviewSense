import pandas as pd
from transformers import pipeline

# Load the summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Function to summarize reviews dynamically
def summarize_reviews(reviews):
    """Summarizes reviews dynamically based on their combined length."""
    if not reviews:
        return "No reviews available."

    combined_reviews = " ".join(reviews)
    max_input_length = 1024  # BART model's max token limit

    # Adjust summary length dynamically based on the input length
    if len(combined_reviews) > max_input_length:
        combined_reviews = combined_reviews[:max_input_length]
        max_summary_length = 100
        min_summary_length = 50
    else:
        max_summary_length = 50
        min_summary_length = 20

    summary = summarizer(
        combined_reviews,
        max_length=max_summary_length,
        min_length=min_summary_length,
        do_sample=False
    )
    return summary[0]["summary_text"]

# Function to process and summarize reviews for each product
def process_reviews(dataframe):
    """
    Groups reviews by product and sentiment, then generates summaries.
    Input: Pandas DataFrame with columns: "Product Name", "Review", "Sentiment"
    Output: Summarized DataFrame with columns: "Product Name", "Positive Summary", "Negative Summary"
    """
    summarized_data = []

    grouped_data = dataframe.groupby("Product Name")
    for product, group in grouped_data:
        # Separate positive and negative reviews
        positive_reviews = group[group["sentiment"] == "positive"]["Review"].tolist()
        negative_reviews = group[group["sentiment"] == "negative"]["Review"].tolist()

        # Generate summaries
        positive_summary = summarize_reviews(positive_reviews)
        negative_summary = summarize_reviews(negative_reviews)

        # Append summarized results
        summarized_data.append({
            "Product Name": product,
            "Positive Summary": positive_summary,
            "Negative Summary": negative_summary,
        })

    return pd.DataFrame(summarized_data)

# Example usage (optional, remove in production):
if __name__ == "__main__":
    # Create a sample DataFrame
    data = pd.DataFrame({
        "Product Name": ["Product A", "Product A", "Product B", "Product B"],
        "Review": ["Great product!", "Works well!", "Not good.", "Terrible experience!"],
        "Sentiment": ["positive", "positive", "negative", "negative"]
    })

    summarized_data = process_reviews(data)
    print(summarized_data)
