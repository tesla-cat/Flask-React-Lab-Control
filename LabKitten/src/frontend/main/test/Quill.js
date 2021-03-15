
import React, { useState, useEffect } from 'react'
import {List, Body, Input, Row, Btn} from '../components/main'
import { fire } from '../functionalities/firebase'
import { useNavigation } from '@react-navigation/native'
import { auth } from 'firebase'

export {Temporary}

const url = 'https://doc-kitten.github.io/editor'

function Temporary(){
    useEffect(()=>{
        window.onmessage = function(e){
            if(e.data){
                var delta = JSON.parse(e.data)
                console.log(delta)
            }
        }
    },[])
    
    var webView
    return(
        <Body>
            <iframe ref={r=> webView = r }
                src={url} frameborder="0" width='100%' height='100%' allowTransparency
                allowFullScreen="true" webkitallowfullscreen="true" mozallowfullscreen="true"
            ></iframe>
            
        </Body>
    )
}

function listenUpdate(callback){
    window.onmessage = function(e){
        if(e.data) callback(JSON.parse(e.data))
    }
}

function updateContent(id, data){
    fire().collection('docContents').doc(id).update(data)
}



/**
<Btn on={()=>{
                if(webView){
                    var delta = [
                        { insert: 'Hi ' },
                        { insert: 'World!', attributes: { bold: true } },
                        { insert: '\n' }
                    ]
                    var message = {delta}
                    webView.contentWindow.postMessage(JSON.stringify(message), '*')
                }
            }} >hi</Btn>
            <Btn on={()=>{
                if(webView){
                    var update = true
                    var message = {update}
                    webView.contentWindow.postMessage(JSON.stringify(message), '*')
                }
            }} >hi</Btn>
*/

