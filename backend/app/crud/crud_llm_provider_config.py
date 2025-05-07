from typing import List, Optional, Any

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.models.llm_provider_config import LLMProviderConfigs
from app.schemas.llm_provider_config import LLMProviderConfigCreate, LLMProviderConfigUpdate
from app.core.security import encrypt_api_key, decrypt_api_key # Assuming these are now in security.py

class CRUDLLMProviderConfig:
    def get(self, db: Session, llm_config_id: int) -> Optional[LLMProviderConfigs]:
        return db.query(LLMProviderConfigs).filter(LLMProviderConfigs.llm_config_id == llm_config_id).first()

    def get_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[LLMProviderConfigs]:
        return (
            db.query(LLMProviderConfigs)
            .filter(LLMProviderConfigs.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_owner(
        self, db: Session, *, obj_in: LLMProviderConfigCreate, user_id: int
    ) -> LLMProviderConfigs:
        obj_in_data = jsonable_encoder(obj_in)
        if obj_in.api_key:
            obj_in_data["api_key"] = encrypt_api_key(obj_in.api_key)
        
        # Ensure base_url is converted to string if it's a Pydantic HttpUrl object
        if obj_in.base_url:
            obj_in_data["base_url"] = str(obj_in.base_url)

        db_obj = LLMProviderConfigs(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: LLMProviderConfigs,
        obj_in: LLMProviderConfigUpdate | dict[str, Any],
    ) -> LLMProviderConfigs:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True) # Use model_dump for Pydantic v2

        if "api_key" in update_data and update_data["api_key"]:
            update_data["api_key"] = encrypt_api_key(update_data["api_key"])
        elif "api_key" in update_data and update_data["api_key"] is None: # Allow clearing API key
            update_data["api_key"] = "" # Store as empty string or handle as per model definition

        # Ensure base_url is converted to string if it's a Pydantic HttpUrl object and is being updated
        if "base_url" in update_data and update_data["base_url"] is not None:
             update_data["base_url"] = str(update_data["base_url"])


        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, llm_config_id: int) -> Optional[LLMProviderConfigs]:
        obj = db.query(LLMProviderConfigs).get(llm_config_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

llm_provider_config = CRUDLLMProviderConfig()