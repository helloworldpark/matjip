from abc import ABC, abstractmethod


class URL(ABC):

    @abstractmethod
    def url(self):
        pass
