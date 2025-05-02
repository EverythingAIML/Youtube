import pandas as pd
from urllib import request
import numpy as np
from gensim.models import Word2Vec

# Download the playlist dataset
playlist = request.urlopen('https://storage.googleapis.com/maps-premium/dataset/yes_complete/train.txt')

# Decode and process the dataset, skipping the first two metadata lines
playlist_lines = playlist.read().decode('utf-8').split('\n')[2:]

# Filter out playlists containing only a single track
playlist_data = [line.strip().split() for line in playlist_lines if len(line.split()) > 1]

# Fetch and prepare the song metadata
song_response = request.urlopen('https://storage.googleapis.com/maps-premium/dataset/yes_complete/song_hash.txt')
song_lines = song_response.read().decode('utf-8').split('\n')

# Create a DataFrame containing song ID, title, and artist
song_records = [entry.strip().split('\t') for entry in song_lines]
song_metadata = pd.DataFrame(song_records, columns=['id', 'title', 'artist']).set_index('id')

# Train our Word2Vec model
embedding_model = Word2Vec(
    sentences=playlist_data, vector_size=32, window=20, negative=50, workers=4
)

# Ask the model for songs similar to song #1345
song_id = 1345

for song in embedding_model.wv.most_similar(positive=str(song_id)):
    print(song)

def recommendations(song_id):
    similar_songs = np.array(
        embedding_model.wv.most_similar(positive=str(song_id), topn=5)
    )[:, 0]
    return song_metadata.iloc[similar_songs]

# Extract recommendations
print(recommendations(song_id))
