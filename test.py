import requests

# URL вебхука твоего папы
webhook_url = 'https://miramgazy.app.n8n.cloud/webhook/6c740239-c83b-42a2-aa78-71bfef56afef'

# Тестовые данные, которые отправим
data = {
    'event': 'test_event',
    'message': 'Hello, this is a test payload from Python script.'
}

# Отправляем POST-запрос с JSON-данными
response = requests.post(webhook_url, json=data)

# Проверяем результат
print(f'Status Code: {response.status_code}')
print(f'Response Text: {response.text}')
