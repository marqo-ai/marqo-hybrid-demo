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

document.getElementById('toggle-sponsored').addEventListener('change', () => {
    performSearch();
});

document.getElementById('search_type').addEventListener('change', () => {
    performSearch();
});

document.getElementById('retrieval_method').addEventListener('change', () => {
    performSearch();
    const retrievalMethodValue = document.getElementById('retrieval_method').value;
    const alphaController = document.getElementById('alpha-controller');
    const rerankMethod = document.getElementById('ranking_method');
    if (retrievalMethodValue === 'disjunction') {
        rerankMethod.innerHTML = `<p>RRF</p>`;
        alphaController.classList.remove('hidden');
    } else if (retrievalMethodValue === 'tensor') {
        rerankMethod.innerHTML = `<p>Lexical</p>`;
        alphaController.classList.add('hidden');
    } else if (retrievalMethodValue === 'lexical') {
        rerankMethod.innerHTML = `<p>Tensor</p>`;
        alphaController.classList.add('hidden');
    }
});

document.getElementById('alpha').addEventListener('change', () => {
    performSearch();
});

document.getElementById('order_by').addEventListener('change', () => {
    performSearch();
});

async function getNumberOfDocuments() {
    const response = await fetch('/number_of_documents', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    });
    const data = await response.json();
    document.getElementById('total-documents').innerText = `Total Documents: ${data["numberOfDocuments"]}`;
}

async function performSearch() {
    const query = document.getElementById('query').value;
    const search_type = document.getElementById('search_type').value;
    const retrieval_method = document.getElementById('retrieval_method').value || null;
    const order_by = document.getElementById('order_by').value || null;
    let alpha = parseFloat(document.getElementById('alpha').value);
    if (alpha === undefined || alpha === null) {
        alpha = 0.5;
    }
    const loadingSpinner = document.getElementById('loading');
    const showSponsored = document.getElementById('toggle-sponsored').checked;

    loadingSpinner.style.display = 'block';

    const searchResponse = await fetch('/search', {
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

    const searchData = await searchResponse.json();

    loadingSpinner.style.display = 'none';

    if (showSponsored) {
        const sponsoredResponse = await fetch('/sponsored_search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query,
                search_type,
                auctionSpots: 3,
                retrieval_method,
                order_by,
                alpha
            })
        });

        const sponsoredData = await sponsoredResponse.json();
        displayResults(searchData.hits, sponsoredData.hits);
    } else {
        displayResults(searchData.hits);
    }
}

function displayResults(results, sponsoredResults = []) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';

    let insertedSponsored = false;

    results.forEach((result, index) => {
        if (!insertedSponsored && index >= 3 && sponsoredResults.length > 0) {
            sponsoredResults.forEach(sponsored => {
                const sponsoredItem = createResultItem(sponsored, true);
                resultsDiv.appendChild(sponsoredItem);
            });
            insertedSponsored = true;
        }
        const resultItem = createResultItem(result);
        resultsDiv.appendChild(resultItem);
    });

    if (!insertedSponsored && sponsoredResults.length > 0) {
        sponsoredResults.forEach(sponsored => {
            const sponsoredItem = createResultItem(sponsored, true);
            resultsDiv.appendChild(sponsoredItem);
        });
    }
}

function createResultItem(result, isSponsored = false) {
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

    if (isSponsored) {
        const sponsoredBadge = document.createElement('span');
        sponsoredBadge.className = 'sponsored-badge';
        sponsoredBadge.innerText = 'Sponsored';
        resultItem.appendChild(sponsoredBadge);
    }

    return resultItem;
}

function validateAlphaInput(input) {
    if (input.value < 0) input.value = 0;
    if (input.value > 1) input.value = 1;
}

// Initial load
getNumberOfDocuments();
