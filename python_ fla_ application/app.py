from flask import Flask, render_template, request, jsonify
import pandas as pd
from scraping_code import scrape_amazon_reviews
from bart_model_code import process_reviews  # Import summarization logic
import joblib

app = Flask(__name__)

# Load the logistic regression model and vectorizer
logreg_model = joblib.load('logreg_model.pkl')
vectorizer = joblib.load('vectorizer.pkl')

# Route to render the index.html page
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle scraping reviews
@app.route('/scrape', methods=['POST'])
def scrape_reviews():
    data = request.get_json()
    base_url = data.get('url')
    max_reviews = data.get('max_reviews', 100)
    
    try:
        # Call the scraping function
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
    reviews_list = data.get("reviews", [])
    

    try:
        df = pd.DataFrame(reviews_list)
        print(df)
        # print(df.columns)
    
        if 'Review' not in df.columns:
            return jsonify({'success': False, 'message': "'Review' column is missing."})

        # Apply sentiment analysis
        df['sentiment'] = df['Review'].apply(
            lambda Review: logreg_model.predict(vectorizer.transform([Review]))[0]
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
        # print(df)
        required_columns = {"Product Name", "Review", "sentiment"}
        if not required_columns.issubset(df.columns):
            return jsonify({'success': False, 'message': f'Missing required columns: {required_columns - set(df.columns)}'})

        # Summarize the reviews
        summarized_data = process_reviews(df)
        print(summarized_data)
        return jsonify({'success': True, 'data': summarized_data.to_dict(orient='records')})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/analyze_reviews', methods=['POST'])
def analyze_reviews():
    data = request.get_json()  # Get JSON data from the request
    reviews = data.get('reviews', [])  # Extract 'reviews' list

    if not reviews:
        return jsonify({'success': False, 'message': 'No reviews provided.'})

    try:
        # Convert reviews list into DataFrame
        df = pd.DataFrame(reviews)

        required_columns = {"Review", "sentiment", "Rating"}
        if not required_columns.issubset(df.columns):
            missing_columns = required_columns - set(df.columns)
            return jsonify({'success': False, 'message': f'Missing required columns: {missing_columns}'})

        print(df.columns)
        # Count positive and negative sentiments
        sentiment_counts = df['sentiment'].value_counts().to_dict()
        print(sentiment_counts)
        # Count star ratings (1-5 stars)
        rating_counts = df['Rating'].value_counts().to_dict()
        print(rating_counts)
        # Prepare the summarized data
        summarized_data = {
            'sentiment_counts': {
                'positive': sentiment_counts.get('positive', 0),
                'negative': sentiment_counts.get('negative', 0)
            },
            'rating_counts': {
                '5 stars': rating_counts.get('5.0', 0),
                '4 stars': rating_counts.get('4.0', 0),
                '3 stars': rating_counts.get('3.0', 0),
                '2 stars': rating_counts.get('2.0', 0),
                '1 star': rating_counts.get('1.0', 0)
            }
        }
        print(summarized_data)
        return jsonify({'success': True, 'data': summarized_data})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
