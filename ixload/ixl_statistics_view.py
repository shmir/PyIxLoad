"""
Classes and utilities to read IxLoad statistics views (==csv files).

@author yoram@ignissoft.com
"""

from os import path
import csv
from collections import OrderedDict

from ixload.ixl_app import IxlApp


class IxlStatView(object):

    def __init__(self, view, results_dir=None):
        """
        :param view: requested statistics view.
        :param results_dir: results directory, default - controller results directory.
        """

        self.view = view
        if not results_dir:
            controller = IxlApp.controller
            results_dir = controller.results_dir
        self.results_dir = results_dir

    def read_stats(self):
        """ Reads the statistics view from the CSV file and saves it in statistics dictionary.

        The original CSV file is saved in self.csv list so the test can access the raw data at any time.
        """

        with open(path.join(self.results_dir.replace('\\', '/'), self.view + '.csv'), 'rb') as csvfile:
            self.csv_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            self.csv = []
            for row in self.csv_reader:
                self.csv.append(row)

        self.statistics = OrderedDict()
        for row in self.csv:
            if row:
                row_header = row.pop(0)
                if row_header.replace('.', '').isdigit():
                    self.statistics[int(float(row_header))] = row
                elif 'Elapsed' in row_header:
                    self.captions = row

    def get_all_stats(self):
        """
        :returns: all statistics values for all time stamps.
        """

        all_stats = OrderedDict()
        for time_stamp in self.statistics:
            all_stats[time_stamp] = self.get_time_stamp_stats(time_stamp)
        return all_stats

    def get_time_stamp_stats(self, time_stamp):
        """
        :param obj_name: requested object name
        :returns: all statistics values for the requested time stamp.
        """

        return OrderedDict(zip(self.captions, self.statistics[time_stamp]))

    def get_stats(self, stat_name):
        """
        :param stat_name: requested statistics name.
        :returns: all values of the requested statistic for all objects.
        """

        return [self.get_stat(r, stat_name) for r in self.statistics.keys()]

    def get_stat(self, time_stamp, stat_name):
        """
        :param time_stamp: requested time stamp.
        :param stat_name: requested statistics name.
        :return: str, the value of the requested statics for the requested time stamp.
        """

        return self.statistics[time_stamp][self.captions.index(stat_name)]

    def get_counters(self, stat_name):
        """
        :param stat_name: requested statistics name.
        :returns: all values of the requested statistic for all objects.
        """

        return [self.get_counter(r, stat_name) for r in self.statistics.keys()]

    def get_counter(self, time_stamp, stat_name):
        """
        :param time_stamp: requested time stamp.
        :param stat_name: requested statistics name.
        :return: int, the value of the requested statics for the requested time stamp.
        """

        return int(self.statistics[time_stamp][self.captions.index(stat_name)])
