from pocketsphinx import AudioFile

def STT(audio_file, hmm, lm, dic ):
    '''Imports a .wav file and converts speech to text using pocketsphinx'''

    # configure transcription parameters
    config = {
        'audio_file': audio_file,
        'hmm': hmm,
        'lm': lm,
        'dic': dic
    }

    # extract phrases from audio and merge them in a "text" variable
    text = ""
    audio = AudioFile(**config)
    for phrase in audio:
        #print(phrase)
        text = text + str(phrase) + " "
    return text


