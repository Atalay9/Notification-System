from abc import ABC, abstractmethod

class AlarmChannel(ABC):


    @abstractmethod
    def send(self, message: str):
        pass