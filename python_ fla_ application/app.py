from flask import Flask, render_template, request, jsonify
import pandas as pd
from scraping_code import scrape_amazon_reviews  # Assuming scraping function is implemented here
from bart_model_code import process_reviews  # Assuming summarization function is implemented here
import joblib

app = Flask(__name__)

# Load the logistic regression model and vectorizer
logreg_model = joblib.load('logreg_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')

# Route to render the index.html page
@app.route('/')
def home():
    return render_template('index.html')  # Make sure index.html exists

# Route to handle scraping reviews
@app.route('/scrape', methods=['POST'])
def scrape_reviews():
    data = request.get_json()
    base_url = data.get('url')
    max_reviews = data.get('max_reviews', 100)

    try:
        # Call the scraping function (scrape_amazon_reviews)
        reviews_df = scrape_amazon_reviews(base_url, max_reviews=max_reviews)

        if not reviews_df.empty:
            # Convert the dataframe to dictionary format and return as JSON
            return jsonify({'success': True, 'data': reviews_df.to_dict(orient='records')})
        else:
            return jsonify({'success': False, 'message': 'No reviews found.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Route to handle sentiment analysis of the reviews
@app.route('/analyze', methods=['POST'])
def analyze_sentiments():
    data = request.get_json()
    reviews = data.get('reviews', [])

    if not reviews:
        return jsonify({'success': False, 'message': 'No reviews provided.'})

    try:
        df = pd.DataFrame(reviews)
        if 'review' not in df.columns:
            return jsonify({'success': False, 'message': "'review' column is missing."})

        # Apply sentiment analysis using Logistic Regression model
        df['sentiment'] = df['review'].apply(
            lambda review: logreg_model.predict(vectorizer.transform([review]))[0]
        )
        return jsonify({'success': True, 'data': df.to_dict(orient='records')})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Route to handle summarizing reviews
@app.route('/summarize', methods=['POST'])
def summarize_reviews():
    data = request.get_json()
    reviews = data.get('reviews', [])

    if not reviews:
        return jsonify({'success': False, 'message': 'No reviews provided.'})

    try:
        df = pd.DataFrame(reviews)
        required_columns = {"product_name", "review", "sentiment"}
        if not required_columns.issubset(df.columns):
            return jsonify({'success': False, 'message': f'Missing required columns: {required_columns - set(df.columns)}'})

        # Summarize the reviews using the summarization function (process_reviews)
        summarized_data = process_reviews(df)
        return jsonify({'success': True, 'data': summarized_data.to_dict(orient='records')})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
