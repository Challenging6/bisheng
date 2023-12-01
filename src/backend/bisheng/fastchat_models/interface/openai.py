# import json
import openai
import asyncio
from openai import AsyncOpenAI, OpenAI
from .types import ChatInput, ChatOutput, Choice, Usage
from .utils import get_ts


class ChatCompletion(object):

    def __init__(self, api_key, api_base_url, proxy=None, **kwargs):
        openai.api_key = api_key
        openai.api_base = api_base_url
        openai.proxy = proxy
        self.client = OpenAI(api_key=api_key, base_url=api_base_url)
        self.async_client = AsyncOpenAI(api_key=api_key, base_url=api_base_url)
        

    async def async_chat(self, **kwargs):
        chat_completion = await self.async_client.chat.completions.create(**kwargs)   
        yield chat_completion
        
    def __call__(self, inp: ChatInput, verbose=False):
        messages = inp.messages
        model = inp.model
        top_p = 0.7 if inp.top_p is None else inp.top_p
        temperature = 0.97 if inp.temperature is None else inp.temperature
        stream = False if inp.stream is None else inp.stream
    
        max_tokens = 1024 if inp.max_tokens is None else inp.max_tokens
        stop = None
        if inp.stop is not None:
            stop = inp.stop.split('||')

        new_messages = [m.dict() for m in messages]
        created = get_ts()
        payload = {
            'model': model,
            'messages': new_messages,
            'temperature': temperature,
            'top_p': top_p,
            'stop': stop,
            'max_tokens': max_tokens,
            
        }
        if inp.functions:
            payload.update({'functions': inp.functions})

        if verbose:
            print('payload', payload)

        req_type = 'chat.completion'
        status_message = 'success'
        choices = []
        usage = Usage()
        try:
            resp = self.client.chat.completions.create(**payload)
            status_code = 200
            choices = resp.choices
            usage = resp.usage
        except Exception as e:
            status_code = 400
            status_message = str(e)

        if status_code != 200:
            raise Exception(status_message)

        return ChatOutput(status_code=status_code,
                          status_message=status_message,
                          model=model,
                          object=req_type,
                          created=created,
                          choices=choices,
                          usage=usage)
