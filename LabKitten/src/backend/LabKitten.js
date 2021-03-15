
const net = require('net')
const {auth,fire} = require('./firebase')
const {WebRTC} = require('./WebRTC')

class LabKitten{
    constructor({email,password,experimentName,port,debug}){
        this.email = email; this.password = password
        this.expName = experimentName
        this.port = port; this.debug = debug
        this.peers = {}

        this.initServer()
        this.listenWebRTC()
    }
    initServer(){
        net.createServer(socket=>{
            socket.on('data',data=>{
                if(this.debug==='True') console.log('received',data.byteLength,'bytes')
                Object.values(this.peers).map(peer=>{
                    //console.log('send to ', peer.doc.id)
                    peer.send(data.toString())
                })
            })
        }).listen(this.port,()=>console.log('server started at local port',this.port))
    }

    signIn(){
        return auth().signInWithEmailAndPassword(this.email, this.password).then(user=>{
            if(!auth().currentUser.emailVerified){
                console.log('retry after email verification')
            }
            else{ this.uid = auth().currentUser.uid }
        }).catch(e=>console.log(e))
    }
    setExperiment(){
        return this.signIn().then(()=>{
            this.expId = [this.uid, this.expName].join('.')
            return fire().collection('experiments').doc(this.expId).set({uid:this.uid, experimentName: this.expName})
        })
    }
    listenWebRTC(){
        this.setExperiment().then(()=>{
            fire().collection('WebRTCforExperiments').where('expId','==',this.expId).onSnapshot(snap=>{
                snap.docChanges().forEach(change=>{
                    if(change.type=='added'){
                        this.peers[change.doc.id] = new WebRTC({role:'answerer', docId:change.doc.id, collection:'WebRTCforExperiments'})
                    }
                    else{
                        delete this.peers[change.doc.id]
                    }
                })
            })
        })
    }
}

// demo

const port = process.argv[2] 
const email = process.argv[3] 
const password = process.argv[4] 
const debug = process.argv[5] 
const experimentName = process.argv[6] 

var labKitten = new LabKitten({email,password,experimentName,port,debug})

