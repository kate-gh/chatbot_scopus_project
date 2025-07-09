def get_top_results(query, index, model, articles, k=5, year_start=None, year_end=None):
    query_vector = model.encode([query])
    D, I = index.search(query_vector, k * 10)  # on élargit la recherche brute pour filtrer ensuite

    filtered = []
    for idx in I[0]:
        article = articles[idx]
        year_str = article.get("date_publication", "")[:4]
        if year_str.isdigit():
            year = int(year_str)
            if year_start and year < int(year_start):
                continue
            if year_end and year > int(year_end):
                continue
        filtered.append(article)
        if len(filtered) == k:
            break

    return filtered
