
import React, { useState, useEffect, useRef } from 'react'
import {List, Body, Box} from '../components/main'
import {ExperimentCard} from '../components/cards'
import {auth, getExperiments } from '../functionalities/firebase'
import { useNavigation } from '@react-navigation/native'

import {Canvas, useFrame, extend, useThree } from 'react-three-fiber'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'

extend({ OrbitControls })


export {Three}


function Three(){
    
    return(
        <Body>
            <Canvas>
                <ambientLight></ambientLight>
                <pointLight position={[10,10,10]}></pointLight>
                <ThreeBox position={[0, 0, 0]}></ThreeBox>
                <Control />
            </Canvas>
        </Body>
    )
}



function ThreeBox(props){
    const mesh = useRef()
    const [hovered, setHovered] = useState(false)
    const [active, setActive] = useState(false)

    function sinWave(f,phi){
        var t = new Date().getTime() // ms
        var y = Math.sin( 2*Math.PI*f*t/1000 + phi )
        return y
    }

    const [render, setRender] = useState(false)
    useEffect(()=>{
        setTimeout(()=>{
            setRender(!render)
            mesh.current.position.x = sinWave(1, 0)
            mesh.current.position.y = sinWave(1, Math.PI/2)
        },10) // 100 fps
    },[render])

    return(
        <mesh {...props} ref={mesh} 
            scale = {active ? [1.5, 1.5, 1.5] : [1, 1, 1] }
            onClick = {()=>setActive(!active)}
            onPointerOver = {()=>setHovered(true)}
            onPointerOut = {()=>setHovered(false)}     
        >
            <boxGeometry attach='geometry' args={[1, 1, 1]}></boxGeometry>
            <meshStandardMaterial attach='material' color={hovered ? 'hotpink' : 'yellow' }></meshStandardMaterial>
        </mesh>
    )
}


  
function Control(){
    const {camera, gl:{ domElement } } = useThree()
    return <orbitControls args={[camera, domElement]}/>
}


