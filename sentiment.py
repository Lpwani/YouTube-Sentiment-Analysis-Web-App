# import nltk
# import matplotlib.pyplot as plt
# from nltk.corpus import stopwords
# from nltk.sentiment.vader import SentimentIntensityAnalyzer
# from nltk.stem import WordNetLemmatizer
# from wordcloud import WordCloud, STOPWORDS
# from utilities import CleanCache

# # nltk.download('vader_lexicon')
# # nltk.download('stopwords')
# # nltk.download('wordnet')

# wnl = WordNetLemmatizer()
# sia = SentimentIntensityAnalyzer()
# stop_words = stopwords.words('english')

# # def clean(org_comments):
# #     y = []
# #     for x in org_comments:
# #         x = x.split()
# #         x = [i.lower().strip() for i in x]
# #         x = [i for i in x if i not in stop_words]
# #         x = [i for i in x if len(i) > 2]
# #         x = [wnl.lemmatize(i) for i in x]
# #         y.append(' '.join(x))
# #     return y

# # def create_wordcloud(clean_reviews):
# #     for_wc = ' '.join(clean_reviews)
# #     wcstops = set(STOPWORDS)
# #     wc = WordCloud(width=1400, height=800, stopwords=wcstops, background_color='white').generate(for_wc)
# #     plt.figure(figsize=(20, 10), facecolor='k', edgecolor='k')
# #     plt.imshow(wc, interpolation='bicubic')
# #     plt.axis('off')
# #     plt.tight_layout()
# #     CleanCache(directory='static/images')
# #     plt.savefig('static/images/woc.png')
# #     plt.close()

# def returnsentiment(x):
#     score = sia.polarity_scores(x)['compound']

#     if score > 0:
#         sent = 'Positive'
#     elif score == 0:
#         sent = 'Negative'
#     else:
#         sent = 'Neutral'
#     return score, sent

import torch
from transformers import pipeline

sia = pipeline("sentiment-analysis")

def returnsentiment(x):
    result = sia(x)[0]
    score = result['score']
    
    if score > 0.75:
        sent = 'Positive'
    elif score < 0.6:
        sent = 'Negative'
    else:
        sent = 'Neutral'
    
    return score, sent
