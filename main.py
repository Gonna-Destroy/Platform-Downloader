from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from os.path import join, basename
from yt_dlp import YoutubeDL
# from yt_dlp.utils import DownloadError, ExtractorError
from pydantic import BaseModel
import time
from uuid import uuid4
import json
import re
from multiprocessing import Process, Lock, Manager

# import logging
import clean


app = FastAPI()


lock = Lock()
manager = Manager()
progresses = manager.dict()
processes = {}


# logger = logging.getLogger('processor')
# file_handler = logging.FileHandler(filename='logs/processes.log', mode='a')
# file_handler.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)


class VideoRequest(BaseModel):
    format: str
    quality: str
    url: str

class Uuid_Video(BaseModel):
    title: str


app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")
templates = Jinja2Templates(directory="templates")


@app.on_event('startup')
async def start():
    clear = Process(target=clean.cleaning, daemon=True)
    clear.start()


@app.get("/")
async def general(request: Request):
    return templates.TemplateResponse("index.html", context={'request': request})
    

@app.post("/download", response_class=HTMLResponse)
async def send_download_page(request: Request, url: str = Form(...)):
    return templates.TemplateResponse('download.html', {'request': request, 'link': url})


@app.get('/static/{filepath}')
async def static(filepath: str):
    return FileResponse(f"static/{filepath}")
    

def download_video(opt, url, uuid):
    with YoutubeDL(opt) as video:
        video.download(url)


@app.post('/success', response_class=JSONResponse)
async def load_video(video_info: VideoRequest):
    
    format_video = video_info.format.lower()
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
        format_video = 'mp4'
        opt = {
            'format': 'mp4',
            'outtmpl': join('downloads/',f'{title}.%(ext)s'),
            'progress_hooks': [lambda data: update_progress(data, f'{title}.{format_video}')]
        }
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
         
    uuid = f'{title}.{format_video}'

    process = Process(target=download_video, args=(opt, video_info.url, uuid))
    processes[uuid] = process
    process.start()
        
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
        global lock
        with lock:
            progresses[title] = progress
    elif status == 'finished':
        with lock:
            progresses[title] = "100.0"


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
    title = ''
    try:
        while True:
            message = await websocket.receive_text()
            response = json.loads(message)
            uuid = response.get('uuid')
            title = basename(uuid)
            
            with lock:
                percent = progresses.get(title)

            await websocket.send_json({'curper': percent })

            if percent == "100.0":
                await websocket.close()
    except WebSocketDisconnect:
        process = processes.get(title)
        progress = progresses.pop(title)
        process.kill()

    