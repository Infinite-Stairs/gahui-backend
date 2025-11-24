import { useState } from 'react'
import './App.css'
import Title from './layout/Title'
import {BrowserRouter as Router, Routes, Route} from "react-router-dom"

const App = () => {

  return (
    <>
    <Router>
      <Routes>
        <Route path="/" element={<Title />} /> 
      </Routes>
    </Router>
    </>
  );
}

export default App