from __future__ import annotations
import os
from ..services import VoiceService
from ..domain.ports import VoiceStorage


class TelegramVoiceStorage(VoiceStorage):
    async def download_voice(self, file_id: str, bot_token: str, save_path: str) -> bool:
        return await VoiceService.download_voice_file(file_id, bot_token, save_path)

    async def convert_ogg_to_wav(self, ogg_path: str, wav_path: str) -> bool:
        return await VoiceService.convert_ogg_to_wav(ogg_path, wav_path)

    async def cleanup(self, *file_paths: str) -> None:
        for p in file_paths:
            try:
                if os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass
