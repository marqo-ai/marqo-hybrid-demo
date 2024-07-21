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

document.getElementById('search-btn').addEventListener('click', performSearch);
document.getElementById('query').addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
        performSearch();
    }
});

document.getElementById('search_type').addEventListener('change', () => {
    const hybridOptions = document.getElementById('hybrid-options');
    const searchType = document.getElementById('search_type').value;
    if (searchType === 'hybrid') {
        hybridOptions.classList.remove('hidden');
    } else {
        hybridOptions.classList.add('hidden');
    }
});


/**
 * Validate inputs and make changes to selector status as needed
 * @param {string} retrievalMethod 
 */
function validateSelectors(retrievalMethod) {
    const rankingMethodSelector = document.getElementById('ranking_method');
    if (retrievalMethod === 'disjunction') {
        rankingMethodSelector.innerHTML = `<p>RRF</p>`;
    } else if (retrievalMethod === 'lexical') {
        rankingMethodSelector.innerHTML = `<p>Tensor</p>`;
    } else if (retrievalMethod === 'tensor') {
        rankingMethodSelector.innerHTML = `<p>Lexical</p>`;
    } 
}


document.getElementById('retrieval_method').addEventListener('change', () => {
    const retrievalMethod = document.getElementById('retrieval_method').value;
    validateSelectors(retrievalMethod);
});


async function performSearch() {
    const query = document.getElementById('query').value;
    const search_type = document.getElementById('search_type').value;
    const retrieval_method = document.getElementById('retrieval_method').value || null;
    const order_by = document.getElementById('order_by').value || null;
    const alpha = parseFloat(document.getElementById('alpha').value) || 0.5;
    const loadingSpinner = document.getElementById('loading');
    const searchTimeElement = document.getElementById('search-time');

    loadingSpinner.style.display = 'block';
    searchTimeElement.innerHTML = '';

    const startTime = Date.now();

    const response = await fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            query,
            search_type,
            retrieval_method,
            order_by,
            alpha
        })
    });

    const data = await response.json();
    const endTime = Date.now();
    const searchTime = endTime - startTime;

    loadingSpinner.style.display = 'none';
    searchTimeElement.innerHTML = `Search time: ${searchTime}ms`;

    displayResults(data.hits);
}

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

        const img = document.createElement('img');
        img.src = result.product_image;
        resultItem.appendChild(img);

        const info = document.createElement('div');
        info.innerHTML = `<h3>${result.title}</h3>
                          <p>Store: ${result.store}</p>
                          <p>Rating: ${result.average_rating} (${result.rating_number} reviews)</p>
                          <p>Price: $${result.price}</p>`;
        resultItem.appendChild(info);

        resultsDiv.appendChild(resultItem);
    });
}
