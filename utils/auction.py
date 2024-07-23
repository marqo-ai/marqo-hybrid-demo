from typing import List

def auction_spots_with_score(results: List[dict], n_spots: int) -> List[dict]:
    for res in results:
        res['rank_score'] = res['bid_amount'] * res['_score']
    
    results.sort(key=lambda x: x['rank_score'], reverse=True)
    
    top_sponsored = results[:n_spots]
    
    for i in range(len(top_sponsored) - 1):
        next_score = top_sponsored[i + 1]['_score']
        next_bid_amount = top_sponsored[i + 1]['bid_amount']
        current_score = top_sponsored[i]['_score']
        top_sponsored[i]['price_to_pay'] = (next_score * next_bid_amount) / current_score
    
    top_sponsored[-1]['price_to_pay'] = top_sponsored[-1]['bid_amount']
    
    final_results = top_sponsored
    
    return final_results