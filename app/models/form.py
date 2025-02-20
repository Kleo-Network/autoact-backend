from pydantic import BaseModel
from app.mongodb import get_forms


class Form:
    def __init__(
        self,
        domain: str,
        mapping: dict,
        parent_container: str,
    ):
        # Type assertions for validation
        assert isinstance(domain, str)
        assert isinstance(mapping, dict)
        assert isinstance(parent_container, str)

        self.document = {
            "domain": domain,
            "mapping": mapping,
            "parent_container": parent_container,
        }

    async def save(self):
        existing_form = await find_form_by_domain(
            self.document["domain"]
        )  # Ensure this function is async
        if existing_form:
            return existing_form
        else:
            await get_forms().insert_one(
                self.document
            )  # Uses the get_forms function imported at the top
        return self.document


class CreateFormRequest(BaseModel):
    domain: str
    mapping: dict
    parent_container: str