import tempfile
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import whisper
from transformers import pipeline
# Importing other libraries
import joblib
import numpy as np
import sys
import os

# Audio Imports
import pyaudio
import wave
import librosa
# Opening Model
MLP = joblib.load("back/emotion_app/assets/MLP.joblib")

# Audio Capture Parameters
CHUNKSIZE = 1024
RATE = 44100
p = pyaudio.PyAudio()
def start_stream(index=1):
    """Initializing PyAudio Capture Stream"""
    global stream
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=RATE,
                    input=True, frames_per_buffer=CHUNKSIZE,
                    input_device_index=index)
def stop_stream():
    """Terminate stream."""
    stream.stop_stream()
    stream.close()
def get_emotion(filename:str):
    """Predict emotion."""
    global stream
    start_stream()
    frames = []
    for _ in range(0, int(RATE / CHUNKSIZE * 1)):
        data = stream.read(CHUNKSIZE)
        frames.append(data)
    with wave.open(filename, 'wb') as file:
        file.setnchannels(1)
        file.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        file.setframerate(RATE)
        file.writeframes(b''.join(frames))
    features = get_features(filename)
    emotion=MLP.predict(features)[0]
    stop_stream()
    p.terminate()
    return emotion
def get_features(filename: str):
    """
    Extract features from audio required for model training.

    return in required format.
    """
    # Reading the file in and extracting required data
    raw_data, sr = librosa.load(filename)

    # Creating an empty numpy array to add data later on
    data = np.array([])

    # Calculating & Appending mfcc
    mfcc = np.mean(librosa.feature.mfcc(
        y=raw_data, sr=sr, n_mfcc=40).T, axis=0)
    data = np.hstack((data, mfcc))

    # Calculating & Appending chroma
    stft = np.abs(librosa.stft(raw_data))
    chroma = np.mean(librosa.feature.chroma_stft(
        S=stft, sr=sr,).T, axis=0)
    data = np.hstack((data, chroma))

    # Calculating & Appending mel
    mel = np.mean(librosa.feature.melspectrogram(
        y=raw_data, sr=sr).T,axis=0)
    data = np.hstack((data, mel))

    x = []
    x.append(data)
    return np.array(x)
# Whisperモデルのロード
model = whisper.load_model('base')  # 'tiny', 'small', 'medium', 'large'から選択可能

# 感情分析モデルのロード
sentiment_model = pipeline('sentiment-analysis', model='daigo/bert-base-japanese-sentiment')
@csrf_exempt
def transcribe_audio(request):
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

        # 感情分析の実行
        try:
            emotion = get_emotion(temp_file_path)
        except Exception as e:
            return JsonResponse({'error': f'感情分析中にエラーが発生しました: {str(e)}'}, status=500)
        finally:
            # 一時ファイルの削除
            temp_file.close()

        return JsonResponse({'text': text, 'emotion': emotion})
    else:
        return JsonResponse({'error': '無効なリクエストメソッドです。'}, status=405)
