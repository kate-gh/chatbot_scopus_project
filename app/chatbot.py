def get_top_results(query, index, model, articles, k=5):
    query_vector = model.encode([query])
    D, I = index.search(query_vector, k)
    return [articles[i] for i in I[0]]
