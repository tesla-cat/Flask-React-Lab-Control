
const firebase = require("firebase/app") 
require("firebase/firestore")
const spawn = require("child_process").spawn

firebase.initializeApp({
  apiKey: "AIzaSyDuNZv1DauGOJWmbemUzCkXajt5La0wN-A",
  authDomain: "qcrew2021.firebaseapp.com",
  projectId: "qcrew2021",
  storageBucket: "qcrew2021.appspot.com",
  messagingSenderId: "197393268910",
  appId: "1:197393268910:web:e9a8c373956c84b9ddad3f",
  measurementId: "G-80EYHZ0BF4"
})

const db = firebase.firestore()
const dataDB = db.collection('data')

setInterval(()=>{
  getJsonData().then((json)=>{
    console.log('sent')
    dataDB.doc('qcrew').set({ json })
  })
}, 3e3)

function getJsonData(){
  return new Promise((res, rej)=>{
    const pyFile = './getDataV1.py'
    const pythonProcess = spawn('python',[pyFile])
    pythonProcess.stdout.on('data', (data)=>{
      res(data.toString())
      pythonProcess.kill()
    })
  })
}