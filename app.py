import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import data
from recommender import get_best_for_genre

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

movies = data.load_movies()
ratings = data.load_ratings()
rated_movies = data.load_movies_rated(movies, ratings)
genres = data.load_genres(movies)


app.layout = html.Div(children =[
    html.H1(children="Movie Recommender"),
    dcc.Dropdown(id="genre-select", options=[{'label': genre, 'value': genre} for genre in genres]),
    html.Div(id="genre-recs")
])

@app.callback(
    dash.dependencies.Output('genre-recs', 'children'),
    [dash.dependencies.Input('genre-select', 'value')]
)
def update_genre_recs(value):
    if value:
        recommendations = get_best_for_genre(value, rated_movies)
        header = [html.Thead(html.Tr([html.Th("ID"), html.Th("Movie"), html.Th("Rating")]))]
        rows = [
            html.Tr([html.Td(movie_id), html.Td(movie['name']), html.Td(f"{movie['rating'] + 3:.2f}")])
            for movie_id, movie in recommendations[['name', 'rating']].iterrows()
        ]
        body = [html.Tbody(rows)]
        return dbc.Table(header + body)

if __name__ == "__main__":
    app.run_server(debug=True)