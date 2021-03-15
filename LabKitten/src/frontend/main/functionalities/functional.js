
export {updateJsonTree}

function updateJsonTree(obj, keys, value){
    var parent = obj
    keys.map((key, index)=>{
        if(index < keys.length - 1){
            parent[key] = parent[key] || {}
            parent = parent[key]           
        }
        else{
            parent[key] = value
        }
    })
    //console.log(JSON.stringify(obj,null,2))
    return obj
}
