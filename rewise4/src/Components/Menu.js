import { NavLink } from 'react-router-dom';
import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import NavDropdown from 'react-bootstrap/NavDropdown';
import '../Styles/Menu.css';

function Menu() {
  return (
    <Navbar bg="dark" data-bs-theme="dark" expand="lg" className="bg-body-tertiary">
      <Container>
        <Navbar.Brand as={NavLink} to="/" end>REWISE4</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link as={NavLink} to="/Learn">Learn</Nav.Link>
            <Nav.Link as={NavLink} to="/Quiz">Quiz</Nav.Link>
            <Nav.Link as={NavLink} to="/Track">Track</Nav.Link>
            <Nav.Link as={NavLink} to="/About">About</Nav.Link>
            <Nav.Link as={NavLink} to="https://flockx.io">FlockX</Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}

export default Menu;