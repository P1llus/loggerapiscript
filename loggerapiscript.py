#!/usr/bin/env python3

"""Script to generate searches on the ArcSight Logger"""

import arcsightrest
import argparse


def parse_command_line():
    parser = argparse.ArgumentParser(
            description='Script used to send search queries '
            'to ArcSight Logger API')

    # General informations
    parser.add_argument('target', help='IP Address of the Loggger')
    parser.add_argument('username', help='Username to access the logger')
    parser.add_argument('password', help='Password to access the logger')
    parser.add_argument('-s', '--unsecuressl', action='store_true',
                        help='Disable ssl warnings')


    # Commands
    command_subparser = parser.add_subparsers(dest='action', metavar='action')

    # Query
    query = command_subparser.add_parser('query', help='search informations')
    query.add_argument('query', help='Query to be used in the search')
    query.add_argument(
        '--starttime', help='From which time the query should look')
    query.add_argument('--endtime', help='To which time the query should look')
    query.add_argument(
        '--discoverfields', help='Try to discover fields in the events found')
    query.add_argument('--summaryfields', help='The list of fields')
    query.add_argument('--fieldssummary', help='Use fields summary')
    query.add_argument(
        '--localsearch', help='Indicates the search is local only')
    query.add_argument('--searchtype', help='Interactive search or not')
    query.add_argument(
        '--timeout', help='The number of milliseconds to keep the '
        'search after it has finished running')
    query.add_argument(
        '--wait', action='store_true', help='Wait for search to finish')

    # Past search
    search = command_subparser.add_parser(
        'search', help='actions on previous search')
    search.add_argument(
        'search_id', help='Search id of a currently running search')
    search_subparser = search.add_subparsers(
        dest='search_kind', metavar='kind')

    # Status settings
    status = search_subparser.add_parser(
        'status', help='Status of running search')
    status.add_argument(
        '--wait', action='store_true', help='Wait for search to finish')

    # Histogram Settings
    histogram = search_subparser.add_parser(
        'histogram', help='Get histogram overview of specific earch')

    # Drilldown Settings
    drilldown = search_subparser.add_parser(
        'drilldown', help='Gets drilldown of specific search')
    drilldown.add_argument(
        '--starttime', help='From which time the search should look')
    drilldown.add_argument(
        '--endtime', help='To which time the search should look')

    # Event Settings
    event = search_subparser.add_parser(
        'event', help='Get all information from a finished search')
    event.add_argument(
        '--dir', help='Sort direction based on event time')
    event.add_argument('--field')
    event.add_argument('--length')
    event.add_argument('--offset')

    # Raw Event Settings
    raw_event = search_subparser.add_parser(
        'rawevent', help='Get the raw event results from a search')
    raw_event.add_argument(
        'row_id', help='Specific row id for the raw event')

    # Chart Data Settings
    chart_data = search_subparser.add_parser(
        'chartdata', help='Returns data in a chart format')
    chart_data.add_argument('--field')
    chart_data.add_argument('--length')
    chart_data.add_argument('--offset')

    # Retrieve all arguments
    args = parser.parse_args()

    if args.command is None:
        # Not sure if this one is mandatory
        parser.error('you should provide an action to execute')
    elif args.command == 'search' and args.search_kind is None:
        parser.error(
            "you should provide the kind of search "
            "when performing the 'search' action")
    else:
        return args


def query(arc, args):
    search_id, response = arc.search(
        args.query,
        start_time=args.starttime,
        end_time=args.endtime,
        discover_fields=args.discoverfields,
        summary_fields=args.summaryfields,
        fields_summary=args.fieldssummary,
        local_search=args.localsearch,
        search_type=args.searchtype,
        timeout=args.timeout)
    if args.wait:
        arc.wait(search_id)
    return search_id


def search(arc, search_id, kind, args):
    if kind == 'histogram':
        return arc.histogram(search_id=search_id)

    if kind == 'drilldown':
        return arc.drilldown(
            search_id=search_id,
            start_time=args.starttime,
            end_time=args.endtime)

    if kind == 'event':
        return arc.events(
            search_id=search_id,
            dir=args.dir,
            fields=args.fields,
            length=args.length,
            offset=args.offset)

    if kind == 'rawevent':
        return arc.raw_events(search_id, row_ids=args.rowids)

    if kind == 'chartdata':
        return arc.events(
            search_id=search_id,
            length=args.length,
            offset=args.offset)

    if kind == 'status':
        if args.wait:
            arc.wait(search_id)
        return arc.search_complete(search_id=search_id)


if __name__ == '__main__':
    args = parse_command_line()

    # Sets the target Logger Server
    arcsightrest.ArcsightLogger.TARGET = args.target
    arc = arcsightrest.ArcsightLogger(
        args.username,
        args.password,
        args.unsecuressl)

    if args.command == 'query':
        print(query(arc, args))
    elif args.command == 'search':
        print(search(arc, args.search_id, args.search_kind, args))