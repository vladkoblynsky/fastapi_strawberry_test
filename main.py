from typing import Any, List

import strawberry
from fastapi import FastAPI, Depends, Request, Response
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse
from strawberry.fastapi import GraphQLRouter
from strawberry.dataloader import DataLoader

from app import models
from app.auth.schema import Mutation as AuthMutation
from app.dataloaders import load_users, loader
from app.models import User
from app.post.schema import Mutation as PostMutation
from app.database import SessionLocal, engine
from app.user.crud import get_user_by_email, get_users_by_ids
from app.post.schema import Query as PostQuery
from app.user.schema import Query as UserQuery

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Settings(BaseModel):
    authjwt_secret_key: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    # Configure application to store and get JWT from cookies
    authjwt_token_location: set = {"cookies"}
    # Disable CSRF Protection for this example. default is True
    authjwt_cookie_csrf_protect: bool = False
    # authjwt_access_cookie_key: str = 'access'
    # authjwt_refresh_cookie_key: str = 'refresh'


@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@strawberry.type
class Query(UserQuery, PostQuery):
    pass


@strawberry.type
class Mutation(AuthMutation, PostMutation):
    pass


async def get_context(request: Request, response: Response, db: Session = Depends(get_db),
                      authorize: AuthJWT = Depends()):
    authorize.jwt_optional()
    user_email = authorize.get_jwt_subject()
    user = get_user_by_email(db, user_email) if user_email else None
    return {
        "db": db,
        "authorize": authorize,
        "request": request,
        "response": response,
        "user": user,
        "loader": loader
    }


def get_graphiql_html() -> str:
    path = "./static/graphiql.html"
    with open(path) as f:
        template = f.read()
    return template.replace("{{ SUBSCRIPTION_ENABLED }}", "true")


schema = strawberry.Schema(query=Query, mutation=Mutation)


class MyGraphqlRouter(GraphQLRouter):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Get the HTTP POST route added by the base constructor.
        base_http_route = next(
            route
            for route in self.routes
            if isinstance(route, APIRoute) and "POST" in route.methods
        )

        # Remove the original route from the defined routes.
        self.routes.remove(base_http_route)

        # Wrap the original route.
        async def handle_http_query(
                request: Request,
                response: Response,
                context: Any = Depends(self.context_getter),
                root_value: Any = Depends(self.root_value_getter),
        ) -> Response:
            route_response: Response = await base_http_route.endpoint(
                request=request,
                context=context,
                root_value=root_value,
            )
            # Add ephemeral response headers.
            for key, value in response.raw_headers:
                route_response.raw_headers.append((key, value))
            return route_response

        # Register the wrapper route.
        self.add_api_route("", handle_http_query, include_in_schema=True, methods=["POST"])
        # Allow a trailing slash.
        self.add_api_route("/", handle_http_query, include_in_schema=False, methods=["POST"])

    def get_graphiql_response(self) -> HTMLResponse:
        html = get_graphiql_html()
        return HTMLResponse(html)


graphql_app = MyGraphqlRouter(schema, debug=False, context_getter=get_context)

app.include_router(graphql_app, prefix="/graphql")
