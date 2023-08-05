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
from flask import Flask, jsonify, render_template
#bias detector intializer
tokenizer = AutoTokenizer.from_pretrained("d4data/bias-detection-model")
model = TFAutoModelForSequenceClassification.from_pretrained("d4data/bias-detection-model")
#get images from article
from newspaper import Article
#Gets text and gives a bias score from 0-1
def get_bias_score(summary):
    classifier = pipeline('text-classification', model=model, tokenizer=tokenizer)
    result = classifier([summary])  # Wrap the summary in a list

    # Get the label and score from the result
    label = result[0]['label']
    score = result[0]['score']

    # Check if the label is "BIASED" or "NON_BIASED" and calculate the biased_score accordingly
    if label == 'Biased':
        biased_score = score
    elif label == 'Non-biased':
        biased_score = 1.0 - score
    else:
        raise ValueError(f"Unexpected label: {label}")

    return biased_score


#Bias score has max length of 512, so will split longer texts into sections less than 512
def split_text(text, max_segment_length=512):
    segments = [] #segment array to store each portion less than 512
    words = text.split() #Separates text into words separated by a space 
    current_segment = "" #current segment goes through next words and adds them to a segment before adding them to a list
    for word in words:
        if len(current_segment) + len(word) + 1 <= max_segment_length: #Checks each time if it has exceeded limit
            current_segment += word + " " #adds next word
        else:
            segments.append(current_segment.strip()) #adds segments to list without any unnecessary starting/ending whitespace
            current_segment = word + " " #resets current_segment variable
    segments.append(current_segment.strip()) #adds segment that might be left over if it has not exceeded the 512 length
    return segments
#summarizes text it sees on a website given its url
def summarize_article(url, num_sentences=7):
    # Fetch the article content using requests
    response = requests.get(url)
    #response.text is the raw html code of the url
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
        article = Article(url) #Uses newspaper library, creating Article object from it
        article.download()
        article.parse()
        return article.top_image #After parsing through the article, returns the top image
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
        summary_segments = split_text(article_summary)
        bias = 0.0  # Initialize the bias score
        for segment in summary_segments:
            # Calculate the bias score for each segment and average the results
            bias_segment = get_bias_score(segment)
            bias += bias_segment
        bias /= len(summary_segments)  # Calculate the average bias score

        # Create a dictionary to represent the article data
        article_data = {
            'title': title,
            'published_at': published_at,
            'summary': article_summary,
            'bias_score': bias,  # Get the bias score
            'url': article_url,
            'image_url': article_image_url

        }
        if not article_summary or len(article_summary.split('.')) < 5: #prevents short summaries or possible paywalls
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
    for article in articles_data:
        article_summary = article['summary']
        article['bias_score'] = get_bias_score(article_summary)
    return render_template('news_feed.html', articles=articles_data)

@app.route('/articles_json')
def articles_json():
    return jsonify(articles=articles_data)
if __name__ == "__main__":
    app.run(debug=True)
