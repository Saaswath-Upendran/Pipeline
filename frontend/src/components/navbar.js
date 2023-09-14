import React from 'react';
import { Menu } from 'semantic-ui-react';
import { Link } from 'react-router-dom';

const NavBar = () => {
  return (
    <Menu>
      <Menu.Item header> PGx Pipeline</Menu.Item>
      {/* <Menu.Item as={Link} to="/" exact>
        Home
      </Menu.Item> */}
      <Menu.Item as={Link} to="/">
        Bam Pipeline
      </Menu.Item>
      {/* <Menu.Item as={Link} to="/final-results/:patientName">
        Final Results
      </Menu.Item> */}
      {/* <Menu.Item as={Link} to="/history">
        Previous Run 
      </Menu.Item> */}
      {/* <Menu.Item as={Link} to="/contact">
        Contact
      </Menu.Item> */}
    </Menu>
  );
};

export default NavBar;
