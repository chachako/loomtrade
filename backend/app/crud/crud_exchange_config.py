from sqlalchemy.orm import Session
from typing import List, Optional, Any

from app.models.exchange_config import ExchangeAPIKeys # Model name is ExchangeAPIKeys
from app.schemas.exchange_config import ExchangeConfigCreate, ExchangeConfigUpdate
from app.core.security import encrypt_api_key

def get_exchange_config(db: Session, api_key_id: int, user_id: int) -> Optional[ExchangeAPIKeys]:
    """
    Get an exchange configuration by its ID and user ID.
    """
    return db.query(ExchangeAPIKeys).filter(ExchangeAPIKeys.api_key_id == api_key_id, ExchangeAPIKeys.user_id == user_id).first()

def get_exchange_configs_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[ExchangeAPIKeys]:
    """
    Get all exchange configurations for a specific user.
    """
    return db.query(ExchangeAPIKeys).filter(ExchangeAPIKeys.user_id == user_id).offset(skip).limit(limit).all()

def create_exchange_config(db: Session, *, obj_in: ExchangeConfigCreate, user_id: int) -> ExchangeAPIKeys:
    """
    Create a new exchange configuration.
    API key, secret key, and passphrase are encrypted before storing.
    """
    encrypted_api_key = encrypt_api_key(obj_in.api_key)
    encrypted_secret_key = encrypt_api_key(obj_in.secret_key)
    encrypted_passphrase = encrypt_api_key(obj_in.passphrase) if obj_in.passphrase else None

    db_obj = ExchangeAPIKeys(
        user_id=user_id,
        exchange_name=obj_in.exchange_name,
        market_type=obj_in.market_type,
        api_key=encrypted_api_key,
        secret_key=encrypted_secret_key,
        passphrase=encrypted_passphrase,
        permissions=obj_in.permissions,
        is_active=obj_in.is_active
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_exchange_config(
    db: Session, *, db_obj: ExchangeAPIKeys, obj_in: ExchangeConfigUpdate | dict[str, Any]
) -> ExchangeAPIKeys:
    """
    Update an existing exchange configuration.
    If API key, secret key, or passphrase are provided in obj_in, they are re-encrypted.
    """
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True) # Pydantic V2
        # update_data = obj_in.dict(exclude_unset=True) # Pydantic V1

    if "api_key" in update_data and update_data["api_key"] is not None:
        update_data["api_key"] = encrypt_api_key(update_data["api_key"])
    if "secret_key" in update_data and update_data["secret_key"] is not None:
        update_data["secret_key"] = encrypt_api_key(update_data["secret_key"])
    if "passphrase" in update_data: # Allows clearing passphrase by sending null/None
        update_data["passphrase"] = encrypt_api_key(update_data["passphrase"]) if update_data["passphrase"] else None
    
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_exchange_config(db: Session, *, api_key_id: int, user_id: int) -> Optional[ExchangeAPIKeys]:
    """
    Delete an exchange configuration by its ID and user ID.
    """
    db_obj = db.query(ExchangeAPIKeys).filter(ExchangeAPIKeys.api_key_id == api_key_id, ExchangeAPIKeys.user_id == user_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj

# Placeholder for a generic CRUD base if it exists or is planned.
# For now, direct implementation is used.
# from .base import CRUDBase
# class CRUDExchangeConfig(CRUDBase[ExchangeAPIKeys, ExchangeConfigCreate, ExchangeConfigUpdate]):
#     pass
# exchange_config = CRUDExchangeConfig(ExchangeAPIKeys)