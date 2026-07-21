from app.generators.templates.create_template import CreateTemplate
from app.generators.templates.edit_template import EditTemplate
from app.generators.templates.delete_template import DeleteTemplate
from app.generators.templates.search_template import SearchTemplate
from app.generators.templates.login_template import LoginTemplate
from app.generators.templates.upload_template import UploadTemplate


class TemplateRegistry:

    def __init__(self):

        self.templates = {

            "CREATE": CreateTemplate(),

            "EDIT": EditTemplate(),

            "DELETE": DeleteTemplate(),

            "SEARCH": SearchTemplate(),

            "LOGIN": LoginTemplate(),

            "UPLOAD": UploadTemplate()

        }

    def get(self, intent):

        return self.templates.get(intent)