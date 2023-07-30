# main.py
from datetime import datetime

import chat_manager
import kd_listeners
from audio_utils import KeywordDetector, Transcriber
from file_manager import FileManager
import time
import config
import event_flags as ef


def main():
    kw_detector = KeywordDetector("computer")
    kw_detector.add_keyword_listener(kd_listeners.kwl_start_recording)
    kw_detector.add_partial_listener(lambda pr: kd_listeners.pl_no_speech(pr))

    kw_detector.add_keyword_listener(kd_listeners.kwl_print_keyword_message)

    if config.ENABLE_ALL_PARTIAL_RESULT_LOG:
        kw_detector.add_partial_listener(kd_listeners.pl_print_all_partials)

    if config.ENABLE_ACTIVE_SPEECH_LOG:
        kw_detector.add_partial_listener(kd_listeners.pl_print_active_speech_only)

    chat_session = chat_manager.ChatSession()
    transcriber = Transcriber(config.PATH_PROMPT_BODIES_AUDIO, config.TRANSCRIPTION_PATH)

    kw_detector.start()

    try:
        while True:
            transcriber.transcribe_bodies()
            if ef.silence.is_set():
                transcriber.do_request(chat_session)
                convo = chat_session.messages
                timestamp = FileManager.get_datetime_string()
                FileManager.save_json(f'{config.CONVERSATIONS_PATH}conversation_{timestamp}.json', convo)
            time.sleep(1)
    except KeyboardInterrupt:
        print("Closing the program")
        kw_detector.close()
        kw_detector.join()


if __name__ == '__main__':
    main()
