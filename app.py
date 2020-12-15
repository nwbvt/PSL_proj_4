import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import json
import data
from recommender import get_best_for_genre, user_based_collaborative

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

movies = data.load_movies()
ratings = data.load_ratings()
rated_movies = data.load_movies_rated(movies, ratings)
genres = data.load_genres(movies)
user_ratings = data.load_user_ratings(ratings)

genre_tab = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row(dbc.Col(html.H2(children="By Genre"))),
            dbc.Row(dbc.Col(dcc.Dropdown(id="genre-select", options=[{'label': genre, 'value': genre} for genre in genres]))),
            html.Br(),
            dbc.Row(dbc.Col(html.H3(children="Recommendations"))),
            dbc.Row(dbc.Col(html.Div(id="genre-recs")))
        ]
    )
)

ratings_tab = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row(children=[
                dbc.Col(dcc.Dropdown(id="selected-movie", options=[{'label': movie['name'], 'value': movie_id}
                                                                    for movie_id, movie in movies.iterrows()]), width=9),
                dbc.Col(dbc.Input(id="rating", placeholder="Movie Rating", type="number"), width=2),
                dbc.Col(dbc.Button("Rate", id="rate-movie", color="primary"), width=1)
            ]),
            dbc.Row(dbc.Col(html.H3(children="My ratings"))),
            dbc.Row(dbc.Col(html.Div(id="rating-output"))),
            dbc.Row(dbc.Col(html.Div(id="my-ratings", style={'display': 'none'}))),
            html.Br(),
            dbc.Row(dbc.Col(html.H3(children="Recommendations"))),
            dbc.Row(dbc.Col(html.Div(id="recs")))
        ]
    )
)

app.layout = dbc.Container(children =[
    html.Br(),
    dbc.Row(dbc.Col(html.H1(children="Movie-O-Tron Recommendation Engine"))),
    dbc.Tabs([
        dbc.Tab(genre_tab, label="By Genre"),
        dbc.Tab(ratings_tab, label="By Ratings")
    ])
])

def display_recs(recommendations, n=20):
    header = [html.Thead(html.Tr([html.Th("ID"), html.Th("Movie")]))]
    rows = [
        html.Tr([html.Td(movie_id), html.Td(movie['name'])])
        for movie_id, movie in recommendations[:n].iterrows()
    ]
    body = [html.Tbody(rows)]
    return dbc.Table(header + body, bordered=True, dark=True, hover=True, responsive=True, striped=True)


@app.callback(
    dash.dependencies.Output('genre-recs', 'children'),
    [dash.dependencies.Input('genre-select', 'value')]
)
def update_genre_recs(value):
    if value:
        recommendations = get_best_for_genre(value, rated_movies, min_ratings=100)
        return display_recs(recommendations)
    else:
        return dbc.Alert("Choose a genre", color="primary")


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
        return dbc.Table(header + body, bordered=True, hover=True, responsive=True, striped=True)

@app.callback(
    dash.dependencies.Output('recs', 'children'),
    dash.dependencies.Input('my-ratings', 'children')
)
def update_recs(ratings):
    if ratings:
        recs = user_based_collaborative(json.loads(ratings), user_ratings, movies, num_users=1000)
        return display_recs(recs)
    else:
        return dbc.Alert("Rate some movies", color="primary")


if __name__ == "__main__":
    app.run_server(debug=True)