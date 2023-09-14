import React, { useEffect, useState } from "react";
import axios from "axios";
import { Container, Menu, Segment,Table } from 'semantic-ui-react'
import { useParams } from 'react-router-dom';
const Final_Results = () => {
    const [activeItem, setActiveItem] = useState("Aldy results");
    const [Edata, setData] = useState([]);
    const {patientName} = useParams()
    console.log(patientName)
    useEffect(() => {
        fetchData(activeItem);
    }, [activeItem, patientName]);

    const handleItemClick = (e, { name }) => {
        setActiveItem(name);
    };
    const ArrayData = async ()=>{
        let response = await axios.get(`${process.env.REACT_APP_API_URL}/api/results5/${patientName}`);
        const res = response.data
        console.log(res);
        setData(res);
    }
    const fetchData = async (itemName) => {
        try {
            let response;
            if (itemName === "Aldy results") {
                response = await axios.get(`${process.env.REACT_APP_API_URL}/api/results1/${patientName}`);
            } else if (itemName === "Additional Gene results") {
                response = await axios.get(`${process.env.REACT_APP_API_URL}/api/results4/${patientName}`);
            } else if (itemName === "Final results") {
                // Handle fetching of final results
                ArrayData()
            }

            if (response) {
                const responseData = response.data;
                console.log(responseData)
                const fixedData = responseData.replace(/NaN/g, 'null');
                const parsedData = JSON.parse(fixedData);
                setData(parsedData);
            }
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };
    return (
        <div style={{ overflowX: 'auto' }} >

            <Menu attached='top' tabular>
                <Menu.Item
                    name='Aldy results'
                    active={activeItem === 'result 1'}
                    onClick={handleItemClick}
                />
                <Menu.Item
                    name='Additional Gene results'
                    active={activeItem === 'result 4'}
                    onClick={handleItemClick}
                />
                 <Menu.Item
                    name='Final results'
                    active={activeItem === 'result 4'}
                    onClick={handleItemClick}
                />
            </Menu>

            <Segment attached='bottom'>
                <h2>{activeItem}</h2>
                <Table celled striped>
                    <Table.Header>
                        <Table.Row>
                            {Edata.length > 0 && Object.keys(Edata[0]).map((key, index) => (
                                <Table.HeaderCell key={index}>{key}</Table.HeaderCell>
                            ))}
                        </Table.Row>
                    </Table.Header>
                    <Table.Body >
                        {Edata.map((row, index) => (
                            <Table.Row key={index}>
                                {Object.values(row).map((value, index) => (
                                    <Table.Cell collapsing key={index}>{value}</Table.Cell>
                                ))}
                            </Table.Row>
                        ))}
                    </Table.Body>
                </Table>
            </Segment>
        </div>
        
    );
}

export default Final_Results;
