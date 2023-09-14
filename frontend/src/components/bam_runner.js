import React, { useState, } from "react";
import { Container, Form, Input, Label } from 'semantic-ui-react';
import { useNavigate } from 'react-router-dom';
import axios from "axios";

import Notification from "./notification";
import LastRunInformation from "./info";




const Pgx_bam_form = () => {
  const [sorted_bam, setSorted_bam] = useState("");
  const [sorted_bam_bai, setSorted_bam_bai] = useState("");
  const [vcf_file, setVcf_file] = useState("");
  const [vcf_file_tbi, setVcf_file_tbi] = useState("");
  const [patient_name, setPatient_name] = useState("");
  const [notification,setNotification] = useState([])


  const history = useNavigate();
  
  const printFormData = (formData) => {
    for (let pair of formData.entries()) {
      console.log(pair[0] + ', ' + pair[1]);
    }
  };
  const resetFormFields = () => {
    setSorted_bam("");
    setSorted_bam_bai("");
    setVcf_file("");
    setVcf_file_tbi("");
    setPatient_name("");
  };
  
  const removeNotification = (notificationToRemove) => {
    setNotification(notification.filter(notification => notification !== notificationToRemove));
  };
  // Usage:
  const addNotification = (message, type) => {
    const newNotification = { message, type };

    setNotification([...notification, newNotification]);

    // Automatically remove the notification after a delay
    setTimeout(() => {
      removeNotification(newNotification);
    }, 7000); // 5 seconds
  };


  

  const FileHandler = async (e) => {
    e.preventDefault();
    if (sorted_bam && vcf_file) {
      console.log(sorted_bam["name"],vcf_file)
      const formField = new FormData();
      formField.append('sorted_bam', sorted_bam);
      formField.append('sorted_bam_bai', sorted_bam_bai);
      formField.append('vcf_file', vcf_file);
      formField.append('vcf_file_tbi', vcf_file_tbi);
      formField.append('patient_name', patient_name);
      addNotification(`Pipeline Started for ${patient_name}`,"success")
      function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
          var cookies = document.cookie.split(';');
          for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();  // Use native trim method
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
            }
          }
        }
        return cookieValue;
      }
      
      try {
        await axios({
          method: 'POST',
          url:`${process.env.REACT_APP_API_URL}/api/bam_runner`,
          headers: {
            'Content-Type': 'multipart/form-data',    
            'X-CSRFToken': getCookie('csrftoken') // Replace with your actual CSRF token
          },
          data:formField


        }).then(()=>{
          
          // history.push("/final-results")
          addNotification(`Pipeline Completed for ${patient_name}`,"success")
          resetFormFields();
        });
        
        
        
      } catch (error) {
        console.error('An error occurred:', error);
        addNotification("Error in pipeline","error")
      }
    } else {
      alert('Please fill all the fields');
    }
    
  };
  
  return (
    <div>

    
    <Container textAlign="left">

    <Notification notifications={notification} removeNotification={removeNotification}/>

      <h3 className="">PGx Bam Pipeline</h3>
      <Form size="large" onSubmit={FileHandler}>
        <Form.Field>
          <Label>Patient Name</Label>
          <Form.Input
            placeholder="patient name"
            type="text"
            value = {patient_name}
            onChange={(e) => setPatient_name(e.target.value)}
          />
        </Form.Field>
        <Form.Field>
          <Label>Sorted Bam File</Label>
          <Form.Input
            type="file"
            onChange={(e) => setSorted_bam(e.target.files[0])}
          />
        </Form.Field>
        <Form.Field>
          <Label>Sorted Bam bai File</Label>
          <Form.Input
            type="file"
            onChange={(e) => setSorted_bam_bai(e.target.files[0])}
          />
        </Form.Field>
        <Form.Field>
          <Label>VCF File</Label>
          <Form.Input
            type="file"
            onChange={(e) => setVcf_file(e.target.files[0])}
          />
        </Form.Field>
        <Form.Field>
          <Label>VCF File tbi</Label>
          <Form.Input
            type="file"
            onChange={(e) => setVcf_file_tbi(e.target.files[0])}
          />
        </Form.Field>
        <Form.Button type="submit">Submit</Form.Button>
      </Form>
    </Container>
    <br>
    </br>
    <LastRunInformation/>
    </div>
  );
};

export default Pgx_bam_form;
