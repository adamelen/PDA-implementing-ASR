import os
import pyaudio
import wave

class RecordControl:
    ''' A <<Controller>> class that controls the recording process '''

    # define callback
    def callback(self, in_data, frame_count, time_info, status):
        data = None
        self.wf.writeframes(in_data)
        return (data, pyaudio.paContinue)

    def __init__(self, file_name):
        # instantiate PyAudio and open wav file
        self.p = pyaudio.PyAudio()
        self.wf = wave.open(file_name, 'wb')
        # open stream using callback
        self.stream = self.p.open(format=pyaudio.paInt16,
                          channels=1,
                          rate=16000,
                          input=True,
                          stream_callback=self.callback)
        # prepare wav file
        self.wf.setnchannels(1)
        self.wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        self.wf.setframerate(16000)

    def record(self):
        # start the stream
        print("Recording starts")
        self.stream.start_stream()

    def stop_recording(self):
        # stop stream
        self.stream.stop_stream()
        self.stream.close()
        self.wf.close()

        # close PyAudio
        self.p.terminate()
        print("Recording Done")
