import logging
import argparse

from autobot.version import name, version

""" Entry point of Autobot application"""
def main():
    #Parsing arguments
    parser = argparse.ArgumentParser('{} - v.{}'.format(name, version))
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

    # This must be here because PluginsLoader need above components
    from autobot import AutoBot

    AutoBot(args.settings_file, args.config_dir).startup()