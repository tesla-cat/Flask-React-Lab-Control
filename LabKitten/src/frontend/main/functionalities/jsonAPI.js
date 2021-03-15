
export {getMovies, httpGetAsync}

function httpGetAsync(theUrl){
    return new Promise((resolve, reject)=>{
        var xmlHttp = new XMLHttpRequest()
        xmlHttp.onreadystatechange = function() { 
            if (xmlHttp.readyState == 4 && xmlHttp.status == 200) resolve(xmlHttp.responseText)
        }
        xmlHttp.open("GET", theUrl, true) // true for asynchronous 
        xmlHttp.send(null)
    })
}

function getMovies(keyword){
    if(! keyword) return new Promise((resolve,reject)=>{}) 
    const url2 = 'https://api.okzy.tv/api.php/provide/vod/at/json/?ac=detail&wd='
    return httpGetAsync(url2 + keyword).then(res=>cleanMovies(res))
}

function cleanMovies(res){
    var movies = {}
    JSON.parse(res).list.map((movie, index)=>{
        var sources = movie.vod_play_url.split('$$$').map(source=>{
            var epsodes = source.split('#').map(episode=>episode.split('$'))
            return epsodes
        })
        delete movie.vod_play_url
        movies[index] = {...movie, sources}
    })
    return movies
}

