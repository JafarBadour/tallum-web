from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import random
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///words.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False)
    translation = db.Column(db.String(100), nullable=False)
    example_sentence = db.Column(db.Text, nullable=False)
    positive_score = db.Column(db.Integer, default=0)
    negative_score = db.Column(db.Integer, default=0)
    
    @property
    def net_score(self):
        return self.positive_score - self.negative_score

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/next-word')
def get_next_word():
    # Get word with lowest net score (positive - negative)
    words = Word.query.order_by(Word.positive_score - Word.negative_score).limit(10).all()
    if not words:
        return jsonify({'error': 'No words available'}), 404
    
    # Randomly select from the 10 lowest scoring words
    word = random.choice(words)
    return jsonify({
        'id': word.id,
        'word': word.word,
        'translation': word.translation,
        'example_sentence': word.example_sentence
    })

@app.route('/api/check-answer', methods=['POST'])
def check_answer():
    data = request.get_json()
    word_id = data.get('word_id')
    user_answer = data.get('answer', '').strip().lower()
    
    word = Word.query.get(word_id)
    if not word:
        return jsonify({'error': 'Word not found'}), 404
    
    correct_answer = word.translation.lower()
    is_correct = user_answer == correct_answer
    
    if is_correct:
        word.positive_score += 1
        word.negative_score = max(0, word.negative_score // 2)
    else:
        word.negative_score += 1
        word.positive_score = max(0, word.positive_score // 2)
    
    db.session.commit()
    
    return jsonify({
        'correct': is_correct,
        'correct_answer': word.translation,
        'positive_score': word.positive_score,
        'negative_score': word.negative_score,
        'net_score': word.net_score
    })

@app.route('/api/get-sentence/<int:word_id>')
def get_sentence(word_id):
    word = Word.query.get(word_id)
    if not word:
        return jsonify({'error': 'Word not found'}), 404
    
    return jsonify({
        'example_sentence': word.example_sentence
    })

@app.route('/api/stats')
def get_stats():
    total_words = Word.query.count()
    avg_positive = db.session.query(db.func.avg(Word.positive_score)).scalar() or 0
    avg_negative = db.session.query(db.func.avg(Word.negative_score)).scalar() or 0
    
    return jsonify({
        'total_words': total_words,
        'average_positive_score': round(avg_positive, 2),
        'average_negative_score': round(avg_negative, 2)
    })

def init_db():
    with app.app_context():
        db.create_all()
        
        # Check if we already have words
        if Word.query.count() == 0:
            # Sample words data (you can expand this to 1000 words)
            sample_words = [
                {'word': 'bonjour', 'translation': 'hello', 'example_sentence': 'Bonjour, comment allez-vous?'},
                {'word': 'merci', 'translation': 'thank you', 'example_sentence': 'Merci beaucoup pour votre aide.'},
                {'word': 'au revoir', 'translation': 'goodbye', 'example_sentence': 'Au revoir, à bientôt!'},
                {'word': 'oui', 'translation': 'yes', 'example_sentence': 'Oui, je comprends.'},
                {'word': 'non', 'translation': 'no', 'example_sentence': 'Non, je ne sais pas.'},
                {'word': 's\'il vous plaît', 'translation': 'please', 'example_sentence': 'S\'il vous plaît, aidez-moi.'},
                {'word': 'excusez-moi', 'translation': 'excuse me', 'example_sentence': 'Excusez-moi, où est la gare?'},
                {'word': 'je ne comprends pas', 'translation': 'i don\'t understand', 'example_sentence': 'Je ne comprends pas cette phrase.'},
                {'word': 'parlez-vous anglais', 'translation': 'do you speak english', 'example_sentence': 'Parlez-vous anglais?'},
                {'word': 'combien ça coûte', 'translation': 'how much does it cost', 'example_sentence': 'Combien ça coûte ce livre?'}
            ]
            
            for word_data in sample_words:
                word = Word(**word_data)
                db.session.add(word)
            
            db.session.commit()
            print("Database initialized with sample words!")

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 