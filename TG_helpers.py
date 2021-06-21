"""
Advit Deepak, Jun 2021
Sample TigerGraph Demo - singAlong-TG

This file, TG-helpers.py, stores the helper functions utilzed in this demo. The
three helper functions, initLoadVerses(songList), findSimVerse(userInput), and
cosSimilarity(line1, line2) are explained in more detail below.

All TigerGraph-related information used to establish a connection between this
Python script and our TigerGraph Cloud graph are included below.

"""

import pyTigerGraph as tg

TG_HOST = "https://sing-along.i.tgcloud.io" # The link to GraphStudio
TG_USERNAME = "tigergraph" # Login related information
TG_PASSWORD = "singAlong"  # Login related information
TG_GRAPHNAME = "verse_sim" # The name of the graph (different from solution name)
TG_SECRET = "dal7hejdkhfql6loksa0uui321r0tvna" # The value used for authentication

conn = tg.TigerGraphConnection(host=TG_HOST, username=TG_USERNAME, password=TG_PASSWORD, graphname=TG_GRAPHNAME)
token = conn.getToken(TG_SECRET)



# This method creates all vertices and edges within the graph (if needed).
# Additionally, it runs a GSQL query (stored/written in GraphStudio) to
# identify communities of vertices. This can all be visualized in GraphStudio.

def initLoadVerses(songList):

    # If we have already loaded the vertices, no need to redo
    if (len(conn.getVertexTypes()) > 0): return

    songCounter = 1
    for song in songList:
        # Parsing through each song within singList
        lrc_file = open(song.getLrcSrc(), 'r')

        counter = 1
        for line in lrc_file:
            # Parsing through each verse within each loaded song
            time, verse = line.split('|'); verse = verse.strip()

            #The primary vertex ID, or infoID, is simply "songNum-lineNum"
            infoId = repr(songCounter) + "-" + repr(counter)

            # "upsertVertex" allows us to create a new vertex with the necessary attributes
            conn.upsertVertex('verse', infoId, {'song_title' : song.getTitle(), 'song_verse' : verse, 'song_time' : time, 'song_line' : counter})
            counter += 1

        songCounter += 1

    # And voila, all vertices have been loaded!
    # Now, we must generate any edges as needed

    vertices = conn.getVertices('verse')
    for vertex1 in vertices:

        # For each vertex, store its ID and verse
        info1 = vertex1.get("v_id")
        line1 = vertex1.get("attributes").get("song_verse")

        for vertex2 in vertices:

            # Choose another vertex to compute similarity between
            info2 = vertex2.get("v_id")
            line2 = vertex2.get("attributes").get("song_verse")

            if (info1 == info2): continue # Make sure they are not the same vertex

            sim = cosSimilarity(line1, line2)

            if (sim > 0.5): # If similarity is above 0.5, create weighted edge
                conn.upsertEdge('verse', info1, 'similarity', 'verse', info2, {'weight' : sim})


    # After we add all edges, we can run the GSQL query to detect any communities.
    # This query, titled "connComp", is further detailed in the README. Every
    # vertex is labelled (attribute) with its respective community ID.
    conn.runInstalledQuery('connComp')



# This method traverses through the generated graph every time the user sings
# a new line. Instead of iterating through every single vertex (simply unscalable),
# this method only has to iterate through each community of vertices.

def findSimVerse(userInput):

    vertices = conn.getVertices('verse')
    ignoreComm = [] # All community ID's we can skip over
    possibleVtx = {} # The ID's and similarity values for promising vertices

    for vertex in vertices:
        # If this community has already been checked, ignore!
        comm_id = vertex.get('attributes').get('comm_id')
        if (comm_id in ignoreComm): continue

        sim = cosSimilarity(userInput, vertex.get('attributes').get('song_verse'))
        if (sim < 0.5):
            ignoreComm.append(comm_id) # Not similar, no need to check community!
        else:
            possibleVtx[vertex.get('v_id')] = sim # Add to map of possible candidates

    # If no possible candidates found, the user's input simply isn't in the graph!
    if (len(possibleVtx) == 0):
        return None, None, None, None, None

    # Determine the vertex with the highest similarity value from possibleVtx
    maxVtx = max(possibleVtx, key=possibleVtx.get)
    vtx = conn.getVerticesById('verse', maxVtx)[0]

    # Use the labelling ID format ("songNum-lineNum") to determine the next line
    # AKA finding the vertex ID which holds the next line of the particular song
    nextVtxID = maxVtx.split('-')[0] + "-" + repr(int(maxVtx.split('-')[1]) + 1)
    nVtx = conn.getVerticesById('verse', nextVtxID)[0]

    return vtx.get('attributes').get('song_title'), vtx.get('attributes').get('song_verse'), vtx.get('attributes').get('song_line'), nVtx.get('attributes').get('song_verse'), nVtx.get('attributes').get('song_time')



# This method calculates the similarity between two strings using an
# implementation of the cosine similarity algorithm. A float is returned.

def cosSimilarity(line1, line2):
    # Converts both verses into lists of words
    l1_list = line1.lower().split()
    l2_list = line2.lower().split()

    # Creates a set of words for each verse
    l1_set = {w for w in l1_list}
    l2_set = {w for w in l2_list}

    l1 = []; l2 = []

    # Sees whether each word is present in verse1, verse2, or both
    rvector = l1_set.union(l2_set)
    for w in rvector:
        if w in l1_set: l1.append(1)
        else: l1.append(0)
        if w in l2_set: l2.append(1)
        else: l2.append(0)

    # Computes the dot product of the two vectors
    c = 0
    for i in range(len(rvector)):
        c+= l1[i]*l2[i]

    # Divides the dot product by the magnitude of the vectors
    return c / float((sum(l1)*sum(l2))**0.5)
