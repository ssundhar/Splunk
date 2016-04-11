#!/usr/bin/env python
"""
A script for fetching security detection events from Code42 Installation
and printing them out in either csv or json format.
"""

# pylint: disable=import-error
import os
import sys
import argparse
from dateutil import parser as date_parser
from datetime import datetime
import logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "utils"))
import c42api
import argutil


def _run():
    """Initializes the state for the script based on command line input."""
    arg_parser = argparse.ArgumentParser()
    args = _setup_args(arg_parser)
    if args.logfile:
        c42api.set_log_file(args.logfile)

    if args.output or args.logfile:
        c42api.set_log_level(logging.DEBUG)
    else:
        c42api.set_log_level(logging.ERROR)
    server = argutil.server_from_args(args)
    is_json = args.format == 'json'
    device_guids = c42api.devices(server, args.device)

    def generate_detection_events():
        """
        Since write_json() wants to take a generator and fetch_detection_events()
        returns tuples, where the detection events are an array in the tuple, we use
        this auxilary function to allow us to stream the events to write_json()
        """
        event_filters = [c42api.create_filter_by_utc_datetime(args.min_date, args.max_date)] * len(device_guids)
        guids_and_filters = zip(device_guids, event_filters)
        for _, _, detection_events in c42api.fetch_detection_events(server, guids_and_filters):
            for event in detection_events:
                yield event

    with c42api.common.smart_open(args.output, overwrite=True) as out:
        if is_json:
            c42api.write_json(out, generate_detection_events())
        else:
            c42api.write_csv(out, generate_detection_events(), args.header, shallow=True)


@argutil.output_options('json', 'csv')
@argutil.logging_options
@argutil.server_options
@argutil.devices_options
def _setup_args(arg_parser):
    """Plain, boring argument setup. All the magic is in the decorators."""
    arg_parser.add_argument('--min-date', type=date_parser.parse,
                            default=datetime.utcfromtimestamp(0),
                            help='Optional lower bound')
    arg_parser.add_argument('--max-date', type=date_parser.parse,
                            default=datetime.utcnow(),
                            help='Optional upper bound')
    return arg_parser.parse_args()

if __name__ == '__main__':
    _run()
