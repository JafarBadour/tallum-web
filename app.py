from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///words.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False)
    translation = db.Column(db.String(100), nullable=False)
    example_sentence = db.Column(db.Text, nullable=False)

class UserWord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), nullable=False)
    positive_score = db.Column(db.Integer, default=0, nullable=False)
    negative_score = db.Column(db.Integer, default=0, nullable=False)
    
    @property
    def net_score(self):
        return self.positive_score - self.negative_score
    
    # Relationship to get the word details
    word = db.relationship('Word', backref='user_words')

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')
        
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.id
        session['username'] = user.username
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/next-word')
def get_next_word():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    
    # Get words with lowest net score for this user
    # Use a subquery to get UserWord scores, defaulting to 0 if no score exists
    subquery = db.session.query(
        Word.id,
        db.func.coalesce(UserWord.positive_score, 0).label('positive_score'),
        db.func.coalesce(UserWord.negative_score, 0).label('negative_score')
    ).outerjoin(UserWord, db.and_(Word.id == UserWord.word_id, UserWord.user_id == user_id)).subquery()
    
    # Get words ordered by net score (positive - negative)
    words_with_scores = db.session.query(
        Word.id,
        Word.word,
        Word.translation,
        Word.example_sentence,
        subquery.c.positive_score,
        subquery.c.negative_score
    ).join(subquery, Word.id == subquery.c.id).order_by(
        subquery.c.positive_score - subquery.c.negative_score
    ).limit(10).all()
    
    if not words_with_scores:
        return jsonify({'error': 'No words available'}), 404
    
    # Randomly select from the 10 lowest scoring words
    word_data = random.choice(words_with_scores)
    return jsonify({
        'id': word_data.id,
        'word': word_data.word,
        'translation': word_data.translation,
        'example_sentence': word_data.example_sentence
    })

@app.route('/api/check-answer', methods=['POST'])
def check_answer():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json()
    word_id = data.get('word_id')
    user_answer = data.get('answer', '').strip().lower()
    user_id = session['user_id']
    
    word = Word.query.get(word_id)
    if not word:
        return jsonify({'error': 'Word not found'}), 404
    
    # Get or create UserWord record for this user and word
    user_word = UserWord.query.filter_by(user_id=user_id, word_id=word_id).first()
    if not user_word:
        user_word = UserWord(user_id=user_id, word_id=word_id, positive_score=0, negative_score=0)
        db.session.add(user_word)
    
    correct_answer = word.translation.lower()
    is_correct = user_answer == correct_answer
    
    if is_correct:
        user_word.positive_score = (user_word.positive_score or 0) + 1
        user_word.negative_score = max(0, (user_word.negative_score or 0) // 2)
    else:
        user_word.negative_score = (user_word.negative_score or 0) + 1
        user_word.positive_score = max(0, (user_word.positive_score or 0) // 2)
    
    db.session.commit()
    
    return jsonify({
        'correct': is_correct,
        'correct_answer': word.translation,
        'positive_score': user_word.positive_score,
        'negative_score': user_word.negative_score,
        'net_score': user_word.net_score
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
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    
    total_words = Word.query.count()
    
    # Count learned words for this user (positive score > 3)
    learned_words = UserWord.query.filter(
        UserWord.user_id == user_id,
        UserWord.positive_score >= 1.0
    ).count()
    
    # Calculate average scores for this user
    avg_positive = db.session.query(db.func.avg(UserWord.positive_score)).filter(
        UserWord.user_id == user_id
    ).scalar() or 0
    
    avg_negative = db.session.query(db.func.avg(UserWord.negative_score)).filter(
        UserWord.user_id == user_id
    ).scalar() or 0
    
    return jsonify({
        'total_words': total_words,
        'learned_words': learned_words,
        'average_positive_score': round(avg_positive, 2),
        'average_negative_score': round(avg_negative, 2)
    })

def init_db():
    with app.app_context():
        db.create_all()
        
        # Check if we already have words
        if Word.query.count() == 0:
            # Load words from dutch_words.json if it exists
            try:
                import json
                with open('dutch_words.json', 'r', encoding='utf-8') as f:
                    words_data = json.load(f)
                
                for word_data in words_data:
                    word = Word(
                        word=word_data['word'],
                        translation=word_data['translation'],
                        example_sentence=word_data['example_sentence']
                    )
                    db.session.add(word)
                
                db.session.commit()
                print(f"Database initialized with {len(words_data)} Dutch words!")
            except FileNotFoundError:
                print("dutch_words.json not found. Database initialized with empty word table.")
            except Exception as e:
                print(f"Error loading words: {e}")
                print("Database initialized with empty word table.")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000, host='0.0.0.0') 