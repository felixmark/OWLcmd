import os
from modules.constants import Constants


class Sites(object):
    SEPARATOR_LIGHT = "-" * 80
    SEPARATOR_BOLD = "=" * 80

    @staticmethod
    def get_site(site_filename):
        with open(os.path.join(Constants.FOLDER_SITES, site_filename), "r", encoding='utf-8') as file_site:
            return [Sites.parse_line(line) for line in file_site.read().splitlines(False)]

    @staticmethod
    def parse_line(line):
        line = line.replace('[WEBSITE_TITLE]', Constants.WEBSITE_TITLE)
        line = line.replace('[VERSION]', Constants.VERSION)
        return line
