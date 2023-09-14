import React from 'react';
import './App.css';
import { Route, Routes } from "react-router-dom"
// import HomePage from './components/home';
import NavBar from './components/navbar';
import Pgx_bam_form from './components/bam_runner';
import Final_Results from './components/final_results_view';
import LastRunInformation from './components/info';


function App() {
  return (
      <div className="App">
        <NavBar/>
        <Routes>
            {/* <Route path="/" element={<HomePage/>} /> */}
            <Route path="/" element={<Pgx_bam_form/>} />
            <Route path="/final-results/:patientName" element={<Final_Results/>} />
            {/* <Route path='/history' element={<LastRunInformation/>}></Route> */}
        </Routes>


      </div>
  );
}

export default App;
