"""
AITuber Brain - Main orchestrator.
Coordinates STT, LLM, TTS and sends events to Overlay via WebSocket.
"""
import argparse
import asyncio
import json
from pathlib import Path

import websockets

from apps.brain import config
from apps.brain.llm import get_llm_provider
from apps.brain.stt import get_stt_provider
from apps.brain.tts import get_tts_provider
from apps.brain.utils import audio_to_mouth_values, cleanup_temp_file, read_wav_data
from apps.brain.vad import VoiceActivityDetector


class BrainOrchestrator:
    """Main orchestrator for AITuber brain."""

    def __init__(self):
        self.stt = get_stt_provider(config.STT_PROVIDER)
        self.llm = get_llm_provider(config.LLM_PROVIDER)
        self.tts = get_tts_provider(config.TTS_PROVIDER)
        self.overlay_url = f"ws://{config.OVERLAY_HOST}:{config.OVERLAY_PORT}/ws"
        self.websocket = None
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Load persona system prompt."""
        prompt_path = Path(__file__).parent / "persona" / "system_prompt.ja.md"
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        return "あなたは親しみやすいAIアシスタントです。"

    async def connect_overlay(self):
        """Connect to overlay WebSocket."""
        try:
            self.websocket = await websockets.connect(self.overlay_url)
            print(f"Connected to overlay: {self.overlay_url}")
        except Exception as e:
            print(f"Warning: Could not connect to overlay: {e}")
            self.websocket = None

    async def send_to_overlay(self, data: dict):
        """Send message to overlay."""
        if self.websocket:
            try:
                await self.websocket.send(json.dumps(data))
            except Exception as e:
                print(f"Error sending to overlay: {e}")

    async def process_text(self, text: str):
        """Process a single text input through the pipeline."""
        print(f"\n[INPUT] {text}")

        # LLM generation
        print("[LLM] Generating response...")
        response = self.llm.generate(text, self.system_prompt)
        print(f"[LLM] {response}")

        # Send utter_start
        await self.send_to_overlay({
            "type": "utter_start",
            "text": response,
            "subtitle": response
        })

        # TTS synthesis
        print("[TTS] Synthesizing speech...")
        wav_path = self.tts.synthesize(response)
        print(f"[TTS] Audio saved: {wav_path}")

        # Read audio and generate mouth values
        try:
            audio_data, sample_rate = read_wav_data(wav_path)
            mouth_values = audio_to_mouth_values(audio_data, sample_rate)
            print(f"[MOUTH] Generated {len(mouth_values)} mouth values")

            # Stream mouth values
            for value in mouth_values:
                await self.send_to_overlay({"type": "mouth", "value": round(value, 2)})
                await asyncio.sleep(0.033)  # ~30Hz
        except Exception as e:
            print(f"Error processing audio: {e}")
        finally:
            cleanup_temp_file(wav_path)

        # Send utter_end
        await self.send_to_overlay({"type": "utter_end"})
        print("[DONE]\n")

    async def run_text_mode(self, initial_text: str = None):
        """Run in text input mode."""
        await self.connect_overlay()

        if initial_text:
            await self.process_text(initial_text)
        else:
            print("Text mode: Enter text to process (Ctrl+C to quit)")
            while True:
                try:
                    text = input("> ")
                    if text.strip():
                        await self.process_text(text)
                except KeyboardInterrupt:
                    print("\nExiting...")
                    break

        if self.websocket:
            await self.websocket.close()

    async def run_mic_mode(self):
        """Run in microphone mode."""
        await self.connect_overlay()

        vad = VoiceActivityDetector()
        print("Microphone mode: Speak to interact (Ctrl+C to quit)")

        try:
            for audio_segment in vad.segment_audio_from_mic():
                # STT transcription
                print("[STT] Transcribing...")
                text = self.stt.transcribe(audio_segment)
                if text:
                    await self.process_text(text)
                else:
                    print("[STT] No speech detected")
        except KeyboardInterrupt:
            print("\nExiting...")

        if self.websocket:
            await self.websocket.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AITuber Brain")
    parser.add_argument("--text", type=str, help="Process single text input")
    parser.add_argument("--mic", action="store_true", help="Use microphone mode")
    args = parser.parse_args()

    orchestrator = BrainOrchestrator()

    if args.mic or config.USE_MIC:
        asyncio.run(orchestrator.run_mic_mode())
    else:
        asyncio.run(orchestrator.run_text_mode(args.text))


if __name__ == "__main__":
    main()
