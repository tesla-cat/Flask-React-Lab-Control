
import React from 'react'
import {
    View, Text, TextInput, TouchableOpacity, 
    FlatList, Image, StyleSheet
} from 'react-native'


export {Input, Txt, Btn, Btn2, Icon, Avatar, Body, Row, List, 
    IconBtn, Box, Dummy, Link, Frame}

const Input = ({children, p, on, n, w})=>
    <TextInput 
        style={[{
            outline: 'none', 
            fontSize:18, 
            fontWeight:'bold',
            color:'blue', 
            textAlign:'center', 
            alignSelf:'center',
            padding:4,
            margin: 6,
            width: w,
        }, n>1 ? inputStyles.multiLine : inputStyles.oneLine ]} 
        value={children} 
        placeholder={p} 
        onChangeText={on}
        numberOfLines={n}
        multiline={n>1}
    ></TextInput>

const inputStyles = StyleSheet.create({
    oneLine: {
        borderBottomWidth:3,
        borderBottomColor:'skyblue', 
    },
    multiLine: {
        borderWidth:3,
        borderColor:'skyblue',
        borderRadius: 30,  
    }
})

const Txt = ({children,c,s=16,f='ZCOOLXiaoWei', v, ctr})=>
    <Text style={{
        fontSize:s, fontFamily:f, fontWeight:'bold', color:c,
        writingMode:v && 'vertical-rl', 
        textAlign:ctr && 'center',
        flexWrap:'wrap',
    }}>{children}</Text>

const Btn = ({children, on, c='white',bg='grey'})=>
    <TouchableOpacity 
        style={{
            backgroundColor:bg, 
            margin:10, 
            paddingHorizontal:20, 
            paddingVertical:5,
            borderRadius:30, 
            justifyContent:'center',
            alignItems:'center',
        }} 
        onPress={on}
    >
        <Txt c={c}>{children}</Txt>
    </TouchableOpacity>

const Btn2 = ({children, on, c})=>
    <TouchableOpacity onPress={on}>
        <Txt c={c}>{children}</Txt>
    </TouchableOpacity>

const uri0 = 'https://raw.githubusercontent.com/lab-kitten/lab-kitten/master/images/icons/'
function iconUri(name){ return [uri0,name,'.svg'].join('') }
const Icon = ({children, s=25})=>
    <View 
        style={{
            height:s, 
            width:s,
            padding:3,
        }}
    >
        <Image 
            style={{flex:1}} 
            resizeMode='contain' 
            source={{uri: iconUri(children) }}
        ></Image>
    </View>

const IconBtn = ({children, on, s})=>
    <TouchableOpacity 
        onPress={on} 
    >
        <Icon s={s}>{children}</Icon>
    </TouchableOpacity>

const Avatar = ({children, s=25, r})=>
    <View 
        style={{
            height:s, 
            width:s 
        }}
    >
        <Image 
            style={{flex:1, borderRadius:r}} 
            source={{uri: children}}
        ></Image>
    </View>

const Body = ({children, style})=>
    <View 
        style={[{
            backgroundColor:'white', 
            flex:1, 
            justifyContent:'center'
        }, style]}
    >
        {children}
    </View>

const Row = ({children, style})=>
    <View 
        style={[{
            flexDirection:'row', 
            justifyContent:'space-evenly', 
            alignItems:'center',
            flexWrap:'wrap',
        }, style]}
    >
        {children}
    </View>

const Box = ({children,f, h, w})=>
    <View 
        style={{
            flex:f, 
            height:h, 
            width:w 
        }}
    >
        {children}
    </View>

const Dummy=()=> <View style={{flex:1}}></View>

const List = ({children, Card})=>
    <FlatList 
        data={Object.entries(children)} 
        keyExtractor={item=>item[0]} 
        renderItem={({item,index})=>(
            <Card id={item[0]} data={item[1]} index={index}></Card>
        )}
    ></FlatList>

// ========== not react native ==========

function Link({children, h}){
    if(h.startsWith('#')) return <a href={h} style={{margin:6}}>{children}</a>
    else return <a href={h} style={{margin:6}} target='_blank'>{children}</a>
}

function Frame({children, w,h}){
    return <iframe width={w} height={h} src={children} frameBorder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowFullScreen></iframe>
}