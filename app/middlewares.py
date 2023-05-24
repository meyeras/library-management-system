from typing import Any, Callable, Awaitable

from fastapi import Request, Response

def sqlalchemy_to_dict(obj):
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        result[column.name] = value
    return result


class SQLAlchemyToPydanticMiddleware:
    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send):
        async def wrapped_receive():
            return await receive()

        print("Before getting response from the handler")
        response = await self.app(scope, wrapped_receive, send)
        print("After getting response from the handler")
        response_model = getattr(scope.get("endpoint"), "response_model", None)
        print("The response model repr is {0}".format(str(response_model)))
        if response_model and not isinstance(response, response_model):
            response_dict = response.dict()
            response = response_model(**response_dict)

        return response
