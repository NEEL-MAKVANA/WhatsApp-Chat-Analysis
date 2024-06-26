import re
import pandas as pd
from textblob import TextBlob


def preprocess(data):
    pattern = "\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s"

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({"user_message": messages, "message_date": dates})
    # convert message_date type
    df["message_date"] = pd.to_datetime(df["message_date"], format="%m/%d/%Y, %H:%M - ")

    df.rename(columns={"message_date": "date"}, inplace=True)

    users = []
    messages = []
    sentiments = []  # New list to store sentiment analysis results
    for message in df["user_message"]:
        entry = re.split("([\w\W]+?):\s", message)
        if entry[1:]:  # user name
            users.append(entry[1])
            message_text = " ".join(entry[2:])
            messages.append(message_text)
            sentiment = analyze_sentiment(message_text)  # Perform sentiment analysis
            sentiments.append(sentiment)

        else:
            users.append("group_notification")
            messages.append(entry[0])
            sentiments.append("Neutral")

    df["user"] = users
    df["message"] = messages
    df["sentiment"] = sentiments  # Add sentiment analysis results to DataFrame
    df.drop(columns=["user_message"], inplace=True)

    df["only_date"] = df["date"].dt.date
    df["year"] = df["date"].dt.year
    df["month_num"] = df["date"].dt.month
    df["month"] = df["date"].dt.month_name()
    df["day"] = df["date"].dt.day
    df["day_name"] = df["date"].dt.day_name()
    df["hour"] = df["date"].dt.hour
    df["minute"] = df["date"].dt.minute

    period = []
    for hour in df[["day_name", "hour"]]["hour"]:
        if hour == 23:
            period.append(str(hour) + "-" + str("00"))
        elif hour == 0:
            period.append(str("00") + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df["period"] = period

    return df


def analyze_sentiment(message):
    blob = TextBlob(str(message))
    sentiment_score = blob.sentiment.polarity
    if sentiment_score > 0:
        return "Positive"
    elif sentiment_score < 0:
        return "Negative"
    else:
        return "Neutral"
