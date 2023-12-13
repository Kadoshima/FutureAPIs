import boto3

# MinIOのエンドポイント、アクセスキー、シークレットキーを設定
endpoint_url = 'http://172.18.0.53:9000'
aws_access_key_id = 'future'
aws_secret_access_key = 'futurepass'

# boto3を使ってMinIOリソースを作成
s3 = boto3.resource(
    's3',
    endpoint_url=endpoint_url,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# バケット名を指定
bucket_name = "future-test"

# バケットが存在しない場合は作成
try:
    s3.meta.client.head_bucket(Bucket=bucket_name)
except botocore.exceptions.ClientError:
    s3.create_bucket(Bucket=bucket_name)

# テストファイルの内容
file_content = "これはテストファイルです。"
file_name = "test.txt"

# バケットにファイルをアップロード
s3.Object(bucket_name, file_name).put(Body=file_content)
