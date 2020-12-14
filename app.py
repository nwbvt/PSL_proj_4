import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import json
import data
from recommender import get_best_for_genre, recommend_from_ratings

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

movies = data.load_movies()
ratings = data.load_ratings()
rated_movies = data.load_movies_rated(movies, ratings)
genres = data.load_genres(movies)
user_ratings = data.load_user_ratings(ratings)


app.layout = html.Div(children =[
    html.H1(children="Movie Recommender"),
    html.H2(children="By Genre"),
    dcc.Dropdown(id="genre-select", options=[{'label': genre, 'value': genre} for genre in genres]),
    html.Br(),
    html.H3(children="My recommendations"),
    html.Div(id="genre-recs"),
    html.Hr(),
    html.H2(children="By ratings"),
    html.H3(children="My ratings"),
    html.Div(id="my-ratings", style={'display': 'none'}),
    html.Div(children=[
        dcc.Dropdown(id="selected-movie", options=[{'label': movie['name'], 'value': movie_id} for movie_id, movie in movies.iterrows()]),
        dbc.Input(id="rating", placeholder="Movie Rating", type="number"),
        html.Button("Rate", id="rate-movie"),
        html.Div(id="rating-output")
    ]),
    html.Br(),
    html.H3(children="My recommendations"),
    html.Div(id="recs"),
])

def display_recs(recommendations):
    header = [html.Thead(html.Tr([html.Th("ID"), html.Th("Movie")]))]
    rows = [
        html.Tr([html.Td(movie_id), html.Td(movie['name'])])
        for movie_id, movie in recommendations.iterrows()
    ]
    body = [html.Tbody(rows)]
    return dbc.Table(header + body)


@app.callback(
    dash.dependencies.Output('genre-recs', 'children'),
    [dash.dependencies.Input('genre-select', 'value')]
)
def update_genre_recs(value):
    if value:
        recommendations = get_best_for_genre(value, rated_movies, min_ratings=100, n=20)
        return display_recs(recommendations)

@app.callback(
    dash.dependencies.Output('my-ratings', 'children'),
    dash.dependencies.Input('rate-movie', 'n_clicks'),
    dash.dependencies.State('my-ratings', 'children'),
    dash.dependencies.State('selected-movie', 'value'),
    dash.dependencies.State('rating', 'value'))
def rate_movie(clicks, current, movie, rating):
    if movie:
        current = json.loads(current) if current else {}
        current[movie] = rating
        return json.dumps(current)

@app.callback(
    dash.dependencies.Output('rating-output', 'children'),
    dash.dependencies.Input('my-ratings', 'children')
)
def update_ratings(ratings):
    if ratings:
        ratings = json.loads(ratings)
        header = [html.Thead(html.Tr([html.Th("ID"), html.Th("Movie"), html.Th("Rating")]))]
        rows = [
            html.Tr([html.Td(movie_id), html.Td(movies.loc[int(movie_id)]['name']), html.Td(f"{rating:.2f}")])
            for movie_id, rating in ratings.items()
        ]
        body = [html.Tbody(rows)]
        return dbc.Table(header + body)

@app.callback(
    dash.dependencies.Output('recs', 'children'),
    dash.dependencies.Input('my-ratings', 'children')
)
def update_recs(ratings):
    if ratings:
        recs = recommend_from_ratings(json.loads(ratings), user_ratings, movies, num_users=1000, n=20)
        return display_recs(recs)


if __name__ == "__main__":
    app.run_server(debug=True)