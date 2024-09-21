import tempfile
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import whisper
from transformers import pipeline

# Whisperモデルのロード
model = whisper.load_model('base')  # 'tiny', 'small', 'medium', 'large'から選択可能

# 感情分析モデルのロード
sentiment_model = pipeline('sentiment-analysis', model='daigo/bert-base-japanese-sentiment')
@csrf_exempt
def transcribe_audio(request):
    if request.method == 'POST':
        if request.method == 'POST':
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return JsonResponse({'error': '音声ファイルが提供されていません。'}, status=400)

        # 音声ファイルを一時ファイルに保存
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            for chunk in audio_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        # Whisperで音声をテキストに変換
        try:
            result = model.transcribe(temp_file_path, language='ja')
            text = result.get('text')
        except Exception as e:
            return JsonResponse({'error': f'音声認識中にエラーが発生しました: {str(e)}'}, status=500)
        finally:
            # 一時ファイルの削除
            temp_file.close()

        # 感情分析の実行
        try:
            sentiment = sentiment_model(text)
        except Exception as e:
            return JsonResponse({'error': f'感情分析中にエラーが発生しました: {str(e)}'}, status=500)

        return JsonResponse({'text': text, 'sentiment': sentiment})
    else:
        return JsonResponse({'error': '無効なリクエストメソッドです。'}, status=405)
