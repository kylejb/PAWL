"""Provide `/reactions` service class."""
from .base import ServiceBase


class Reactions(ServiceBase):
    """Reactions is a Service class that represents the `/reactions` endpoint."""

    def like_post(post_urn: str):
        # POST https://api.linkedin.com/v2/reactions?actor={organizationUrn|personUrn}
        # https://docs.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/reactions-and-social-metadata?tabs=http#create-a-reaction-on-a-share-or-a-comment # noqa
        ...
