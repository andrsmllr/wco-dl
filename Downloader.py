# -*- coding: utf-8 -*-

import os
import re
from cfscrape import create_scraper
from requests import session
from tqdm import tqdm

class Downloader(object):
    def __init__(self, logger, download_url, backup_url, hidden_url, output, header, user_agent, show_info, settings, quiet):
        self.settings = settings
        self.sess = session()
        self.sess = create_scraper(self.sess)
        self.show_name = show_info[0]
        self.season = re.search(r'(\d+)', show_info[1]).group(1).zfill(self.settings.get_setting('seasonPadding'))
        

        if show_info[2] == "":
            self.episode = '{0}'.format(re.search(r'(\d+)', show_info[3]).group(1).zfill(
                self.settings.get_setting('episodePadding')))
        else:
            self.episode = '{0}'.format(re.search(r'(\d+)', show_info[2]).group(1).zfill(
                self.settings.get_setting('episodePadding')))

        self.desc = show_info[3]
        self.show_url = show_info[4]
        self.header = header
        self.output = output
        self.download_url = download_url
        self.backup_url = backup_url
        self.hidden_url = hidden_url
        self.user_agent = user_agent
        self.logger = logger
        self.quiet = quiet

        if self.settings.get_setting('includeShowDesc'):
            self.file_name = self.settings.get_setting('saveFormat').format(show=self.show_name, season=self.season,
                                                                       episode=self.episode, desc=self.desc)
        else:
            self.file_name = self.settings.get_setting('saveFormat').format(show=self.show_name, season=self.season,
                                                                       episode=self.episode)
        self.file_path = self.output + os.sep + "{0}.mp4".format(self.file_name)


    def start_download(self):
        file_exists = os.path.exists(self.file_path)

        if not self.settings.get_setting('checkIfFileIsAlreadyDownloaded') and file_exists:
            print('[wco-dl] - {0} skipped, file exists!.'.format(self.file_name))
            return

        if self.settings.get_setting('checkIfFileIsAlreadyDownloaded') and self.check_if_downloaded(self.download_url):
            print('[wco-dl] - {0} skipped, file already downloaded!.'.format(self.file_name))
            return

        if file_exists:
            file_size = os.path.getsize(self.file_path)
        else:
            file_size = 0

        if (self.settings.get_setting('allowToResumeDownloads') and file_exists and file_size > 0):
            already_downloaded_bytes = file_size

            while True:
                if not self._download(self.download_url, already_downloaded_bytes):
                    print('[wco-dl] - Failed to download from primary URL...')

                # Try to download from backup URL if file size did not change
                # after trying to download from primary URL
                if (os.path.getsize(self.file_path) == already_downloaded_bytes):
                    print('[wco-dl] - Trying to download using the backup URL...')
                    self._download(self.backup_url, already_downloaded_bytes)

                return
        else:
            print('[wco-dl] - Downloading {0}'.format(self.file_name))
            while True:
                if not self._download(self.download_url):
                    print('[wco-dl] - Trying to download using the backup URL...')
                    if not self._download(self.backup_url):
                        print(f'[wco-dl] - Download for {self.file_name} did not complete, '
                            f'please create an issue on GitHub.\n')
                        f_path = os.path.dirname(os.path.realpath(__file__)) + os.sep
                        with open(f_path + "failed.txt", "a+") as failed:
                            failed.write("{0},{1},{2}".format(self.file_name, self.output, self.show_url))
                        break
                    else:
                        break
                else:
                    break


    def check_if_downloaded(self, url):
        print('[wco-dl] - Checking if video is already downloaded, this may take some time, you can turn this off in your settings.')
        if os.path.exists(self.file_path):
            file_size = int(os.path.getsize(self.file_path))
        else:
            return False

        # TODO: this should be threaded, getting the headers can take longer than downloading again
        content_size = int(self.sess.get(url, headers=self.header).headers["content-length"])

        if file_size == content_size:
            return True

        return False


    def _download(self, url, resume_bytes=0):
        while True:
            file_exists = os.path.exists(self.file_path)

            if file_exists:
                file_size = os.path.getsize(self.file_path)
            else:
                file_size = 0

            if (resume_bytes > 0 and file_exists and file_size > 0):
                print('Resuming download, you can turn this off in your settings.')
                host_url = self.sess.get(url).url
                resume_header = {
                    'Host': host_url.split("//")[-1].split("/")[0].split('?')[0],
                    'User-Agent': self.user_agent,
                    'Accept': 'video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Connection': 'keep-alive',
                    'Referer': self.hidden_url.replace('https://wcostream.net', 'https://www.wcostream.net'),
                    'Range': 'bytes={0}-'.format(resume_bytes),
                }
                dlr = self.sess.get(host_url, stream=True, headers=resume_header)
                try:
                    with open(self.file_path, 'ab') as handle:
                        if (not self.quiet):
                            with tqdm(unit_scale=1024, miniters=1, desc='Downloading', initial=int(resume_bytes), total=int(dlr.headers['content-length'], 0)) as pbar:
                                for data in dlr.iter_content(chunk_size=1024):
                                    handle.write(data)
                                    pbar.update(len(data))
                        else:
                            for data in dlr.iter_content(chunk_size=1024):
                                handle.write(data)
                except Exception as e:
                    if self.logger:
                        print('Error: {}'.format(e), end='\n\n')
                    return
                return
            else:
                dlr = self.sess.get(url, stream=True, headers=self.header)  # Downloading the content using python.
                try:
                    with open(self.file_path, "wb") as handle:
                        if (not self.quiet):
                            with tqdm(unit='B', unit_scale=True, unit_divisor=1024, miniters=1, desc="Downloading", total=int(dlr.headers['content-length'], 0)) as pbar:
                                for data in dlr.iter_content(chunk_size=1024):
                                    handle.write(data)
                                    pbar.update(len(data))
                        else:
                            for data in dlr.iter_content(chunk_size=1024):
                                handle.write(data)
                except Exception as e:
                    if self.logger:
                        print('Error: {}'.format(e), end='\n\n')
                    return False

            if not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0:
                # print("[wco-dl] - Download for {0} did not complete, please try again.\n".format(self.file_name))
                # Upon failure of download append the episode name, file_name, to a text file in the same directory
                # After finishing download all the shows the program will see if that text file exists and attempt
                # to re-download the missing files
                return False
            else:
                print('[wco-dl] - Download for {0} completed.\n'.format(self.file_name))
                return True
