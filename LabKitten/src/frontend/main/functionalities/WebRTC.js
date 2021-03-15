
const {fire, auth} = require('./firebase')

class WebRTC{
    constructor({role, docId, data, collection}){
        this.role = role
        this.remoteRole = role==='offerer'?'answerer':'offerer'
        this.collection = collection||'WebRTC'
        this.col = fire().collection(this.collection)
        if(docId) this.doc = this.col.doc(docId)
        this.data = data
        
        if(this.role ==='offerer'){
            if(!this.doc){ 
                this.col.add(this.data).then(doc=>{
                    this.doc = doc
                    this.initOfferer()
                })
            }
            else this.initOfferer()
        }
        else this.initAnswerer()
    }

    initOfferer(){
        this.db = this.doc.collection('signal')
        this.deleteDB().then(()=>{
            this.initPeer()
            this.listenDescription()
            this.makeChannel()
            this.makeDescription()
        })
    }

    initAnswerer(){
        this.db = this.doc.collection('signal')
        this.listenDescription()
    }

    send(data){
        if(this.localChannel && this.localChannel.readyState==='open'){
            this.localChannel.send(data)
        }
        else if(this.remoteChannel && this.remoteChannel.readyState==='open'){
            this.remoteChannel.send(data)
        }
    }

    deleteDB(){
        return this.db.get().then(docs=>{
            var promises = []
            docs.forEach(doc => promises.push(doc.ref.delete()))
            console.log(['@WebRTC.deleteDB',promises.length,'deleted from',this.collection,this.doc.id,'signal'].join('\n'))
            return Promise.all(promises)
        })
    }
    
    makeChannel(){
        this.localChannel = this.peer.createDataChannel(this.role)
        this.localChannel.onopen = e=>this.log('local channel opened')
        this.localChannel.onmessage= this.onMessage
    }
    makeDescription(){   
        var promise = this.role==='offerer'?this.peer.createOffer():this.peer.createAnswer()
        promise.then(description=>{
            this.peer.setLocalDescription(description).then(()=>{
                const {type,sdp} = description
                this.db.doc(this.role).set({type,sdp})
            })
        })
    }
    listenDescription(){
        this.db.doc(this.remoteRole).onSnapshot(doc=>{
            if(doc.exists){
                if(this.role==='answerer') this.initPeer()
                this.peer.setRemoteDescription(new RTCSessionDescription(doc.data()))
                .then(()=>{
                    this.log('remote description set')
                    if(this.role==='answerer') this.makeDescription()
                })
                .catch(e=>this.log(`>> ERROR set description ${e}`))
            }
        })
    }
    
    initPeer(){
        this.peer = new RTCPeerConnection()
        this.listenLocalEvent()
        this.listenRemoteEvent()
    }
    listenLocalEvent(){
        this.peer.onicecandidate=e=>{
            if(!e.candidate) return
            const {candidate,sdpMid,sdpMLineIndex} = e.candidate
            this.db.doc(this.role+'ICE').set({candidate,sdpMid,sdpMLineIndex})
        }
        this.peer.ondatachannel=e=>{
            this.remoteChannel = e.channel
            this.remoteChannel.onopen = e=>this.log('remote channel opened')
            this.remoteChannel.onmessage= this.onMessage
        }
    }
    listenRemoteEvent(){
        this.db.doc(this.remoteRole+'ICE').onSnapshot(doc=>{
            if(doc.exists){
                this.peer.addIceCandidate(new RTCIceCandidate(doc.data()))
                .then(()=>{
                    this.log('remote ice set')
                })
                .catch(e=>this.log(`>> ERROR set ice ${e}`))
            }
        })
    }

    log(x){ console.log( this.role ,x) }
    destroy(){
        while(!this.doc){}
        return this.deleteDB().then(()=> this.doc.delete() )
    }
}

function offerWebRTC(expId, data){
    const uid = auth().currentUser.uid
    return new WebRTC({
        role:'offerer', 
        data:{
            expId, uid, ...data
        }, 
        collection:'WebRTCforExperiments'
    })
}

export {WebRTC, offerWebRTC}
