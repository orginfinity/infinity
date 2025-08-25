import requests
import base64 
import os
from azure.identity import DefaultAzureCredential
import time
from io import BytesIO 
import chainlit as cl

async def performVideo(prompt):

    # Set environment variables or edit the corresponding values here.
    endpoint = "https://umesh-meoam0uu-swedencentral.openai.azure.com"

    # Keyless authentication
    credential = DefaultAzureCredential()
    token = credential.get_token("https://cognitiveservices.azure.com/.default")

    api_version = 'preview'
    headers= { "Authorization": f"Bearer {token.token}", "Content-Type": "application/json" }

    # 1. Create a video generation job
    create_url = f"{endpoint}/openai/v1/video/generations/jobs?api-version={api_version}"
    body = {
        "prompt": prompt,
        "width": 480,
        "height": 480,
        "n_seconds": 5,
        "model": "sora"
    }
    response = requests.post(create_url, json=body)
    response.raise_for_status()
    print("Full response JSON:", response.json())
    job_id = response.json()["id"]
    print(f"Job created: {job_id}")

    # 2. Poll for job status
    status_url = f"{endpoint}/openai/v1/video/generations/jobs/{job_id}?api-version={api_version}"
    status=None
    while status not in ("succeeded", "failed", "cancelled"):
        time.sleep(5)  # Wait before polling again
        status_response = requests.get(status_url, headers=headers).json()
        status = status_response.get("status")
        print(f"Job status: {status}")

    # 3. Retrieve generated video 
    if status == "succeeded":
        generations = status_response.get("generations", [])
        if generations:
            print(f"✅ Video generation succeeded.")
            generation_id = generations[0].get("id")
            video_url = f"{endpoint}/openai/v1/video/generations/{generation_id}/content/video?api-version={api_version}"
          
         
        
            headers= { "Authorization": f"Bearer {token.token}", "Content-Type": "video/mp4" }

            video_response = requests.get(video_url, headers=headers)
            if video_response.ok:            
                  
                output_filename = "output.mp4"
                with open(output_filename, "wb") as file:
                    file.write(video_response.content)
                    print(f'Generated video saved as "{output_filename}"')

                    directory = "/tmp"
                    print("printing files")
                    for item in os.listdir(directory):
                        print(item)

                    video = cl.Video(path="/tmp/" + output_filename)
                    await cl.Message(content="",elements=[video]).send()   
                    
        else:
            raise Exception("No generations found in job result.")
    else:
        raise Exception(f"Job didn't succeed. Status: {status}")

async def convertBytesToMP4(bytes):
    import cv2
    import numpy as np

    # Example: Assuming `video_bytes` contains the video data in bytes
    video_bytes = bytes # Replace with your actual byte data

    # Convert bytes to a NumPy array
    video_array = np.frombuffer(video_bytes, dtype=np.uint8)

    # Decode the video bytes into frames using OpenCV
    video_stream = cv2.VideoCapture(cv2.imdecode(video_array, cv2.IMREAD_COLOR))

    # Process the video frames
    while True:
        ret, frame = video_stream.read()
        if not ret:
            break
        # Perform operations on the frame (e.g., display or process)
        cv2.imshow('Frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    video_stream.release()
    cv2.destroyAllWindows()