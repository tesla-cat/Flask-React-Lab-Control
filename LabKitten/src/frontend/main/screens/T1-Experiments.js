
import React, { useState, useEffect } from 'react'
import {List, Body, Input, Row, Btn} from '../../components/main'
import {ExperimentCard, MovieCard} from '../../components/cards'
import {auth, getExperiments, del } from '../../functionalities/firebase'
import { useNavigation } from '@react-navigation/native'

export {Experiments}

function Experiments(){
    const nav = useNavigation()
    const [experiments, setExperiments] = useState({})
	useEffect(()=>{
		auth().onAuthStateChanged(()=>{
			if(auth().currentUser){
                getExperiments(e=>setExperiments(e))
            }
            else nav.navigate('SignUp')
		})
    },[])

    return(
        <Body>
            <List Card={ExperimentCard}>{experiments}</List>
        </Body>
    )
}

