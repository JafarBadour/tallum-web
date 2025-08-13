from app import app, db, Word
import json
# Sample dataset of 1000+ words (French to English)
# You can replace this with your own dataset or load from a CSV file


def clear_words_from_db():
    with app.app_context():
        Word.query.delete()
        db.session.commit()

def add_words_to_db():
    with app.app_context():
        # Check if words already exist
        existing_count = Word.query.count()
        print(f"Currently {existing_count} words in database")
        
        # Add new words
        added_count = 0
        for word_data in json.load(open('dutch_words.json')):
            # Check if word already exists
            existing_word = Word.query.filter_by(word=word_data['word']).first()
            if not existing_word:
                word = Word(**word_data)
                db.session.add(word)
                added_count += 1
        
        if added_count > 0:
            db.session.commit()
            print(f"Added {added_count} new words to database")
        else:
            print("No new words to add")
        
        total_count = Word.query.count()
        print(f"Total words in database: {total_count}")

if __name__ == '__main__':
    clear_words_from_db()
    add_words_to_db() 