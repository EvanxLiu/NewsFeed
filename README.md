

https://github.com/EvanxLiu/NewsFeed/assets/92675742/65c4eb2a-4405-47f6-bef9-e874f253fc7f

# NewsFeed
A news feed displaying summaries of the top articles in a region alongside a measure of its bias using NLP. 

This is a web application that fetches the top news articles from the US using the NewsAPI and performs bias detection on the article summaries. The bias detection is based on a pre-trained transformer model from the Hugging Face Transformers library. The app then displays the news articles along with an animated bias bar representing the bias score for each article.

Libraries Used
The following libraries were used in the development of this web app:

Flask: Flask is a micro web framework in Python that allows you to easily build web applications. It is used here to create the backend server that fetches news articles and serves the HTML templates.

Transformers (Hugging Face): Transformers is a library developed by Hugging Face that provides easy access to pre-trained NLP models. In this project, we use it to perform bias detection on the article summaries.

Requests: Requests is a popular Python library used for making HTTP requests. It is used here to fetch data from the NewsAPI and web articles.

BeautifulSoup: BeautifulSoup is a Python library used for parsing HTML and extracting data from web pages. It is used here to parse the article text from the HTML of the web articles.

Sumy: Sumy is a library for automatic text summarization in Python. It is used here to generate summaries of the fetched news articles.

Newspaper3k: Newspaper3k is a Python library used for extracting and parsing news articles from web pages. It is used here to extract the top image from each article for display.

**Setup and Running the App**
Install the required libraries by running pip install flask transformers requests beautifulsoup4 sumy newspaper3k.

Run the Python file and open your web browser and go to http://127.0.0.1:5000/ to access the News Bias Detection web app.

Currently working on UI
