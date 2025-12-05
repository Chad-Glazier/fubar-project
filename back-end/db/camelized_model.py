import humps
from pydantic import BaseModel, ConfigDict

class CamelizedModel(BaseModel):
	model_config = ConfigDict(
        alias_generator = humps.camelize,
        populate_by_name = True
    )
