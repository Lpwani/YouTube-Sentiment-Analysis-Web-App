# import nltk
# import matplotlib.pyplot as plt
# from nltk.corpus import stopwords
# from nltk.sentiment.vader import SentimentIntensityAnalyzer
# from nltk.stem import WordNetLemmatizer
# from wordcloud import WordCloud, STOPWORDS
# from utilities import CleanCache

# nltk.download('vader_lexicon')
# nltk.download('stopwords')
# nltk.download('wordnet')

# wnl = WordNetLemmatizer()
# sia = SentimentIntensityAnalyzer()
# stop_words = stopwords.words('english')

# def clean(org_comments):
#     y = []
#     for x in org_comments:
#         x = x.split()
#         x = [i.lower().strip() for i in x]
#         x = [i for i in x if i not in stop_words]
#         x = [i for i in x if len(i) > 2]
#         x = [wnl.lemmatize(i) for i in x]
#         y.append(' '.join(x))
#     return y


import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from utilities import CleanCache

nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('wordnet')

wnl = WordNetLemmatizer()
sia = SentimentIntensityAnalyzer()
stop_words = set(stopwords.words('english'))
tokenizer = RegexpTokenizer(r'\w+')

def clean(org_comments):
    comments_series = pd.Series(org_comments)
    cleaned_comments = comments_series.apply(lambda x: ' '.join([wnl.lemmatize(token) for token in tokenizer.tokenize(x.lower()) if token not in stop_words and len(token) > 2]))
    return cleaned_comments.tolist()