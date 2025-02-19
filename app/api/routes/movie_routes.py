from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.handlers.movie_handler import MovieHandler
from app.schemas.movie import MovieCreate, MovieResponse, MovieListResponse

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.post("/", response_model=MovieResponse, status_code=201)
def create_movie(
    movie_data: MovieCreate, db: Session = Depends(get_db)
) -> MovieResponse:
    """Cria um novo filme e retorna os dados formatados."""
    return MovieHandler.create_movie(db, movie_data)


@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie_by_id(movie_id: int, db: Session = Depends(get_db)) -> MovieResponse:
    """Obtém um filme pelo ID."""
    return MovieHandler.get_movie_by_id(db, movie_id)


@router.get("/title/{title}", response_model=MovieResponse)
def get_movie_by_title(title: str, db: Session = Depends(get_db)) -> MovieResponse:
    """Obtém um filme pelo título."""
    return MovieHandler.get_movie_by_title(db, title)


@router.get("/", response_model=MovieListResponse)
def get_all_movies(db: Session = Depends(get_db)) -> MovieListResponse:
    """Obtém todos os filmes cadastrados."""
    return MovieHandler.get_all_movies(db)


@router.delete("/{movie_id}", status_code=204)
def delete_movie(movie_id: int, db: Session = Depends(get_db)) -> None:
    """Deleta um filme pelo ID."""
    return MovieHandler.delete_movie(db, movie_id)
