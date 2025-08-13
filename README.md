# Tallum - Foreign Word Learning Application

A Flask-based web application for learning foreign words with intelligent repetition based on user performance.

## Features

- **Smart Repetition**: Words are presented based on their learning score (positive - negative)
- **Interactive Learning**: Type translations and get immediate feedback
- **Hint System**: Show example sentences when you need help
- **Progress Tracking**: Visual feedback on word scores and overall statistics
- **Beautiful UI**: Modern, responsive design with smooth animations

## How It Works

1. **Word Selection**: The app selects words with the lowest net score (positive - negative)
2. **User Input**: You type the translation of the displayed word
3. **Scoring System**:
   - **Correct Answer**: Positive score +1, Negative score halved
   - **Incorrect Answer**: Negative score +1, Positive score halved
4. **Hints**: Click "Show Sentence" to see an example sentence with the word
5. **Progress**: Words you struggle with appear more frequently

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Navigate to the project directory**:
   ```bash
   cd tallum_web
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Add more words to the database** (optional):
   ```bash
   python add_words.py
   ```

5. **Open your browser** and go to:
   ```
   http://localhost:5000
   ```

## Database Structure

The application uses SQLite with the following schema:

```sql
CREATE TABLE word (
    id INTEGER PRIMARY KEY,
    word VARCHAR(100) NOT NULL,
    translation VARCHAR(100) NOT NULL,
    example_sentence TEXT NOT NULL,
    positive_score INTEGER DEFAULT 0,
    negative_score INTEGER DEFAULT 0
);
```

## API Endpoints

- `GET /` - Main application page
- `GET /api/next-word` - Get next word to learn
- `POST /api/check-answer` - Submit and check user answer
- `GET /api/get-sentence/<word_id>` - Get example sentence for a word
- `GET /api/stats` - Get learning statistics

## Customization

### Adding Your Own Words

1. **Edit the word list** in `add_words.py`
2. **Run the script** to add words to the database:
   ```bash
   python add_words.py
   ```

### Loading from CSV

You can modify `add_words.py` to load words from a CSV file:

```python
import csv

def load_words_from_csv(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            word_data = {
                'word': row['word'],
                'translation': row['translation'],
                'example_sentence': row['example_sentence']
            }
            # Add to database...
```

### Changing the Language

The current sample data is French to English. To change the language:

1. Update the sample words in `add_words.py`
2. Modify the UI text in `templates/index.html`
3. Update the application title and descriptions

## File Structure

```
tallum_web/
├── app.py              # Main Flask application
├── add_words.py        # Script to add words to database
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── templates/
│   └── index.html     # Main application template
└── words.db           # SQLite database (created automatically)
```

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in `app.py`:
   ```python
   app.run(debug=True, port=5001)
   ```

2. **Database errors**: Delete `words.db` and restart the application

3. **Import errors**: Make sure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

### Development

To run in development mode with auto-reload:
```bash
export FLASK_ENV=development
python app.py
```

## Contributing

Feel free to contribute by:
- Adding more words to the database
- Improving the UI/UX
- Adding new features like spaced repetition algorithms
- Supporting multiple languages
- Adding user accounts and progress tracking

## License

This project is open source and available under the MIT License. 