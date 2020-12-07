import os
from modules.constants import Constants


class Sites(object):
    SEPARATOR_LIGHT = "-" * 80
    SEPARATOR_BOLD = "=" * 80

    @staticmethod
    def get_site(site_filename):
        with open(os.path.join(Constants.FOLDER_SITES, site_filename), "r") as file_site:
            return file_site.read().splitlines(False)
