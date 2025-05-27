from abc import ABC, abstractmethod

class BaseSensor(ABC):
    @abstractmethod
    def read(self) -> float:
        """Return the current sensor reading as a float (e.g., temperature in Celsius)"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the sensor's name"""
        pass
