"""
Advit Deepak, Jun 2021
Sample TigerGraph Demo - singAlong-TG

This file, singAlong-TG.py, is the main program of this demo. TigerGraph's
Python library, Cloud Portal, and GSQL queries are all utilized in this example.

Make sure to check out the README and demo video for a walkthrough of this
project. For more information, kindly refer to the user documentation found at:

    https://docs.tigergraph.com/

This program loads songs from the songs database (dir_songs, dir_lrc) and
generates a graph on TigerGraph's Cloud Portal. Each verse (line of a song) is
given a unique ID and stored as a vertex. This example (with four loaded audio
tracks) utilizes a total of 147 vertices. If any two lines have a cosine
similarity above 0.5 (meaning the two verses contain similar words), a weighted
edge between them is created. This TG graph has a total of 244 edges.

Then, using a custom GSQL query, all communities of vertices are identified
within the graph. This means that all groups of vertices that sound similar
are bunched together. The community ID of each vertex is stored as an attribute.

During runtime, the user enters their vocal input which is translated to text
using Google's speech_recognition package. Now, we must determine which line
the user has just sung. Instead of having to check every single vertex to
determine this, we can simply check each community. After choosing a random
vertex, the program computes its similarity to the user's input. If above 0.5,
the program checks all other vertices in that community. If below 0.5, then
the program simply moves to the next community. By storing each verse in a
graph database, this program can run in real-time. Instead of having to iterate
through every loaded verse, it only has to check each community once.

Once the verse has been determined, the program simply plays the song starting
from the next verse, effectively allowing the user to "sing along". Currently,
the program has the following three songs loaded (all from Disney's Tangled):

1. "When Will My Life Begin?" - Mandy Moore
2. "I See The Light" - Mandy Moore
3. "I've Got A Dream" - Mandy Moore

Just for fun, a custom "Happy Birthday" song has been included as well :)

For more information, including demonstration videos, output screenshots,
as well as future directions and improvements, check out the README.pdf

Enjoy singing!

"""

import pyaudio, wave
import sys, os, keyboard

import speech_recognition as sr
from multiprocessing import Process

from Song import Song
from TG_helpers import initLoadVerses
from TG_helpers import findSimVerse


# Prints out the titles and artists of all loaded songs
def displayInformation(songList):
    for i, song in enumerate(songList):
        print()
        print("Lodaded song #" + str(i + 1) + ":")
        print("    Title: " + song.getTitle())
        print("   Artist: " + song.getArtist())
        print("  Seconds: %.2f" % (song.getSongLength()))

    print()

# Records the user's voice, translates, and returns string
def getUserVerse():
    r = sr.Recognizer()
    mic = sr.Microphone()
    print("Listening!")

    # This can be a little finicky. Need to ensure you are speaking clearly
    # and directly into the mic. Although it adjusts for ambient noise, this
    # solution may or may not be sufficient given the user's environment.
    with mic as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    print("Recognizing!")
    try:
        text = r.recognize_google(audio) # If can successfuly translate
    except:
        text = None # If cannot translate the inputted audio from mic

    return text



if __name__ == "__main__":
    songList = []

    # Currently loading three songs from the Disney movie Tangled
    whenWillMyLife = Song("Mandy Moore", "When Will My Life Begin")
    iSeeTheLight = Song("Mandy Moore", "I See The Light")
    iveGotADream = Song("Mandy Moore", "I've Got A Dream")

    birthdayWish = Song("Hriday Chhabria", "Hriday's Birthday Wish")

    songList.append(birthdayWish); songList.append(whenWillMyLife);
    songList.append(iSeeTheLight); songList.append(iveGotADream)

    displayInformation(songList) # Prints out the loaded songs for the user

    initLoadVerses(songList) # TG-related function, detailed in TG_helpers.py



    while True:
        print("\n---------------------- New Session ----------------------\n")

        # Prompts the user to sing their verse
        userVerse = getUserVerse()
        if userVerse is None:
            print("Error! Unable to recognize voice."); exit()

        print("\nUser's Verse: " + userVerse)


        # This TG-related function traverses the graph, returning the matching verse
        currTitle, currVerse, lineNum, nextVerse, start_Str = findSimVerse(userVerse)

        if lineNum is None:
            print("Error! Unable to find line."); exit()

        currSong = [song for song in songList if song.getTitle() == currTitle]
        currSong = currSong[0]

        print("\nDetected Song: " + currTitle)
        print("         Artist: " + currSong.getArtist())
        print("         Verse: \"" + currVerse + "\"\n")

        print("Line Number: " + str(lineNum))

        # Converts the string format "X:YZ" into the total number of seconds
        start_Sec = int(start_Str.split(':')[0]) * 60 + int(start_Str.split(':')[1])
        print("Start time: " + start_Str + "\n")

        # Before playing verse, prints out the upcoming verse for the user
        print("User's sung (inputted) verse: " + currVerse)
        print("     Currently playing verse: " + nextVerse + "\n")


        # Begins a Process to play the song (process allows the user to exit)
        # at any time with a simple keypress. Song plays in background
        p = Process(target=currSong.playSong, args=(start_Sec,)); p.start()

        decision = input("Press Q to stop playback. ")
        if decision == "Q":
            p.terminate()
        else:
            print("The song will continue until it ends.")


        # Asks the user whether they wish to continue singing or to quit
        decision = input("Quit? (Q) or Continue Singing (any other input): ")
        print()

        if decision == "Q":
            break


    print("\n---------------------- End Session ----------------------\n")
    print("Thanks for singing today!")
