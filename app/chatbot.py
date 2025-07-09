def get_top_results(query, index, model, articles, year_start=None, year_end=None, k=5):
    query_vector = model.encode([query])
    D, I = index.search(query_vector, k * 5)  # élargir les résultats pour filtrage

    filtered = []
    for i in I[0]:
        article = articles[i]

        # Récupérer l’année
        year_str = article.get("date_publication") or article.get("prism:coverDate", "")
        year = int(year_str[:4]) if year_str and year_str[:4].isdigit() else None

        # Appliquer le filtre
        if year_start and year_end and year:
            if int(year_start) <= year <= int(year_end):
                filtered.append(article)
        else:
            filtered.append(article)

        if len(filtered) >= k:
            break

    return filtered
