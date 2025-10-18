import boto3
import os
import uuid

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3 = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY,  region_name="ap-northeast-2")

# ------------------------------
#  s3 경로 변환 함수
# ------------------------------
def convert_path(path):
    if(path=="m"):
        return os.getenv("S3_PATH_M")
    else:
        return "N"

# ------------------------------
#  s3 경로 생성 함수
# ------------------------------
def create_keyName(path):
    unique_id = str(uuid.uuid4())
    return f"{path}/{unique_id}.webp"

# ------------------------------
#  s3 업로드 함수
# ------------------------------
def upload_s3(output, keyName, contentType):
    S3.put_object(
        Bucket=BUCKET_NAME,
        Key=keyName,
        Body=output,
        ContentType=contentType,
    )

    return f"https://{BUCKET_NAME}.s3.ap-northeast-2.amazonaws.com/{keyName}"