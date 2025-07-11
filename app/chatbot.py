from datetime import date  # à mettre en haut du fichier si pas déjà importé

def get_top_results(query, index, model, articles, k=5, year_start=None, year_end=None):
    query_vector = model.encode([query])
    D, I = index.search(query_vector, k * 10)  # on élargit la recherche brute pour filtrer ensuite

    filtered = []
    for idx in I[0]:
        article = articles[idx]
        year_val = article.get("date_publication")

        #  Gérer le type de date correctement
        if isinstance(year_val, date):
            year = year_val.year
        elif isinstance(year_val, str) and year_val[:4].isdigit():
            year = int(year_val[:4])
        else:
            year = None

        #  Filtrage
        if year_start and year and year < int(year_start):
            continue
        if year_end and year and year > int(year_end):
            continue

        filtered.append(article)
        if len(filtered) == k:
            break

    return filtered
