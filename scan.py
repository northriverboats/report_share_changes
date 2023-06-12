#!/usr/bin/env python3
"""Script to scan folder names and prodocue a list of changes based on the
set name of files from the day before
"""

import click
import datetime
from dotenv import load_dotenv
from envelopes import Envelope
from smtplib import SMTPException # allow for silent fail in try exception
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

def split_address(email_address):
    """Return a tuple of (address, name), name may be an empty string
       Can convert the following forms
         exaple@example.com
         <example@exmaple.con>
         Example <example@example.com>
         Example<example@example.com>
    """
    address = email_address.split('<')
    if len(address) == 1:
        return (address[0], '')
    if address[0]:
        return (address[1][:-1], address[0].strip())
    return (address[1][:-1], '')

def mail_results(subject, body, attachment=''):
    """ Send emial with html formatted body and parameters from env"""
    envelope = Envelope(
        from_addr=split_address(os.environ.get('MAIL_FROM')),
        subject=subject,
        html_body=body
    )

    # add standard recepients
    tos = os.environ.get('MAIL_TO','').split(',')
    if tos[0]:
        for to in tos:
            envelope.add_to_addr(to)

    # add carbon coppies
    ccs = os.environ.get('MAIL_CC','').split(',')
    if ccs[0]:
        for cc in ccs:
            envelope.add_cc_addr(cc)

    # add blind carbon copies recepients
    bccs = os.environ.get('MAIL_BCC','').split(',')
    if bccs[0]:
        for bcc in bccs:
            envelope.add_bcc_addr(bcc)

    if attachent:
        envelope.add_attachment(attachment)

    # send the envelope using an ad-hoc connection...
    try:
        _ = envelope.send(
            os.environ.get('MAIL_SERVER'),
            port=os.environ.get('MAIL_PORT'),
            login=os.environ.get('MAIL_LOGIN'),
            password='zcrkyqvgbxkxnjdg',
            tls=True
        )
    except SMTPException:
        print("SMTP EMail error")

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
