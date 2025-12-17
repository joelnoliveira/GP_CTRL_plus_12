import { Link } from "react-router-dom";
import Logo from "../components/Logo.jsx";
import Button from "../components/Button.jsx"
import UserIcon from "../components/UserIcon.jsx"
import "../styles/components/navbar.css"

export default function Navbar(
  {
    isLoggedIn = false,
  }
) {
  return (
    <div className="navbar">
      <Link to="/">
          <Logo 
            size="medium"
          />
      </Link>

      {isLoggedIn ? 
        (
          <UserIcon 
            size="large"
          />
        ) 
        :
        (
          <div className="navbar__btn-container">
            <Link to="/register">
              <Button 
                size={"large"}
                variant={"default"}
                text={"Register"}
              />
            </Link>

            <Link to="/login">
              <Button 
                size={"large"}
                variant={"alternative"}
                text={"Login"}
              />
            </Link>
        </div>
        )
      }
    </div>
  );
}
