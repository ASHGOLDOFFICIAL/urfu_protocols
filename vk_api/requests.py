import dataclasses

from vk_api.requester import VkApiRequester

_RESPONSE = 'response'


@dataclasses.dataclass
class User:
    name: str
    surname: str
    user_id: str
    deactivated: bool


class VkApiRequests:
    def __init__(self, requester: VkApiRequester):
        self._requester = requester

    def get_user(self, user_id: str) -> User | None:
        user = self._requester.make_request(
            'users.get',
            'user_ids={}'.format(user_id)
        )
        if user is None or _RESPONSE not in user or 'error' in user:
            return None
        
        response = user[_RESPONSE][0]
        user_id = response['id']
        name = response['first_name']
        surname = response['last_name']
        deactivated = 'deactivated' in response.keys()
        return User(
            user_id=user_id,
            name=name,
            surname=surname,
            deactivated=deactivated)

    def get_friends(self, user_id: str) -> list[User] | None:
        friends = self._requester.make_request(
            'friends.get',
            'user_id={}'.format(user_id)
        )
        if friends is None or _RESPONSE not in friends or 'error' in friends:
            return None
        
        return list(filter(None, [
            self.get_user(user_id)
            for user_id in friends[_RESPONSE]['items']
        ]))