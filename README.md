# Enterprise Email Assistant

AI-powered email composition, analysis, and optimization using Hugging Face models. No API key required - uses free Hugging Face inference.

## Features

- **✍️ Email Composition**: Generate professional emails with customizable tones
- **😊 Sentiment Analysis**: Analyze emotional tone of emails
- **📝 Email Summarization**: Get concise summaries of long email threads
- **🧪 A/B Testing**: Generate two email variants to test performance
- **🎯 Tone Improvement**: Rewrite emails with different tones

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: Native HTML, CSS, JavaScript
- **AI Models**: Hugging Face Transformers
  - GPT-2: For email text generation
  - DistilBERT: For sentiment analysis
  - BART: For text summarization

All models are loaded from Hugging Face Hub with free inference.

## Project Structure

```
hf_email_assistant/
├── app.py              # Flask backend with API endpoints
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html     # HTML frontend
├── static/
│   ├── style.css      # CSS styling
│   └── app.js         # JavaScript for API calls
└── README.md
```

## Local Development

```bash
pip install -r requirements.txt
python app.py
```

The app will be available at http://localhost:5000

## API Endpoints

- `POST /api/compose` - Generate email
- `POST /api/sentiment` - Analyze sentiment
- `POST /api/summarize` - Summarize email
- `POST /api/abtest` - Generate A/B variants
- `POST /api/improve` - Improve email tone

## Requirements

- Python 3.8+
- flask >= 3.0.0
- transformers >= 4.30.0
- torch >= 2.0.0

## License

MIT License
