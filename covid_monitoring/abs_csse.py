from abc import ABC, abstractmethod


class AbsCsse(ABC):
    """
    abstract class for csse data collection and plotting
    """

    @abstractmethod
    def get_data(self):
        """
        retrieves data from csse repo
        """

    @abstractmethod
    def preprocess_data(self):
        """
        cleans the csse data into a format for plotting
        """

    @abstractmethod
    def plot_data(self):
        """
        plot the csse time series data as an altair chart
        """
