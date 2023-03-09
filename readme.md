# StableGram

Stable Diffusion and ChatGPT Image Posting Automation for Instagram

Here is an example page where ChatGPT produces "random" prompts for Stable Diffusion and captions the images accordingly. This page posts pictures automatically everday:

https://www.instagram.com/stablegpt/

## Installation
```bash
git clone https://github.com/cbauer2018/StableGram.git
cd StableGram
pip install -r requirements.txt
```

## Usage 

1. Create an API key from Stable Diffusion and OpenAI:

https://beta.dreamstudio.ai/

https://platform.openai.com/

2. Create a txt file or use "example_config.txt" to input config settings. Format txt file as follows:

```txt
STABLE DIFFUSION API KEY
OPENAI API KEY
CHATGPT PROMPT
INSTAGRAM USERNAME
INSTAGRAM PASSWORD
```

### Note: 
Include this at the end or near the end of the ChatGPT prompt so the program can correctly parse ChatGPT's output:
```txt
Format your response as Prompt: and then Caption: after that which will be a caption that can be used on Instagram that is trending tab friendly.
```

## Testing
If you want to test the images produced without posting the image add TEST:
```bash
python3 post.py config.txt TEST
```