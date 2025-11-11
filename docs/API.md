# API仕様書

## Overlay WebSocket API

### エンドポイント
```
ws://localhost:5173/ws
```

### イベント型

#### 1. utter_start
発話開始時に送信。

```json
{
  "type": "utter_start",
  "text": "こんにちは、視聴者の皆さん！",
  "subtitle": "こんにちは、視聴者の皆さん！"
}
```

**フィールド:**
- `type` (string): "utter_start"
- `text` (string): 発話内容（フル）
- `subtitle` (string): 字幕表示用テキスト

#### 2. mouth
口パク値の更新（30-60Hz）。

```json
{
  "type": "mouth",
  "value": 0.75
}
```

**フィールド:**
- `type` (string): "mouth"
- `value` (float): 口の開き具合 (0.0=閉じている, 1.0=最大)

#### 3. utter_end
発話終了時に送信。

```json
{
  "type": "utter_end"
}
```

**フィールド:**
- `type` (string): "utter_end"

## Brain HTTP API（将来拡張用）

現在はWebSocketのみ対応。将来的にREST APIを追加予定。

### 計画中のエンドポイント

#### POST /api/v1/chat
```json
{
  "message": "こんにちは"
}
```

**Response:**
```json
{
  "response": "こんにちは！何かお手伝いできることはありますか？",
  "audio_url": "/audio/12345.wav"
}
```

#### GET /api/v1/status
システムステータスの取得。

**Response:**
```json
{
  "status": "running",
  "providers": {
    "stt": "local",
    "llm": "api", 
    "tts": "local"
  },
  "uptime": 3600
}
```

## Provider Interface

### LLM Provider

```python
class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text response from prompt."""
        pass
```

### STT Provider

```python
class STTProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_data: np.ndarray, sample_rate: int = 16000) -> str:
        """Transcribe audio data to text."""
        pass
```

### TTS Provider

```python
class TTSProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str) -> str:
        """Synthesize text to speech and return WAV file path."""
        pass
```

## エラーハンドリング

すべてのプロバイダはエラー時にダミー実装にフォールバックします。

```python
try:
    result = provider.generate(prompt)
except Exception as e:
    logger.warning(f"Provider failed: {e}, using fallback")
    result = dummy_provider.generate(prompt)
```

## レート制限

- WebSocket接続: 制限なし
- API（将来）: 100リクエスト/分

## 認証

- ローカル実行: 認証なし
- 本番環境: API Keyまたはトークンベース（将来実装）
