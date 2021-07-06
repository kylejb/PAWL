"""Provide the API's ServiceBase superclass."""
from copy import deepcopy
from typing import TYPE_CHECKING, Optional, Any, Dict

if TYPE_CHECKING:  # no cover
    from ... import pawl


class ServiceBase:
    """Superclass for all services in `linkedin/api`."""

    # TODO - confirm instance of self and complete logic (or reconsider approach for headers)
    @property
    def required_headers(self):
        # if headers is None:
        headers = {
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._linkedin.auth.access_token}",
        }
        # else:
        # headers.update(
        #     {
        #         "X-Restli-Protocol-Version": "2.0.0",
        #         "Content-Type": "application/json",
        #     }
        # )
        return headers

    @staticmethod
    def _safely_add_arguments(argument_dict, key, **new_arguments):
        """Replace argument_dict[key] with a deepcopy and update.

        This method is often called when new parameters need to be added to a request.
        By calling this method and adding the new or updated parameters we can insure we
        don't modify the dictionary passed in by the caller.
        """
        value = deepcopy(argument_dict[key]) if key in argument_dict else {}
        value.update(new_arguments)
        argument_dict[key] = value

    @classmethod
    def parse(cls, data: Dict[str, Any], linkedin: "pawl.Linkedin") -> Any:
        """Return an instance of ``cls`` from ``data``.

        :param data: The structured data.
        :param linkedin: An instance of :class:`.Linkedin`.
        """
        return cls(linkedin, _data=data)

    def __init__(
        self, linkedin: "pawl.Linkedin", _data: Optional[Dict[str, Any]] = None
    ):
        self._linkedin = linkedin
        if _data:
            for attribute, value in _data.items():
                setattr(self, attribute, value)
