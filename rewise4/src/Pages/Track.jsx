// import { useNavigate } from 'react-router-dom';
import { Routes, Route } from 'react-router-dom';
// import { NavLink } from "react-router-dom";
import About from "./About.jsx";
import Menu from "../Components/Menu.js"
import '../Styles/Track.css'
// import child1 from "../Data/Leo.png"

function Sidebar() {
  return (
    <div className='sidebar'>
      {/* <div> */}
        {/* <img source={child1} alt={"Hi"}/> */}
      {/* </div> */}
    </div>
  );
}

function Interface() {
  return (
    <div>
      <Sidebar />
      {/* Stats page */}
    </div>
  );
}

const Track = () => {
  return (
    <div>
      <Routes>
        <Route path="/Track" element={<Track />} />
        <Route path="/About" element={<About />} />
        <Route path="/" element={<Interface />} />
      </Routes>
    </div>
  );
};

export default Track;