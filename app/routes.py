from flask import Blueprint, render_template, request, session, send_file, redirect, url_for
from app.faiss_index import build_index
from app.chatbot import get_top_results
from app.db import (
    get_connection,
    get_authors_by_article,
    get_publications_by_author,
    get_publications_by_domain,
    get_publications_by_country
)
import pdfkit
from io import BytesIO
from datetime import datetime
import plotly.graph_objs as go
import plotly.offline as opy

bp = Blueprint('main', __name__)
index, articles, model = build_index()

# 🔁 Historique depuis BDD
def get_user_history(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT question, response, created_at FROM messages WHERE user_id = %s ORDER BY created_at", (user_id,))
    history = [{
        'user': row['question'],
        'bot': row['response'],
        'time': row['created_at'].strftime('%Y-%m-%d %H:%M')
    } for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return history

# 🧠 Page principale du chatbot
@bp.route('/', methods=['GET', 'POST'])
def index_route():
    user = session.get('user')
    is_guest = user is None

    # On utilise un historique temporaire pour les invités
    if is_guest:
        if 'guest_history' not in session:
            session['guest_history'] = []

    if request.method == 'POST':
        question = request.form['question']
        year_start = request.form.get('year_start')
        year_end = request.form.get('year_end')
        author_filter = request.form.get('author_filter')

        try:
            response_data = get_top_results(
                question, index, model, articles,
                year_start=year_start,
                year_end=year_end
            )

            no_resume_keywords = [
                "sans résumé", "without abstract", "just title", "only title",
                "only titles", "titre seulement", "no abstract", "skip abstract"
            ]
            no_resume = any(keyword in question.lower() for keyword in no_resume_keywords)

            formatted = []
            for res in response_data:
                title = res.get('titre', 'Unknown title')
                date = res.get('date_publication', 'Unknown date')
                journal = res.get('revue', 'Unknown journal')
                doi = res.get('doi', '')
                abstract = res.get('resume', 'No abstract available')

                authors = get_authors_by_article(res.get('id'))
                authors_str = ", ".join(authors) if authors else "Unknown author"

                if author_filter and not any(author_filter.lower() in a.lower() for a in authors):
                    continue

                block = f"""<b>📝 Title:</b> {title}<br>
<b>👤 Authors:</b> {authors_str}<br>
<b>📅 Date:</b> {date}<br>
<b>📚 Journal:</b> {journal}"""

                if not no_resume:
                    block += f"<br><b>📜 Abstract:</b> {abstract}"
                if doi:
                    block += f"<br><b>🔗 DOI:</b> {doi}"

                formatted.append(block)

            response_text = "<b>🔎 Here are the most relevant articles:</b><br><br>" + "<br><br>".join(formatted) if formatted else "No articles matched your filters."

        except Exception as e:
            print("Error in get_top_results:", e)
            response_text = "An error occurred during the search."

        if is_guest:
            session['guest_history'].append({
                'user': question,
                'bot': response_text,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M')
            })
        else:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO messages (user_id, question, response) VALUES (%s, %s, %s)",
                    (user['id'], question, response_text)
                )
                conn.commit()
                cursor.close()
                conn.close()
            except Exception as e:
                print("Database save error:", e)

    if is_guest:
        history = session.get('guest_history', [])
    else:
        history = get_user_history(user['id'])

    return render_template('index.html', history=history, user=user or {'name': 'Invité'}, is_guest=is_guest)

# 📥 Télécharger une réponse
@bp.route('/download/<int:msg_id>')
def download_pdf(msg_id):
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))

    history = get_user_history(user['id'])
    if msg_id >= len(history):
        return "Message not found", 404

    msg = history[msg_id]
    question = msg['user']
    response = msg['bot'].replace('\n', '<br>')

    html = f"""
    <html>
    <head><meta charset="UTF-8"></head>
    <body>
        <h2>Question:</h2><p>{question}</p>
        <h2>Response:</h2><p>{response}</p>
    </body>
    </html>
    """
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    pdf_bytes = pdfkit.from_string(html, False, configuration=config)
    pdf_file = BytesIO(pdf_bytes)
    return send_file(pdf_file, download_name="response.pdf", as_attachment=True)

# 📄 Télécharger toute la discussion
@bp.route('/download-all')
def download_all_pdf():
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))

    history = get_user_history(user['id'])
    if not history:
        return "No history found", 404

    body = ""
    for i, msg in enumerate(history):
        question = msg['user']
        reponse = msg['bot'].replace('\n', '<br>')
        body += f"""
            <h3>Message {i+1}</h3>
            <p><strong>Question:</strong> {question}</p>
            <p><strong>Response:</strong><br>{reponse}</p>
            <hr>
        """

    html = f"""
    <html>
    <head><meta charset="utf-8"><style>body {{ font-family: Arial; }}</style></head>
    <body><h1>Chat History</h1>{body}</body></html>
    """

    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    options = {'encoding': 'UTF-8'}
    pdf_bytes = pdfkit.from_string(html, False, configuration=config, options=options)
    pdf_file = BytesIO(pdf_bytes)
    return send_file(pdf_file, download_name="full_chat.pdf", as_attachment=True)

# 📊 Visualisation des données
@bp.route('/visualizations')
def visualizations():
    df1 = get_publications_by_author()
    fig1 = go.Figure([go.Bar(x=df1['author'], y=df1['total'])])
    fig1.update_layout(title='Top 10 Authors by Publications', xaxis_title='Author', yaxis_title='Publications')
    graph1 = opy.plot(fig1, output_type='div')

    df2 = get_publications_by_domain()
    fig2 = go.Figure([go.Pie(labels=df2['domain'], values=df2['total'])])
    fig2.update_layout(title='Top Research Domains')
    graph2 = opy.plot(fig2, output_type='div')

    df3 = get_publications_by_country()
    fig3 = go.Figure([go.Bar(x=df3['country'], y=df3['total'])])
    fig3.update_layout(title='Publications by Country', xaxis_title='Country', yaxis_title='Publications')
    graph3 = opy.plot(fig3, output_type='div')

    return render_template('visualizations.html', graph1=graph1, graph2=graph2, graph3=graph3)


@bp.route('/discussions')
def discussions():
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, question, response, created_at FROM messages WHERE user_id = %s ORDER BY created_at DESC", (user['id'],))
    discussions = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('discussions.html', discussions=discussions, user=user)

@bp.route('/delete-message/<int:msg_id>', methods=['POST'])
def delete_message(msg_id):
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE id = %s AND user_id = %s", (msg_id, user['id']))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('main.discussions'))
