import './App.css';
import './Styles/Learn.css';
import { Routes, Route } from 'react-router-dom';
import About from "./Pages/About.jsx";
import Menu from "./Components/Menu.js"
import Learn from './Pages/Learn.jsx';
import Quiz from './Pages/Quiz.jsx';
import Track from './Pages/Track.jsx';

function Dashboard() {
  return (
    <div className="contentcontainer">
      <div className='infobox'>
        <h1 style={{textAlign: "center"}}>NEWS</h1>
        <p>"Children are better at learning than adults. This is due to many reasons, such as adults not caring about stuff." - Disgraced Chemist</p>
        <a href='h'>Learn more</a>
      </div>
      <div className='infobox'>
        <h1 style={{textAlign: "center"}}>Your Lessons</h1>
        <p>Biology - The Immune System</p>
        <p>Physics - Alternating and Direct Current</p>
        <a href='/Learn'>Get started</a>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <div className="page">
      <Menu/>
      <Routes>
        <Route path="/About" element={<About />} />
        <Route path="/" element={<Dashboard />} />
        <Route path="/Learn/*" element={<Learn />} />
        <Route path="/Quiz/*" element={<Quiz />} />
        <Route path="/Track" element={<Track />} />
      </Routes>
    </div>
  );
}