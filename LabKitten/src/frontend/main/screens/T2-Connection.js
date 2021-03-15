
import React, { useState, useEffect } from 'react'
import {View, ScrollView, ActivityIndicator} from 'react-native'
import {useRoute, useNavigation} from '@react-navigation/native'

import {Input, Txt, IconBtn, Row, Body} from '../../components/main'
import {Plots} from '../../components/plotly'

import {styles} from '../../styles/main'

const { offerWebRTC } =  require('../../functionalities/WebRTC')

export {Connection}

function Connection(){
    const p = useRoute().params
    const nav = useNavigation()

    const [peer, setPeer] = useState()
    const [plotData, setPlotData] = useState()
    const [form, setForm] = useState({ info: 'made by () on device ()' })

    function makePeer(){
        var peer_ = offerWebRTC(p.id, form) 
        peer_.onMessage = ({data})=> { setPlotData(JSON.parse(data))}
        setPeer(peer_)
    }
    
    useEffect(()=>{
        if(!p) return
        setPlotData()
        if(peer){
            if(p.id != peer.data.expId){
                peer.destroy().then(()=>{
                    makePeer()
                })
            }
        }
        else makePeer()
    }, [p])

    if(!p) return <Body><Row><Txt>please select one experiment</Txt></Row></Body>

    return(
        <Body>
            <ScrollView>
                <View style={styles.card}>
                    <Row>
                        <View style={{flex:1}}>
                            <Txt>a connection to {p.data.experimentName}</Txt>
                        </View>
                        <IconBtn on={()=>nav.navigate('Experiment', p)}>{'more'}</IconBtn>
                    </Row>
                    <Row>
                        <Row style={{flex:1}}>
                            <Input p='info' on={info=>{ setForm(Object.assign({...form}, {info})) }}>{form.info}</Input>
                        </Row>
                        <IconBtn on={()=>{ 
                            if(peer && peer.doc){
                                //fire().collection('WebRTCforExperiments').doc(peer.doc.id).update(form)
                                alert('a bug to be fixed: updating the info causes disconnection')
                            }
                        }} >{'check'}</IconBtn>
                    </Row>
                </View>
                
                {plotData? <Plots>{plotData}</Plots>: <ActivityIndicator size='large'></ActivityIndicator>}
            </ScrollView>
        </Body>
    )
}

