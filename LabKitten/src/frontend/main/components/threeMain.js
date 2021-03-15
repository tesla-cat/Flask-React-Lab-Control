
import React,{useState, useEffect} from 'react'
import { Canvas, extend, useThree} from 'react-three-fiber'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'

export {Ball,BallWithPath,  OrbControl, MyCanvas}

extend({ OrbitControls })

const Ball = ({p=[0,0,0], r=1, c='blue', opa=1, t=true})=>
    <mesh position={p} >
        <sphereGeometry attach='geometry' args={[r,32,32]}/>
        <meshStandardMaterial attach='material' color={c} opacity={opa} transparent={t}/>
    </mesh>

function BallWithPath({p=[0,0,0], r=0.05, c='blue', opa=1, n=6}){
    const [posList, setPosList] = useState(Array(n).fill(p))
    useEffect(()=>{
        var pl = [...posList]
        pl.push(p)
        pl.shift() 
        setPosList(pl)
    },[p])
    return posList.reverse().map((pos, index) =>{
        var decay = 0.9**index
        return <Ball p={pos} r={r*decay} c={c} opa={opa*decay} t={false}/>
    })
}

function OrbControl(){
    const {camera, gl: {domElement}} = useThree()
    return <orbitControls args={[camera, domElement]}/>
}

const MyCanvas = ({ children, ambI=0.2, ptPos=[0,0,2], ptI=10 })=>
    <Canvas>
        <ambientLight intensity={ambI}/>
        <pointLight position={ptPos} intensity={ptI} />
        <axesHelper/>
        <OrbControl/>
        {children}
    </Canvas>