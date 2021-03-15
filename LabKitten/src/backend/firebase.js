
const firebase = require("firebase/app")
require("firebase/auth")
require("firebase/firestore")

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


module.exports = {auth,fire}
