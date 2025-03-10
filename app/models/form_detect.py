from pydantic import BaseModel
from app.mongodb import get_database


class FormDetectionModel:
    def __init__(
        self,
        url: str,
        provider: bool,
        domain: str,
        iframe: str,
        form: bool,
    ):
        # Type assertions for validation
        assert isinstance(url, str)
        assert isinstance(provider, bool)
        assert isinstance(domain, str)
        assert isinstance(iframe, str)
        assert isinstance(form, bool)

        self.document = {
            "url": url,
            "provider": provider,
            "domain": domain,
            "iframe": iframe,
            "form": form
        }

    async def save(self):
        existing_record = await find_form_detection_by_domain(
            self.document["domain"]
        )
        if existing_record:
            form_detections = get_form_detections()
            await form_detections.update_one(
                {"domain": self.document["domain"]},
                {"$set": self.document}
            )
            return self.document
        else:
            await get_form_detections().insert_one(
                self.document
            )
        return self.document

async def find_form_detection_by_domain(domain: str):
    """
    Helper function to find a form detection record by domain
    """
    form_detections = get_form_detections()
    return await form_detections.find_one({"domain": domain})

def get_form_detections():
    db = get_database()
    return db["form_detections"]

class FormDetectionRequest(BaseModel):
    url: str
    dom: str
    iframe: bool

class FormDetectionResponse(BaseModel):
    form: bool