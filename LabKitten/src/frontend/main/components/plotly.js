
import React from 'react'
import Plotly from "plotly.js/dist/plotly"
import createPlotlyComponent from "react-plotly.js/factory"
const Plot = createPlotlyComponent(Plotly)

export {Plots, Plot}

function Plots({children}){
    const {plots, commonX} = children
    return plots.map((plot, idx)=>{
        const {data, layout} = plot
        data.map((d,i)=>{ 
            if(d.x == 'commonX') data[i].x = commonX
        })
        return <Plot key={idx} data={data} layout={layout}/>
    })
}