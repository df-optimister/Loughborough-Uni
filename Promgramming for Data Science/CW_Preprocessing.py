#!/usr/bin/env python
# coding: utf-8

# In[ ]:


'''
This code is written by Keunwoo Kim(F429147). It process of cleaning data and saving as a database before use for programming.
'''


# In[302]:


import pandas as pd


# In[303]:


#A.
df = pd.read_csv('COP504CWData/songs.csv')
df.head


# In[304]:


df.dropna()
df.isnull().sum()


# In[305]:


dfSongs = df


# In[306]:


dfSongs.rename(columns={'duration_ms' : 'duration'}, inplace=True)
dfSongs


# In[308]:


dfSongs['duration'] = (dfSongs['duration']*0.001).round(3)


# In[309]:


#B.
filtered_dfSongs = dfSongs[
(dfSongs['popularity'] > 50) &
(dfSongs['speechiness'] >= 0.33) &
(dfSongs['speechiness'] <= 0.66) &
(dfSongs['danceability'] > 0.2)
]
filtered_dfSongs['speechiness'].head()


# In[311]:


#C.
SongTable = pd.DataFrame({
    'Song_ID': range(1, len(filtered_dfSongs) + 1), 
    'Song': filtered_dfSongs['song'], 
    'Duration': filtered_dfSongs['duration'], 
    'Explicit': filtered_dfSongs['explicit'], 
    'Year': filtered_dfSongs['year'], 
    'Popularity': filtered_dfSongs['popularity'],
    'Danceability': filtered_dfSongs['danceability'],
    'Speechiness': filtered_dfSongs['speechiness']
})

GenreTable = pd.DataFrame({
    'Genre_ID': range(1, len(filtered_dfSongs) + 1), 
    'Genre': filtered_dfSongs['genre']
})

ArtistTable = pd.DataFrame({
    'Artist_ID': range(1, len(filtered_dfSongs) + 1), 
    'ArtistName': filtered_dfSongs['artist']
})

#Added all the columns in MasterID with Master_ID to prevent column order from getting mixed when calling the data frame while programming.
MasterID = pd.DataFrame({
    'Master_ID': range(1, len(filtered_dfSongs) + 1),
    'Song_ID': range(1, len(filtered_dfSongs) + 1), 
    'Song': filtered_dfSongs['song'],
    'Genre_ID': range(1, len(filtered_dfSongs) + 1), 
    'Genre': filtered_dfSongs['genre'],
    'Artist_ID': range(1, len(filtered_dfSongs) + 1), 
    'ArtistName': filtered_dfSongs['artist'],
    'Duration': filtered_dfSongs['duration'], 
    'Explicit': filtered_dfSongs['explicit'], 
    'Year': filtered_dfSongs['year'], 
    'Popularity': filtered_dfSongs['popularity'],
    'Danceability': filtered_dfSongs['danceability'],
    'Speechiness': filtered_dfSongs['speechiness']
})


# In[312]:


import sqlite3
conn = sqlite3.connect('CWDatabase.db')
SongTable.to_sql('SongTable', conn, if_exists='replace', index=False)
GenreTable.to_sql('GenreTable', conn, if_exists='replace', index=False)
ArtistTable.to_sql('ArtistTable', conn, if_exists='replace', index=False)
MasterID.to_sql('MasterID', conn, if_exists='replace', index=False)
conn.close()


# In[313]:


conn = sqlite3.connect('CWDatabase.db')
query = 'SELECT * FROM MasterID'
x = pd.read_sql_query(query, conn)
x


# In[ ]:




