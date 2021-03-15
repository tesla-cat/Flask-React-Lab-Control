
export {saveHistory, loadHistory, clearHistory}

function saveHistory(p, url, info){
    var history = localStorage.getItem('history') 
    history = JSON.parse(history) || {}
    if(!history.movies) history.movies = {}
    history.movies[p.vod_id] = {...p, url, info}
    localStorage.setItem('history', JSON.stringify(history))    
}

function loadHistory(){
    var history = localStorage.getItem('history') 
    if(!history) return {}
    var {movies} = JSON.parse(history)
    return movies
}

function clearHistory(ids){
    var history = localStorage.getItem('history') 
    if(!history) return 
    history = JSON.parse(history)
    ids.map(id=> delete history.movies[id] )
    localStorage.setItem('history', JSON.stringify(history))    
}

