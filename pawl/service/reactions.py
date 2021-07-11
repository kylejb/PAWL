"""Provide `/reactions` service class."""
from .base import ServiceBase
from ..constants import API_PATH


class Reactions(ServiceBase):
    """Reactions is a Service class that represents the `/reactions` endpoint."""

    # POST https://api.linkedin.com/v2/reactions?actor={organizationUrn|personUrn}
    # https://docs.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/reactions-and-social-metadata?tabs=http#create-a-reaction-on-a-share-or-a-comment # noqa
    def like_post(
        self,
        post_urn: str,
        person_id: str = None,
    ):
        # TODO: Refactor OOP design
        if person_id is None and self._linkedin.current_user_id is None:
            person_id = self._linkedin.current_user.basic_profile()["id"]
        elif person_id is None:
            person_id = self._linkedin.current_user_id

        json_content = {"root": post_urn, "reactionType": "LIKE"}
        json_response = self._linkedin.post(
            json=json_content,
            path=f"v2/{API_PATH['reactions']}?actor=urn%3Ali%3Aperson%3A{person_id}",
        )
        return json_response
