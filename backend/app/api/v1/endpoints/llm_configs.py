from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps # For get_current_active_user
from app.core.security import decrypt_api_key # Not strictly needed here if schema handles exclusion

router = APIRouter()

@router.post("/", response_model=schemas.LLMProviderConfig)
def create_llm_config(
    *,
    db: Session = Depends(deps.get_db),
    config_in: schemas.LLMProviderConfigCreate,
    current_user: models.Users = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new LLM provider configuration for the current user.
    The API key will be encrypted before storage.
    """
    # Check if a config with the same provider and model already exists for this user (optional, good practice)
    # existing_config = db.query(models.LLMProviderConfigs).filter(
    #     models.LLMProviderConfigs.user_id == current_user.user_id,
    #     models.LLMProviderConfigs.provider_name == config_in.provider_name,
    #     models.LLMProviderConfigs.model_name == config_in.model_name
    # ).first()
    # if existing_config:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="An LLM provider configuration with this provider and model already exists.",
    #     )
    
    llm_config = crud.llm_provider_config.create_with_owner(
        db=db, obj_in=config_in, user_id=current_user.user_id
    )
    # Prepare the response object according to LLMProviderConfig schema
    return schemas.LLMProviderConfig(
        llm_config_id=llm_config.llm_config_id,
        user_id=llm_config.user_id,
        provider_name=llm_config.provider_name,
        model_name=llm_config.model_name,
        base_url=str(llm_config.base_url) if llm_config.base_url else None, # Ensure HttpUrl is string
        is_active=llm_config.is_active,
        api_key_set=bool(llm_config.api_key and llm_config.api_key.strip()), # Check if encrypted key is non-empty
        created_at=llm_config.created_at
    )

@router.get("/", response_model=List[schemas.LLMProviderConfig])
def read_llm_configs(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.Users = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve LLM provider configurations for the current user.
    """
    llm_configs = crud.llm_provider_config.get_by_user(
        db=db, user_id=current_user.user_id, skip=skip, limit=limit
    )
    # Transform to schema, ensuring api_key_set is correctly determined
    response_configs = []
    for config in llm_configs:
        response_configs.append(
            schemas.LLMProviderConfig(
                llm_config_id=config.llm_config_id,
                user_id=config.user_id,
                provider_name=config.provider_name,
                model_name=config.model_name,
                base_url=str(config.base_url) if config.base_url else None,
                is_active=config.is_active,
                api_key_set=bool(config.api_key and config.api_key.strip()),
                created_at=config.created_at
            )
        )
    return response_configs

@router.get("/{config_id}", response_model=schemas.LLMProviderConfig)
def read_llm_config(
    *,
    db: Session = Depends(deps.get_db),
    config_id: int,
    current_user: models.Users = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific LLM provider configuration by ID.
    Ensures the configuration belongs to the current user.
    """
    llm_config = crud.llm_provider_config.get(db=db, llm_config_id=config_id)
    if not llm_config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LLM configuration not found")
    if llm_config.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    return schemas.LLMProviderConfig(
        llm_config_id=llm_config.llm_config_id,
        user_id=llm_config.user_id,
        provider_name=llm_config.provider_name,
        model_name=llm_config.model_name,
        base_url=str(llm_config.base_url) if llm_config.base_url else None,
        is_active=llm_config.is_active,
        api_key_set=bool(llm_config.api_key and llm_config.api_key.strip()),
        created_at=llm_config.created_at
    )

@router.put("/{config_id}", response_model=schemas.LLMProviderConfig)
def update_llm_config(
    *,
    db: Session = Depends(deps.get_db),
    config_id: int,
    config_in: schemas.LLMProviderConfigUpdate,
    current_user: models.Users = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an LLM provider configuration.
    If api_key is provided, it will be re-encrypted.
    Ensures the configuration belongs to the current user.
    """
    llm_config = crud.llm_provider_config.get(db=db, llm_config_id=config_id)
    if not llm_config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LLM configuration not found")
    if llm_config.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    updated_llm_config = crud.llm_provider_config.update(db=db, db_obj=llm_config, obj_in=config_in)
    
    return schemas.LLMProviderConfig(
        llm_config_id=updated_llm_config.llm_config_id,
        user_id=updated_llm_config.user_id,
        provider_name=updated_llm_config.provider_name,
        model_name=updated_llm_config.model_name,
        base_url=str(updated_llm_config.base_url) if updated_llm_config.base_url else None,
        is_active=updated_llm_config.is_active,
        api_key_set=bool(updated_llm_config.api_key and updated_llm_config.api_key.strip()),
        created_at=updated_llm_config.created_at
    )

@router.delete("/{config_id}", response_model=schemas.LLMProviderConfig) # Or a simple success message
def delete_llm_config(
    *,
    db: Session = Depends(deps.get_db),
    config_id: int,
    current_user: models.Users = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an LLM provider configuration.
    Ensures the configuration belongs to the current user.
    """
    llm_config = crud.llm_provider_config.get(db=db, llm_config_id=config_id)
    if not llm_config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LLM configuration not found")
    if llm_config.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    # Store data for response before deleting
    deleted_config_data = schemas.LLMProviderConfig(
        llm_config_id=llm_config.llm_config_id,
        user_id=llm_config.user_id,
        provider_name=llm_config.provider_name,
        model_name=llm_config.model_name,
        base_url=str(llm_config.base_url) if llm_config.base_url else None,
        is_active=llm_config.is_active,
        api_key_set=bool(llm_config.api_key and llm_config.api_key.strip()), # Will likely be true before delete
        created_at=llm_config.created_at
    )
    
    crud.llm_provider_config.remove(db=db, llm_config_id=config_id)
    return deleted_config_data # Or return a message like {"message": "LLM configuration deleted successfully"}