import boto3
import botocore.config
import json
from datetime import datetime

bedrock = boto3.client(
    "bedrock-runtime",
    region_name="eu-north-1"
)

def generate_blog(topic: str):
    try:
        # Using Converse API format for Qwen model
        messages = [
            {
                "role": "user",
                "content": [{"text": f"Write a detailed blog about {topic}"}]
            }
        ]

        response = bedrock.converse(
            modelId="qwen.qwen3-32b-v1:0",
            messages=messages,
            inferenceConfig={
                "maxTokens": 2000,
                "temperature": 0.7,
                "topP": 0.9
            }
        )

        # Extract the response text from Converse API response
        blog_text = response["output"]["message"]["content"][0]["text"]
        
        return blog_text

    except Exception as e:
        print(f"Error generating the blog: {e}")
        return None


def save_blog_details_s3(s3_key, s3_bucket, generate_blog):
    s3 = boto3.client('s3')

    try:
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=generate_blog)
        print("Blog saved to S3")

    except Exception as e:
        print(f"Error when saving the blog to S3: {e}")


def lambda_handler(event, context):
    try:
        # Parse the event body
        event_body = json.loads(event['body'])
        blog_topic = event_body['blog_topic']

        # Generate the blog
        generated_blog = generate_blog(topic=blog_topic)

        if generated_blog:
            current_time = datetime.now().strftime('%H%M%S')
            s3_key = f"blog-output/{current_time}.txt"
            s3_bucket = 'awsbedrock8004'
            save_blog_details_s3(s3_key, s3_bucket, generated_blog)

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Blog generation completed successfully',
                    's3_key': s3_key
                })
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'message': 'Blog generation failed'
                })
            }

    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error: {str(e)}'
            })
        }


   



