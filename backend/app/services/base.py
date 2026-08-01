from typing import Generic, TypeVar

from app.repositories.base import BaseRepository

RepoType = TypeVar("RepoType", bound=BaseRepository)


class BaseService(Generic[RepoType]):
    """
    Abstract Base Service injecting repository dependencies.
    """
    def __init__(self, repository: RepoType):
        self.repository = repository
