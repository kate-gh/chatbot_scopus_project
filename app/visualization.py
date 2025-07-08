import plotly.graph_objs as go
from app.db import (
    get_publications_by_year,
    get_publications_by_domain,
    get_all_keywords
)
from collections import Counter

def generate_yearly_chart():
    df = get_publications_by_year()
    print("📊 Colonnes année chargées :", df.columns)
    fig = go.Figure(data=[
        go.Bar(
            x=df['year'],
            y=df['total'],
            marker_color='rgb(26, 118, 255)'
        )
    ])
    fig.update_layout(
        title='Nombre de publications par année',
        xaxis_title='Année',
        yaxis_title='Nombre de publications',
        template='plotly_white'
    )
    return fig.to_html(full_html=False)

def generate_domain_chart():
    df = get_publications_by_domain()
    fig = go.Figure(data=[
        go.Pie(
            labels=df['domaine_recherche'],
            values=df['total'],
            hole=0.4
        )
    ])
    fig.update_layout(
        title='Répartition des publications par domaine de recherche',
        template='plotly_white'
    )
    return fig.to_html(full_html=False)

def generate_keywords_chart(top_n=10):
    keywords = get_all_keywords()
    counter = Counter(keywords)
    most_common = counter.most_common(top_n)

    labels = [item[0] for item in most_common]
    values = [item[1] for item in most_common]

    fig = go.Figure(data=[
        go.Bar(x=labels, y=values, marker_color='green')
    ])
    fig.update_layout(
        title=f'Top {top_n} mots-clés les plus fréquents',
        xaxis_title='Mot-clé',
        yaxis_title='Fréquence',
        template='plotly_white'
    )
    return fig.to_html(full_html=False)
