
import { updateJsonTree } from './functional'

//========================================================

var firebase = require("firebase/app")
require("firebase/auth")
require("firebase/firestore")
require("firebase/storage")

firebase.initializeApp({
    apiKey: "AIzaSyAiMSvhJ1Ce3Wf_xxXBFEhyGTf0fAJg-Q0",
    authDomain: "lab-kitten.firebaseapp.com",
    databaseURL: "https://lab-kitten.firebaseio.com",
    projectId: "lab-kitten",
    storageBucket: "lab-kitten.appspot.com",
    messagingSenderId: "247443746356",
    appId: "1:247443746356:web:11bae44b3f5a4e7fb96461",
    measurementId: "G-RXHZK2D1LD"
})

const auth = firebase.auth
const fire = firebase.firestore
const store = firebase.storage

//========================================================

function checkEmail(email){
    var domain = email.split('@')[1]
    if(! (domain && domain.includes('edu')) ){
        alert('please enter an edu email')
        return false
    }
    else{
        return true
    }
}

function signUp(form){
    var {email, password} = form
    if(! checkEmail(email)) return
    auth().createUserWithEmailAndPassword(email,password)
    .then(user=>{
        auth().currentUser.sendEmailVerification()
        .then(()=>alert('verification email sent, retry after verification'))
        .then(()=>auth().signOut())
    })
    .catch(({code})=>{
        if(code=='auth/email-already-in-use'){
            signIn(email,password)
        }
        else{
            alert(code); console.log(code)
        }
    })
}

function signIn(email,password){
    auth().signInWithEmailAndPassword(email,password)
    .then(user=>{
        if(! auth().currentUser.emailVerified){
            alert('retry after email verification')
            auth().signOut()
        }
    })
    .catch(({code})=>{
        alert(code); console.log(code)
    })
}

function passwordReset(form){
    var {email} = form
    if(! checkEmail(email)) return
    auth().sendPasswordResetEmail(email)
    .then(()=>alert('password reset email sent'))
}

//========================================================

function get(collection, key, value, resolve){
    fire().collection(collection).where(key,'==',value).onSnapshot(snap=>{
        var results = {}
        snap.forEach(doc=>{ if(doc.exists) results[doc.id] = doc.data() })
        resolve(results)
    })
}

function get2(collection, array, item, resolve){
    fire().collection(collection).where(array,'array-contains',item).onSnapshot(snap=>{
        var results = {}
        snap.forEach(doc=>{ if(doc.exists) results[doc.id] = doc.data() })
        resolve(results)
    })
}

function getExperiments(resolve){
    get('experiments','uid', auth().currentUser.uid , resolve)
}

function getOffers(expId, resolve){
    get('WebRTCforExperiments','expId',expId,resolve)
}

function getHelps(targetId, resolve){
    get('helps','targetId',targetId,resolve)
}

function getDocs(resolve){
    get2('docs', 'collaborators', auth().currentUser.email, resolve)
}

//========================================================

function getDocTree(p, resolve){
    fire().collection('docs').doc(p.id).collection('children').onSnapshot(snap=>{
        var tree = {}
        snap.forEach(doc=>{
            var {path} = doc.data()
            tree = updateJsonTree(tree, path.split('/'), doc.id)
        })
        resolve(tree)
    })
}

//========================================================

function del(collection,id,subcols=[]){
    var doc = fire().collection(collection).doc(id)
    return Promise.all( 
        subcols.map(col=>{
            return doc.collection(col).get().then(docs=>{
                var promises = []
                docs.forEach(doc =>{
                    promises.push(doc.ref.delete())
                })
                console.log(['@firebase.del',promises.length,'deleted from',collection,id,col].join('\n'))
                return Promise.all(promises)
            })
        })
    ).then(()=> doc.delete() )
}

function delExperiment(id){
    return del('experiments',id)
}

function delOffer(id){
    return del('WebRTCforExperiments',id,['signal'])
}

//========================================================

function saveSettings(id, form){
    if(! Object.values(form).every(v=>v)) return
    var {title, collaborators, uid} = form
    collaborators = collaborators.split('\n').map(v=>v.trim())
    var email = auth().currentUser.email
    if(! collaborators.includes(email)) collaborators.push(email) 
    var doc = id ? fire().collection('docs').doc(id) : fire().collection('docs').doc()
    doc.set({title, collaborators, uid})
    return doc.id
}

function saveDocPage(p, form, delta){
    const {path} = form
    if(!path){ alert('please specify a path'); return }

    var col1 = fire().collection('docPages')
    var col2 = fire().collection('docs').doc(p.id).collection('children')
    var pageDoc = p.childId ? col1.doc(p.childId) : col1.doc()

    Promise.all( delta.ops.map((op, index)=>{
        var {insert:{image}} = op
        if( image && image.startsWith('data')){
            return urltoFile(image, 'hi').then(file=>{
                var ref = store().ref(['userFiles', auth().currentUser.uid, pageDoc.id+index].join('/'))
                return ref.put(file).then(snap=>{
                    return ref.getDownloadURL().then(url=>{
                        op.insert.image = url                        
                        return op
                    })                    
                })
            })
        }
        else return op
    }) ).then(ops=>{
        pageDoc.set({delta: JSON.stringify({delta: ops }) , path})
        console.log(pageDoc.id)
        col2.doc(pageDoc.id).set({path})
    })    
}

function urltoFile(url, filename, mimeType='image/png'){
    return fetch(url).then(res=>res.arrayBuffer())
    .then(buf=>new File([buf], filename, {type:mimeType}))
}

//========================================================

export {
    auth, fire, 
    signUp, passwordReset, 
    get, getExperiments, getOffers, getDocs, getHelps,
    del, delExperiment , delOffer ,
    saveSettings, saveDocPage, 
    getDocTree, 
}
