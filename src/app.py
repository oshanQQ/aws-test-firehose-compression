import os
import json
import boto3
import random
import string
import time
from io import BytesIO
import base64

# Firehoseクライアントの初期化
firehose = boto3.client("firehose")

# 環境変数からFirehoseストリーム名を取得
GZIP_STREAM = os.environ["GZIP_STREAM"]
SNAPPY_STREAM = os.environ["SNAPPY_STREAM"]
ZIP_STREAM = os.environ["ZIP_STREAM"]
HADOOP_SNAPPY_STREAM = os.environ["HADOOP_SNAPPY_STREAM"]
NO_COMPRESSION_STREAM = os.environ["NO_COMPRESSION_STREAM"]

# すべてのストリームのリスト
STREAMS = [
    GZIP_STREAM,
    SNAPPY_STREAM,
    ZIP_STREAM,
    HADOOP_SNAPPY_STREAM,
    NO_COMPRESSION_STREAM,
]


# 指定されたサイズのテストデータを生成
def generate_test_data(size_mb=10):
    # 1MBあたりの文字数を概算（UTF-8では1文字1バイトとして）
    chars_per_mb = 1024 * 1024
    total_chars = size_mb * chars_per_mb

    # ランダムな文字列を生成
    data = "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(total_chars)
    )

    # JSONフォーマットに変換
    result = {"timestamp": time.time(), "data": data}

    return json.dumps(result)


# データをFirehoseに送信する（バッチサイズの制限を考慮）
def send_to_firehose(stream_name, data, batch_size=4 * 1024 * 1024):
    # データをバイト列に変換
    data_bytes = data.encode("utf-8")
    data_size = len(data_bytes)

    # 4MBごとにバッチ分割
    for i in range(0, data_size, batch_size):
        chunk = data_bytes[i : i + batch_size]

        # Base64エンコードしてFirehoseに送信
        encoded_data = base64.b64encode(chunk).decode("utf-8")

        response = firehose.put_record(
            DeliveryStreamName=stream_name, Record={"Data": encoded_data}
        )

        print(
            f"Sent chunk {i//batch_size + 1} to {stream_name}, RecordId: {response['RecordId']}"
        )


def lambda_handler(event, context):
    try:
        # 各ストリーム用に10MBのデータを生成（合計で50MB程度）
        for stream in STREAMS:
            print(f"Generating and sending data to {stream}")
            data = generate_test_data(10)  # 10MBのデータ生成
            send_to_firehose(stream, data)

        return {
            "statusCode": 200,
            "body": json.dumps("Data successfully sent to all Firehose streams"),
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"statusCode": 500, "body": json.dumps(f"Error: {str(e)}")}
