
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QImage, QPalette, QBrush
from PyQt5.QtGui import QPixmap

import pandas as pd
import numpy as np

import plotly.graph_objects as go
import plotly.express as px


df = pd.read_csv("./imdb_top_1000.csv")
df['Gross'] = df['Gross'].str.replace(',', '').astype('float')
df['Runtime'] = df['Runtime'].apply(lambda text: text.split()[0]).astype('int')
df['Certificate'] = df['Certificate'].replace(np.nan, 'Unknown')

poster_link = np.array(df['Poster_Link'])
series_title = np.array(df['Series_Title'])
released_year =np.array(df['Released_Year'])
certificate = np.array(df['Certificate'])
runtime = np.array(df['Runtime'])

imdb_rating = np.array(df['IMDB_Rating'])
overview = np.array(df['Overview'])
meta_score = np.array(df['Meta_score'])
director = np.array(df['Director'])
gross = np.array(df['Gross'])
star1 = np.array(df['Star1'])
star2 = np.array(df['Star2'])
star3 = np.array(df['Star3'])
star4 = np.array(df['Star4'])


data = pd.read_csv("./imdb_top_1000.csv")
data.dropna(inplace=True, subset=("Gross"))

all_directors = data.Director.values
data.loc[:,"Gross"] = data.Gross.map(lambda x: x.replace(",",""))

data.Released_Year.replace("PG", "1990", inplace=True)
data.Released_Year = data.Released_Year.astype(int)
data.Gross = data.Gross.astype(int)

director_sorted_movies = {}
for director in all_directors:
    director_sorted_movies[director] = data[data.Director == director].reset_index(drop=True)

# print(director_sorted_movies["Frank Darabont"].shape)
nodes_x = {}
nodes_y = {}
edges_x = {}
edges_y = {}

nof_directors = all_directors.shape[0]

for director in all_directors:
    director_nodes_x = []
    director_nodes_y = []
    director_edges_x = []
    director_edges_y = []

    for i in range(director_sorted_movies[director].shape[0]):
        movie = director_sorted_movies[director].loc[i]
        director_nodes_x.append(movie.Released_Year)
        director_nodes_y.append(movie.Meta_score) #dodajemy lokalizacje kropek

    for i in range(len(director_nodes_x)):
        for j in range(i + 1, len(director_nodes_x)):
            director_edges_x.append(director_nodes_x[i])
            director_edges_x.append(director_nodes_x[j])
            director_edges_x.append(None)
            director_edges_y.append(director_nodes_y[i])
            director_edges_y.append(director_nodes_y[j])
            director_edges_y.append(None) #dodajemy lokalizacje linii
    nodes_x[director] = director_nodes_x #przypisujemy do danego reżysera
    nodes_y[director] = director_nodes_y
    edges_x[director] = director_edges_x
    edges_y[director] = director_edges_y

parsed_nodes_x = []
parsed_edges_x = []
parsed_nodes_y = []
parsed_edges_y = []
label_for_point = []
for director in all_directors:
    parsed_nodes_x += nodes_x[director]
    parsed_nodes_y += nodes_y[director]
    parsed_edges_x += edges_x[director]
    parsed_edges_y += edges_y[director]
    range_size = director_sorted_movies[director].shape[0] #zmieniamy słownik na liste dla każdego reżysera
    for i in range(range_size):
        movie = director_sorted_movies[director].loc[i]
        label_for_point += [f"{director} ({range_size}): {movie.Series_Title}"] #to dla hover info

graph_nodes = go.Scatter(x=parsed_nodes_x, y=parsed_nodes_y,mode='markers',hoverinfo="text", hovertext=label_for_point,marker=dict(size=8, line_width=2))

graph_edges = go.Scatter(x=parsed_edges_x, y=parsed_edges_y, line=dict(width=0.1, color='#888'), hoverinfo='none', mode='lines')

def dots():
    fig = go.Figure(data=[graph_nodes,graph_edges], layout=go.Layout(title='Filmy i reżyserzy', titlefont_size=16, showlegend=False, hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40), xaxis=dict(showgrid=True, zeroline=False, showticklabels=True),
                    yaxis=dict(showgrid=True, zeroline=False, showticklabels=True)))
    fig.show()

#funkcje grafu(lewa strona)
def years_of_release():
    fig = px.histogram(data_frame=df.sort_values(by='Released_Year'), x='Released_Year', color_discrete_sequence=['gold'])

    fig.update_layout(font=dict(family='Calibri', size=18, color='white'), title=dict(text='<b>Filmy w latach 1920 - 2020<b>', font=dict(size=30), x=.5),
                      paper_bgcolor= 'black', plot_bgcolor='black', xaxis = dict(title='Rok premiery', showgrid=False), yaxis=dict(title='Ilość', showgrid=False))
    fig.show()

df['genre'] = df['Genre'].apply(lambda text: text.split(',')[0])
df.drop(columns='Genre', inplace=True)

genre = np.array(df['genre'])

def bar_plot(column_name, data_frame=df, tribe='value_counts', by=None, limit=3, **kwargs):

    if type(column_name) != str or column_name not in data_frame.columns:
        raise ValueError('Nie ma takiej kolumny')

    if type(limit) != int:
        raise ValueError(f'limit ma być int, a użyto {type(limit)}')

    if tribe == 'sort':
        if not by or by not in data_frame.columns:
            raise ValueError('by - musi być zawarte w danych')
        data = data_frame.sort_values(by=by, ascending=False).head(limit)
        y = data[by].values
        x = data[column_name]
        title = by

    elif tribe == 'value_counts':
        data = data_frame[column_name].value_counts().head(limit)
        x = data.index
        y = data.values
        title = column_name

    fig = px.bar(x=x, y=y, color_discrete_sequence=['gold'])

    fig.update_layout(font=dict(family='Calibri', size=18, color='white'), title=dict(text=f'<b>Filmy IMDB - {title}', font=dict(size=30), x=.5),
                      paper_bgcolor='black', plot_bgcolor='black', xaxis=dict(title=f'{title}', showgrid=False), yaxis=dict(title=f'Ilość', showgrid=False))
    fig.show()

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "TOP 1000 FILMÓW IMDB"
        self.left = 100
        self.top = 100
        self.width = 1400
        self.height = 800
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)


        oImage = QImage("./golden.jpg")
        sImage = oImage.scaled(QSize(800, 1400))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))
        self.setPalette(palette)

        layout1 = QGridLayout()

        label = QLabel()
        pixmap = QPixmap('./imdb2.png')
        label.setPixmap(pixmap)
        layout1.addWidget(label, 1, 1)

        label2 = QLabel()
        pixmap2 = QPixmap('./film.png')
        label2.setPixmap(pixmap2)
        layout1.addWidget(label2, 1, 0)

        label3 = QLabel()
        pixmap3 = QPixmap('./film2.png')
        label3.setPixmap(pixmap3)
        layout1.addWidget(label3, 1, 2)

        self.genre = QPushButton("Gatunek filmu", self)
        self.IMDB_Rating = QPushButton("Ocena IMDB", self)
        self.Director = QPushButton("Reżyser", self)
        self.Certificate = QPushButton("Certyfikat", self)
        self.Star1 = QPushButton("Gwiazda nr 1", self)
        self.Star2 = QPushButton("Gwiazda nr 2", self)
        self.Star3 = QPushButton("Gwiazda nr 3", self)
        self.Star4 = QPushButton("Gwiazda nr 4", self)
        self.Runtime = QPushButton("Sortowanie po czasie filmu", self)
        self.Released_Year = QPushButton("Tabela kolumnowa - ilość filmów w latach 1920-2020", self)
        self.dots = QPushButton("Graf połączeń film-reżyser (oś X - rok wydania, oś Y - Wynik Metascore)", self)

        self.nlimit = QLabel("<b>Podaj limit wykresu kolumnowego(domyślnie 3):<b>")
        self.limit = QSpinBox(self)
        self.limit.setMaximum(1000)

        layout1.addWidget(self.limit, 12, 1)
        layout1.addWidget(self.nlimit, 12, 0)

        layout1.addWidget(self.dots, 2, 1)
        self.dots.clicked.connect(dots)

        layout1.addWidget(self.genre, 2, 0)
        layout1.addWidget(self.IMDB_Rating, 3, 0)
        layout1.addWidget(self.Director, 4, 0)
        layout1.addWidget(self.Certificate, 5, 0)
        layout1.addWidget(self.Star1, 6, 0)
        layout1.addWidget(self.Star2, 7, 0)
        layout1.addWidget(self.Star3, 8, 0)
        layout1.addWidget(self.Star4, 9, 0)
        layout1.addWidget(self.Released_Year, 10, 0)
        layout1.addWidget(self.Runtime, 11, 0)

        self.filtration_name = QLineEdit("Tu wpisz o co chcesz zapytać", self)
        layout1.addWidget(self.filtration_name, 2, 2)

        self.actor = QPushButton("Aktor", self)
        self.actor.setToolTip('W pole wpisz jaki aktor/aktorka Cię interesuje, my wypiszemy w jakich filmach grał/grała!')
        layout1.addWidget(self.actor, 3, 2)

        def filtr_aktor():
            # aktor= input("Jaki aktor / aktorka Cię interesuje? ")
            aktor = self.filtration_name.text()
            maks = 0
            tytul = []
            intro = "Ten aktor/aktorka jest znany/znana z filmów: \n"
            n = len(star1)
            again = 1
            while again == 1:
                for i in range(n):
                    if star1[i] == aktor or star2[i] == aktor or star3[i] == aktor or star4[i] == aktor:
                        tytul.append(series_title[i])
                        maks = maks + 1
                if maks == 0:
                    def show_message_box():
                        message_box = QMessageBox()
                        message_box.setText("Przepraszamy, ale nie posiadamy danych dotyczących wybranego aktora. Podaj dane innego aktora.")
                        message_box.setWindowTitle("ODPOWIEDŹ")
                        message_box.exec_()
                    show_message_box()
                    break
                else:
                    again = 0
            print("Filmy, w których grał / grała", aktor, "to", tytul)

            if tytul != []:
                def show_message_box():
                    message_box = QMessageBox()
                    listToStr = ', \n'.join(map(str, tytul))
                    message_box.setText(intro + listToStr)
                    message_box.setWindowTitle("ODPOWIEDŹ")
                    message_box.exec_()
                show_message_box()

        self.actor.clicked.connect(filtr_aktor)

        self.runtime_filtr = QPushButton("Długość filmu", self)
        self.runtime_filtr.setToolTip('W pole wpisz tytuł filmu jaki Cię interesuje, my wypiszemy jest czas trwania!')
        layout1.addWidget(self.runtime_filtr, 4, 2)


        def czas_trwania():
            # tytul = input("Podaj tytuł filmu: ")
            tytul = self.filtration_name.text()
            n = len(series_title)
            again = 1
            intro = 'Czas trwania filmu '
            mid = ' wynosi '
            end = ' min.'
            czas_trwania = 0
            while again == 1:
                for i in range(n):
                    if series_title[i] == tytul:
                        czas_trwania = runtime[i]
                if czas_trwania == 0:
                    def show_message_box():
                        message_box = QMessageBox()
                        message_box.setText("Przepraszamy, ale podany tytuł nie istnieje w naszej bazie. Sprawdź, czy tytuł został wpisany prawidłowo lub podaj inny tytuł.")
                        message_box.setWindowTitle("BŁĄD")
                        message_box.exec_()
                    show_message_box()
                    break
                else:
                    again = 0
            print('Czas trwania filmu', tytul, 'wynosi', czas_trwania, 'min.')
            if czas_trwania != 0:
                def show_message_box():
                    message_box = QMessageBox()
                    message_box.setText(intro + str(tytul) + mid + str(czas_trwania) + end)
                    message_box.setWindowTitle("ODPOWIEDŹ")
                    message_box.exec_()
                show_message_box()

        self.runtime_filtr.clicked.connect(czas_trwania)

        self.naj_kasowy = QPushButton("Najbardziej kasowy film", self)
        self.naj_kasowy.setToolTip('Pwoemy Ci jaki film jest najbardziej kasowy!')
        layout1.addWidget(self.naj_kasowy, 5, 2)

        def najbardziej_kasowy_film_z_calej_bazy():
            maks = 0
            tytul = ''
            intro = "Ten film to: "
            wynik = " z wynikiem "
            dollars = " dolarów"
            n = len(gross)
            for i in range(n):
                if gross[i] > maks:
                    maks = gross[i]
                    tytul = series_title[i]
            print("Najbardziej kasowy film to", tytul, "z wynikiem", maks, "dolarów")

            def show_message_box():
                message_box = QMessageBox()
                message_box.setText(intro + str(tytul) + wynik + str(maks) + dollars)
                message_box.setWindowTitle("ODPOWIEDŹ")
                message_box.exec_()
            show_message_box()

        self.naj_kasowy.clicked.connect(najbardziej_kasowy_film_z_calej_bazy)

        self.naj_kasowy_rok = QPushButton("Najbardziej kasowy film w danym roku", self)
        self.naj_kasowy_rok.setToolTip('Powiemy Ci jaki film jest najbardziej kasowy w danym roku (podaj go u góry)!')
        layout1.addWidget(self.naj_kasowy_rok,   6, 2)

        def najbardziej_kasowy_film():
            rok = self.filtration_name.text()
            # rok = input("Dla jakiego roku chcesz poznać najbardziej kasowy film:  ")
            maks = 0
            tytul = ''
            intro = "Ten film to: "
            wynik = " z wynikiem "
            dollars = " dolarów"
            n = len(gross)
            again = 1
            while again == 1:
                for i in range(n):
                    if released_year[i] == rok:
                        if gross[i] > maks:
                            maks = gross[i]
                            tytul = series_title[i]
                if maks == 0:
                    def show_message_box():
                        message_box = QMessageBox()
                        message_box.setText("Przepraszamy, ale nie posiadamy danych dla podanego roku. Podaj inny rok.")
                        message_box.setWindowTitle("ODPOWIEDŹ")
                        message_box.exec_()
                    show_message_box()
                    break
                else:
                    again = 0
            print("Najbardziej kasowy film to", tytul, "z wynikiem", maks, "dolarów")
            if maks != 0:
                def show_message_box():
                    message_box = QMessageBox()
                    message_box.setText(intro + str(tytul) + wynik + str(maks) + dollars)
                    message_box.setWindowTitle("ODPOWIEDŹ")
                    message_box.exec_()
                show_message_box()

        self.naj_kasowy_rok.clicked.connect(najbardziej_kasowy_film)

        self.opis = QPushButton("Opis filmu", self)
        self.opis.setToolTip('Podamy Ci opis do danego filmu (podaj tytuł u góry)!')
        layout1.addWidget(self.opis, 7, 2)


        def opis_filmu():
            # tytul = input("Podaj tytuł filmu: ")
            tytul = self.filtration_name.text()
            n = len(series_title)
            opis = ''
            intro = "Opis tego filmu po angielsku to: \n"
            again = 1
            while again == 1:
                for i in range(n):
                    if series_title[i] == tytul:
                        opis = overview[i]
                if opis == '':
                    def show_message_box():
                        message_box = QMessageBox()
                        message_box.setText("Przepraszamy, ale podany tytuł nie istnieje w naszej bazie. Sprawdź, czy tytuł został wpisany prawidłowo lub podaj inny tytuł.")
                        message_box.setWindowTitle("ODPOWIEDŹ")
                        message_box.exec_()
                    show_message_box()
                    break
                else:
                    again = 0
            print(opis)
            if opis != '':
                def show_message_box():
                    message_box = QMessageBox()
                    message_box.setText(intro + str(opis))
                    message_box.setWindowTitle("ODPOWIEDŹ")
                    message_box.exec_()
                show_message_box()

        self.opis.clicked.connect(opis_filmu)

        self.ocena = QPushButton("Najlepiej oceniane filmy", self)
        self.ocena.setToolTip('Podaj gatunek filmu, a my podamy nalepiej oceniane filmy z tego gatunku!')
        layout1.addWidget(self.ocena, 8, 2)


        def najlepiej_oceniane_filmy():
            # gatunek = input("Podaj interesujący Cię gatunek filmów: ")
            gatunek = self.filtration_name.text()
            intro = "Te filmy to: \n"
            pause = ", \n"
            ocena = []
            n = len(genre)
            again = 1
            while again == 1:
                for i in range(n):
                    if genre[i] == gatunek:
                        ocena.append([imdb_rating[i], series_title[i]])
                if len(ocena) == 0:
                    def show_message_box():
                        message_box = QMessageBox()
                        message_box.setText("Przepraszamy, ale nie posiadamy filmów z tego gatunku. Podaj inny gatunek.")
                        message_box.setWindowTitle("ODPOWIEDŹ")
                        message_box.exec_()
                    show_message_box()
                    break
                else:
                    ocena.sort()
                    again = 0

            def show_message_box():
                message_box = QMessageBox()
                message_box.setText(intro + ocena[-1][1] + pause + ocena[-2][1] + pause + ocena[-3][1] + pause + ocena[-4][1] + pause + ocena[-5][1])
                message_box.setWindowTitle("ODPOWIEDŹ")
                message_box.exec_()
            show_message_box()
            print('Najlepiej oceniane filmy to:\n', ocena[-1][1], '\n', ocena[-2][1], '\n', ocena[-3][1], '\n', ocena[-4][1], '\n', ocena[-5][1])

        self.ocena.clicked.connect(najlepiej_oceniane_filmy)

        self.setLayout(layout1)
        self.show()

        self.Released_Year.clicked.connect(lambda: years_of_release())
        self.genre.clicked.connect(lambda: bar_plot('genre', limit=int(self.limit.value())) if int(self.limit.value()) != 0 else bar_plot('genre', limit=3))
        self.IMDB_Rating.clicked.connect(lambda: bar_plot('IMDB_Rating', limit=int(self.limit.value())) if int(self.limit.value()) != 0 else bar_plot('IMDB_Rating', limit=3))
        self.Director.clicked.connect(lambda: bar_plot('Director', limit=int(self.limit.value())) if int(self.limit.value()) != 0 else bar_plot('Director', limit=3))
        self.Certificate.clicked.connect(lambda: bar_plot('Certificate', limit=int(self.limit.value())) if int(self.limit.value()) != 0 else bar_plot('Certificate', limit=3))
        self.Star1.clicked.connect(lambda: bar_plot('Star1', limit=int(self.limit.value())) if int(self.limit.value()) != 0 else bar_plot('Star1', limit=3))
        self.Star2.clicked.connect(lambda: bar_plot('Star2', limit=int(self.limit.value())) if int(self.limit.value()) != 0 else bar_plot('Star2', limit=3))
        self.Star3.clicked.connect(lambda: bar_plot('Star3', limit=int(self.limit.value())) if int(self.limit.value()) != 0 else bar_plot('Star3', limit=3))
        self.Star4.clicked.connect(lambda: bar_plot('Star4', limit=int(self.limit.value())) if int(self.limit.value()) != 0 else bar_plot('Star4', limit=3))
        self.Runtime.clicked.connect(lambda: bar_plot('Series_Title', tribe = 'sort', by='Runtime', limit= int(self.limit.value())) if int(self.limit.value()) != 0 else bar_plot('Series_Title', tribe = 'sort', by='Runtime', limit=3))

app = QApplication(sys.argv)
ex = App()
app.exec_()