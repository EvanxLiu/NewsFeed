#imports for bias detector
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
from transformers import pipeline
#imports for newsAPI
import requests
#imports for text summarizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
#get plain text hhtml code of website
from bs4 import BeautifulSoup
#connects python to html page
from flask import Flask, render_template
#bias detector intializer
tokenizer = AutoTokenizer.from_pretrained("d4data/bias-detection-model")
model = TFAutoModelForSequenceClassification.from_pretrained("d4data/bias-detection-model")
#get images from article
from newspaper import Article
#Gets text and gives a bias score from 0-1
def bias_score(summary):
    classifier = pipeline('text-classification', model=model, tokenizer=tokenizer) 
    result = classifier(summary)
    return result

#Bias score 
def split_text(text, max_segment_length=512):
    segments = []
    words = text.split()
    current_segment = ""
    for word in words:
        if len(current_segment) + len(word) + 1 <= max_segment_length:
            current_segment += word + " "
        else:
            segments.append(current_segment.strip())
            current_segment = word + " "
    segments.append(current_segment.strip())
    return segments
#summarizes text it sees on a website given its url
def summarize_article(url, num_sentences=7):
    # Fetch the article content using requests
    response = requests.get(url)
    article_text = response.text

    #beautifulsoup4 library parses html to only get text
    soup = BeautifulSoup(article_text, 'html.parser')
    article_text = ' '.join([p.text for p in soup.find_all('p')])

    # Initialize the summarizer
    summarizer = LexRankSummarizer()
    parser = PlaintextParser.from_string(article_text, Tokenizer('english'))

    # Get the summary with the specified number of sentences
    summary = summarizer(parser.document, num_sentences)
    return ' '.join([str(sentence) for sentence in summary])

#this gets the top articles of the day from the US
url = ('https://newsapi.org/v2/top-headlines?'
       'country=us&'
       'apiKey=897e05902e254ca09ec68c4abb50d7ea')
response = requests.get(url)

#gets a url and finds an image from it to put as a thumbnail
def extract_image_url(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.top_image
    except:
        print("Error while extracting image URL from the article.")
        return None

if response.status_code == 200:
    data = response.json()
    articles = data['articles']
    articles_data = []  
    counter = 0
    for article in articles:
        #Paywalled sites
        blocked_sources = ["Wall Street Journal"]
        # Check if the source is YouTube
        if "youtube.com" in article['url']:
            continue  # Skip this article and proceed to the next one
        if article['source']['name'] in blocked_sources:
            continue
        # Extract relevant article information
        title = article['title'] 
        source = article['source']['name'] 
        published_at = article['publishedAt']
        article_url = article['url']
        article_image_url = extract_image_url(article_url)
        article_summary = summarize_article(article_url)
        bias = bias_score(article_summary)

        # Create a dictionary to represent the article data
        article_data = {
            'title': title,
            'published_at': published_at,
            'summary': article_summary,
            'bias_score': bias_score(article_summary),  
            'url': article_url,
            'image_url': article_image_url
        }
        if not article_summary or len(article_summary.split('.')) < 5:
            print("Skipped article due to empty or short summary.")
            continue
        # Append the article_data dictionary to the articles_data list
        articles_data.append(article_data)
        counter += 1
        #Stops at the 6 top articles
        if counter == 6:
            break
else:
    print("Request failed with status code:", response.status_code)


#Connecting to HTML File


app = Flask(__name__)
@app.route('/')
def news_feed():
    return render_template('news_feed.html', articles=articles_data)

if __name__ == "__main__":
    app.run(debug=True)
