document.addEventListener("DOMContentLoaded", load)

function load(){
    const urls = [
        'static/pictures/second-picture.jpg',
        'static/pictures/third-picture.jpg',
        'static/pictures/fourth-picture.jpg'
    ];

    const images = [];

    urls.forEach(url => {
        image = new Image()
        image.src = url
        images.push(image)
    })
}