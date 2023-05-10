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

        parser.add_argument('-i', '--input', nargs="*",
                            help='The URL of the show to download.')
        parser.add_argument('-o', '--output',
                            help='The directory to which downloaded files are saved.')
        parser.add_argument('-b', '--batch', nargs="*",
                            help='Get download URLs from batch file (one URL per line).')
        parser.add_argument('-s', '--settings', default="./settings.json", type=str,
                            help='Path to settings file.')
        parser.add_argument('-eps', '--episodes', nargs=1, default='All',
                            help='The episodes to download. Can be a range, for example -eps 1-4')
        parser.add_argument('-ses', '--seasons', nargs=1, default='All',
                            help='The seasons to download. Can be a range, for example -ses 1-4')
        parser.add_argument('-xeps', '--exclude-episodes', nargs=1, default=None,
                            help='The episodes to not download (e.g. OVA). Can be a range, for example -xeps 1-4')
        #parser.add_argument('-xses', '--exclude-seasons', nargs="1", default=None,
        #                    help='The episodes to not download (e.g. OVA). Can be a range, for example -xsps 1-4')
        parser.add_argument('-n', '--newest', action='store_true',
                            help='Get the newest episode in the series.')
        parser.add_argument('-sh', '--show_downloaded_animes', action='store_true',
                            help='Show all downloaded shows and episodes')
        parser.add_argument('-us', '--update_shows', action='store_true',
                            help='Update all shows in your database that have new episodes.')
        parser.add_argument('-hd', '--highdef',
                            help='If you wish to get 720p', action="store_true")
        parser.add_argument('-t', '--num-threads', default=1, type=int,
                            help='Create this many threads to run multiple downloads in parallel.')
        parser.add_argument('-v', "--verbose", action="store_true",
                            help="Prints important debugging messages on screen.")
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

        if args.version:
            print("Current Version : {0}".format(__version__))
            exit()

        settings = Settings(args.settings)
        database = DownloadsDatabase(settings)

        if settings.get_setting('checkForUpdates'):
            Main.check_for_new_version()

        logger = args.verbose or False
        quiet = args.quiet or False
        urls = []

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

        if args.update_shows:
            print("Updating all shows in database, this may take a while.")
            urls = list(database.iterate_urls())
            for url in urls:
                Lifter(
                    url=url,
                    resolution=args.highdef,
                    logger=logger,
                    season=args.seasons,
                    ep_range=args.episodes,
                    exclude=args.exclude_episodes,
                    output=args.output,
                    newest=args.newest,
                    settings=settings,
                    database=database,
                    update=True,
                    quiet=quiet
                )
            print('Done updating shows in data')
            # Clear the urls list, in the next step normal downloads are processed
            urls = []

        for batch_file in args.batch or []:
            with open(batch_file, 'r') as batch_urls:
                for url in batch_urls:
                    url = url.strip(" \n")
                    url = url.replace('https://wcostream.net', 'https://www.wcostream.net')
                    urls.append(url)

        for url in args.input or []:
            url = url.strip(" \n")
            url = url.replace('https://wcostream.net', 'https://www.wcostream.net')
            urls.append(url)

        # Ensure each url is only listed once
        urls = list(set(urls))

        if isinstance(args.episodes, list):
            if '-' in args.episodes[0]:
                args.episodes = args.episodes[0].split('-')
            else:
                args.episodes = args.episodes[0]

        if isinstance(args.seasons, list):
            args.seasons = args.seasons[0]

        if isinstance(args.exclude_episodes, list):
            args.exclude_episodes = args.exclude_episodes[0].split(',')

        if len(urls) == 0:
            print("No download URL specfied. Run __main__.py --help")
            exit()

        for url in urls:
            Lifter(
                url=url,
                resolution=args.highdef,
                logger=logger,
                season=args.seasons,
                ep_range=args.episodes,
                exclude=args.exclude_episodes,
                output=args.output,
                newest=args.newest,
                settings=settings,
                database=database,
                threads=args.num_threads,
                quiet=quiet
            )


if __name__ == '__main__':
    Main.main()
