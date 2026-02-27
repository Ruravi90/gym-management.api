from fastapi import APIRouter, Depends, HTTPException, status, Request
from app import crud, models, schemas
from app.utils.auth import get_current_user
from app.models.user import User as UserModel
from app.models.client import Client as ClientModel
from app.models.membership import Membership as MembershipModel
from app.schemas.payment import PreferenceCreate, PreferenceResponse
from app.config import settings
import mercadopago
from app.utils.logging import logger

router = APIRouter()

sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)

async def get_current_client(current_user: UserModel = Depends(get_current_user)) -> ClientModel:
    client = await ClientModel.get_or_none(user_id=current_user.id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client profile not found for this user"
        )
    return client

@router.post("/create-preference", response_model=PreferenceResponse)
async def create_payment_preference(
    preference_data: PreferenceCreate,
    client: ClientModel = Depends(get_current_client)
):
    """
    Create a Mercado Pago preference for a membership purchase.
    """
    try:
        # 1. Get membership type
        membership_type = await crud.membership.get_membership_type(preference_data.membership_type_id)
        if not membership_type:
            raise HTTPException(status_code=404, detail="Membership type not found")

        # 2. Create pending membership record
        # This gives us an ID to use as external_reference in Mercado Pago
        membership = await crud.membership.create_membership({
            "client_id": client.id,
            "membership_type_id": membership_type.id,
            "price": membership_type.price,
            "price_paid": 0.0,
            "status": "pending",
            "payment_status": "pending",
            "payment_method": "mercadopago",
            "type": membership_type.name
        })

        # 3. Create Mercado Pago preference
        preference_body = {
            "items": [
                {
                    "title": f"Membresía: {membership_type.name}",
                    "quantity": 1,
                    "unit_price": float(membership_type.price),
                    "currency_id": "MXN"
                }
            ],
            "payer": {
                "email": client.email if client.email else "user@example.com",
                "name": client.name
            },
            "back_urls": {
                "success": settings.MP_SUCCESS_URL,
                "failure": settings.MP_FAILURE_URL,
                "pending": settings.MP_PENDING_URL
            },
            "auto_return": "all",
            "notification_url": settings.MP_WEBHOOK_URL if settings.MP_WEBHOOK_URL else None,
            "external_reference": str(membership.id)
        }

        if not preference_body["notification_url"]:
            del preference_body["notification_url"]

        logger.info(f"Creating MP preference with body: {preference_body}")
        preference_result = sdk.preference().create(preference_body)
        
        if preference_result["status"] >= 400:
            logger.error(f"Mercado Pago API Error: {preference_result['response']}")
            raise Exception(f"Mercado Pago Error: {preference_result['response'].get('message', 'Unknown error')}")
            
        preference = preference_result["response"]

        # 4. Update membership with preference ID
        if "id" not in preference:
            logger.error(f"Mercado Pago response missing 'id': {preference}")
            raise Exception("Mercado Pago response missing preference ID")

        membership.mp_preference_id = preference["id"]
        await membership.save()

        return {
            "preference_id": preference["id"],
            "init_point": preference["init_point"],
            "sandbox_init_point": preference["sandbox_init_point"]
        }
    except Exception as e:
        logger.error(f"Error creating MP preference: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating payment preference: {str(e)}")

@router.post("/webhook")
async def mercadopago_webhook(request: Request):
    """
    Handle Mercado Pago IPN/Webhook notifications.
    """
    try:
        data = await request.json()
        logger.info(f"Mercado Pago Webhook received: {data}")

        resource_id = None
        topic = None

        if "data" in data and "id" in data["data"]:
            resource_id = data["data"]["id"]
            topic = data.get("type")
        elif "id" in data and "topic" in data:
            resource_id = data["id"]
            topic = data["topic"]

        if topic == "payment" and resource_id:
            logger.info(f"Processing payment {resource_id}...")
            payment_info = sdk.payment().get(resource_id)
            payment_data = payment_info["response"]
            
            status = payment_data.get("status")
            external_reference = payment_data.get("external_reference")
            
            if external_reference:
                membership_id = int(external_reference)
                membership = await MembershipModel.get_or_none(id=membership_id)
                
                if membership:
                    membership.mp_payment_id = str(resource_id)
                    membership.mp_payment_status = status
                    
                    if status == "approved":
                        membership.status = "active"
                        membership.payment_status = "paid"
                        membership.price_paid = float(payment_data.get("transaction_amount", membership.price))
                        # Update client membership type
                        client = await membership.client
                        client.membership_type = membership.type
                        await client.save()
                        logger.info(f"Membership {membership_id} activated successfully.")
                    elif status in ["rejected", "cancelled", "refunded"]:
                        membership.status = "cancelled"
                        membership.payment_status = "unpaid"
                        logger.warning(f"Membership {membership_id} payment {status}.")
                    
                    await membership.save()
                else:
                    logger.warning(f"Membership {membership_id} not found for external_reference.")
            else:
                logger.warning(f"No external_reference found in payment {resource_id}.")

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error in MP webhook: {str(e)}")
        # We return 200 to MP so they stop retrying, but we log the error
        return {"status": "error", "message": str(e)}
