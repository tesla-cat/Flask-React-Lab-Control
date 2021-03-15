import React, { useState } from 'react'
import {View} from 'react-native'
import {Btn, Row, Txt} from '../components/main'

import Plotly from "plotly.js"
import createPlotlyComponent from 'react-plotly.js/factory'
const Plot = createPlotlyComponent(Plotly)

const {WebRTC} = require('../functionalities/WebRTC')

export {WebRTCtest}

function WebRTCtest(){
    const [data, setData] = useState({x:[],y:[]})    
    function makePeer(role){
        var peer = new WebRTC({role, docId:'test'})
        if(role==='offerer'){ 
            peer.onMessage = e=>setData(JSON.parse(e.data))
        }
        else{
            setInterval(()=>{
                var time = new Date().getTime()/1000
                var {x,y} = makeSin(time-1,time,100,1)
                peer.send(JSON.stringify({x,y}))
            },100)
        }
    }

    return(
        <View style={{backgroundColor:'white', flex:1, justifyContent:'center'}}>
            <Row>
				<Btn bg='grey' c='white' on={()=>makePeer('offerer')}>make offer</Btn>	
				<Btn bg='grey' c='white' on={()=>makePeer('answerer')}>make answer</Btn>
			</Row>
            <Plot data={[{x: data.x, y: data.y, type: 'scatter'}]}
                layout={{width: 600, height: 600, title: 'Monitor Your Lab !'}}
            />
        </View>
    )
}

function makeSin(t0,t1,N,f){
    const dt = (t1-t0)/N
    const t = Array(N).fill(1).map((v,i)=>t0+i*dt)
    const sin = t.map(ti=>Math.sin(2*Math.PI*f*ti))
    return {x:t, y:sin}
}
