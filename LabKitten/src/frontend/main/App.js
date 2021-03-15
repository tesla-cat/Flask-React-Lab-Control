
import React from 'react'
import {View} from 'react-native'
import {NavigationContainer} from '@react-navigation/native'
import { createStackNavigator } from '@react-navigation/stack'

import {IconBtn, Row, Box, Btn, Txt} from './components/main'

import {HomeTabs} from './HomeTabs'

import {Experiment} from './screens/lab-kitten/S1-Experiment'

import {DocSettings} from './screens/doc-kitten/S1-DocSettings'

import { Helpers } from './screens/angel-kitten/T2-Helping'

export {appName}
export default App

const appName = 'angel-kitten'
const Stack = createStackNavigator()

function App(){
    return(
        <View style={{height:'100vh', maxWidth:'100vw', margin:'auto'}}>
            <NavigationContainer>
                <Stack.Navigator screenOptions={{
                    headerStyle: {
                        height:50,
                    },
                }}>
                    <Stack.Screen name='HomeTabs' component={HomeTabs} 
                        options={{ headerTitle: props => <LogoTitle {...props} /> }}
                    />
                </Stack.Navigator>
            </NavigationContainer>
        </View>
    )
}

function LogoTitle(){
    return(
        <Row>
            <IconBtn s={40} on={()=>openTab('https://github.com/lab-kitten/lab-kitten')}>{appName||'lab-kitten'}</IconBtn>
            <Box w={10}></Box>
            <Btn on={()=>openTab('https://github.com/lab-kitten/lab-kitten')}>{appName}</Btn>
            <Box f={1}></Box>
        </Row>
    )
}

function openTab(url){
    window.open(url, '_blank')
}


/*
    <Stack.Screen name='Experiment' component={Experiment} 
        options={({ route }) => ({ 
            title: ['connections to', route.params.data.experimentName].join(' ')
        })}
    />
    <Stack.Screen name='DocSettings' component={DocSettings} 
        options={({ route }) => ({title: route.params? 'doc settings':'new doc'})}
    />
    <Stack.Screen name='Helpers' component={Helpers} 
        options={({ route }) => ({title: 'Helpers'})}
    />
*/