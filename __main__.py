#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import platform
import requests
from Lifter import Lifter
from version import __version__
from Settings import Settings
from DownloadsDatabase import DownloadsDatabase

class Main:
    """Main class of the wco-dl package"""

    @staticmethod
    def arguments():
        """Function that parses command line arguments"""

        parser = argparse.ArgumentParser(description='wco-dl downloads shows from wcostream.net')

        parser.add_argument('-i', '--input', nargs=1,
                            help='The URL of the show to download.')
        parser.add_argument('-s', '--settings', default="./settings.json", type=str,
                            help='Path to settings file.')
        parser.add_argument('-hd', '--highdef',
                            help='If you wish to get 720p', action="store_true")
        parser.add_argument('-epr', '--episode-range', nargs=1, default='All',
                            help='The episodes to download.')
        parser.add_argument('-ser', '--season-range', nargs=1, default='All',
                            help='The seasons to download.')
        parser.add_argument('-x', '--exclude', nargs=1, default=None,
                            help='The episodes to not download (e.g. OVA).')
        parser.add_argument('-o', '--output', nargs=1,
                            help='The directory to which downloaded files are saved.')
        parser.add_argument('-v', "--verbose", action="store_true",
                            help="Prints important debugging messages on screen.")
        parser.add_argument('-n', '--newest', action='store_true',
                            help='Get the newest episode in the series.')
        parser.add_argument('-sh', '--show_downloaded_animes', action='store_true',
                            help='Show all downloaded shows and episodes')
        parser.add_argument('-us', '--update_shows', action='store_true',
                            help='Update all shows in your database that have new episodes.')
        parser.add_argument('-b', '--batch', nargs=1,
                            help='Get download URLs from batch file (one URL per line).')
        parser.add_argument('-t', '--threads', nargs=1, default=None,
                            help='Create threads to run multiple downloads in parallel.')
        parser.add_argument('-q', "--quiet", action="store_true",
                            help="Do not show download progress.")
        parser.add_argument('--version', action='store_true',
                            help='Print version and exit.')

        return parser.parse_args()


    @staticmethod
    def check_for_new_version():
        """Check if a new version is available and print message"""

        latest_version = requests.get('https://raw.githubusercontent.com/EpicUnknown/wco-dl/master/version.py').text.split("'")[1]
        if (__version__ < latest_version):
            print('Newer version available, on https://github.com/EpicUnknown/wco-dl', end='\n\n')


    @staticmethod
    def main():
        """Main entry point"""

        args = Main.arguments()
        settings = Settings(args.settings)
        database = DownloadsDatabase(settings)

        if settings.get_setting('checkForUpdates'):
            Main.check_for_new_version()

        logger = args.verbose or False
        quiet = args.quiet or False

        if args.version:
            print("Current Version : {0}".format(__version__))
            exit()

        if args.show_downloaded_animes:
            database.print_shows()
            exit()

        if args.verbose:
            logging.basicConfig(format='%(levelname)s: %(message)s', filename="Error Log.log", level=logging.DEBUG)
            logging.debug('You have successfully set the Debugging On.')
            logging.debug("Arguments Provided : {0}".format(args))
            logging.debug("Operating System : {0} - {1} - {2}"
                          .format(platform.system(), platform.release(), platform.version()))
            logging.debug("Python Version : {0} ({1})"
                          .format(platform.python_version(), platform.architecture()[0]))
            logger = True

        if args.highdef:
            args.highdef = '720'
        else:
            args.highdef = '480'

        if args.batch:
            if isinstance(args.threads, list):
                args.threads = args.threads[0]

            with open(args.batch[0], 'r') as anime_list:
                for anime in anime_list:
                    anime = anime.strip(" \n")
                    anime = anime.replace('https://wcostream.net', 'https://www.wcostream.net')
                    Lifter(
                        url=anime,
                        resolution=args.highdef,
                        logger=logger,
                        season=args.season_range,
                        ep_range=args.episode_range,
                        exclude=args.exclude,
                        output=args.output,
                        newest=args.newest,
                        settings=settings,
                        database=database,
                        threads=args.threads,
                        quiet=quiet
                    )

            print('Done')
            exit()

        if args.update_shows:
            print("Updating all shows, this will take a while.")
            for url in database.iterate_urls():
                Lifter(
                    url=url,
                    resolution=args.highdef,
                    logger=logger,
                    season=args.season,
                    ep_range=args.episoderange,
                    exclude=args.exclude,
                    output=args.output,
                    newest=args.newest,
                    settings=settings,
                    database=database,
                    update=True,
                    quiet=quiet
                )
            print('Done')
            exit()

        if args.input is None:
            print("Please enter the required argument. Run __main__.py --help")
            exit()

        if isinstance(args.episoderange, list):
            if '-' in args.episoderange[0]:
                args.episoderange = args.episoderange[0].split('-')
            else:
                args.episoderange = args.episoderange[0]
        if isinstance(args.season, list):
            args.season = args.season[0]
        if isinstance(args.output, list):
            args.output = args.output[0]
        if isinstance(args.exclude, list):
            args.exclude = args.exclude[0].split(',')
        if isinstance(args.threads, list):
            args.threads = args.threads[0]

        Lifter(
            url=args.input[0].replace('https://wcostream.net', 'https://www.wcostream.net'),
            resolution=args.highdef,
            logger=logger,
            season=args.season_range,
            ep_range=args.episode_range,
            exclude=args.exclude,
            output=args.output,
            newest=args.newest,
            settings=settings,
            database=database,
            threads=args.threads,
            quiet=quiet
        )


if __name__ == '__main__':
    Main.main()
