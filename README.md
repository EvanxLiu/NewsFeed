

https://github.com/EvanxLiu/NewsFeed/assets/92675742/65c4eb2a-4405-47f6-bef9-e874f253fc7f

# NewsFeed
A news feed displaying summaries of the top articles in a region alongside a measure of its bias using NLP. 

This is a web application that fetches the top news articles from the US using the NewsAPI and performs bias detection on the article summaries. The bias detection is based on a pre-trained model from the Hugging Face Transformers library. The app then uses flask and displays the news articles with a bias score for each article.

**Setup and Running the App**
Install the required libraries by running pip install flask transformers requests beautifulsoup4 sumy newspaper3k.

Run the Python file and open your web browser and go to http://127.0.0.1:5000/ to access the News Bias Detection web app.

Currently working on UI
