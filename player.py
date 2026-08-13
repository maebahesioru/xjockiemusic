# player.py - 1曲ずつ再生するWebRTCオーディオトラック
# サンサンサンデーの再生技術を応用（avでデコード→48kHzステレオs16フレーム）
import asyncio
import av
import numpy as np
from aiortc.mediastreams import AudioFrame, AudioStreamTrack


class SongTrack(AudioStreamTrack):
    kind = 'audio'

    def __init__(self, sample_rate=48000):
        super().__init__()
        self.sample_rate = sample_rate
        self._container = None
        self._iter = None
        self._resampler = None
        self._buf = b''
        self._pending = None
        self._current = None
        self._ended = asyncio.Event()
        self._started = asyncio.Event()
        self._skip = False
        self._paused = False
        self._volume = 1.0

    def pause(self):
        """一時停止（無音を流し続ける）"""
        self._paused = True

    def resume(self):
        """再開"""
        self._paused = False

    @property
    def paused(self):
        return self._paused

    def set_volume(self, v):
        """音量設定（0〜200・100=標準）"""
        self._volume = max(0.0, min(2.0, v / 100.0))

    def seek(self, seconds):
        """現在の曲を±seconds秒シーク"""
        if self._container is not None:
            try:
                self._container.seek(int(seconds * 1000000), backward=seconds < 0)
                self._iter = iter(self._container.decode(self._container.streams.audio[0]))
                self._buf = b''
            except Exception as e:
                print('シークエラー:', str(e)[:80])

    def skip(self):
        """現在の曲をスキップ（次の曲があれば自動再生）"""
        self._skip = True

    @property
    def current(self):
        return self._current

    def load(self, path):
        """次の曲をセット（現在再生中なら、終了後に自動で再生される）"""
        self._pending = path

    def has_pending(self):
        return self._pending is not None

    def is_playing(self):
        return self._container is not None

    async def wait_started(self, timeout=30):
        await asyncio.wait_for(self._started.wait(), timeout)

    async def wait_ended(self, timeout=None):
        await asyncio.wait_for(self._ended.wait(), timeout)

    def _open(self, path):
        if self._container is not None:
            self._container.close()
        self._container = av.open(path)
        self._iter = iter(self._container.decode(self._container.streams.audio[0]))
        self._resampler = av.AudioResampler(format='s16', layout='stereo', rate=self.sample_rate)
        self._buf = b''

    def _frame(self, data):
        audio = AudioFrame(format='s16', layout='stereo', samples=self.sample_rate // 50)
        audio.sample_rate = self.sample_rate
        audio.planes[0].update(data)
        return audio

    async def recv(self):
        need = self.sample_rate * 2 * 2 // 50  # 20ms stereo s16
        while True:
            # 一時停止中は無音
            if self._paused:
                return self._frame(b'\x00' * need)
            # スキップ処理
            if self._skip and self._container is not None:
                self._skip = False
                self._container.close()
                self._container = None
                self._started.clear()
                self._ended.set()
                if self._pending is not None:
                    self._current = self._pending
                    self._pending = None
                    self._open(self._current)
                    self._ended.clear()
                    self._started.set()
                else:
                    return self._frame(b'\x00' * need)
            if self._container is None:
                if self._pending is None:
                    return self._frame(b'\x00' * need)  # 無音
                self._current = self._pending
                self._pending = None
                self._open(self._current)
                self._ended.clear()
                self._started.set()
            while len(self._buf) < need:
                try:
                    frame = next(self._iter)
                except StopIteration:
                    # 曲終了 → 次の曲があれば自動再生
                    self._container.close()
                    self._container = None
                    self._started.clear()
                    self._ended.set()
                    if self._pending is not None:
                        self._current = self._pending
                        self._pending = None
                        self._open(self._current)
                        self._ended.clear()
                        self._started.set()
                    else:
                        return self._frame(b'\x00' * need)
                    continue
                out = self._resampler.resample(frame)
                if not out:
                    continue
                for f in out:
                    self._buf += bytes(f.planes[0])
            chunk, self._buf = self._buf[:need], self._buf[need:]
            if self._volume != 1.0:
                a = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) * self._volume
                chunk = np.clip(a, -32768, 32767).astype(np.int16).tobytes()
            return self._frame(chunk)
