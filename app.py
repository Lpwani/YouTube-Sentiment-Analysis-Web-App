# from flask import Flask, render_template, request, redirect, url_for, session
# from scraper import returnytcomments
# from sentiment import returnsentiment
# from utilities import CleanCache
# from preprocessing import clean
# from wordcloud1 import create_wordcloud
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

# app = Flask(__name__)
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# app.secret_key = 'vsw'

# # Define a variable to store result data globally
# result_data = None

# # Function to send email
# def send_email(receiver_email, subject, body):
#     sender_email = "nileshpandhare70@gmail.com"  # Enter your email
#     sender_password = "WWE@1234"  # Enter your email password

#     msg = MIMEMultipart()
#     msg['From'] = sender_email
#     msg['To'] = receiver_email
#     msg['Subject'] = subject

#     msg.attach(MIMEText(body, 'plain'))

#     try:
#         with smtplib.SMTP('smtp.gmail.com', 587) as server:
#             server.starttls()
#             server.login(sender_email, sender_password)
#             text = msg.as_string()
#             server.sendmail(sender_email, receiver_email, text)
#         print("Email sent successfully!")
#     except Exception as e:
#         print("Error sending email:", str(e))

# @app.route('/')
# def home():
#     return render_template('home.html')

# np1, nn1, nne1, n1, dic1 = 0, 0, 0, 0, 0

# @app.route('/results', methods=['GET'])
# def result():
#     global result_data  # Use the global variable
#     url = request.args.get('url')
#     receiver_email = request.args.get('email')  # Get user email from the form

#     org_comments = returnytcomments(url)
#     temp = [i for i in org_comments if 5 < len(i) <= 500]
#     org_comments = temp

#     clean_comments = clean(org_comments)

#     create_wordcloud(clean_comments)

#     np, nn, nne = 0, 0, 0

#     predictions = []
#     scores = []

#     for i in clean_comments:
#         score, sent = returnsentiment(i)
#         scores.append(score)
#         if sent == 'Positive':
#             predictions.append('POSITIVE')
#             np += 1
#         elif sent == 'Negative':
#             predictions.append('NEGATIVE')
#             nn += 1
#         else:
#             predictions.append('NEUTRAL')
#             nne += 1

#     dic = []

#     for i, cc in enumerate(clean_comments):
#         x = {}
#         x['sent'] = predictions[i]
#         x['clean_comment'] = cc
#         x['org_comment'] = org_comments[i]
#         x['score'] = scores
#         dic.append(x)

#     result_data = {
#         'n': len(clean_comments),
#         'nn': nn,
#         'np': np,
#         'nne': nne,
#         'dic': dic
#     }

#     # Construct email body
#     email_body = f"Number of comments analyzed: {len(clean_comments)}\n"
#     email_body += f"Number of positive comments: {np}\n"
#     email_body += f"Number of neutral comments: {nne}\n"
#     email_body += f"Number of negative comments: {nn}\n\n"

#     email_body += "Comments:\n"
#     for obj in dic:
#         email_body += f"Sentiment: {obj['sent']}\n"
#         email_body += f"Original Comment: {obj['org_comment']}\n\n"

#     # Send email to the user
#     send_email(receiver_email, "Analysis Result", email_body)

#     return render_template('result.html', n=len(clean_comments), nn=nn, np=np, nne=nne, dic=dic)

# @app.route('/wc')
# def wc():
#     return render_template('wc.html')

# @app.route('/visualization')
# def visualization():
#     global result_data  # Use the global variable

#     # If data exists, pass it to the template, otherwise provide default values
#     if result_data:
#         n = result_data['n']
#         nn = result_data['nn']
#         np = result_data['np']
#         nne = result_data['nne']
#         dic = result_data['dic']
#     else:
#         n, nn, np, nne, dic = 0, 0, 0, 0, []

#     # Render the visualization.html template
#     return render_template('visualization.html', n=n, nn=nn, np=np, nne=nne, dic=dic)

# if __name__ == '__main__':
#     app.run(debug=True)








# from flask import Flask, render_template, request, redirect, url_for, session
# from flask_mail import Mail, Message
# from scraper import returnytcomments
# from sentiment import returnsentiment
# from utilities import CleanCache
# from preprocessing import clean
# from wordcloud1 import create_wordcloud
# from random_forest_model import RandomForestSentimentClassifier

# app = Flask(__name__)
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# app.secret_key = 'vsw'

# # Configure mail settings
# app.config['MAIL_SERVER'] = 'smtp.googlemail.com'  # Your SMTP server
# app.config['MAIL_PORT'] = 587  # Port for TLS/STARTTLS
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = 'nileshpandhare70@gmail.com'  # Your email address
# app.config['MAIL_PASSWORD'] = 'ubez ymkr kfin futo'  # Your email password

# mail = Mail(app)

# # Define a variable to store result data globally
# result_data = None

# # Initialize the random forest classifier
# rf_classifier = RandomForestSentimentClassifier()

# @app.route('/')
# def home():
#     return render_template('home.html')

# np1, nn1, nne1, n1, dic1 = 0, 0, 0, 0, 0

# @app.route('/results', methods=['GET'])
# def result():
#     global result_data  # Use the global variable
#     url = request.args.get('url')
#     user_email = request.args.get('email')  # Get the user's email

#     org_comments = returnytcomments(url)
#     temp = [i for i in org_comments if 5 < len(i) <= 500]
#     org_comments = temp

#     clean_comments = clean(org_comments)

#     create_wordcloud(clean_comments)

#     np, nn, nne = 0, 0, 0

#     predictions = []
#     scores = []

#     for i in clean_comments:
#         score, sent = returnsentiment(i)
#         scores.append(score)
#         if sent == 'Positive':
#             predictions.append('POSITIVE')
#             np += 1
#         elif sent == 'Negative':
#             predictions.append('NEGATIVE')
#             nn += 1
#         else:
#             predictions.append('NEUTRAL')
#             nne += 1

#     dic = []

#     for i, cc in enumerate(clean_comments):
#         x = {}
#         x['sent'] = predictions[i]
#         x['clean_comment'] = cc
#         x['org_comment'] = org_comments[i]
#         x['score'] = scores
#         dic.append(x)
   
#     result_data = {
#         'n': len(clean_comments),
#         'nn': nn,
#         'np': np,
#         'nne': nne,
#         'dic': dic
#     }

#     # Train random forest model
#     X_train = clean_comments
#     y_train = predictions
#     rf_classifier.train(X_train, y_train)

#     # Send email with analysis result
#     send_email(user_email, result_data)

#     return render_template('result.html', n=len(clean_comments), nn=nn, np=np, nne=nne, dic=dic)

# def send_email(email, result_data):
#     msg = Message(subject="Youtube Video Comments Sentiment Analysis Result",
#                   sender=app.config['MAIL_USERNAME'],
#                   recipients=[email])
#     msg.html = render_template("email_template.html", result_data=result_data)
#     mail.send(msg)

# @app.route('/wc')
# def wc():
#     return render_template('wc.html')

# @app.route('/visualization')
# def visualization():
#     global result_data  # Use the global variable

#     # If data exists, pass it to the template, otherwise provide default values
#     if result_data:
#         n = result_data['n']
#         nn = result_data['nn']
#         np = result_data['np']
#         nne = result_data['nne']
#         dic = result_data['dic']
#     else:
#         n, nn, np, nne, dic = 0, 0, 0, 0, []

#     # Render the visualization.html template
#     return render_template('visualization.html', n=n, nn=nn, np=np, nne=nne, dic=dic)

# if __name__ == '__main__':
#     app.run(debug=True)








from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from flask_pymongo import PyMongo
import bcrypt
from scraper import returnytcomments
from sentiment import returnsentiment
from utilities import CleanCache
from preprocessing import clean
from wordcloud1 import create_wordcloud
from random_forest_model import RandomForestSentimentClassifier

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = 'vsw'

# Configure mail settings
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'  # Your SMTP server
app.config['MAIL_PORT'] = 587  # Port for TLS/STARTTLS
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'nileshpandhare70@gmail.com'  # Your email address
app.config['MAIL_PASSWORD'] = 'ubez ymkr kfin futo'  # Your email password

mail = Mail(app)

# MongoDB configuration
app.config['MONGO_DBNAME'] = 'YotubeAnalyzer'
app.config['MONGO_URI'] = 'mongodb+srv://projectuser2:projectuser2@yotubeanalyzer.wjcpili.mongodb.net/YoutubeAnalyzer?retryWrites=true&w=majority&appName=YotubeAnalyzer'

mongo = PyMongo(app)

# Initialize the random forest classifier
rf_classifier = RandomForestSentimentClassifier()

# Define a variable to store result data globally
result_data = None


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name': request.form['username']})

    if login_user:
        if bcrypt.checkpw(request.form['pass'].encode('utf-8'), login_user['password']):
            session['username'] = request.form['username']
            return redirect(url_for('home'))
    
    return render_template('register.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name': request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one({'name': request.form['username'], 'password': hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('home'))
        else:
            return 'Username already in database'
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('home.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/results', methods=['GET'])
def result():
    global result_data  # Use the global variable
    url = request.args.get('url')
    user_email = request.args.get('email')  # Get the user's email

    org_comments = returnytcomments(url)
    temp = [i for i in org_comments if 5 < len(i) <= 500]
    org_comments = temp

    clean_comments = clean(org_comments)

    create_wordcloud(clean_comments)

    np, nn, nne = 0, 0, 0

    predictions = []
    scores = []

    for i in clean_comments:
        score, sent = returnsentiment(i)
        scores.append(score)
        if sent == 'Positive':
            predictions.append('POSITIVE')
            np += 1
        elif sent == 'Negative':
            predictions.append('NEGATIVE')
            nn += 1
        else:
            predictions.append('NEUTRAL')
            nne += 1

    dic = []

    for i, cc in enumerate(clean_comments):
        x = {}
        x['sent'] = predictions[i]
        x['clean_comment'] = cc
        x['org_comment'] = org_comments[i]
        x['score'] = scores
        dic.append(x)
   
    result_data = {
        'n': len(clean_comments),
        'nn': nn,
        'np': np,
        'nne': nne,
        'dic': dic
    }

    # Train random forest model
    X_train = clean_comments
    y_train = predictions
    rf_classifier.train(X_train, y_train)

    # Send email with analysis result
    send_email(user_email, result_data)

    return render_template('result.html', n=len(clean_comments), nn=nn, np=np, nne=nne, dic=dic)

def send_email(email, result_data):
    msg = Message(subject="Youtube Video Comments Sentiment Analysis Result",
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[email])
    msg.html = render_template("email_template.html", result_data=result_data)
    mail.send(msg)

@app.route('/wc')
def wc():
    return render_template('wc.html')

@app.route('/visualization')
def visualization():
    global result_data  # Use the global variable

    # If data exists, pass it to the template, otherwise provide default values
    if result_data:
        n = result_data['n']
        nn = result_data['nn']
        np = result_data['np']
        nne = result_data['nne']
        dic = result_data['dic']
    else:
        n, nn, np, nne, dic = 0, 0, 0, 0, []

    # Render the visualization.html template
    return render_template('visualization.html', n=n, nn=nn, np=np, nne=nne, dic=dic)

    
if __name__ == '__main__':
    app.run(debug=True)
