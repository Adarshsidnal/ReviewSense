document.addEventListener('DOMContentLoaded', () => {
    const scrapeButton = document.getElementById('scrape-button');
    const reviewsContainer = document.getElementById('reviews-container');

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
            let summaryHtml = '<h3>Review Summaries:</h3>';

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
