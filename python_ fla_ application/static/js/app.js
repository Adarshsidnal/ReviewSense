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

        try {
            const response = await fetch('/scrape', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: productUrl,
                    max_reviews: 100, // Default number of reviews to scrape
                }),
            });

            const result = await response.json();

            if (result.success) {
                const reviews = result.data;
                if (reviews.length === 0) {
                    reviewsContainer.innerHTML = '<p>No reviews found for this product.</p>';
                    return;
                }

                // Display reviews in the container
                let reviewsHtml = '<h3>Scraped Reviews:</h3><ul>';
                reviews.forEach((review) => {
                    reviewsHtml += `<li><strong>Rating:</strong> ${review.Rating || 'No Rating'}<br>`;
                    reviewsHtml += `<strong>Review:</strong> ${review.Review || 'No Review'}</li><hr>`;
                });
                reviewsHtml += '</ul>';
                reviewsContainer.innerHTML = reviewsHtml;
            } else {
                reviewsContainer.innerHTML = `<p>Error: ${result.message}</p>`;
            }
        } catch (error) {
            console.error('Error scraping reviews:', error);
            reviewsContainer.innerHTML = '<p>An error occurred while scraping reviews.</p>';
        }
    });
});
