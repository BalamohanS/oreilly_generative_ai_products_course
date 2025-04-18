import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine

class AppConfig:
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
    KNOWLEDGE_BASE_CUSTOMER_SUPPORT_ID = os.environ["KNOWLEDGE_BASE_CUSTOMER_SUPPORT_ID"]
    KNOWLEDGE_BASE_MARKETING_BOT_ID = os.environ["KNOWLEDGE_BASE_MARKETING_BOT_ID"]
    LANGFUSE_PUBLIC_KEY = os.environ["LANGFUSE_PUBLIC_KEY"]
    LANGFUSE_SECRET_KEY = os.environ["LANGFUSE_SECRET_KEY"]
    AWS_REGION = "eu-central-1"
    SCHEMA_NAME = "oreillyproductscrmdb"
    S3_STAGING_DIR = "s3://oreillygenaiproductscrmdata/crm_data/"
    LANGFUSE_HOST = "http://localhost:3000"

def create_database_engine(config: AppConfig):
    connect_str = (
        "awsathena+rest://athena.{region_name}.amazonaws.com:443/"
        "{schema_name}?s3_staging_dir={s3_staging_dir}"
    )
    return create_engine(
        connect_str.format(
            region_name=config.AWS_REGION,
            schema_name=config.SCHEMA_NAME,
            s3_staging_dir=quote_plus(config.S3_STAGING_DIR)
        )
    )