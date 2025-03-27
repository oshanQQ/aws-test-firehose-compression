import os
import json
import boto3
import random
import string
import time

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
def generate_test_data(size_kb):
    # 1KBあたりの文字数を概算（UTF-8では1文字1バイトとして）
    chars_per_kb = 1024
    total_chars = size_kb * chars_per_kb

    # ランダムな文字列を生成
    data = "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(total_chars)
    )

    # JSONフォーマットに変換
    result = {"timestamp": time.time(), "data": data}

    return json.dumps(result)


# データをFirehoseに送信する（バッチサイズの制限を考慮）
def send_to_firehose(stream_name, data):
    response = firehose.put_record(
        DeliveryStreamName=stream_name, Record={"Data": data}
    )

    print(f"Sent data to {stream_name}, RecordId: {response['RecordId']}")


def lambda_handler(event, context):
    # 各ストリーム用に1KBのデータを生成（合計で5KB程度）
    for stream in STREAMS:
        print(f"Generating and sending data to {stream}")
        data = generate_test_data(1)  # 1KBのデータ生成
        send_to_firehose(stream, data)
