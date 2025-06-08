import sys

import argparse

from vk_api.requester import VkApiRequester
from vk_api.requests import VkApiRequests


def _main(args: argparse.Namespace):
    requester = VkApiRequester(args.token)
    requests = VkApiRequests(requester)
    
    user = requests.get_user(args.id)
    if user is None:
        print("Unknown user", file=sys.stderr)
        sys.exit(1)
    
    friends = requests.get_friends(user.user_id)
    if friends is None:
        print(f"Couldn't get friends for {user.user_id}", file=sys.stderr)
        sys.exit(1)
        
    for friend in friends:
        if friend.deactivated:
            continue
        print(friend.name, friend.surname, f'[{friend.user_id}]')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="VK API"
    )
    parser.add_argument(
        "token",
        type=str,
        help="API token"
    )
    parser.add_argument(
        "id",
        type=str,
        help="User ID"
    )
    _main(parser.parse_args())
