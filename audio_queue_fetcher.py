import threading
import time
import wave

import pyaudio

import config


class AudioQueueFetcher(threading.Thread):
    def __init__(self, audio_queue, running, channels=config.PYAUDIO_CHANNELS, frames_per_buffer=8000):
        threading.Thread.__init__(self)
        self.audio_queue = audio_queue
        self.running = running

        self.pa = pyaudio.PyAudio()
        self.channels = channels
        self.frames_per_buffer = frames_per_buffer
        self.default_device_info = self.pa.get_default_input_device_info()
        self.sample_rate = int(self.default_device_info['defaultSampleRate'])

    def dump_audio(self, data, filename="audio_dumps/dump.raw"):
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(data)

    def run(self):
        stream = self.pa.open(format=config.PYAUDIO_FORMAT,
                              channels=config.PYAUDIO_CHANNELS,
                              rate=self.sample_rate,
                              input=True,
                              frames_per_buffer=config.PYAUDIO_FRAMES_PER_BUFFER)
        while self.running.is_set():
            data = stream.read(self.frames_per_buffer)
            self.audio_queue.put((time.time(), data))
        stream.stop_stream()
        stream.close()
        self.pa.terminate()

    def stop(self):
        self.running.clear()