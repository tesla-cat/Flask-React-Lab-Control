
import React from 'react'
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs'

import {Icon} from './components/main'

import {SignUp} from './screens/common/SignUp'

import {Experiments} from './screens/lab-kitten/T1-Experiments'
import {Connection} from './screens/lab-kitten/T2-Connection'

import {Movies} from './screens/movie-kitten/T1-Movies'
import {Player} from './screens/movie-kitten/T2-Player'

import {Docs} from './screens/doc-kitten/T1-Docs'
import {DocTree} from './screens/doc-kitten/T2-DocTree'
import {DocPage} from './screens/doc-kitten/T3-DocPage'

import { Game } from './screens/3d-kitten/T1-Game'

import { SupplicantInfo } from './screens/angel-kitten/T1-SupplicantInfo'
import { Helping } from './screens/angel-kitten/T2-Helping'

import {appName} from './App'

export {HomeTabs}

const routeToIcon = {
    SignUp: 'authentication', 
    Experiments: 'experiment', Connection: 'connection',
    Movies: 'movies', Player: 'player',
    SupplicantInfo:'info', Helping: 'helping',
}

const Tab = createBottomTabNavigator()

function HomeTabs(){
    return (
        <Tab.Navigator
            screenOptions={({ route }) => ({
                tabBarIcon: ({ focused, color, size }) => {
                    return <Icon>{ routeToIcon[route.name] }</Icon>
                },
            })}
            tabBarOptions={{
                activeTintColor: 'tomato',
                inactiveTintColor: 'gray',
            }}
        >
            <Tab.Screen name='Movies' component={Movies} options={{title:'Movies'}}/>
            <Tab.Screen name='Player' component={Player} options={{title:'Player'}}/>
            <Tab.Screen name='SignUp' component={SignUp} options={{title:'Auth'}}/>
        </Tab.Navigator>
    )
}

/**
 *          { appName === 'lab-kitten' ? (
                <>
                    <Tab.Screen name='Experiments' component={Experiments} options={{title:'Experiments'}}/>
                    <Tab.Screen name='Connection' component={Connection} options={{title:'Connection'}}/>
                </>
            ) : undefined }
            { appName === 'movie-kitten' ? (
                <>
                    <Tab.Screen name='Movies' component={Movies} options={{title:'Movies'}}/>
                    <Tab.Screen name='Player' component={Player} options={{title:'Player'}}/>
                </>
            ) : undefined }
            { appName === 'doc-kitten' ? (
                <>
                    <Tab.Screen name='Docs' component={Docs} options={{title:'Docs'}}/>
                    <Tab.Screen name='DocTree' component={DocTree} options={{title:'Doc Tree'}}/>
                    <Tab.Screen name='DocPage' component={DocPage} options={{title:'Doc Page'}}/>
                </>
            ) : undefined }
            { appName === '3d-kitten' ? (
                <>
                    <Tab.Screen name='Game' component={Game} options={{title:'Game'}}/>
                </>
            ) : undefined }
            { appName === 'angel-kitten' ? (
                <>
                    <Tab.Screen name='SupplicantInfo' component={SupplicantInfo} options={{title:'Supplicant Info'}}/>
                    <Tab.Screen name='Helping' component={Helping} options={{title:'Helping Will'}}/>
                </>
            ) : undefined }
            { (appName === 'lab-kitten' || appName === 'doc-kitten') ? (
                <>
                    <Tab.Screen name='SignUp' component={SignUp} options={{title:'Auth'}}/>
                </>
            ) : undefined }
 */
