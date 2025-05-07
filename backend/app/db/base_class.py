from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base:
    """Base class which provides automated table name
    and surrogate primary key column.
    """

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"

    # id: Mapped[int] = mapped_column(primary_key=True, index=True) # SQLAlchemy 2.0 style
    # If using SQLAlchemy < 2.0, you might use:
    # id = Column(Integer, primary_key=True, index=True)
    # For UUIDs, which are generally better for distributed systems:
    # from sqlalchemy import Column, UUID as SQLAlchemy_UUID
    # import uuid
    # id = Column(SQLAlchemy_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # For now, let's let each model define its own PK as per technical_specs.md
    # which sometimes specifies UUID and sometimes INT.
    # We will ensure each model has a PK.