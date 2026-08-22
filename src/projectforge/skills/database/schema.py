from pydantic import BaseModel, Field

class FieldDef(BaseModel):
    name: str
    data_type: str
    nullable: bool = False
    primary_key: bool = False
    unique: bool = False
    default: str | None = None
    description: str

class Relationship(BaseModel):
    from_entity: str
    from_field: str
    to_entity: str
    to_field: str
    type: str
    description: str

class Index(BaseModel):
    name: str
    entity: str
    fields: list[str]
    unique: bool = False
    rationale: str

class Entity(BaseModel):
    name: str
    description: str
    fields: list[FieldDef] = Field(min_length=1)
    indexes: list[Index] = []

class DatabaseOutput(BaseModel):
    database_type: str
    type_rationale: str
    entities: list[Entity] = Field(min_length=1)
    relationships: list[Relationship]
    seed_data_suggestions: list[str]
    normalization_notes: str
    migration_strategy: str
