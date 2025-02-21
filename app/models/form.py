from pydantic import BaseModel
from app.mongodb import get_forms


class Form:
    def __init__(
        self,
        domain: str,
        mapping: dict,
        parent_container: str,
        verified: bool = False,
    ):
        # Type assertions for validation
        assert isinstance(domain, str)
        assert isinstance(mapping, dict)
        assert isinstance(parent_container, str)
        assert isinstance(verified, bool)

        self.document = {
            "domain": domain,
            "mapping": mapping,
            "parent_container": parent_container,
            "verified": verified
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

async def find_form_by_domain(domain: str):
    """
    Helper function to find a form by domain
    """
    forms_collection = get_forms()
    return await forms_collection.find_one({"domain": domain})

class CreateFormRequest(BaseModel):
    domain: str
    mapping: dict
    parent_container: str
    verified: bool