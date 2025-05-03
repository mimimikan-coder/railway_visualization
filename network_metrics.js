import React, {useState, useEffect} from "react";
import axios from "axios";
import {BarChart, Bar, XAxis, YAxis, Tooltip, Legend, CartesianGrid, ResponsiveContainer} from "recharts";

const NetworkMetrics = () => {
    const [data, setData] = useState([]);

    useEffect(() => {
        axios.get("https://localhost:5000/network-metrics")
        .then((res)=>{
            const metrics = res.data;
            const charData = [
                {name: "average path length", value: metrics.average_path_length},
                {name: "network density", value:metrics.density},
                {name: "clustering coef", value:metricsl.clustering_coef}
            ];
            setData(charData);
        })
        .catch((error) => console.error("ERROR:", error));
    }, []);

    return (
        <ResponsiveContainer width="100%" height={400}>
            <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#8884d8" />
            </BarChart>
        </ResponsiveContainer>
    );
};

export default NetworkMetrics;