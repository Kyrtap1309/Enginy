from abc import ABC, abstractmethod

class EnginePart(ABC):

    @abstractmethod
    def analyze(self):
        pass