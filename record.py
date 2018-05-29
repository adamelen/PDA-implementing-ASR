import os
import pyaudio
import wave

def record():
    '''Function "record": records speaker's speech and saves it to "speak.wav"'''
    # instantiate PyAudio
    p = pyaudio.PyAudio()

    # prepare wav file
    wf = wave.open('speak.wav', 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)

    # define callback
    def callback(in_data, frame_count, time_info, status):
        data = None
        wf.writeframes(in_data)
        return (data, pyaudio.paContinue)

    # open stream using callback
    stream = p.open(format=pyaudio.paInt16,
                  channels=1,
                  rate=16000,
                  input=True,
                  stream_callback=callback)

    # start the stream
    print("Recording starts")
    stream.start_stream()
 
    # wait for stream to finish
    raw_input("When you finish, press Enter")

    # stop stream
    stream.stop_stream()
    stream.close()
    wf.close()

    # close PyAudio
    p.terminate()
    print("Recording Done")
    return
