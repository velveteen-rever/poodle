# audio_fetcher.py

import threading
import time
import wave

import pyaudio

import config


class AudioFetcher(threading.Thread):
    def __init__(self, audio_queue, running, channels=1, rate=16000, frames_per_buffer=8000):
        threading.Thread.__init__(self)
        self.audio_queue = audio_queue
        self.running = running

        self.pa = pyaudio.PyAudio()
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self.default_device_info = self.pa.get_default_input_device_info()
        self.sample_rate = int(self.default_device_info['defaultSampleRate'])

    @property
    def get_sample_rate(self):
        return self.sample_rate

    @property
    def get_device_info(self):
        return self.default_device_info

    def run(self):
        pa = pyaudio.PyAudio()
        stream = pa.open(format=config.PYAUDIO_FORMAT,
                         channels=config.PYAUDIO_CHANNELS,
                         rate=self.sample_rate,
                         input=True,
                         frames_per_buffer=config.PYAUDIO_FRAMES_PER_BUFFER)
        while self.running.is_set():
            data = stream.read(2000)
            self.audio_queue.put((time.time(), data))
        stream.close()

    def dump_audio(self, data, filename="audio_dumps/dump.raw"):
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(data)

    def stop(self):
        self.running.clear()
