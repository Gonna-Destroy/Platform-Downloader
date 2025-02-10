from fastapi import FastAPI, Request, HTTPException, Form, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from os import remove
from os.path import isdir, isfile, join, basename, exists
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError, ExtractorError
from pydantic import BaseModel
import asyncio
import time
from uuid import uuid4
import json
import storage
import re

app = FastAPI()
class VideoRequest(BaseModel):
    format: str
    quality: str
    url: str

class Uuid_Video(BaseModel):
    title: str


app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def general(request: Request):
    try: 
        return templates.TemplateResponse("index.html", context={'request': request})
    except:
        return templates.TemplateResponse("error.html", context={'request': request, 'message': '404 Ресурс недоступен.'})


@app.post("/download", response_class=HTMLResponse)
async def send_download_page(request: Request, url: str = Form(...)):
    # try:
    #     response = requests.head(url=url, allow_redirects=True) 
    #     if response.status_code == 200:
    #         try: 
    #             return templates.TemplateResponse('download.html', context={'request': request, 'link': url})
    #         except:
    #             return templates.TemplateResponse("error.html", context={'request': request, 'message': '404 Ресурс недоступен.'})
    #     else:
    #         return templates.TemplateResponse('error.html', {'request': request, 'message': 'По данному URL видео недоступно для скачивания, возможно оно было перемещено.'})
    # except requests.RequestException:
    #     return templates.TemplateResponse('error.html', {'request': request, 'message': 'По данному URL видео недоступно для скачивания, возможно оно было перемещено.'})

    return templates.TemplateResponse('download.html', {'request': request, 'link': url})

@app.get('/static/{filepath}')
async def static(filepath: str):
    if isfile(f"static/{filepath}"):
        return FileResponse(f"static/{filepath}")
    else:
        raise HTTPException(status_code=404, detail="This file is not found!")

def download_video(opt, url):
    with YoutubeDL(opt) as video:
        video.download(url)

@app.post('/success', response_class=JSONResponse)
async def load_video(request: Request, background_task: BackgroundTasks, video_info: VideoRequest):
    
    format_video = video_info.format.lower()
    opt = {}
    title = f"{int(time.time())}_{uuid4()}"

    if format_video == 'mp4':
        opt = {
            'format': 'mp4',
            'outtmpl': join('downloads/',f'{title}.%(ext)s'),
            'progress_hooks': [lambda data: update_progress(data, f'{title}.{format_video}')]
        }
    elif format_video == 'mp3':
        opt = {
            'format': 'bestaudio/best',
            'outtmpl': join('downloads/', f'{title}.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [lambda data: update_progress(data, f'{title}.{format_video}')]

        }
    elif format_video == 'webm':
        # opt = {
        #         'format': 'bestvideo+bestaudio/best', 
        #         'outtmpl': join('downloads/', 'your_video.%(ext)s'),
        #         'postprocessors': [{
        #             'key': 'FFmpegVideoConvertor',
        #             'preferedformat': 'webm'
        #         }]
        #     }
        opt = {
            'format': 'mp4',
            'outtmpl': join('downloads/',f'{title}.%(ext)s'),
            'progress_hooks': [lambda data: update_progress(data, f'{title}.{format_video}')]

        }
        format_video = 'mp4'
    elif format_video == 'ogg':
         opt = {
            'format': 'bestaudio/best',
            'outtmpl': join('downloads/', f'{title}.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'vorbis',
                'preferredquality': '192',
            }],
            'progress_hooks': [lambda data: update_progress(data, f'{title}.{format_video}')]
        }

    background_task.add_task(download_video, opt, video_info.url)
        
    return JSONResponse(content={
            'load': 'start',
            'url': f'downloads/{title}.{format_video}',
        })

def extract_percent(percent_str):
    match = re.search(r'(\d+(\.\d+)?)%', percent_str)
    return match.group(1) if match else "0"

def update_progress(data, title):
    status = data.get('status')
    if status == 'downloading':
        progress_full = data['_percent_str'].strip()
        progress = extract_percent(progress_full)
        storage.update_element(progress, title)
    elif status == 'finished':
        storage.update_element("100.0", title)
    # elif status in ['extracting', 'preparing']:
    #     update_element("preparing", title)

@app.get('/error')
async def get_error(request: Request):
    return templates.TemplateResponse('error.html', {
          'request': request,
          'message': 'К сожалению, видео скачать не удалось в данном формате...\nПроверьте, пожалуйста, URL.'
    })

@app.get('/success')
async def get_video_page(request: Request, format: str, url: str):
    select = ''
    if format.lower() == 'ogg' or format.lower() == 'mp3':
         select = 'audio'
    else: select = 'video'
    return templates.TemplateResponse(f'{select}.html', {'request': request, 'link': url, 'format': format})


def split_video(path, chunk_size = 1024 * 1024):
    with open(f'downloads/{path}', mode='rb') as video:
        while chunk := video.read(chunk_size):
            yield chunk


@app.get('/downloads/{filename}.{format}', response_class=StreamingResponse)
async def get_video(filename: str, format: str):
    path = f'{filename}.{format.lower()}'
    if format.lower() == 'mp3' or format.lower() == 'ogg':
        return StreamingResponse(split_video(path), media_type=f'audio/{format.lower()}')
    else: 
        return StreamingResponse(split_video(path), media_type=f'video/{format.lower()}')


@app.websocket('/progress')
async def get_progress(websocket: WebSocket):
    await websocket.accept()
    while True:
        message = await websocket.receive_text()
        response = json.loads(message)
        uuid = response.get('uuid')
        
        percent = storage.get_element(basename(uuid))

        await websocket.send_json({'curper': percent })

        if percent == "100.0":
            await websocket.close()
            storage.delete_item(basename(uuid))


@app.get('/delete')
async def delete_video(uuid: str):
    remove(uuid)
    if exists(uuid) is False:
        print('true')