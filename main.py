from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from os import remove
from os.path import isdir, isfile, join
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError, ExtractorError
from pydantic import BaseModel

app = FastAPI()

class VideoRequest(BaseModel):
    format: str
    quality: str
    url: str

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

@app.post('/success', response_class=JSONResponse)
async def load_video(request: Request, video_info: VideoRequest):
    format_video = video_info.format.lower()
    opt = {}
    if format_video == 'mp4':
        opt = {
            'format': 'mp4',
            'outtmpl': join('downloads/','your_video.%(ext)s')
        }
    elif format_video == 'mp3':
        opt = {
            'format': 'bestaudio/best',
            'outtmpl': join('downloads/', 'your_audio.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }] }
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
            'outtmpl': join('downloads/','your_video.%(ext)s')
        }
        format_video = 'mp4'
    elif format_video == 'ogg':
         opt = {
            'format': 'bestaudio/best',
            'outtmpl': join('downloads/', 'your_audio.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'vorbis',
                'preferredquality': '192',
            }]
        }
    try:
        with YoutubeDL(opt) as video:
            video.download([video_info.url])
            if format_video == 'ogg' or format_video == 'mp3':
                return JSONResponse(
                    content={
                        'load': 'loaded',
                        'url': f'downloads/your_audio.{format_video}'
                    }
                )
            else:
                return JSONResponse(
                    content={
                        'load': 'loaded',
                        'url': f'downloads/your_video.{format_video}'
                    }
                )
    except ExtractorError:
                return JSONResponse(
                content={
                    'load': 'not loaded'
                }
            )
    except DownloadError:
                return JSONResponse(
                content={
                    'load': 'not loaded'
                }
            )
        
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

def split_video(path, chunk_size = 1024 * 4024):
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
