import React, {useEffect, useState} from 'react'
import { Text, View, ScrollView } from 'react-native'

//======================================
import firebase from "firebase/app"
import "firebase/firestore"
import Plot from 'react-plotly.js'
import { Button, Dimensions } from 'react-native'

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
//======================================

const {width, height} = Dimensions.get('window')
const isPC = width > height

type dataType = { json?: string }
type varListType = {
  xs: { l: string, x: number[] }[],
  ys: { l: string, y: number[], x: number }[],
}

export default function Data(){
  const [data, setData] = useState<dataType>({})
  useEffect(()=>{ listenData(setData) },[])
  
  const varList: varListType = parseData(data)
  if(!varList) return null
  return(
    <ScrollView contentContainerStyle={{flexDirection: 'row', flexWrap:'wrap', justifyContent:'center'}}>
      {varList.ys.map((y, idx)=>{
        const x = varList.xs[y.x]
        return <Fig id={`fig${idx}`} x={x.x} y={y.y} xl={x.l} yl={y.l}/>
      })}
    </ScrollView>
  )
}

type FigType = { id: string, x: number[], y: number[], xl: string, yl: string }
function Fig(p: FigType){
  const [show, setShow] = useState(true)
  const data = [ { x: p.x, y: p.y} ]
  const font = { family: 'Courier New, monospace', size: 18, color: '#7f7f7f' }
  const layout = { xaxis: { title: { text: p.xl, font } }, yaxis: { title: { text: p.yl, font } } } 
  return(
    <View style={{width: isPC? '30%':'100%', margin: isPC? 10: 0 }}>
      <View style={{flexDirection: 'row', padding: 10}}>
        <Text style={{fontSize: 20, fontWeight:'bold', marginLeft: 10}}>{p.yl}</Text>
        <Text style={{fontSize: 20, fontWeight:'bold', marginLeft: 10, color:'blue'}}>{last(p.y)}</Text>
        <View style={{flex: 1}}></View>
        <Button title={show? 'hide': 'show'} onPress={()=>{ setShow(!show) }}></Button>
      </View>
      <View style={{flex: 1, display: show?'flex':'none'}}>
        <Plot data={data} layout={layout}/>
      </View>
    </View>
  )
}

function last(a: any[]){ return a[a.length-1] }

function parseData(data: dataType){
  if(data.json) return JSON.parse(data.json)
}

function listenData(setData: React.Dispatch<React.SetStateAction<dataType>>){
  dataDB.doc('qcrew').onSnapshot((res)=>{
    const data = res.data() 
    if(data) setData(data)
  })
}