import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Table } from 'semantic-ui-react';
import { Link,useNavigate } from 'react-router-dom';

const LastRunInformation = () => {
    const [myArray, setMyArray] = useState([]);
    const navigate = useNavigate();
    useEffect(() => {
        loadata();
        const refresh = setInterval(loadata, 10000);

        return () => {
            clearInterval(refresh); // Clear the interval when the component is unmounted
        };
    }, []);

    const loadata = () => {
        try {
            axios.get(`${process.env.REACT_APP_API_URL}/api/history`)
                .then(response => {
                    // Update MyArray state with the fetched data
                    setMyArray(response.data);
                })
                .catch(error => {
                    console.log('Error:', error);
                });
        } catch (error) {
            console.log(error);
        }
    };

    const handleLinkClick = (e, name) => {
        e.preventDefault();
        console.log(name)
        navigate(`/final-results/${name}`);
    };

    return (
        <Container>
            <Table celled>
                <Table.Header>
                    <Table.Row>
                        {myArray.length > 0 &&
                            Object.keys(myArray[0]).map((key, index) => (
                                <Table.HeaderCell key={index}>{key}</Table.HeaderCell>
                            ))}
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {myArray.map((row, rowIndex) => (
                        <Table.Row key={rowIndex}>
                            {Object.keys(row).map((key, cellIndex) => (
                                <Table.Cell key={cellIndex}>
                                    {key === 'patient_name' ? (
                                        <Link
                                            to={`/final-results/${row[key]}`}
                                            onClick={(e) => handleLinkClick(e, row[key])}
                                        >
                                            {row[key]}
                                        </Link>
                                    ) : (
                                        row[key]
                                    )}
                                </Table.Cell>
                            ))}
                        </Table.Row>
                    ))}
                </Table.Body>
            </Table>
        </Container>
    );
};

export default LastRunInformation;
