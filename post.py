import os
import io
import warnings
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import openai
from instagrapi import Client
import sys


def readconfig(filename)-> list[str]:
    file = open(filename)
    return file.readlines()

def create_prompt_caption(content:str) -> list[str]:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "user", "content": content},
    ])

    parsePrompt = response['choices'][0]['message']['content'].split("Prompt: ")[1]
    prompt = parsePrompt.split("Caption:")[0]
    caption = parsePrompt.split("Caption:")[1].replace('"', '')
    return [prompt,caption]



def createimage(prompt:str) -> str:

    
    # Set up our connection to the Stable Diffusion API.
    stability_api = client.StabilityInference(
    key=os.environ['STABILITY_KEY'], # API Key reference.
    verbose=True, # Print debug messages.
    engine="stable-diffusion-768-v2-1", # Set the engine to use for generation.
    # Available engines: stable-diffusion-v1 stable-diffusion-v1-5 stable-diffusion-512-v2-0 stable-diffusion-768-v2-0
    # stable-diffusion-512-v2-1 stable-diffusion-768-v2-1 stable-inpainting-v1-0 stable-inpainting-512-v2-0
    )


    # Set up our initial generation parameters.
    answers = stability_api.generate(
        prompt=prompt,
                     # If a seed is provided, the resulting generated image will be deterministic.
                    # What this means is that as long as all generation parameters remain the same, you can always recall the same image simply by generating it again.
                    # Note: This isn't quite the case for Clip Guided generations, which we'll tackle in a future example notebook.
        steps=30, # Amount of inference steps performed on image generation. Defaults to 30.
        cfg_scale=8.0, # Influences how strongly your generation is guided to match your prompt.
                   # Setting this value higher increases the strength in which it tries to match your prompt.
                   # Defaults to 7.0 if not specified.
        width=1024, # Generation width, defaults to 512 if not included.
        height=1024, # Generation height, defaults to 512 if not included.
        samples=1, # Number of images to generate, defaults to 1 if not included.
        sampler=generation.SAMPLER_K_DPMPP_2M # Choose which sampler we want to denoise our generation with.
                                                 # Defaults to k_dpmpp_2m if not specified. Clip Guidance only supports ancestral samplers.
                                                 # (Available Samplers: ddim, plms, k_euler, k_euler_ancestral, k_heun, k_dpm_2, k_dpm_2_ancestral, k_dpmpp_2s_ancestral, k_lms, k_dpmpp_2m)
    )

    # Set up our warning to print to the console if the adult content classifier is tripped.
    #If adult content classifier is not tripped, save generated images.
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn(
                "Your request activated the API's safety filters and could not be processed."
                "Please modify the prompt and try again.")
            if artifact.type == generation.ARTIFACT_IMAGE:

                full_path = os.path.realpath(__file__)
                img = Image.open(io.BytesIO(artifact.binary))

                #Create /images directory if none exists
                imagepath = os.path.dirname(full_path)+ "/images/"
                isExist = os.path.exists(imagepath)
                if not isExist:
                    os.makedirs(imagepath)


                path = imagepath + str(artifact.seed)+ ".jpg"
                img.save(path) # Save our generated images with their seed number as the filename.
                return path
    
    return None

def postcontent(username:str, password:str, imagepath:str, caption:str):
    bot = Client()
    bot.login(username,password)
    media = bot.photo_upload(path= imagepath, caption=caption.replace('"', ''))

if __name__ == "__main__":

    mode = "POST"

    try:
     assert len(sys.argv) >= 2
     if len(sys.argv) > 2:
        mode = sys.argv[2]
    except AssertionError:
        print("Usage: python3 post.py config.txt")
        raise

    
    config = readconfig(sys.argv[1])
    try:
     assert len(config) == 5
    except AssertionError:
        print("There must be 5 lines in config file: Stable Diffusion API key, OpenAI API key, ChatGPT Prompt, Instagram Username, Password")
        raise


    #Set environment variables
    os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
    os.environ['STABILITY_KEY'] = config[0].strip()
    os.environ['OPENAI_API_KEY'] = config[1].strip()
    openai.api_key = os.getenv("OPENAI_API_KEY")



    response = create_prompt_caption(config[2].strip())
    imagepath = createimage(response[0].strip())
    if(mode.upper() == "TEST"):
        print("Generated Prompt: " + response[0])
        print("Caption: " + response[1])
        sys.exit()

    postcontent(username=config[3].strip(), password=config[4].strip(), imagepath=imagepath, caption=response[1])
