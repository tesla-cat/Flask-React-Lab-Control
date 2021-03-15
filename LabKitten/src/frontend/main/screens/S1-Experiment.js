
import React, { useState, useEffect } from 'react'
import {useRoute} from '@react-navigation/native'

import {List, Body, Row, Btn} from '../../components/main'
import {OfferCard} from '../../components/cards'
import {getOffers, delOffer } from '../../functionalities/firebase'

export {Experiment}

function Experiment(){
    const p = useRoute().params
    const [offers, setOffers] = useState({})
    useEffect(()=>{
        getOffers(p.id, o=>setOffers(o))
    },[])

    return(
        <Body>
            <Row>
                <Btn on={()=>{
                    Object.keys(offers).map(id=> delOffer(id) )
                }}>delete all</Btn>
            </Row>
            <List Card={OfferCard}>{offers}</List>
        </Body>
    )
}