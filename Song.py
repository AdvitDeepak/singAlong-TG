"""
Advit Deepak, Jun 2021
Sample TigerGraph Demo - singAlong-TG

This file, Song.py, represents the song class used to store and represent each
song loaded into the main singAlong-TG.py file. Each song contains the artist,
the title, the length (in seconds), and the locations to its accompanying files.

Each song comes with two files:

1. The audio file, stored in a .wav format
   This program currently only supports .wav files. These must be generated
   by the user, named appropriately (see naming convention as described within
   the __init__ method), and stored in the appropriate directory.

2. The LRC file, stored in a .txt. format

   This file contains each verse and its timestamp. It is a modified version of
   the standard LRC: https://en.wikipedia.org/wiki/LRC_(file_format). Each line
   simply contains a timestamp, pipeline, then the verse. For example, entries
   resemble the following format: "0:09|All those days watching from the window"

"""

import sys, os
import pyaudio, wave
import speech_recognition as sr

class Song:

    # Initializes the song using the inputted artist and title strings.
    def __init__(self, artist, title):
        self.artist = artist
        self.title = title

        # Stores the paths to each file (audio, audio-syncronized LRC)

        # Assumes that the files (audio - .wav, LRC - .txt) will
        # be titled in the following format:
        #     1. The song name, but with all spaces replaced by underscores
        #     2. All capitalization and punctuation marks removed
        #     3. Suffix is either "___aud" or "___lrc"
        #
        #     Example: "when_will_my_life_begin___lrc.txt" will be valid

        self.audSrc = os.path.abspath(os.curdir) + "/dir_songs/" + title.replace(" ", "_").lower() + "___aud.wav"
        self.lrcSrc = os.path.abspath(os.curdir)+"/dir_lrc/" + title.replace(" ", "_").lower() + "___lrc.txt"

        # Calculates the length of the song (in seconds)
        with sr.AudioFile(self.audSrc) as source:
            r = sr.Recognizer()
            audio = r.record(source)
        self.length = len(audio.frame_data)/(audio.sample_rate*audio.sample_width)

    # Returns the name of the artist
    def getArtist(self):
        return self.artist

    # Returns the name of the song
    def getTitle(self):
        return self.title

    # Returns the file location of the song (.wav)
    def getAudSrc(self):
        return self.audSrc

    # Returns the file location of the audio-syncronized LRC (.txt)
    def getLrcSrc(self):
        return self.lrcSrc

    # Returns the length of the song in seconds
    def getSongLength(self):
        return self.length

    # Plays the song from the specified start time to the end time. If the end
    # time is not inputed, it automatically defaults to the song's length
    def playSong(self, startTime, endTime=None):

        # Checks whether no end time has been specified. Python does not allow
        # default parameters within a class method to contain instance variables
        if endTime is None:
            endTime = self.length

        wf = wave.open(self.audSrc, 'rb')

        py_audio = pyaudio.PyAudio()
        stream = py_audio.open(format=py_audio.get_format_from_width(wf.getsampwidth()),
                               channels=wf.getnchannels(),
                               rate=wf.getframerate(),
                               output=True)

        # Sets the start position of the song
        n_frames = int(startTime * wf.getframerate())
        wf.setpos(n_frames)

        # Sets the end position of the song
        n_frames = int((endTime - startTime) * wf.getframerate())
        frames = wf.readframes(n_frames)

        stream.write(frames)

        # Terminates once the song has finished played
        stream.close()
        py_audio.terminate()
        wf.close()
