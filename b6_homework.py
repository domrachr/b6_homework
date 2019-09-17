from bottle import route
from bottle import run
from bottle import HTTPError
from bottle import request

import album_hw as album

@route("/albums/<artist>")
def albums(artist):
    """
    Принимает параметры artists из GET-запроса и ищет в базе все его альбомы.
    Выводит количество найденных альбомов и их список
    Пример строки-запроса в браузере:
        http://localhost:8080/albums/Beatles
    """    
    session, albums_list = album.find(artist = artist)
    if not albums_list:
        message = "Альбомов {} не найдено".format(artist)
        result = HTTPError(404, message)
    else:
        album_names = [album.album for album in albums_list]
        result = "В базе найдено {} альбомов {}<br>".format(len(album_names), artist)
        result += "Список альбомов:<br>"
        result += "<br>".join(album_names)
    return result

@route("/albums",method="POST")
def albums():
    """
    Принимает POST-запрос на добавление альбома и, если такого ещё нет, добавляет его в базу
    Пример запроса через httpie:
        http -f POST http://localhost:8080/albums artist="Beatles" genre="Rock and roll" album="Gold Collection" year="2019"
    """    

    try: 
        # используем блок try для перехвата исключений при вводе некорректных данных
        user_data = {
            "year": int(request.forms.get("year")),
            "artist": request.forms.get("artist"),
            "genre": request.forms.get("genre"),
            "album": request.forms.get("album")
        }
    except ValueError:
        # исключение возникнет, если в параметре year передается не число
        result = HTTPError(400, "Некорректные параметры")
    else:
        # если все данные переданы корректно
        al = album.Album(year=user_data["year"], artist=user_data["artist"], genre=user_data["genre"], album=user_data["album"])
        # ищем в базе альбом со всеми параметрами из POST-запроса
        session, albums_list = album.find(year=user_data["year"], artist=user_data["artist"], genre=user_data["genre"], album=user_data["album"])
        if albums_list:
            # если такой альбом найден - сообщаем об этом со статусом 409
            result = HTTPError(409, "Такой альбом уже есть в базе")
        else:
            # если такого альбома нет в базе - добавляем его и сохраняем.
            session.add(al)
            session.commit()
            result = "Альбом добавлен в базу"

    return result


if __name__ == "__main__":
    run(host="localhost", port=8080, debug=True)