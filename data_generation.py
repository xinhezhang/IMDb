import pandas as pd
from pandas import DataFrame, Series


def simplify_data():

    # filter the non-movie kind and merge movie name into the record
    title_movie_only = pd.read_csv('./originalData/movie_basic_info.csv', delimiter='\t', encoding='utf-8',
                               usecols=['tconst', 'titleType', 'primaryTitle'])
    title_movie_only = title_movie_only[title_movie_only['titleType'] == 'movie']
    title_movie_only.drop('titleType', inplace=True, axis='columns')

    data=pd.read_csv('../originalData/principle.csv', delimiter='\t', encoding='utf-8', usecols=['tconst', 'nconst', 'category'])
    data = data[data['category'].isin(['actor', 'actress'])]
    data.drop('category', inplace=True, axis='columns')
    data = pd.merge(title_movie_only, data, on='tconst')

    #  merge the name of actor
    name = pd.read_csv('./originalData/actor_basic_info.csv', delimiter='\t', encoding='utf-8', usecols=['nconst', 'primaryName'])
    data = pd.merge(name, data, on='nconst')
    data.columns=['actorId', 'actorName', 'movieId', 'movieTitle']

    print(data.head())
    data.to_csv("data_simplified.csv", index= False)


def group_data():
    data=pd.read_csv('data_simplified.csv', usecols=['movieId', 'actorId'])

    '''
    Group the data by ActorId
    '''
    data_actor=data.groupby('actorId')['movieId'].apply(list)
    data_actor=data_actor.reset_index()
    data_actor.columns=['actorId', 'movies']
    data_actor['count']= data_actor.movies.apply(lambda x: len(x))
    data_actor= data_actor.sort_values('count', ascending=False)
    data_actor.to_csv('data_actor.csv', index=False)

    '''
    Print the actor who has the most screen credit
    '''
    name = pd.read_csv('actor_name.csv', delimiter='\t', encoding='utf-8', usecols=['nconst', 'primaryName'])
    name.columns=['actorId', 'primaryName']
    actor_top_10_num= data_actor[0:20]
    actor_top_10_num= pd.merge(name, actor_top_10_num, on='actorId')
    actor_top_10_num= actor_top_10_num.sort_values('count', ascending=False)
    print(actor_top_10_num[['primaryName', 'actorId']])


    '''
    Group the data by MovieId
    '''
    data_movie=data.groupby('movieId')['actorId'].apply(list)
    data_movie=data_movie.reset_index()
    data_movie.columns=['movieId', 'actors']
    data_movie.to_csv('data_movie.csv', index= False)


    '''
    Create the Connection Graph:
        We think that if two actors appeared in the same movie, then the two actors are connected, here we want to find the 
        connection Graph 
    '''
    def get_connection(movieList):
        actor_in_movies=list(set([a for b in data_movie[data_movie['movieId'].isin(movieList)].actors.tolist() for a in b]))
        return actor_in_movies

    data_actor['connection']=data_actor['movies'].apply(get_connection)
    data_actor.to_csv('connection.csv', columns=['actorId', 'connection'])

def merge_movie_data():
    '''

    here we merge data to the form of:  movieId,  actors, rating, numVotes, title
    '''

    title_movie_only = pd.read_csv('./originalData/movie_basic_info.csv', delimiter='\t', encoding='utf-8',
                                   usecols=['tconst', 'titleType', 'primaryTitle'])
    title_movie_only = title_movie_only[title_movie_only['titleType'] == 'movie']
    title_movie_only.drop('titleType', inplace=True, axis='columns')
    title_movie_only.columns=['movieId', 'title']


    rating_info = pd.read_csv('originalData/movie_rating_info.csv', delimiter='\t', encoding='utf-8')
    rating_info.columns = ['movieId', 'rating', 'numVotes']

    data_movie = pd.read_csv('data_movie.csv')
    # from ast import literal_eval
    # data_movie.actors = data_movie.actors.apply(literal_eval())

    data_movie= pd.merge(data_movie, rating_info, on='movieId')
    data_movie= pd.merge(data_movie, title_movie_only, on='movieId')
    data_movie.to_csv('movieInfo.csv', index= False)

def merge_actor_data():
    actor_info=pd.read_csv('originalData/actor_basic_info.csv', delimiter='\t', encoding='utf-8')
    actor_info.columns=['actorId', 'primaryName', 'birthYear', 'deathYear', 'primaryProfession', 'knownForTitles']
    data_actor= pd.read_csv('actor_rating.csv')

    actor_info=pd.merge(data_actor, actor_info, on='actorId')
    actor_info.to_csv('actor_info.csv', columns=['actorId', 'primaryName', 'birthYear', 'deathYear', 'ratings','numVotes','count'], index=False)

def get_actor_rating_votes():
    movie_info=pd.read_csv('movieInfo.csv')
    data_actor= pd.read_csv('data_actor.csv')

    from ast import literal_eval
    data_actor.movies= data_actor.movies.apply(literal_eval)

    def get_rating(movieList):
        df=movie_info[movie_info['movieId'].isin(movieList)]
        ratings=df.rating.tolist()
        numVotes=df.numVotes.tolist()
        return ratings, numVotes
    data_actor['ratings'], data_actor['numVotes'] = zip(*data_actor['movies'].map(get_rating))
    data_actor.to_csv('actor_rating.csv', columns=['actorId', 'ratings', 'numVotes', 'count'], index= False)

def connection_analysis():
    '''
    Analysis Actors who has the most connection.
    '''
    connection= pd.read_csv('connection.csv', usecols=['actorId', 'connection'])
    name = pd.read_csv('actor_name.csv', delimiter='\t', encoding='utf-8', usecols=['nconst', 'primaryName'])
    name.columns=['actorId', 'primaryName']
    connection['count']=connection.connection.apply(lambda x: len(x))
    connection= connection.sort_values('count', ascending=False)
    connection_top_100=connection[0:100]
    connection_top_100=pd.merge(connection_top_100, name, on='actorId')
    connection_top_100.to_csv('connection_top_100.csv', columns=['actorId', 'primaryName', 'count'], index= False)


def rating_analysis():
    '''
    analysis the actor who has the most numVotes and rating
    '''
    actor_info= pd.read_csv("actor_info.csv", usecols=['actorId', 'ratings', 'numVotes', 'count', 'primaryName'])
    from ast import literal_eval
    actor_info.numVotes=actor_info.numVotes.apply(literal_eval)
    actor_info.ratings=actor_info.ratings.apply(literal_eval)
    actor_info['averRating']=actor_info.ratings.apply(lambda x: 0 if len(x)==0 else sum(x)/len(x))
    actor_info['averVote']=actor_info.numVotes.apply(lambda x: 0 if len(x)==0 else sum(x)/len(x))
    actor_info['validCount']=actor_info.ratings.apply(lambda x: len(x))
    actor_info= actor_info[actor_info['validCount']>=3]
    actor_info= actor_info[actor_info['averVote']>=50]
    actor_info.sort_values('averRating', ascending=False, inplace=True)
    actor_info.to_csv('actor_rating_sorted.csv', index= False, columns=['actorId', 'primaryName', 'validCount',  'averRating', 'averVote'])
    actor_info.sort_values('averVote', ascending=False, inplace= True)
    actor_info.to_csv('actor_vote_sorted.csv', index=False, columns=['actorId', 'primaryName', 'validCount',  'averRating', 'averVote'])

if __name__=="__main__":
    rating_analysis()