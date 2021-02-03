
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

spawn('python',['./getDataV2.py']).stdout.on('data', (data)=>{
  console.log('sent')
  db.collection('data').doc('qcrew').set({ json: data.toString() })
})