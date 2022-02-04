from abc import ABC, abstractmethod

__all__ = ['Code']


class Code(ABC):
    @abstractmethod
    def tokens(self) -> list[str]:
        """"""

    def __str__(self):
        return "".join(self.tokens())
