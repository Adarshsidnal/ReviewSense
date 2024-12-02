//document.getElementById('scrape-button').addEventListener('click', function () {
//    // Simulate fetching data (replace with actual scraping logic)
//    const sentimentData = { positive: 70, negative: 30 };
//    const ratingData = [50, 30, 10, 5, 5]; // Example rating percentages
//
//    // Create sentiment chart
//    new Chart(document.getElementById('sentiment-chart'), {
//        type: 'pie',
//        data: {
//            labels: ['Positive', 'Negative'],
//            datasets: [{
//                data: [sentimentData.positive, sentimentData.negative],
//                backgroundColor: ['#4CAF50', '#F44336']
//            }]
//        }
//    });
//
//    // Create rating chart
//    new Chart(document.getElementById('rating-chart'), {
//        type: 'pie',
//        data: {
//            labels: ['5 Stars', '4 Stars', '3 Stars', '2 Stars', '1 Star'],
//            datasets: [{
//                data: ratingData,
//                backgroundColor: ['#FFD700', '#C0C0C0', '#CD7F32', '#808080', '#FF4500']
//            }]
//        }
//    });
//});


document.addEventListener('DOMContentLoaded', () => {
    const scrapeButton = document.getElementById('scrape-button');
    const reviewsContainer = document.getElementById('reviews-container');
    const sentimentDiv=document.getElementById('sentiment');
    const ratingsDiv=document.getElementById('ratings');

    scrapeButton.addEventListener('click', async () => {
        const productUrl = document.getElementById('product_url').value.trim();

        if (!productUrl) {
            alert('Please enter a product URL.');
            return;
        }

        // Show loading message
        reviewsContainer.innerHTML = '<p>Loading reviews...</p>';
        console.log("HI");

        try {
            // Step 1: Scrape reviews
            const scrapeResponse = await fetch('/scrape', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: productUrl,
                    max_reviews: 100, // Default number of reviews to scrape
                }),
            });

            const scrapeResult = await scrapeResponse.json();

            if (!scrapeResult.success) {
                reviewsContainer.innerHTML = `<p>Error: ${scrapeResult.message}</p>`;
                return;
            }

            const reviews = scrapeResult.data;
            console.log(reviews);
            if (reviews.length === 0) {
                reviewsContainer.innerHTML = '<p>No reviews found for this product.</p>';
                return;
            }

            // Step 2: Analyze sentiments
            reviewsContainer.innerHTML = '<p>Analyzing sentiments...</p>';

            const analyzeResponse = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ reviews }),
            });

            const analyzeResult = await analyzeResponse.json();

            if (!analyzeResult.success) {
                reviewsContainer.innerHTML = `<p>Error during sentiment analysis: ${analyzeResult.message}</p>`;
                return;
            }

            const analyzedReviews = analyzeResult.data;
            console.log(analyzedReviews);

            reviewsContainer.innerHTML = '<p>Generating review analysis...</p>';

            const reviewAnalysisResponse = await fetch('/analyze_reviews', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ reviews: analyzedReviews })
            });

            const reviewAnalysisResult = await reviewAnalysisResponse.json();

            if (!reviewAnalysisResult.success) {
                reviewsContainer.innerHTML = `<p>Error during review analysis: ${reviewAnalysisResult.message}</p>`;
                return;
            }

            const { sentiment_counts, rating_counts } = reviewAnalysisResult.data;

            const sentimentDiv = document.getElementById('sentiment');
if (!sentimentDiv.querySelector('h3')) {
    const sentimentHeading = document.createElement('h3');
    sentimentHeading.textContent = 'Sentiment Analysis';
    sentimentHeading.style.textAlign = 'top'; // Optional: Center-align heading
    sentimentDiv.prepend(sentimentHeading); // Add heading above chart
}

            renderPieChart(
                'sentimentChart',
                ['Positive', 'Negative'],
                [sentiment_counts.positive, sentiment_counts.negative],
                ['#4CAF50', '#F44336'],
                'Sentiment Analysis'
            );

            const ratingDiv = document.getElementById('ratings');
            if (!ratingDiv.querySelector('h3')) {
                const ratingHeading = document.createElement('h3');
                ratingHeading.textContent = 'Rating Analysis';
                ratingHeading.style.textAlign = 'center'; // Optional: Center-align heading
                ratingDiv.prepend(ratingHeading); // Add heading above chart
            }
            // Rating Pie Chart
            renderPieChart(
                'ratingChart',
                ['5 Stars', '4 Stars', '3 Stars', '2 Stars', '1 Star'],
                [
                    rating_counts['5 stars'] || 0,
                    rating_counts['4 stars'] || 0,
                    rating_counts['3 stars'] || 0,
                    rating_counts['2 stars'] || 0,
                    rating_counts['1 star'] || 0
                ],
                ['#FFD700', '#C0C0C0', '#CD7F32', '#808080', '#FF4500'],
                'Rating Analysis'
            );

            // Step 3: Summarize reviews
            reviewsContainer.innerHTML = '<p>Summarizing reviews...</p>';

            const summarizeResponse = await fetch('/summarize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ reviews: analyzedReviews }),
            });

            const summarizeResult = await summarizeResponse.json();

            if (!summarizeResult.success) {
                reviewsContainer.innerHTML = `<p>Error during summarization: ${summarizeResult.message}</p>`;
                return;
            }

            const summaries = summarizeResult.data;
            console.log(summaries);
            console.log(summaries[0]);

            // Display summaries
            let summaryHtml = '<h3>Review Summaries</h3>';

            if (summaries.length > 0) {
                const firstSummary = summaries[0]; // Access the first object in the array
            
                if (firstSummary['Positive Summary']) {
                    summaryHtml += `<h4>Positive:</h4><p>${firstSummary['Positive Summary']}</p>`;
                } else {
                    summaryHtml += `<h4>Positive:</h4><p>No positive summary available.</p>`;
                }
            
                if (firstSummary['Negative Summary']) {
                    summaryHtml += `<h4>Negative:</h4><p>${firstSummary['Negative Summary']}</p>`;
                } else {
                    summaryHtml += `<h4>Negative:</h4><p>No negative summary available.</p>`;
                }
            } else {
                summaryHtml += `<p>No summaries available.</p>`;
            }
            
            reviewsContainer.innerHTML = summaryHtml;
            


        } catch (error) {
            console.error('Error processing reviews:', error);
            reviewsContainer.innerHTML = '<p>An error occurred while processing reviews.</p>';
        }
    });
});


function renderPieChart(chartId, labels, data, backgroundColors) {
    const ctx = document.getElementById(chartId).getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: backgroundColors
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}



