#imports for bias detector
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
from transformers import pipeline
#imports for newsAPI
import requests
#imports for text summarizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
#get plain text from html
from bs4 import BeautifulSoup
#connects python to html page
from flask import Flask, render_template
tokenizer = AutoTokenizer.from_pretrained("d4data/bias-detection-model")
model = TFAutoModelForSequenceClassification.from_pretrained("d4data/bias-detection-model")


#classifier = pipeline('text-classification', model=model, tokenizer=tokenizer) # cuda = 0,1 based on gpu availability

def bias_score(summary):
    classifier = pipeline('text-classification', model=model, tokenizer=tokenizer) # cuda = 0,1 based on gpu availability
    result = classifier(summary)
    return result

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

url = ('https://newsapi.org/v2/top-headlines?'
       'country=us&'
       'apiKey=897e05902e254ca09ec68c4abb50d7ea')
response = requests.get(url)



if response.status_code == 200:
    data = response.json()
    articles = data['articles']
    articles_data = []  # Initialize the articles_data list
    counter = 0
    for article in articles:
        blocked_sources = ["Wall Street Journal"]
        # Check if the source is YouTube or any other video source
        if "youtube.com" in article['url']:
            continue  # Skip this article and proceed to the next one
        if article['source']['name'] in blocked_sources:
            continue
        # Extract relevant article information
        title = article['title']
        source = article['source']['name']
        published_at = article['publishedAt']
        article_url = article['url']
        #add url to list of top article urls
        article_summary = summarize_article(article_url)
        bias = bias_score(article_summary)
        # Create a dictionary to represent the article data
        article_data = {
            'title': title,
            'published_at': published_at,
            'summary': article_summary,
            'bias_score': bias_score(article_summary),  # Get the score from the bias_result
            'url': article_url,
            'image_url': 'article1.jpg'  # Replace this with the actual image URL if available
        }

        # Append the article_data dictionary to the articles_data list
        articles_data.append(article_data)
        # Print article information with a new line after each article
        #print("Title:", title)
        #print("Source:", source)
        #print("Published At:", published_at)
        #print("URL:", article_url)
        article_summary = summarize_article(article_url)
        #print("Summary:")
        #print(article_summary)
        #print(bias_score(article_summary))
        #print("\n")  # Add a new line after each article
        counter += 1
        #Stops at the 6 top articles
        if counter == 6:
            break
else:
    print("Request failed with status code:", response.status_code)


#Connecting to HTML File


# Your code to fetch data, summarize articles, and calculate bias scores goes here

# Dummy data for demonstration purposes
app = Flask(__name__)
@app.route('/')
def news_feed():
    return render_template('news_feed.html', articles=articles_data)

if __name__ == "__main__":
    app.run(debug=True)
