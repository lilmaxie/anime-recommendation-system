import pandas as pd
import numpy as np
import joblib
from config.paths_config import *


def getAnimeFrame(anime, path_df):
    """
    This function retrieves the anime details from the anime dataframe based on either anime ID or English version name.
    anime : int or str : anime ID (int) or English version name (str)
    path_df : str : path to the anime dataframe CSV file
    Returns a DataFrame row corresponding to the anime.
    """
    
    df = pd.read_csv(path_df)
    if isinstance(anime, int):
        return df[df.anime_id == anime]
    if isinstance(anime, str):
        return df[df.eng_version == anime]

def getSynopsis(anime, path_synopsis_df):
    """
    This function retrieves the synopsis of an anime based on either anime ID or English version name.
    anime : int or str : anime ID (int) or English version name (str)
    path_synopsis_df : str : path to the synopsis dataframe CSV file
    Returns the synopsis string of the anime.
    """
    
    synopsis_df = pd.read_csv(path_synopsis_df)
    if isinstance(anime, int):
        return synopsis_df[synopsis_df.MAL_ID == anime].sypnopsis.values[0]
    if isinstance(anime, str):
        return synopsis_df[synopsis_df.Name == anime].sypnopsis.values[0]

def find_similar_animes(name, path_anime_weights, path_anime2anime_encoded, path_anime2anime_decoded,  path_anime_df, n=10, return_dist=False, neg=False):
    """
    This function finds similar animes based on the provided anime name using precomputed weights.
    name : str : English version name of the anime
    path_anime_weights : str : path to the anime weights file
    path_anime2anime_encoded : str : path to the anime to encoded mapping file
    path_anime2anime_decoded : str : path to the anime to decoded mapping file
    path_anime_df : str : path to the anime dataframe CSV file
    n : int : number of similar animes to find
    return_dist : bool : whether to return distances along with similar animes
    neg : bool : if
        True : find least similar animes
        False : find most similar animes
    Returns a DataFrame of similar animes or distances and indices if requested.
    """
    # Load weights and encoded-decoded mappings
    anime_weights = joblib.load(path_anime_weights)
    anime2anime_encoded = joblib.load(path_anime2anime_encoded)
    anime2anime_decoded = joblib.load(path_anime2anime_decoded)

    # Get the anime ID for the given name
    index = getAnimeFrame(name, path_anime_df).anime_id.values[0]
    encoded_index = anime2anime_encoded.get(index)

    if encoded_index is None:
        raise ValueError(f"Encoded index not found for anime ID: {index}")

    # Compute similarity distances
    weights = anime_weights
    dists = np.dot(weights, weights[encoded_index])  # Ensure weights[encoded_index] is a 1D array
    sorted_dists = np.argsort(dists)

    n = n + 1

    # Select closest or farthest based on 'neg' flag
    if neg:
        closest = sorted_dists[:n]
    else:
        closest = sorted_dists[-n:]

    # Return distances and closest indices if requested
    if return_dist:
        return dists, closest

    # Build the similarity array
    SimilarityArr = []
    for close in closest:
        decoded_id = anime2anime_decoded.get(close)

        anime_frame = getAnimeFrame(decoded_id,  path_anime_df)

        anime_name = anime_frame.eng_version.values[0]
        genre = anime_frame.Genres.values[0]
        similarity = dists[close]

        SimilarityArr.append({
            "anime_id": decoded_id, 
            "name": anime_name, 
            "similarity": similarity, 
            "genre": genre, 
        })

    # Create a DataFrame with results and sort by similarity
    Frame = pd.DataFrame(SimilarityArr).sort_values(by="similarity", ascending=False)
    return Frame[Frame.anime_id != index].drop(['anime_id'], axis=1)

def find_similar_users(item_input, path_user_weights, path_user2user_encoded, path_user2user_decoded, n=10, return_dist=False, neg=False):
    """
    This function finds similar users based on the provided user ID using precomputed weights.
    item_input : int : user ID
    path_user_weights : str : path to the user weights file
    path_user2user_encoded : str : path to the user to encoded mapping file
    path_user2user_decoded : str : path to the user to decoded mapping file
    n : int : number of similar users to find
    return_dist : bool : whether to return distances along with similar users
    neg : bool : if
        True : find least similar users
        False : find most similar users
    Returns a DataFrame of similar users or distances and indices if requested.
    """
    
    try:

        user_weights = joblib.load(path_user_weights)
        user2user_encoded = joblib.load(path_user2user_encoded)
        user2user_decoded = joblib.load(path_user2user_decoded)

        index=item_input
        encoded_index = user2user_encoded.get(index)

        weights = user_weights

        dists = np.dot(weights, weights[encoded_index])
        sorted_dists = np.argsort(dists)

        n=n+1

        if neg:
            closest = sorted_dists[:n]
        else:
            closest = sorted_dists[-n:]
            

        if return_dist:
            return dists, closest
        
        SimilarityArr = []

        for close in closest:
            similarity = dists[close]

            if isinstance(item_input, int):
                decoded_id = user2user_decoded.get(close)
                SimilarityArr.append({
                    "similar_users" : decoded_id, 
                    "similarity" : similarity
                })
        similar_users = pd.DataFrame(SimilarityArr).sort_values(by="similarity", ascending=False)
        similar_users = similar_users[similar_users.similar_users != item_input]
        return similar_users
    except Exception as e:
        print("Error Occured", e)

def get_user_preferences(user_id, path_rating_df, path_anime_df):
    """
    This function retrieves the top animes rated by a user based on their ratings.
    user_id : int : user ID
    path_rating_df : str : path to the ratings dataframe CSV file
    path_anime_df : str : path to the anime dataframe CSV file
    Returns a DataFrame of top animes rated by the user.
    """

    rating_df = pd.read_csv(path_rating_df)
    df = pd.read_csv(path_anime_df)

    animes_watched_by_user = rating_df[rating_df.user_id == user_id]

    user_rating_percentile = np.percentile(animes_watched_by_user.rating, 75)

    animes_watched_by_user = animes_watched_by_user[animes_watched_by_user.rating >= user_rating_percentile]

    top_animes_user = (
        animes_watched_by_user.sort_values(by="rating", ascending=False).anime_id.values
    )

    anime_df_rows = df[df["anime_id"].isin(top_animes_user)]
    anime_df_rows = anime_df_rows[["eng_version", "Genres"]]


    return anime_df_rows

def get_user_recommendations(similar_users, user_pref, path_anime_df, path_synopsis_df, path_rating_df, n=10):
    """
    This function generates anime recommendations for a user based on similar users' preferences.
    similar_users : DataFrame : DataFrame containing similar users
    user_pref : DataFrame : DataFrame containing the user's preferred animes
    path_anime_df : str : path to the anime dataframe CSV file
    path_synopsis_df : str : path to the synopsis dataframe CSV file
    path_rating_df : str : path to the ratings dataframe CSV file
    n : int : number of recommendations to generate
    Returns a DataFrame of recommended animes.
    """

    recommended_animes = []
    anime_list = []

    for user_id in similar_users.similar_users.values:
        pref_list = get_user_preferences(int(user_id), path_rating_df, path_anime_df)

        pref_list = pref_list[~pref_list.eng_version.isin(user_pref.eng_version.values)]

        if not pref_list.empty:
            anime_list.append(pref_list.eng_version.values)

    if anime_list:
            anime_list = pd.DataFrame(anime_list)

            sorted_list = pd.DataFrame(pd.Series(anime_list.values.ravel()).value_counts()).head(n)

            for i, anime_name in enumerate(sorted_list.index):
                n_user_pref = sorted_list[sorted_list.index == anime_name].values[0][0]

                if isinstance(anime_name, str):
                    frame = getAnimeFrame(anime_name, path_anime_df)
                    anime_id = frame.anime_id.values[0]
                    genre = frame.Genres.values[0]
                    synopsis = getSynopsis(int(anime_id), path_synopsis_df)

                    recommended_animes.append({
                        "n" : n_user_pref, 
                        "anime_name" : anime_name, 
                        "Genres" : genre, 
                        "Synopsis": synopsis
                    })
    return pd.DataFrame(recommended_animes).head(n)