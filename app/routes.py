from flask import Blueprint, render_template, request, session, send_file, redirect, url_for
from app.faiss_index import build_index
from app.chatbot import get_top_results
from app.db import get_connection
import pdfkit
import os
from io import BytesIO
from datetime import datetime

bp = Blueprint('main', __name__)
index, articles, model = build_index()

# 🔁 Fonction utilitaire : charger l'historique de l'utilisateur
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
    if not user:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        question = request.form['question']
        year_start = request.form.get('year_start')
        year_end = request.form.get('year_end')

        response_data = get_top_results(
            question, index, model, articles,
            year_start=year_start,
            year_end=year_end
        )

        response_text = "\n\n".join([
            f"📝 {res.get('titre', 'Titre inconnu')}\n📜 {res.get('resume', 'Résumé indisponible')}"
            for res in response_data
        ])

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
            print("Erreur lors de l'enregistrement du message:", e)

    # 🔄 On charge toujours depuis la base
    history = get_user_history(user['id'])
    return render_template('index.html', history=history, user=user)

# 📥 Téléchargement d'une seule réponse
@bp.route('/download/<int:msg_id>')
def download_pdf(msg_id):
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))

    history = get_user_history(user['id'])

    if msg_id >= len(history):
        return "Message non trouvé", 404

    msg = history[msg_id]
    question = msg['user']
    response = msg['bot'].replace('\n', '<br>')

    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; }}
        </style>
    </head>
    <body>
        <h2>Question :</h2><p>{question}</p>
        <h2>Réponse :</h2><p>{response}</p>
    </body>
    </html>
    """

    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    pdf_bytes = pdfkit.from_string(html, False, configuration=config)
    pdf_file = BytesIO(pdf_bytes)

    return send_file(pdf_file, download_name="reponse.pdf", as_attachment=True)

# 📄 Téléchargement de toute la discussion
@bp.route('/download-all')
def download_all_pdf():
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))

    history = get_user_history(user['id'])
    if not history:
        return "Aucune discussion trouvée", 404

    # Contenu HTML structuré avec UTF-8
    body = ""
    for i, msg in enumerate(history):
        question = msg['user']
        reponse = msg['bot'].replace('\n', '<br>')
        body += f"""
            <h3>Message {i+1}</h3>
            <p><strong>Question:</strong> {question}</p>
            <p><strong>Réponse:</strong><br>{reponse}</p>
            <hr>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; }}
            h3 {{ color: #2c3e50; }}
            p {{ font-size: 14px; }}
        </style>
    </head>
    <body>
        <h1>Historique de discussion</h1>
        {body}
    </body>
    </html>
    """

    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    options = {
        'encoding': 'UTF-8'
    }
    pdf_bytes = pdfkit.from_string(html, False, configuration=config, options=options)
    pdf_file = BytesIO(pdf_bytes)

    return send_file(pdf_file, download_name="discussion_complete.pdf", as_attachment=True)
