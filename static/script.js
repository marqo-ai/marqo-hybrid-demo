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

// document.getElementById('search-btn').addEventListener('click', performSearch);
// document.getElementById('query').addEventListener('keydown', (event) => {
//     if (event.key === 'Enter') {
//         performSearch();
//     }
// });

// document.getElementById('search_type').addEventListener('change', () => {
//     const hybridOptions = document.getElementById('hybrid-options');
//     const searchType = document.getElementById('search_type').value;
//     if (searchType === 'hybrid') {
//         hybridOptions.classList.remove('hidden');
//     } else {
//         hybridOptions.classList.add('hidden');
//     }
// });


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

// async function getNumberOfDocuments() {
//     const response = await fetch('/number_of_documents', {
//         method: 'GET', 
//         headers: { 'Content-Type': 'application/json' }
//     });
//     const data = await response.json();
// }

// async function performSearch() {
//     const query = document.getElementById('query').value;
//     const search_type = document.getElementById('search_type').value;
//     const retrieval_method = document.getElementById('retrieval_method').value || null;
//     const order_by = document.getElementById('order_by').value || null;
//     const alpha = parseFloat(document.getElementById('alpha').value) || 0.5;
//     const loadingSpinner = document.getElementById('loading');
//     const searchTimeElement = document.getElementById('search-time');

//     loadingSpinner.style.display = 'block';
//     searchTimeElement.innerHTML = '';

//     const searchResponse = await fetch('/search', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({
//             query,
//             search_type,
//             retrieval_method,
//             order_by,
//             alpha
//         })
//     });

//     const searchData = await searchResponse.json();
//     const searchTime = searchData["processingTimeMs"]

//     loadingSpinner.style.display = 'none';
//     searchTimeElement.innerHTML = `Search time: ${searchTime}ms`;

//     displayResults(searchData.hits);
// }

// /**
//  * Display search results in the results div
//  * @param {Array<SearchResult>} results 
//  */
// function displayResults(results) {
//     const resultsDiv = document.getElementById('results');
//     resultsDiv.innerHTML = '';

//     results.forEach(result => {
//         const resultItem = document.createElement('div');
//         resultItem.className = 'result-item';

//         const img = document.createElement('img');
//         img.src = result.product_image;
//         resultItem.appendChild(img);

//         const info = document.createElement('div');
//         info.innerHTML = `<h3>${result.title}</h3>
//                           <p>Store: ${result.store}</p>
//                           <p>Rating: ${result.average_rating} (${result.rating_number} reviews)</p>
//                           <p>Price: $${result.price}</p>`;
//         resultItem.appendChild(info);

//         resultsDiv.appendChild(resultItem);
//     });
// }

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
    const alpha = parseFloat(document.getElementById('alpha').value) || 0.5;
    const loadingSpinner = document.getElementById('loading');
    const searchTimeElement = document.getElementById('search-time');
    const showSponsored = document.getElementById('toggle-sponsored').checked;

    loadingSpinner.style.display = 'block';
    searchTimeElement.innerHTML = '';

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
    const searchTime = searchData["processingTimeMs"];

    loadingSpinner.style.display = 'none';
    searchTimeElement.innerHTML = `Search time: ${searchTime}ms`;

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

// Initial load
getNumberOfDocuments();
