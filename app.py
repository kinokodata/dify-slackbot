import asyncio
import os
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from dotenv import load_dotenv
import aiohttp

load_dotenv()
DIFY_KEY = os.getenv("DIFY_API_KEY")

app = AsyncApp(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.event("app_mention")
async def handle_app_mention_events(event, say, ack):
    await ack()

    user = event['user']
    query = event['text']
    # クラウド上のDify APIエンドポイントを使用
    url = 'https://api.dify.ai/v1/chat-messages'  # 実際のエンドポイントに変更してください
    headers = {
        'Authorization': f'Bearer {DIFY_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'query': query,
        'response_mode': 'blocking',
        'user': user,
        'conversation_id': '',
        'inputs': {}
    }
    print(headers)
    print(data)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    json_response = await response.json()
                    answer = json_response.get('answer', 'No answer provided.')
                    await say(answer)
                else:
                    error_message = await response.text()
                    await say(f'APIエラー: {response.status}, メッセージ: {error_message}')
    except Exception as e:
        await say(f'エラーが発生しました: {str(e)}')

async def main():
    handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    await handler.start_async()

if __name__ == "__main__":
    asyncio.run(main())