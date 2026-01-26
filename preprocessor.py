import re
import pandas as pd

def preprocess(data):
    # WhatsApp new format:
    # [23/12/25, 6:20:08 PM] User Name: Message
    pattern = r'\[\d{2}/\d{2}/\d{2},\s\d{1,2}:\d{2}:\d{2}\s[AP]M\]\s'

    # Split messages and extract dates
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({
        'user_message': messages,
        'message_date': dates
    })

    # Clean date strings and convert to datetime
    df['message_date'] = (
        df['message_date']
        .str.replace(r'[\[\]]', '', regex=True)
        .str.strip()
    )

    df['message_date'] = pd.to_datetime(
        df['message_date'],
        format='%d/%m/%y, %I:%M:%S %p'
    )

    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Extract users and messages
    users = []
    messages = []

    for message in df['user_message']:
        entry = re.split(r'([^:]+):\s', message)
        if len(entry) > 2:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Date-related features
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Time period feature
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append("23-00")
        elif hour == 0:
            period.append("00-01")
        else:
            period.append(f"{hour}-{hour + 1}")

    df['period'] = period

    return df
