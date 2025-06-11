from concurrent.futures import ThreadPoolExecutor, as_completed

import argparse
from ntplib import NTPClient
from time import ctime

from tabulate import tabulate
from typing import Optional


def _get_time_from(client: NTPClient, server: str) -> Optional[int]:
    response = client.request(server, version=3)
    return response.tx_time


def _main(args: argparse.Namespace):
    client = NTPClient()
    servers = args.servers
    times: dict[str, int] = {}

    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(_get_time_from, client, server): server
            for server in servers
        }

        for future in as_completed(futures):
            server = futures[future]
            try:
                time_value = future.result()
                if time_value is not None:
                    times[server] = time_value
            except Exception as e:
                print(f"Error processing {server}: {e}")

    result = [(server, ctime(time)) for server, time in times.items()]
    t: str = tabulate(sorted(result, key=lambda x: x[0]),
                      headers=["server", "time"])
    print(t)
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="SNTP Comparator"
    )
    parser.add_argument(
        "servers",
        type=str,
        help="Addresses of SNTP servers",
        nargs='+'
    )
    _main(parser.parse_args())
