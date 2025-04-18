from fastapi import APIRouter
from models import MessageRequest
from services import Services
import json
import boto3

services = Services()
router = APIRouter()

def load_image_captions_from_s3(bucket: str, key: str) -> dict:
    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket, Key=key)
    content = response["Body"].read().decode("utf-8")
    return json.loads(content)


captions_data = load_image_captions_from_s3(
    bucket="oreillygenaiproductsmarketingdata",
    key="generated_captions/image_captions.json"
)

caption_list = "\n".join([f"{k}: {v}" for k, v in captions_data.items()])

@router.post("/query/recommend_image/", tags=["Marketing Bot"])
def recommend_image(request: MessageRequest):
    response = services.recommended_image_chain.invoke(
        {"persona": request.message, "caption_list" : caption_list}, config={"callbacks": [services.callback_handler]}
    )
    return {"response": response}