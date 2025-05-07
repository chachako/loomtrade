from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app import crud, schemas, models # Assuming __init__.py in app, crud, schemas, models are set up
from app.api import deps # For get_db and get_current_active_user
from app.models.user import Users # For type hinting current_user

router = APIRouter()

@router.post("/", response_model=schemas.ExchangeConfig)
def create_exchange_configuration(
    *,
    db: Session = Depends(deps.get_db),
    config_in: schemas.ExchangeConfigCreate,
    current_user: Users = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create new exchange configuration for the current user.
    """
    # Check if a config with the same exchange_name and market_type already exists for this user
    # existing_config = db.query(models.ExchangeAPIKeys).filter(
    #     models.ExchangeAPIKeys.user_id == current_user.user_id,
    #     models.ExchangeAPIKeys.exchange_name == config_in.exchange_name,
    #     models.ExchangeAPIKeys.market_type == config_in.market_type
    # ).first()
    # if existing_config:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="An exchange configuration with this name and market type already exists."
    #     )
    config = crud.exchange_config.create_exchange_config(db=db, obj_in=config_in, user_id=current_user.user_id)
    return {
        "api_key_id": config.api_key_id,
        "user_id": config.user_id,
        "exchange_name": config.exchange_name,
        "market_type": config.market_type,
        "api_key_set": bool(config.api_key),
        "secret_key_set": bool(config.secret_key),
        "passphrase_set": bool(config.passphrase), # True if set, False if None or empty
        "permissions": config.permissions,
        "is_active": config.is_active,
        "created_at": config.created_at,
        "last_tested_at": config.last_tested_at,
    }

@router.get("/", response_model=List[schemas.ExchangeConfig])
def read_exchange_configurations(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: Users = Depends(deps.get_current_active_user)
) -> Any:
    """
    Retrieve exchange configurations for the current user.
    """
    configs = crud.exchange_config.get_exchange_configs_by_user_id(db, user_id=current_user.user_id, skip=skip, limit=limit)
    
    response_data = []
    for config in configs:
        response_data.append({
            "api_key_id": config.api_key_id,
            "user_id": config.user_id,
            "exchange_name": config.exchange_name,
            "market_type": config.market_type,
            "api_key_set": bool(config.api_key),
            "secret_key_set": bool(config.secret_key),
            "passphrase_set": bool(config.passphrase),
            "permissions": config.permissions,
            "is_active": config.is_active,
            "created_at": config.created_at,
            "last_tested_at": config.last_tested_at,
        })
    return response_data

@router.get("/{config_id}", response_model=schemas.ExchangeConfig)
def read_exchange_configuration(
    *,
    db: Session = Depends(deps.get_db),
    config_id: int,
    current_user: Users = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get specific exchange configuration by ID for the current user.
    """
    config = crud.exchange_config.get_exchange_config(db=db, api_key_id=config_id, user_id=current_user.user_id)
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exchange configuration not found")
    return {
        "api_key_id": config.api_key_id,
        "user_id": config.user_id,
        "exchange_name": config.exchange_name,
        "market_type": config.market_type,
        "api_key_set": bool(config.api_key),
        "secret_key_set": bool(config.secret_key),
        "passphrase_set": bool(config.passphrase),
        "permissions": config.permissions,
        "is_active": config.is_active,
        "created_at": config.created_at,
        "last_tested_at": config.last_tested_at,
    }

@router.put("/{config_id}", response_model=schemas.ExchangeConfig)
def update_exchange_configuration(
    *,
    db: Session = Depends(deps.get_db),
    config_id: int,
    config_in: schemas.ExchangeConfigUpdate,
    current_user: Users = Depends(deps.get_current_active_user)
) -> Any:
    """
    Update an exchange configuration for the current user.
    """
    db_config = crud.exchange_config.get_exchange_config(db=db, api_key_id=config_id, user_id=current_user.user_id)
    if not db_config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exchange configuration not found")
    
    # # Prevent updating to a duplicate exchange_name and market_type if they are being changed
    # if (config_in.exchange_name and config_in.exchange_name != db_config.exchange_name) or \
    #    (config_in.market_type and config_in.market_type != db_config.market_type):
    #     check_name = config_in.exchange_name if config_in.exchange_name else db_config.exchange_name
    #     check_market_type = config_in.market_type if config_in.market_type else db_config.market_type
        
    #     existing_config = db.query(models.ExchangeAPIKeys).filter(
    #         models.ExchangeAPIKeys.user_id == current_user.user_id,
    #         models.ExchangeAPIKeys.exchange_name == check_name,
    #         models.ExchangeAPIKeys.market_type == check_market_type,
    #         models.ExchangeAPIKeys.api_key_id != config_id # Exclude the current config
    #     ).first()
    #     if existing_config:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Another exchange configuration with this name and market type already exists."
    #         )

    updated_config = crud.exchange_config.update_exchange_config(db=db, db_obj=db_config, obj_in=config_in)
    return {
        "api_key_id": updated_config.api_key_id,
        "user_id": updated_config.user_id,
        "exchange_name": updated_config.exchange_name,
        "market_type": updated_config.market_type,
        "api_key_set": bool(updated_config.api_key),
        "secret_key_set": bool(updated_config.secret_key),
        "passphrase_set": bool(updated_config.passphrase),
        "permissions": updated_config.permissions,
        "is_active": updated_config.is_active,
        "created_at": updated_config.created_at,
        "last_tested_at": updated_config.last_tested_at,
    }

@router.delete("/{config_id}", response_model=schemas.ExchangeConfig) # Or a simple success message
def delete_exchange_configuration(
    *,
    db: Session = Depends(deps.get_db),
    config_id: int,
    current_user: Users = Depends(deps.get_current_active_user)
) -> Any:
    """
    Delete an exchange configuration for the current user.
    """
    config = crud.exchange_config.get_exchange_config(db=db, api_key_id=config_id, user_id=current_user.user_id)
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exchange configuration not found")
    
    deleted_config_data = { # Capture data before deletion for response
        "api_key_id": config.api_key_id,
        "user_id": config.user_id,
        "exchange_name": config.exchange_name,
        "market_type": config.market_type,
        "api_key_set": bool(config.api_key), # Will be true if set before delete
        "secret_key_set": bool(config.secret_key), # Will be true if set before delete
        "passphrase_set": bool(config.passphrase), # Will be true if set before delete
        "permissions": config.permissions,
        "is_active": config.is_active,
        "created_at": config.created_at,
        "last_tested_at": config.last_tested_at,
    }
    crud.exchange_config.delete_exchange_config(db=db, api_key_id=config_id, user_id=current_user.user_id)
    return deleted_config_data # Or return {"message": "Exchange configuration deleted successfully"}


@router.post("/{config_id}/test", response_model=schemas.Msg) # Using a generic Msg schema for now
async def test_exchange_connectivity(
    *,
    db: Session = Depends(deps.get_db),
    config_id: int,
    current_user: Users = Depends(deps.get_current_active_user)
) -> Any:
    """
    Test connectivity to the exchange using the stored credentials.
    This is a framework endpoint. Actual exchange API calls to be implemented later.
    """
    config = crud.exchange_config.get_exchange_config(db=db, api_key_id=config_id, user_id=current_user.user_id)
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exchange configuration not found")

    if not config.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Configuration is not active.")

    # Placeholder for actual connectivity test logic
    # api_key = crud.exchange_config.decrypt_api_key(config.api_key) # Decryption would happen here
    # secret_key = crud.exchange_config.decrypt_api_key(config.secret_key)
    # passphrase = crud.exchange_config.decrypt_api_key(config.passphrase) if config.passphrase else None

    # Example:
    # try:
    #     # test_passed = await some_exchange_client.test_connectivity(
    #     #     exchange_name=config.exchange_name,
    #     #     market_type=config.market_type,
    #     #     api_key=api_key,
    #     #     secret_key=secret_key,
    #     #     passphrase=passphrase
    #     # )
    #     # For now, simulate success
    #     test_passed = True # Simulate success
    #     if test_passed:
    #         # Optionally update last_tested_at
    #         # config.last_tested_at = datetime.utcnow()
    #         # db.commit()
    #         return {"msg": f"Successfully connected to {config.exchange_name} ({config.market_type})."}
    #     else:
    #         return {"msg": f"Failed to connect to {config.exchange_name} ({config.market_type}). Check credentials and permissions."} # Or raise HTTPException
    # except Exception as e:
    #     # Log the exception e
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Connectivity test failed: {str(e)}")

    # Simulated response for now
    # This should be replaced with actual test logic and appropriate responses.
    # For the framework, we just acknowledge the call.
    # In a real scenario, you'd decrypt keys and make an API call.
    
    # Simulate success for framework
    # In a real implementation, you would decrypt keys using functions from security.py (which crud doesn't have direct access to)
    # and then call the actual exchange API.
    # For now, we assume the test passes if the config is found and active.
    # crud.exchange_config.update_exchange_config(db=db, db_obj=config, obj_in={"last_tested_at": datetime.utcnow()}) # Update timestamp on success
    
    # This is a placeholder. Actual decryption and API call logic will be more complex.
    # For now, we'll just return a success message if the config exists.
    
    # Simulating a call to a test function that might exist in a different module
    # e.g. from app.services.exchange_connectivity import test_connection
    # test_result = await test_connection(config, db) # test_connection would handle decryption
    
    # For the purpose of this task (framework only):
    print(f"Framework: Test connectivity called for config_id: {config_id}, user_id: {current_user.user_id}")
    print(f"Exchange: {config.exchange_name}, Market Type: {config.market_type}")
    # Simulate a successful test for now
    from datetime import datetime # Ensure datetime is imported if not already
    crud.exchange_config.update_exchange_config(db=db, db_obj=config, obj_in={"last_tested_at": datetime.utcnow()})
    
    return {"msg": f"Connectivity test initiated for {config.exchange_name} ({config.market_type}). Framework only - actual test pending."}

# Note: A generic `schemas.Msg` would be:
# class Msg(BaseModel):
#     msg: str
# This should be defined in `app/schemas/__init__.py` or a `msg.py` if used commonly.
# For this example, I'll assume it's available or the response type can be adjusted.