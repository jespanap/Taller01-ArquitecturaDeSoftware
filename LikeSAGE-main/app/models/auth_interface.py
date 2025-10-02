from abc import ABC, abstractmethod


class UserAuthenticator(ABC):
    @abstractmethod
    def authenticate(self, username: str, password: str):
        pass
