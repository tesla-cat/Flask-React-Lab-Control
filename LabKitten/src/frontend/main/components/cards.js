
import React, { useState } from 'react'
import {View, Image, TouchableOpacity} from 'react-native'
import {useNavigation} from '@react-navigation/native'

import { Row, Txt, IconBtn, Btn } from './main'

import { delExperiment, delOffer } from '../functionalities/firebase'
import {clearHistory} from '../functionalities/storage'

import {styles} from '../styles/main'


export {ExperimentCard, OfferCard, MovieCard, DocCard}

function ExperimentCard({id, data, index}){
    const nav = useNavigation()
    return(
        <View style={ [{  }, styles.card ] }>
            <Row style={{
                flex:1,
            }}>
                <IconBtn on={()=>delExperiment(id)}>{'delete'}</IconBtn>
                <View style={{
                    flex:1, 
                    paddingHorizontal:10
                }}>
                    <Txt>{[index+1, data.experimentName].join('. ') }</Txt>
                </View>
                <IconBtn on={()=>nav.navigate('Connection',{id,data})}>{'next'}</IconBtn>
            </Row>
        </View>
    )
}

function OfferCard({id, data, index}){
    const nav = useNavigation()
    return(
        <View style={ [{  }, styles.card ] }>
            <Row style={{
                flex:1,
            }}>
                <IconBtn on={()=>delOffer(id)}>{'delete'}</IconBtn>
                <View style={{
                    flex:1, 
                    paddingHorizontal:10
                }}>
                    <Txt>{[index+1, data.info].join('. ') }</Txt>
                </View>
            </Row>
        </View>
    )
}

/*
type_name, vod_actor, vod_content, vod_director, vod_id, vod_lang, 
vod_name, vod_pic, vod_play_url, vod_remarks, vod_year, 
*/
function MovieCard({id, data, index}){
    const nav = useNavigation()
    const [hide, setHide] = useState(false)
    const {
        type_name, vod_actor, vod_content, vod_director, vod_id, vod_lang, 
        vod_name, vod_pic, sources, vod_remarks, vod_year,
    } = data
    if(hide) return <View></View>
    return(
        <View style={{
            margin:10,
            borderRadius: 30,
            overflow: 'hidden',
            backgroundColor:'azure',
            alignSelf:'center',
        }}>
            <TouchableOpacity onPress={()=>{
                nav.navigate('Player', data)
            }}>
                <Image 
                    style={{height:400, width:300 }} 
                    source={{uri: vod_pic}}
                ></Image>
            </TouchableOpacity>
            <Row style={{padding:10}}><Txt c='grey'>{data.info || vod_name}</Txt></Row>
            {data.url? <Row><Btn on={()=>{
                clearHistory([id])
                setHide(true)
            }}>清除记录</Btn></Row> :undefined}
        </View>
    )
}

function DocCard({id, data, index}){
    const nav = useNavigation()
    return(
        <View style={ [{  }, styles.card ] }>
            <Row style={{
                flex:1,
            }}>
                <IconBtn on={()=>nav.navigate('DocSettings',{id, data})}>{'settings'}</IconBtn>
                <View style={{
                    flex:1, 
                    paddingHorizontal:10
                }}>
                    <Txt>{[index+1, data.title].join('. ') }</Txt>
                </View>
                <IconBtn on={()=>nav.navigate('DocTree',{id, data})}>{'next'}</IconBtn>
            </Row>
        </View>
    )
}

