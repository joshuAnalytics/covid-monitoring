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
    def preprocess_data(self, df):
        """
        cleans the csse data into a format for plotting
        """

    @abstractmethod
    def plot_data(self, df, weeks_to_display, y_val):
        """
        plot the csse time series data as an altair chart
        """
