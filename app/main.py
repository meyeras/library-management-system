from fastapi import FastAPI

app = FastAPI()


@app.get("/books")
def get_all_books():
    return [{"Book title": "some title" ,"Book author": "some author", "Book isbn": 93838}]

    