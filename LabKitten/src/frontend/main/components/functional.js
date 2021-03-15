
import React, {useState} from 'react'
import {View} from 'react-native'
import { useNavigation, useRoute } from '@react-navigation/native'

import { Btn} from '../components/main'


export {Parent}

function Parent({obj, ownKey='root', navTo='DocPage'}){
    const nav = useNavigation()
    const p = useRoute().params
    const [showKids, setShowKids] = useState(true)
    if(typeof obj=='string'){
        return(
            <Btn bg='red' on={()=>{ nav.navigate(navTo,{childId: obj, ...p}) }}>{ownKey}</Btn>
        )
    }
    else if(typeof obj=='object'){
        return(
            <View style={{alignItems:'flex-start'}}>
                <Btn on={()=>setShowKids(!showKids)}>{ownKey}</Btn>
                {showKids?<View style={{paddingLeft:20, alignItems:'flex-start'}}>
                    {Object.entries(obj).map(([key, value])=>(
                        <Parent obj={value} ownKey={key}></Parent>                     
                    ))}
                </View>: undefined}
            </View>
        )
    } 
}

