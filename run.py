#!/usr/bin/env python

""" Main module that start """

import autobot.version as version

import logging
import argparse

if __name__ == '__main__':

    #Parsing arguments
    parser = argparse.ArgumentParser('{} - v.{}'.format(version.name, version.version))
    parser.add_argument('settings_file', \
                        help='file containing the main setting of autobot')
    parser.add_argument('config_dir', \
                        help='file containing the configuration for autobot istance')
    parser.add_argument('-l', '--log_level', \
                        metavar='log_level', \
                        default='WARN', \
                        choices=['DEBUG', 'INFO', 'WARN', 'ERROR'], \
                        help='file containing the configuration for autobot istance')

    args = parser.parse_args()

    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', \
                    level=getattr(logging, args.log_level))

    from autobot import AutoBot

    AutoBot(args.settings_file, args.config_dir).startup()
