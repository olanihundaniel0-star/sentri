"""Social graph proximity scoring."""

from __future__ import annotations

from typing import Optional

from sentri.models.profile import SocialGraph


def proximity(social_graph: Optional[SocialGraph], recipient_id: str) -> Optional[float]:
    """Score social proximity to a recipient, or None if no graph is available.

    None is a missingness mask, distinct from 0.0 ("known to have no
    connection") — callers must not conflate an absent social graph with a
    confirmed lack of connection.
    """
    if social_graph is None:
        return None

    if recipient_id in social_graph.friends:
        return 0.7

    for friend_id in social_graph.friends:
        if recipient_id in social_graph.friends_of_friends.get(friend_id, frozenset()):
            return 0.4

    return 0.0
