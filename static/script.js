/**
 * @typedef {Object} SearchResult
 * @property {string} _id
 * @property {string} main_category
 * @property {string} title
 * @property {string} store
 * @property {Array<string>} features
 * @property {number} average_rating
 * @property {number} rating_number
 * @property {number} price
 * @property {string} details
 * @property {string} product_image
 * @property {number} _score
 */

document.getElementById('search-btn').addEventListener('click', async () => {
    const query = document.getElementById('query').value;
    const search_type = document.getElementById('search_type').value;
    const retrieval_method = document.getElementById('retrieval_method').value || null;
    const ranking_method = document.getElementById('ranking_method').value || null;
    const order_by = document.getElementById('order_by').value || null;
    const alpha = parseFloat(document.getElementById('alpha').value) || 0.5;

    const response = await fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            query,
            search_type,
            retrieval_method,
            ranking_method,
            order_by,
            alpha
        })
    });

    const data = await response.json();
    displayResults(data.hits);
});

/**
 * Display search results in the results div
 * @param {Array<SearchResult>} results 
 */
function displayResults(results) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';

    results.forEach(result => {
        const resultItem = document.createElement('div');
        resultItem.className = 'result-item';

        const details = document.createElement('div');
        details.className = 'details';

        const img = document.createElement('img');
        img.src = result.product_image;
        details.appendChild(img);

        const info = document.createElement('div');
        info.innerHTML = `<h3>${result.title}</h3>
                          <p>Store: ${result.store}</p>
                          <p>Rating: ${result.average_rating} (${result.rating_number} reviews)</p>
                          <p>Price: $${result.price}</p>`;
        details.appendChild(info);

        resultItem.appendChild(details);
        resultsDiv.appendChild(resultItem);
    });
}
