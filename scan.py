#!/usr/bin/env python3
"""Script to scan fodlre names and prodocue a list of changes based on the
set name of files from the day before
"""

import click
import datetime
from dotenv import load_dotenv
from emailer import mail_results
import os
import sys
import traceback


#### HEAR BE DRAGONS
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def writeyesterday(yesterday):
  with open(os.environ.get('FILE_NAME'), 'w') as out_file:
    out_file.write('\n'.join(yesterday))
  out_file.close()
  return

def readyesterday():
  with open(os.environ.get('FILE_NAME'), 'r') as in_file:
    yesterday = in_file.read().split('\n')
  in_file.close()
  return yesterday

def readtoday():
  mylist = os.listdir(os.environ.get('FOLDER'))
  mylist.sort()
  dirlist = []
  for item in mylist:
    if os.path.isdir(os.environ.get('FOLDER')+'/'+item):
      dirlist.append(item)

  return dirlist

def comparedays(yesterday, today):
  body = "<p><b>Folders Added</b><hr />\n<pre>"
  boatlist = list(set(today) - set(yesterday))  # boats added
  boatlist.sort()

  if len(boatlist):
    for boat in boatlist:
      body += boat + "\n"
  else:
    body += "None\n"

  body += "</pre>\n</p>\n<p>&nbsp;</p>\n"
  body += "<p><b>Folders Removed</b><hr />\n<pre>"

  boatlist = list(set(yesterday) - set(today))  # boats removed
  boatlist.sort()
  if len(boatlist):
    for boat in boatlist:
      body += boat + "\n"
  else:
    body += "None\n"

  body += "</pre></p>\n";
  return body


@click.command()
@click.option('--debug', '-d', is_flag=True, help='show debug verbosity/do not '
              'save verbosity')
@click.option('--verbose', '-v', default=0, type=int, help='verbosity level 0-3')
def main(debug, verbose):

    # check if help was requested. If so print and bail
    if os.getenv('HELP'):
      with click.get_current_context() as ctx:
        click.echo(ctx.get_help())
        ctx.exit()

    # load environmental variables
    load_dotenv(dotenv_path=resource_path(".env"))

    yesterday =  readyesterday()
    today = readtoday()
    body = comparedays(yesterday, today)
    if debug:
        print(body)
    else:
        mail_results(os.environ.get('TITLE'), body)
        writeyesterday(today)

    sys.exit(0)


if __name__ == "__main__":
    main()
